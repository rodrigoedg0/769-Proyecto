class Consola:
    def __init__(self, sistema):
        self.sistema = sistema

    def iniciar(self):
        print("=== SISTEMA DE PARQUEO ===")

        while True:
            print("\n1. Registrar usuario")
            print("2. Login")
            print("3. Salir")

            op = input("Seleccione: ")

            if op == "1":
                self.registrar_usuario()
            elif op == "2":
                if self.login():
                    self.menu_principal()
            elif op == "3":
                break

    def registrar_usuario(self):
        u = input("Usuario: ")
        p = input("Password: ")
        self.sistema.registrar_usuario(u, p)
        print("Usuario registrado")

    def login(self):
        u = input("Usuario: ")
        p = input("Password: ")

        if self.sistema.login(u, p):
            print("Login exitoso")
            return True
        else:
            print("Credenciales incorrectas")
            return False

    def menu_principal(self):
        while True:
            print("\n--- MENU ---")
            print("1. Registrar Vehiculo")
            print("2. Entrada")
            print("3. Salida")
            print("4. Volver")

            op = input("Seleccione: ")

            if op == "1":
                self.registrar_vehiculo()
            elif op == "2":
                self.entrada()
            elif op == "3":
                self.salida()
            elif op == "4":
                break

    def registrar_vehiculo(self):
        placa = input("Placa: ")
        tipo = input("Tipo: ")

        ok, msg = self.sistema.registrar_vehiculo(placa, tipo)
        print(msg)

    def entrada(self):
        placa = input("Placa: ")
        print(self.sistema.registrar_entrada(placa))

    def salida(self):
        placa = input("Placa: ")
        print(self.sistema.registrar_salida(placa))