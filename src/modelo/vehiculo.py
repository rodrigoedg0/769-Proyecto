import re

class Vehiculo:
    def __init__(self, placa, tipo):
        self.placa = placa.upper().strip()
        self.tipo = tipo.lower()
        self.pais = None
        self.tipo_detectado = None
        self.validar_placa()

    def validar_placa(self):

        # ---------------- GUATEMALA ----------------
        if re.match(r'^[PMC]\d{3}[A-Z]{3}$', self.placa):
            self.pais = "Guatemala"
            self.tipo_detectado = "moto" if self.placa[0] == "M" else "carro"

        # ---------------- EL SALVADOR ----------------
        elif re.match(r'^[PMC]\s?\d{3}-\d{3}$', self.placa):
            self.pais = "El Salvador"
            self.tipo_detectado = "moto" if self.placa[0] == "M" else "carro"

        # ---------------- HONDURAS ----------------
        elif re.match(r'^[A-Z]{3}\s?\d{4}$', self.placa):
            self.pais = "Honduras"
            self.tipo_detectado = "desconocido"

        # ---------------- NICARAGUA ----------------
        elif re.match(r'^[PMTGD]\s?\d{4,5}$', self.placa):
            self.pais = "Nicaragua"
            if self.placa.startswith("M"):
                self.tipo_detectado = "moto"
            else:
                self.tipo_detectado = "carro"

        # ---------------- COSTA RICA ----------------
        elif re.match(r'^([A-Z]{3}-\d{3}|M-\d{3,5})$', self.placa):
            self.pais = "Costa Rica"
            if self.placa.startswith("M-"):
                self.tipo_detectado = "moto"
            else:
                self.tipo_detectado = "carro"

        # ---------------- PANAMÁ ----------------
        elif re.match(r'^(\d{6}|M\d{5})$', self.placa):
            self.pais = "Panamá"
            if self.placa.startswith("M"):
                self.tipo_detectado = "moto"
            else:
                self.tipo_detectado = "carro"

        else:
            raise ValueError("Formato de placa inválido en Centroamérica")

        # ---------------- VALIDACION DE TIPO ----------------
        if self.tipo_detectado != "desconocido":
            if self.tipo != self.tipo_detectado:
                raise ValueError(
                    f"Error: la placa corresponde a {self.tipo_detectado}, no a {self.tipo}"
                )

        return True

    def to_txt(self):
        return f"Placa:{self.placa}\nTipo:{self.tipo}\nPais:{self.pais}\n"