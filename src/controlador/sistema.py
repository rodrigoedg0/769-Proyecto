import os
from datetime import datetime
from src.modelo.usuario import Usuario
from src.modelo.vehiculo import Vehiculo
from src.modelo.movimiento import Movimiento
from src.modelo.parqueo import Parqueo


class Sistema:
    def __init__(self):
        self.parqueo = Parqueo()
        self.usuario_actual = None
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
        with open("data/auditoria/bitacora.txt", "a") as f:
            hora = datetime.now().strftime("%H:%M")
            usuario = self.usuario_actual if self.usuario_actual else "Sistema"
            f.write(f"[{hora}] {usuario} -> {mensaje}\n")

    # -------------------------
    # USUARIOS
    # -------------------------
    def registrar_usuario(self, username, password, rol):
        ruta = "data/configuracion/usuarios.txt"

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
        ruta = "data/configuracion/usuarios.txt"

        if not os.path.exists(ruta):
            return False, None

        with open(ruta, "r") as f:
            for linea in f:
                u, p, r = linea.strip().split(",")
                if u == username and p == password:
                    self.usuario_actual = u
                    self.log("Inicio de sesion")
                    return True, r
        return False, None

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

        if placa in self.parqueo.ocupados:
            return "El vehículo ya está dentro"

        if not self.parqueo.hay_espacio():
            return "Parqueo lleno"

        if placa not in self.parqueo.ocupados:
            self.parqueo.ocupados.append(placa)

        mov = Movimiento(placa)
        ruta = f"data/movimientos/{placa}_historial.txt"

        with open(ruta, "a") as f:
            f.write(mov.to_txt_entrada())

        self.log(f"Entrada: {placa}")
        return f"Entrada registrada: {placa}"

    def registrar_salida(self, placa):
        placa = placa.upper()

        if placa not in self.parqueo.ocupados:
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
        return [str(v) for v in self.parqueo.ocupados if v is not None]

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

    def ver_bitacora(self):
        ruta = "data/auditoria/bitacora.txt"
        if not os.path.exists(ruta):
            return []
        with open(ruta) as f:
            return f.readlines()