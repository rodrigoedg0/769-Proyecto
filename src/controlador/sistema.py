import os
from datetime import datetime
from src.modelo.usuario import Usuario
from src.modelo.vehiculo import Vehiculo
from src.modelo.movimiento import Movimiento
from src.modelo.parqueo import Parqueo

class Sistema:
    def __init__(self):
        self.base_path = "data"
        self.parqueo = Parqueo()
        self.usuario_actual = None
        self.crear_estructura()
        self.inicializar_config()

    # -------------------------
    # CREAR CARPETAS
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

    # -------------------------
    # CONFIG INICIAL
    # -------------------------
    def inicializar_config(self):
        tarifa_path = "data/configuracion/tarifa.txt"

        if not os.path.exists(tarifa_path):
            with open(tarifa_path, "w") as f:
                f.write("tarifa_hora=5\n")

    def obtener_tarifa(self):
        with open("data/configuracion/tarifa.txt", "r") as f:
            linea = f.readline()
            return float(linea.split("=")[1])

    def actualizar_tarifa(self, nueva):
        with open("data/configuracion/tarifa.txt", "w") as f:
            f.write(f"tarifa_hora={nueva}\n")

    # -------------------------
    # AUDITORIA
    # -------------------------
    def log(self, mensaje):
        with open("data/auditoria/bitacora.txt", "a") as f:
            hora = datetime.now().strftime("%H:%M")
            usuario = self.usuario_actual if self.usuario_actual else "Sistema"
            f.write(f"[{hora}] {usuario} -> {mensaje}\n")

    # -------------------------
    # USUARIOS
    # -------------------------
    def registrar_usuario(self, username, password, rol="operador"):
        ruta = "data/configuracion/usuarios.txt"

        # evitar duplicados
        if os.path.exists(ruta):
            with open(ruta, "r") as f:
                for linea in f:
                    if linea.split(",")[0] == username:
                        return "Usuario ya existe"

        with open(ruta, "a") as f:
            user = Usuario(username, password, rol)
            f.write(user.to_txt())

        self.log(f"Usuario creado: {username}")
        return "Usuario registrado"

    def login(self, username, password):
        ruta = "data/configuracion/usuarios.txt"

        if not os.path.exists(ruta):
            return False, None

        with open(ruta, "r") as f:
            for linea in f:
                u, p, r = linea.strip().split(",")
                if u == username and p == password:
                    self.usuario_actual = u
                    return True, r
        return False, None

    def ver_usuarios(self):
        ruta = "data/configuracion/usuarios.txt"

        if not os.path.exists(ruta):
            return []

        usuarios = []
        with open(ruta, "r") as f:
            for linea in f:
                usuarios.append(linea.strip())
        return usuarios

    # -------------------------
    # VEHICULOS
    # -------------------------
    def registrar_vehiculo(self, placa, tipo):
        vehiculo = Vehiculo(placa, tipo)

        if not vehiculo.validar_placa():
            return "Placa inválida"

        ruta = f"data/vehiculos/{vehiculo.placa}.txt"

        if os.path.exists(ruta):
            return "Vehículo ya existe"

        with open(ruta, "w") as f:
            f.write(vehiculo.to_txt())

        self.log(f"Vehículo registrado {placa}")
        return "Vehículo registrado"

    # -------------------------
    # ENTRADA
    # -------------------------
    def registrar_entrada(self, placa):
        if not self.parqueo.hay_espacio():
            return "Parqueo lleno"

        self.parqueo.ingresar(placa)

        mov = Movimiento(placa)
        ruta = f"data/movimientos/{placa}_historial.txt"

        with open(ruta, "a") as f:
            f.write(mov.to_txt_entrada())

        self.log(f"Entrada {placa}")
        return "Entrada registrada"

    # -------------------------
    # SALIDA
    # -------------------------
    def registrar_salida(self, placa):
        ruta = f"data/movimientos/{placa}_historial.txt"

        if not os.path.exists(ruta):
            return "No hay registros"

        tarifa = self.obtener_tarifa()

        mov = Movimiento(placa)
        mov.salida = datetime.now()
        tiempo = 1  # simplificado fase 1
        mov.total = tiempo * tarifa

        with open(ruta, "a") as f:
            f.write(mov.to_txt_salida())

        self.parqueo.retirar(placa)

        self.log(f"Salida {placa} Total Q{mov.total}")
        return f"Salida registrada. Total: Q{mov.total}"

    # -------------------------
    # REPORTES
    # -------------------------
    def reporte_movimientos(self):
        carpeta = "data/movimientos"
        resumen = []

        for archivo in os.listdir(carpeta):
            ruta = os.path.join(carpeta, archivo)
            with open(ruta, "r") as f:
                lineas = f.readlines()
                resumen.append((archivo, len(lineas)))

        return resumen

    def ver_bitacora(self):
        ruta = "data/auditoria/bitacora.txt"
        if not os.path.exists(ruta):
            return []

        with open(ruta, "r") as f:
            return f.readlines()