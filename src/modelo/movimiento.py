from datetime import datetime

class Movimiento:
    def __init__(self, placa):
        self.placa = placa
        self.entrada = datetime.now()
        self.salida = None
        self.total = 0

    def registrar_salida(self):
        self.salida = datetime.now()
        tiempo = (self.salida - self.entrada).total_seconds() / 3600
        self.total = round(tiempo * 5, 2)  # Q5 por hora
        return self.total

    def to_txt_entrada(self):
        return f"ENTRADA,{self.entrada}\n"

    def to_txt_salida(self):
        return f"SALIDA,{self.salida},TOTAL:{self.total}\n"