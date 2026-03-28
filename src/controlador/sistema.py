import os
from src.modelo.usuario import Usuario
from src.modelo.vehiculo import Vehiculo
from src.modelo.movimiento import Movimiento
from src.modelo.parqueo import Parqueo

class Sistema:
    def __init__(self):
        self.base_path = "data"
        self.parqueo = Parqueo()
        self.crear_estructura()

    # 🔹 CREAR CARPETAS AUTOMATICAMENTE
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

    # 🔹 USUARIOS
    def registrar_usuario(self, username, password):
        ruta = "data/configuracion/usuarios.txt"

        with open(ruta, "a") as f:
            user = Usuario(username, password)
            f.write(user.to_txt())

    def login(self, username, password):
        ruta = "data/configuracion/usuarios.txt"

        if not os.path.exists(ruta):
            return False

        with open(ruta, "r") as f:
            for linea in f:
                u, p, _ = linea.strip().split(",")
                if u == username and p == password:
                    return True
        return False

    # 🔹 VEHICULO
    def registrar_vehiculo(self, placa, tipo):
        vehiculo = Vehiculo(placa, tipo)

        if not vehiculo.validar_placa():
            return False, "Placa inválida"

        ruta = f"data/vehiculos/{vehiculo.placa}.txt"

        if os.path.exists(ruta):
            return False, "Vehículo ya existe"

        with open(ruta, "w") as f:
            f.write(vehiculo.to_txt())

        return True, "Vehículo registrado"

    # 🔹 ENTRADA
    def registrar_entrada(self, placa):
        if not self.parqueo.hay_espacio():
            return "Parqueo lleno"

        self.parqueo.ingresar(placa)

        mov = Movimiento(placa)
        ruta = f"data/movimientos/{placa}_historial.txt"

        with open(ruta, "a") as f:
            f.write(mov.to_txt_entrada())

        return "Entrada registrada"

    # 🔹 SALIDA
    def registrar_salida(self, placa):
        ruta = f"data/movimientos/{placa}_historial.txt"

        if not os.path.exists(ruta):
            return "No hay registros"

        mov = Movimiento(placa)
        total = mov.registrar_salida()

        with open(ruta, "a") as f:
            f.write(mov.to_txt_salida())

        self.parqueo.retirar(placa)

        return f"Salida registrada. Total: Q{total}"