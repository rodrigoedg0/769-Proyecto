import re

class Vehiculo:
    def __init__(self, placa, tipo):
        self.placa = placa.upper()
        self.tipo = tipo
        self.validar_placa()

    def validar_placa(self):
        patron = r'^[PMC][0-9]{3}[A-Z]{3}$'
        
        if not re.match(patron, self.placa):
            raise ValueError("Placa inválida o de otro país no válida")
        
        return True

    def to_txt(self):
        return f"Placa:{self.placa}\nTipo:{self.tipo}\n"