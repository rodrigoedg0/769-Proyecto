class Parqueo:
    def __init__(self, capacidad=10):
        self.capacidad = capacidad
        
    def ocupados(self):
        self.ruta= "data/configuracion/ocupados.txt"
        with open(self.ruta, "r") as archivo:
            vehiculos_dentro=[linea.strip() for linea in archivo]
        return vehiculos_dentro

    def hay_espacio(self):
        oc = self.ocupados()
        return len(oc)<self.capacidad

    def ingresar(self, placa):
        if placa not in self.ocupados():
            with open(self.ruta, "a") as archivo:
                archivo.write(f"{placa}\n")

    def retirar(self, placa):
        if placa in self.ocupados():
            with open(self.ruta, "r") as archivo:
                lineas= archivo.readlines()
            lineas= [linea for linea in lineas if linea!= f"{placa}\n"]                
            with open(self.ruta, "w") as archivo:
                archivo.writelines(lineas)