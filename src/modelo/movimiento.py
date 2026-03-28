from datetime import datetime

class Movimiento:
    def __init__(self, placa):
        self.placa = placa
        self.entrada = datetime.now()
        self.salida = None
        self.total = 0

    def to_txt_entrada(self):
        return f"ENTRADA,{self.entrada}\n"

    def to_txt_salida(self):
        return f"SALIDA,{self.salida},TOTAL:{self.total}\n"