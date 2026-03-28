class Consola:
    def __init__(self, sistema):
        self.sistema = sistema
        self.rol = None

    def iniciar(self):
        print("=== SISTEMA DE PARQUEO ===")

        while True:
            print("\n1. Registrar usuario")
            print("2. Login")
            print("3. Salir")

            op = input("Seleccione: ")

            if op == "1":
                self.crear_usuario()
            elif op == "2":
                if self.login():
                    self.menu_principal()
            elif op == "3":
                break

    def crear_usuario(self):
        u = input("Usuario: ")
        p = input("Password: ")
        rol = input("Rol (admin/operador): ")

        print(self.sistema.registrar_usuario(u, p, rol))

    def login(self):
        u = input("Usuario: ")
        p = input("Password: ")

        ok, rol = self.sistema.login(u, p)

        if ok:
            self.rol = rol
            print(f"Bienvenido {u} ({rol})")
            return True
        else:
            print("Error login")
            return False

    def menu_principal(self):
        while True:
            print("\n--- MENU ---")
            print("1. Registrar Vehiculo")
            print("2. Entrada")
            print("3. Salida")
            print("4. Reportes")
            print("5. Configuración")
            print("6. Ver Usuarios")
            print("7. Ver Bitácora")
            print("8. Salir")

            op = input("Seleccione: ")

            if op == "1":
                print(self.sistema.registrar_vehiculo(
                    input("Placa: "), input("Tipo: ")
                ))

            elif op == "2":
                print(self.sistema.registrar_entrada(input("Placa: ")))

            elif op == "3":
                print(self.sistema.registrar_salida(input("Placa: ")))

            elif op == "4":
                self.reportes()

            elif op == "5":
                self.configuracion()

            elif op == "6":
                if self.rol == "admin":
                    for u in self.sistema.ver_usuarios():
                        print(u)
                else:
                    print("Acceso denegado")

            elif op == "7":
                for linea in self.sistema.ver_bitacora():
                    print(linea.strip())

            elif op == "8":
                break

    def reportes(self):
        datos = self.sistema.reporte_movimientos()

        print("\n--- REPORTE ---")
        for archivo, cantidad in datos:
            print(f"{archivo} -> {cantidad} movimientos")

    def configuracion(self):
        if self.rol != "admin":
            print("Solo admin")
            return

        print("\n1. Ver tarifa")
        print("2. Cambiar tarifa")

        op = input("Seleccione: ")

        if op == "1":
            print("Tarifa:", self.sistema.obtener_tarifa())

        elif op == "2":
            nueva = float(input("Nueva tarifa: "))
            self.sistema.actualizar_tarifa(nueva)
            print("Actualizada")