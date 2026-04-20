import os
from datetime import datetime, timedelta
from src.modelo.usuario import Usuario
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
        ruta = "data/configuracion/usuarios.txt"

        if username=="" or password=="" or confirmacion=="" or rol=="":
            return "verifique sus datos"
        
        if password!=confirmacion:
            return "verifique su contraseña"
        
        if os.path.exists(ruta):
            with open(ruta, "r") as f:
                for linea in f:
                    if linea.split(",")[0] == username:
                        return "Usuario ya existe"

        with open(ruta, "a") as f:
            f.write(Usuario(username, password, rol).to_txt())

        self.log(f"Usuario creado: {username}")
        return "Usuario registrado"

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

        ruta = "data/configuracion/usuarios.txt"

        if not os.path.exists(ruta):
            self.ultimo_error_login = "No hay usuarios registrados."
            return False, None

        with open(ruta, "r") as f:
            for linea in f:
                u, p, r = linea.strip().split(",")
                if u == username and p == password:
                    self.usuario_actual = u
                    self.intentos_fallidos.pop(username, None)
                    self.bloqueos_login.pop(username, None)
                    self.log("Inicio de sesion")
                    return True, r

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
        ruta = "data/configuracion/usuarios.txt"
        if not os.path.exists(ruta):
            return []
        with open(ruta, "r") as f:
            return f.readlines()

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

        tarifa = self.obtener_tarifa()

        mov = Movimiento(placa)
        mov.salida = datetime.now()
        mov.total = tarifa

        ruta = f"data/movimientos/{placa}_historial.txt"

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