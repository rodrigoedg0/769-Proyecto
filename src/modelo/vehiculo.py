class Vehiculo:
    def __init__(self, placa, tipo):
        self.placa = placa.upper()
        self.tipo = tipo

    def validar_placa(self):
        return self.placa.isalnum() and len(self.placa) >= 5

    def to_txt(self):
        return f"Placa:{self.placa}\nTipo:{self.tipo}\n"