import os
import base64
import hashlib
from datetime import datetime, timedelta
from src.modelo.vehiculo import Vehiculo
from src.modelo.movimiento import Movimiento
from src.modelo.parqueo import Parqueo


class Sistema:
    MAX_INTENTOS_LOGIN = 4
    BLOQUEO_LOGIN_MINUTOS = 3
    TARIFA_HORA_POR_DEFECTO = 5.0
    TARIFA_MEDIA_HORA_POR_DEFECTO = 2.5
    CONFIG_PARQUEO_RUTA = "data/configuracion/parqueo_config.txt"
    TIPOS_PARQUEO_BASE = ("moto", "carro", "camion", "transporte pesado")
    MINUTOS_EXPIRACION_PIN = 10

    def __init__(self):
        self.parqueo = Parqueo()
        self.usuario_actual = None
        self.intentos_fallidos = {}
        self.bloqueos_login = {}
        self.ultimo_error_login = ""
        self.crear_estructura()
        self.inicializar_config()

    # -------------------------
    # ESTRUCTURA
    # -------------------------
    def crear_estructura(self):
        rutas = [
            "data/configuracion",
            "data/vehiculos",
            "data/movimientos",
            "data/reportes",
            "data/auditoria"
        ]
        for ruta in rutas:
            os.makedirs(ruta, exist_ok=True)

    def inicializar_config(self):
        ruta = "data/configuracion/tarifa.txt"
        if not os.path.exists(ruta):
            self._guardar_tarifas_config(
                self.TARIFA_HORA_POR_DEFECTO,
                self.TARIFA_MEDIA_HORA_POR_DEFECTO
            )
        else:
            tarifa_hora, tarifa_media_hora = self._leer_tarifas_config()
            self._guardar_tarifas_config(tarifa_hora, tarifa_media_hora)
        self._inicializar_config_parqueo()
        self._migrar_usuarios_a_formato_simple()

    def _leer_tarifas_config(self):
        ruta = "data/configuracion/tarifa.txt"
        tarifa_hora = None
        tarifa_media_hora = None

        try:
            with open(ruta, "r", encoding="utf-8") as f:
                for linea in f:
                    if "=" not in linea:
                        continue
                    clave, valor = linea.strip().split("=", 1)
                    try:
                        numero = float(valor)
                    except ValueError:
                        continue

                    if clave == "tarifa_hora":
                        tarifa_hora = numero
                    elif clave == "tarifa_media_hora":
                        tarifa_media_hora = numero
        except FileNotFoundError:
            return self.TARIFA_HORA_POR_DEFECTO, self.TARIFA_MEDIA_HORA_POR_DEFECTO

        if tarifa_hora is None:
            tarifa_hora = self.TARIFA_HORA_POR_DEFECTO
        if tarifa_media_hora is None:
            tarifa_media_hora = tarifa_hora / 2
        return tarifa_hora, tarifa_media_hora

    def _guardar_tarifas_config(self, tarifa_hora, tarifa_media_hora):
        with open("data/configuracion/tarifa.txt", "w", encoding="utf-8") as f:
            f.write(f"tarifa_hora={tarifa_hora}\n")
            f.write(f"tarifa_media_hora={tarifa_media_hora}\n")

    def _config_parqueo_por_defecto(self):
        return {
            "moto": {"habilitado": True, "capacidad": 15, "tarifa_hora": 10.0, "tarifa_media_hora": 5.0},
            "carro": {"habilitado": True, "capacidad": 20, "tarifa_hora": 12.0, "tarifa_media_hora": 6.0},
            "camion": {"habilitado": True, "capacidad": 8, "tarifa_hora": 20.0, "tarifa_media_hora": 10.0},
            "transporte pesado": {"habilitado": True, "capacidad": 5, "tarifa_hora": 25.0, "tarifa_media_hora": 12.5},
        }

    def _inicializar_config_parqueo(self):
        config = self._cargar_configuracion_parqueo()
        self._guardar_configuracion_parqueo(config)

    def _cargar_configuracion_parqueo(self):
        defaults = self._config_parqueo_por_defecto()
        config = {}

        if os.path.exists(self.CONFIG_PARQUEO_RUTA):
            with open(self.CONFIG_PARQUEO_RUTA, "r", encoding="utf-8") as f:
                for linea in f:
                    partes = [p.strip() for p in linea.strip().split("|")]
                    if len(partes) != 5:
                        continue
                    tipo, habilitado_txt, capacidad_txt, tarifa_hora_txt, tarifa_media_txt = partes
                    try:
                        config[tipo.lower()] = {
                            "habilitado": habilitado_txt == "1",
                            "capacidad": int(capacidad_txt),
                            "tarifa_hora": float(tarifa_hora_txt),
                            "tarifa_media_hora": float(tarifa_media_txt),
                        }
                    except ValueError:
                        continue

        for tipo, valores in defaults.items():
            if tipo not in config:
                config[tipo] = dict(valores)
        return config

    def _guardar_configuracion_parqueo(self, config):
        lineas = []
        for tipo in self.TIPOS_PARQUEO_BASE:
            valores = config.get(tipo)
            if not valores:
                continue
            habilitado = "1" if valores.get("habilitado", True) else "0"
            capacidad = int(valores.get("capacidad", 0))
            tarifa_hora = float(valores.get("tarifa_hora", 0))
            tarifa_media = float(valores.get("tarifa_media_hora", 0))
            lineas.append(f"{tipo}|{habilitado}|{capacidad}|{tarifa_hora}|{tarifa_media}\n")

        with open(self.CONFIG_PARQUEO_RUTA, "w", encoding="utf-8") as f:
            f.writelines(lineas)

    def _cifrar_linea_usuario(self, texto):
        token = base64.urlsafe_b64encode(texto.encode("utf-8")).decode("ascii")
        return f"ENC2:{token}\n"

    def _descifrar_linea_legacy(self, token):
        ruta_key = "data/configuracion/usuarios.key"
        if not os.path.exists(ruta_key):
            return ""
        with open(ruta_key, "r", encoding="utf-8") as f:
            llave_txt = f.read().strip()
        if not llave_txt:
            return ""

        try:
            cifrado = base64.urlsafe_b64decode(token.encode("ascii"))
            llave = hashlib.sha256(llave_txt.encode("utf-8")).digest()
            datos = bytes(b ^ llave[i % len(llave)] for i, b in enumerate(cifrado))
            return datos.decode("utf-8")
        except Exception:
            return ""

    def _descifrar_linea_usuario(self, linea):
        linea = linea.strip()
        if not linea:
            return ""
        if linea.startswith("ENC2:"):
            token = linea[5:]
            try:
                return base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8")
            except Exception:
                return ""
        if linea.startswith("ENC:"):
            return self._descifrar_linea_legacy(linea[4:])
        if not linea.startswith("ENC"):
            return linea
        return ""

    def _cargar_usuarios(self):
        ruta = "data/configuracion/usuarios.txt"
        usuarios = []
        if not os.path.exists(ruta):
            return usuarios

        with open(ruta, "r", encoding="utf-8") as f:
            for linea in f:
                contenido = self._descifrar_linea_usuario(linea)
                if not contenido:
                    continue
                partes = contenido.strip().split(",")
                if len(partes) < 3:
                    continue
                u, p, r = partes[:3]
                correo = partes[3] if len(partes) > 3 else ""
                usuarios.append({"username": u, "password": p, "rol": r, "correo": correo})
        return usuarios

    def _guardar_usuarios(self, usuarios):
        ruta = "data/configuracion/usuarios.txt"
        with open(ruta, "w", encoding="utf-8") as f:
            for user in usuarios:
                plano = f"{user['username']},{user['password']},{user['rol']},{user.get('correo', '')}"
                f.write(self._cifrar_linea_usuario(plano))

    def _migrar_usuarios_a_formato_simple(self):
        usuarios = self._cargar_usuarios()
        if not usuarios:
            return
        self._guardar_usuarios(usuarios)

    # -------------------------
    # TARIFA
    # -------------------------
    def obtener_configuracion_parqueo(self):
        config = self._cargar_configuracion_parqueo()
        resultado = []
        for tipo in self.TIPOS_PARQUEO_BASE:
            datos = config[tipo]
            usados = self._ocupados_por_tipo().get(tipo, 0)
            disponibles = max(datos["capacidad"] - usados, 0)
            resultado.append(
                {
                    "tipo": tipo,
                    "habilitado": datos["habilitado"],
                    "capacidad": datos["capacidad"],
                    "ocupados": usados,
                    "disponibles": disponibles,
                    "tarifa_hora": datos["tarifa_hora"],
                    "tarifa_media_hora": datos["tarifa_media_hora"],
                }
            )
        return resultado

    def actualizar_configuracion_tipo(self, tipo, habilitado, capacidad, tarifa_hora, tarifa_media_hora):
        tipo = tipo.strip().lower()
        if tipo not in self.TIPOS_PARQUEO_BASE:
            return "Tipo de vehículo no permitido"
        if capacidad < 0:
            return "La capacidad no puede ser negativa"
        if tarifa_hora <= 0 or tarifa_media_hora <= 0:
            return "Las tarifas deben ser mayores a cero"
        ocupados_tipo = self._ocupados_por_tipo().get(tipo, 0)
        if capacidad < ocupados_tipo:
            return (
                f"No se puede asignar {capacidad} espacios a {tipo}, "
                f"actualmente hay {ocupados_tipo} vehículo(s) dentro."
            )

        config = self._cargar_configuracion_parqueo()
        config[tipo] = {
            "habilitado": bool(habilitado),
            "capacidad": int(capacidad),
            "tarifa_hora": float(tarifa_hora),
            "tarifa_media_hora": float(tarifa_media_hora),
        }
        self._guardar_configuracion_parqueo(config)

        if tipo == "carro":
            self._guardar_tarifas_config(float(tarifa_hora), float(tarifa_media_hora))

        self.log(
            f"Configuración {tipo}: habilitado={bool(habilitado)}, "
            f"capacidad={int(capacidad)}, hora=Q{float(tarifa_hora)}, "
            f"media hora=Q{float(tarifa_media_hora)}"
        )
        return "Configuración actualizada"

    def tipos_disponibles_para_registro(self):
        tipos = []
        for item in self.obtener_configuracion_parqueo():
            if item["capacidad"] > 0:
                tipos.append(item["tipo"])
        return tipos

    def obtener_tarifas_por_tipo(self, tipo):
        tipo = tipo.strip().lower()
        config = self._cargar_configuracion_parqueo()
        if tipo not in config:
            return None
        datos = config[tipo]
        return {
            "tarifa_hora": datos["tarifa_hora"],
            "tarifa_media_hora": datos["tarifa_media_hora"]
        }

    def obtener_tarifas(self):
        tarifas_carro = self.obtener_tarifas_por_tipo("carro")
        if tarifas_carro:
            return tarifas_carro
        tarifa_hora, tarifa_media_hora = self._leer_tarifas_config()
        return {"tarifa_hora": tarifa_hora, "tarifa_media_hora": tarifa_media_hora}

    def actualizar_tarifas(self, tarifa_hora, tarifa_media_hora):
        return self.actualizar_configuracion_tipo(
            "carro", True, self._cargar_configuracion_parqueo()["carro"]["capacidad"], tarifa_hora, tarifa_media_hora
        )

    def obtener_tarifa(self):
        return self.obtener_tarifas()["tarifa_hora"]

    def actualizar_tarifa(self, nueva):
        tarifas = self.obtener_tarifas()
        return self.actualizar_tarifas(nueva, tarifas["tarifa_media_hora"])

    # -------------------------
    # BITACORA
    # -------------------------
    def log(self, mensaje):
        with open("data/auditoria/bitacora.txt", "a", encoding="utf-8") as f:
            hora = datetime.now().strftime("%H:%M")
            usuario = self.usuario_actual if self.usuario_actual else "Sistema"
            f.write(f"[{hora}] {usuario} -> {mensaje}\n")

    # -------------------------
    # USUARIOS
    # -------------------------
    def registrar_usuario(self, username, password, confirmacion, rol):
        username = username.strip()
        if username=="" or password=="" or confirmacion=="" or rol=="":
            return "verifique sus datos"
        if password!=confirmacion:
            return "verifique su contraseña"

        usuarios = self._cargar_usuarios()
        for user in usuarios:
            if user["username"] == username:
                return "Usuario ya existe"

        usuarios.append({"username": username, "password": password, "rol": rol})
        self._guardar_usuarios(usuarios)

        self.log(f"Usuario creado: {username}")
        return "Usuario registrado"

    def recuperar_contrasena(self, username, nueva_password, confirmacion, clave_admin):
        username = username.strip()
        nueva_password = nueva_password.strip()
        confirmacion = confirmacion.strip()
        clave_admin = (clave_admin or "").strip()

        if not username or not nueva_password or not confirmacion or not clave_admin:
            return "verifique sus datos"
        if nueva_password != confirmacion:
            return "verifique su contraseña"
        if not self.Es_admin(clave_admin):
            return "Contraseña de administrador incorrecta"

        actualizado = False
        usuarios = self._cargar_usuarios()
        for user in usuarios:
            if user["username"] == username:
                user["password"] = nueva_password
                actualizado = True
                break
        if not actualizado:
            return "Usuario no existe"

        self._guardar_usuarios(usuarios)
        self.intentos_fallidos.pop(username, None)
        self.bloqueos_login.pop(username, None)
        self.log(f"Recuperación de contraseña para usuario: {username}")
        return "Contraseña actualizada"

    def login(self, username, password):
        username = username.strip()
        self.ultimo_error_login = ""

        bloqueado_hasta = self.bloqueos_login.get(username)
        if bloqueado_hasta and datetime.now() < bloqueado_hasta:
            restante = int((bloqueado_hasta - datetime.now()).total_seconds())
            minutos = (restante + 59) // 60
            self.ultimo_error_login = f"Usuario bloqueado. Intente de nuevo en {minutos} minuto(s)."
            return False, None

        if bloqueado_hasta and datetime.now() >= bloqueado_hasta:
            self.bloqueos_login.pop(username, None)

        if not os.path.exists("data/configuracion/usuarios.txt"):
            self.ultimo_error_login = "No hay usuarios registrados."
            return False, None

        for user in self._cargar_usuarios():
            if user["username"] == username and user["password"] == password:
                self.usuario_actual = user["username"]
                self.intentos_fallidos.pop(username, None)
                self.bloqueos_login.pop(username, None)
                self.log("Inicio de sesion")
                return True, user["rol"]

        intentos = self.intentos_fallidos.get(username, 0) + 1
        self.intentos_fallidos[username] = intentos

        if intentos >= self.MAX_INTENTOS_LOGIN:
            self.bloqueos_login[username] = datetime.now() + timedelta(minutes=self.BLOQUEO_LOGIN_MINUTOS)
            self.intentos_fallidos.pop(username, None)
            self.ultimo_error_login = (
                f"Se bloqueó el usuario por {self.BLOQUEO_LOGIN_MINUTOS} minutos "
                f"por demasiados intentos fallidos."
            )
            self.log(f"Bloqueo de login para usuario: {username}")
            return False, None

        restantes = self.MAX_INTENTOS_LOGIN - intentos
        self.ultimo_error_login = f"Login incorrecto. Intentos restantes antes de bloqueo: {restantes}."
        return False, None
    
    def Es_admin(self, contra):
        with open("data/configuracion/contra_admin.txt", "r") as f:
            if (f.readline()) == contra:
                return True
            else:
                return False

    def obtener_usuarios(self):
        if not os.path.exists("data/configuracion/usuarios.txt"):
            return []
        return [
            f"{user['username']},{user['password']},{user['rol']},{user.get('correo', '')}\n"
            for user in self._cargar_usuarios()
        ]

    def validar_admin_actual(self, password):
        if not self.usuario_actual:
            return False, "No hay sesión activa"

        for user in self._cargar_usuarios():
            if user["username"] != self.usuario_actual:
                continue
            if user["rol"] != "admin":
                return False, "Solo un administrador puede cambiar la tarifa"
            if user["password"] != password:
                return False, "Contraseña incorrecta"
            return True, "Validación correcta"

        return False, "Usuario actual no encontrado"

    # -------------------------
    # VEHICULOS
    # -------------------------
    def registrar_vehiculo(self, placa, tipo):
        try:
            v = Vehiculo(placa, tipo)
            ruta = f"data/vehiculos/{v.placa}.txt"

            if os.path.exists(ruta):
                return "Vehiculo ya existe"

            with open(ruta, "w") as f:
                f.write(v.to_txt())

            self.log(f"Registro vehiculo: {v.placa}")
            return "Vehiculo registrado"

        except ValueError as e:
            return str(e)

    def obtener_vehiculos(self):
        return os.listdir("data/vehiculos")

    def obtener_tipo_vehiculo(self, placa):
        ruta = f"data/vehiculos/{placa.upper()}.txt"
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                for linea in f:
                    if linea.lower().startswith("tipo:"):
                        return linea.split(":", 1)[1].strip().lower()
        except FileNotFoundError:
            return None
        return None

    def _ocupados_por_tipo(self):
        conteo = {}
        for placa in self.parqueo.ocupados():
            tipo = self.obtener_tipo_vehiculo(placa)
            if not tipo:
                continue
            conteo[tipo] = conteo.get(tipo, 0) + 1
        return conteo

    # -------------------------
    # MOVIMIENTOS
    # -------------------------
    def registrar_entrada(self, placa):
        placa = placa.upper()
        ruta_vehiculo = f"data/vehiculos/{placa}.txt"

        if not os.path.exists(ruta_vehiculo):
            return "Vehículo no registrado"

        if placa in self.parqueo.ocupados():
            return "El vehículo ya está dentro"

        tipo = self.obtener_tipo_vehiculo(placa)
        if not tipo:
            return "No se pudo determinar el tipo del vehículo"

        config = self._cargar_configuracion_parqueo()
        datos_tipo = config.get(tipo)
        if not datos_tipo:
            return f"El tipo '{tipo}' no está configurado"
        if not datos_tipo["habilitado"]:
            return f"El parqueo no acepta {tipo}"
        if datos_tipo["capacidad"] <= 0:
            return f"No hay espacios configurados para {tipo}"

        ocupados_tipo = self._ocupados_por_tipo().get(tipo, 0)
        if ocupados_tipo >= datos_tipo["capacidad"]:
            return f"No hay espacios disponibles para {tipo}"

        if placa not in self.parqueo.ocupados():
            self.parqueo.ingresar(placa)

        mov = Movimiento(placa)
        ruta = f"data/movimientos/{placa}_historial.txt"
        tarifas = self.obtener_tarifas_por_tipo(tipo)
        linea_entrada = (
            f"ENTRADA,{mov.entrada.isoformat()},"
            f"TIPO:{tipo},"
            f"TARIFA_HORA:{tarifas['tarifa_hora']},"
            f"TARIFA_MEDIA_HORA:{tarifas['tarifa_media_hora']}\n"
        )

        with open(ruta, "a", encoding="utf-8") as f:
            f.write(linea_entrada)

        self.log(f"Entrada: {placa}")
        return f"Entrada registrada: {placa}"

    def registrar_salida(self, placa):
        placa = placa.upper()

        if placa not in self.parqueo.ocupados():
            return f"{placa} no está en el parqueo"

        ruta = f"data/movimientos/{placa}_historial.txt"

        if not os.path.exists(ruta):
            return "No hay historial del vehículo"

        ultima_entrada = None
        tipo_entrada = None
        tarifa_hora_entrada = None
        tarifa_media_hora_entrada = None
        with open(ruta, "r", encoding="utf-8") as f:
            for linea in f:
                if linea.startswith("ENTRADA"):
                    partes = linea.strip().split(",")
                    if len(partes) < 2:
                        continue
                    fecha_str = partes[1]
                    try:
                        ultima_entrada = datetime.fromisoformat(fecha_str)
                    except ValueError:
                        continue
                    tarifa_hora_entrada = None
                    tarifa_media_hora_entrada = None
                    tipo_entrada = None
                    for parte in partes[2:]:
                        if parte.startswith("TIPO:"):
                            tipo_entrada = parte.split(":", 1)[1].strip().lower()
                        if parte.startswith("TARIFA_HORA:"):
                            try:
                                tarifa_hora_entrada = float(parte.split(":", 1)[1])
                            except ValueError:
                                tarifa_hora_entrada = None
                        elif parte.startswith("TARIFA_MEDIA_HORA:"):
                            try:
                                tarifa_media_hora_entrada = float(parte.split(":", 1)[1])
                            except ValueError:
                                tarifa_media_hora_entrada = None

        if not ultima_entrada:
            return "No se encontró entrada registrada"

        if tarifa_hora_entrada is None or tarifa_media_hora_entrada is None:
            tipo_consulta = tipo_entrada or self.obtener_tipo_vehiculo(placa) or "carro"
            tarifas_actuales = self.obtener_tarifas_por_tipo(tipo_consulta) or self.obtener_tarifas()
            if tarifa_hora_entrada is None:
                tarifa_hora_entrada = tarifas_actuales["tarifa_hora"]
            if tarifa_media_hora_entrada is None:
                tarifa_media_hora_entrada = tarifas_actuales["tarifa_media_hora"]

        salida = datetime.now()

        tiempo = salida - ultima_entrada
        minutos = tiempo.total_seconds() / 60
        total = self._calcular_total_parqueo(
            minutos, tarifa_hora_entrada, tarifa_media_hora_entrada
        )

        mov = Movimiento(placa)
        mov.salida = salida
        mov.total = total

        with open(ruta, "a", encoding="utf-8") as f:
            f.write(mov.to_txt_salida())

        self.parqueo.retirar(placa)

        self.log(f"Salida: {placa} - Q{mov.total}")
        return f"Salida registrada. Total a pagar: Q{mov.total}"

    def _calcular_total_parqueo(self, minutos, tarifa_hora, tarifa_media_hora):
        if minutos <= 0:
            return tarifa_media_hora

        horas_completas = int(minutos // 60)
        minutos_restantes = minutos - (horas_completas * 60)
        total = horas_completas * tarifa_hora

        if minutos_restantes > 0:
            if minutos_restantes <= 30:
                total += tarifa_media_hora
            else:
                total += tarifa_hora
        return round(total, 2)

    def vehiculos_activos(self):
        return self.parqueo.ocupados()

    # -------------------------
    # REPORTES
    # -------------------------
    def reporte_movimientos(self):
        carpeta = "data/movimientos"
        datos = []

        for archivo in os.listdir(carpeta):
            with open(os.path.join(carpeta, archivo)) as f:
                datos.append((archivo, len(f.readlines())))

        return datos

    def leer_reporte_movimiento(self, archivo):
        carpeta = "data/movimientos"
        ruta = os.path.normpath(os.path.join(carpeta, archivo))

        if not ruta.startswith(os.path.normpath(carpeta) + os.sep):
            return "Archivo inválido."
        if not os.path.exists(ruta):
            return "El archivo seleccionado no existe."

        with open(ruta, "rb") as f:
            contenido = f.read()

        for encoding in ("utf-8", "latin-1", "cp1252"):
            try:
                return contenido.decode(encoding)
            except UnicodeDecodeError:
                continue

        return contenido.decode("utf-8", errors="replace")

    def ver_bitacora(self):
        ruta = "data/auditoria/bitacora.txt"
        if not os.path.exists(ruta):
            return []
        with open(ruta, "rb") as f:
            contenido = f.read()

        for encoding in ("utf-8", "latin-1", "cp1252"):
            try:
                return contenido.decode(encoding).splitlines(keepends=True)
            except UnicodeDecodeError:
                continue

        return contenido.decode("utf-8", errors="replace").splitlines(keepends=True)