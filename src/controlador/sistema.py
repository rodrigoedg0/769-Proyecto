import os
import base64
import hashlib
import secrets
from datetime import datetime, timedelta
from src.modelo.vehiculo import Vehiculo
from src.modelo.movimiento import Movimiento
from src.modelo.parqueo import Parqueo


class Sistema:
    MAX_INTENTOS_LOGIN = 4
    BLOQUEO_LOGIN_MINUTOS = 3

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
            with open(ruta, "w") as f:
                f.write("tarifa_hora=5\n")
        self._inicializar_cifrado_usuarios()
        self._migrar_usuarios_a_cifrado()

    def _inicializar_cifrado_usuarios(self):
        self.ruta_key_usuarios = "data/configuracion/usuarios.key"
        if not os.path.exists(self.ruta_key_usuarios):
            with open(self.ruta_key_usuarios, "w", encoding="utf-8") as f:
                f.write(secrets.token_hex(32))

        with open(self.ruta_key_usuarios, "r", encoding="utf-8") as f:
            self._key_usuarios = f.read().strip()

    def _derivar_llave(self):
        return hashlib.sha256(self._key_usuarios.encode("utf-8")).digest()

    def _cifrar_linea_usuario(self, texto):
        datos = texto.encode("utf-8")
        llave = self._derivar_llave()
        cifrado = bytes(b ^ llave[i % len(llave)] for i, b in enumerate(datos))
        token = base64.urlsafe_b64encode(cifrado).decode("ascii")
        return f"ENC:{token}\n"

    def _descifrar_linea_usuario(self, linea):
        linea = linea.strip()
        if not linea:
            return ""
        if not linea.startswith("ENC:"):
            return linea
        token = linea[4:]
        try:
            cifrado = base64.urlsafe_b64decode(token.encode("ascii"))
            llave = self._derivar_llave()
            datos = bytes(b ^ llave[i % len(llave)] for i, b in enumerate(cifrado))
            return datos.decode("utf-8")
        except Exception:
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
                if len(partes) != 3:
                    continue
                u, p, r = partes
                usuarios.append({"username": u, "password": p, "rol": r})
        return usuarios

    def _guardar_usuarios(self, usuarios):
        ruta = "data/configuracion/usuarios.txt"
        with open(ruta, "w", encoding="utf-8") as f:
            for user in usuarios:
                plano = f"{user['username']},{user['password']},{user['rol']}"
                f.write(self._cifrar_linea_usuario(plano))

    def _migrar_usuarios_a_cifrado(self):
        usuarios = self._cargar_usuarios()
        if not usuarios:
            return
        self._guardar_usuarios(usuarios)

    # -------------------------
    # TARIFA
    # -------------------------
    def obtener_tarifa(self):
        with open("data/configuracion/tarifa.txt", "r") as f:
            return float(f.readline().split("=")[1])

    def actualizar_tarifa(self, nueva):
        with open("data/configuracion/tarifa.txt", "w") as f:
            f.write(f"tarifa_hora={nueva}\n")

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

    def recuperar_contrasena(self, username, nueva_password, confirmacion):
        username = username.strip()
        nueva_password = nueva_password.strip()
        confirmacion = confirmacion.strip()

        if not username or not nueva_password or not confirmacion:
            return "verifique sus datos"
        if nueva_password != confirmacion:
            return "verifique su contraseña"
        if not os.path.exists("data/configuracion/usuarios.txt"):
            return "No hay usuarios registrados"

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
            f"{user['username']},{user['password']},{user['rol']}\n"
            for user in self._cargar_usuarios()
        ]

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

        if not self.parqueo.hay_espacio():
            return "Parqueo lleno"

        if placa not in self.parqueo.ocupados():
            self.parqueo.ingresar(placa)

        mov = Movimiento(placa)
        ruta = f"data/movimientos/{placa}_historial.txt"

        with open(ruta, "a") as f:
            f.write(mov.to_txt_entrada())

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
        with open(ruta, "r") as f:
            for linea in f:
                if linea.startswith("ENTRADA"):
                    fecha_str = linea.strip().split(",")[1]
                    ultima_entrada = datetime.fromisoformat(fecha_str)

        if not ultima_entrada:
            return "No se encontró entrada registrada"

        salida = datetime.now()

        tiempo = salida - ultima_entrada
        minutos = tiempo.total_seconds() / 60

        bloques = int(minutos // 30)
        if minutos % 30 > 0:
            bloques += 1

        total = bloques * 5

        mov = Movimiento(placa)
        mov.salida = salida
        mov.total = total

        with open(ruta, "a") as f:
            f.write(mov.to_txt_salida())

        self.parqueo.retirar(placa)

        self.log(f"Salida: {placa} - Q{mov.total}")
        return f"Salida registrada. Total a pagar: Q{mov.total}"

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