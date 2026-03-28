class Parqueo:
    def __init__(self, capacidad=10):
        self.capacidad = capacidad
        self.ocupados = []

    def hay_espacio(self):
        return len(self.ocupados) < self.capacidad

    def ingresar(self, placa):
        if placa not in self.ocupados:
            self.ocupados.append(placa)

    def retirar(self, placa):
        if placa in self.ocupados:
            self.ocupados.remove(placa)