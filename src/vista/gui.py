import tkinter as tk
from tkinter import messagebox, simpledialog
from src.modelo.vehiculo import Vehiculo


class App:
    def __init__(self, sistema):
        self.sistema = sistema
        self.root = tk.Tk()
        self.root.title("Sistema Parqueo")
        self.root.geometry("400x500")

        self.usuario = None
        self.rol = None

        self.login_view()

    def run(self):
        self.root.mainloop()

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    # ---------------- LOGIN ----------------
    def login_view(self):
        self.clear()

        tk.Label(self.root, text="LOGIN").pack()

        self.u = tk.Entry(self.root)
        self.u.pack()

        self.p = tk.Entry(self.root, show="*")
        self.p.pack()

        tk.Button(self.root, text="Login", command=self.login).pack()
        tk.Button(self.root, text="Registrar", command=self.registro).pack()

    def login(self):
        ok, rol = self.sistema.login(self.u.get(), self.p.get())

        if ok:
            self.rol = rol
            messagebox.showinfo("Login", "Inicio de sesión correcto")
            self.menu()
        else:
            messagebox.showerror("Error", "Login incorrecto")

    def registro(self):
        self.clear()
        v = tk.Frame(self.root)
        v.pack() 
        
        label_titulo = tk.Label(v, text="Creacion de usuario")
        label_titulo.grid(row=0, column=0, columnspan=2)

        label_nombre = tk.Label(v, text="Nombre")
        label_nombre.grid(row=1, column=0)
        u = tk.Entry(v)
        u.grid(row=1, column=1)
        
        label_rol = tk.Label(v, text="usuario/admin")
        label_rol.grid(row=2, column=0)
        r = tk.Entry(v)
        r.grid(row=2, column=1)

        label_password = tk.Label(v, text="Contraseña")
        label_password.grid(row=3, column=0)
        p = tk.Entry(v)
        p.grid(row=3, column=1)
        
        label_confirmacion = tk.Label(v, text="Confirmacion")
        label_confirmacion.grid(row=4, column=0)
        c = tk.Entry(v)
        c.grid(row=4, column=1)


        def guardar():
            label_informacion.config(text="")
            c.config(background="white")
            if r.get() == "admin":
                val = self.sistema.Es_admin(simpledialog.askstring("Contraseña", "Ingrese la contraseña de admin:"))
                if  val == False:
                    label_informacion.config(text="ha ingresado una contraseña de admin no valida")
                    return
                
            mensaje = self.sistema.registrar_usuario(u.get(), p.get(), c.get(), r.get())
            label_informacion.config(text=mensaje)
            
            if mensaje =="verifique su contraseña":
                c.config(background="#FFAEA8")
                return
            elif mensaje=="verifique sus datos":
                return
            else: 
                messagebox.showinfo("Info", mensaje)
                self.login_view()           

        tk.Button(v, text="Guardar", command=guardar).grid(row=5, columnspan=2)
        label_informacion = tk.Label(v, font=("arial", 8, "italic"))
        label_informacion.grid(row=6, columnspan=2)
        

    # ---------------- MENU ----------------
    def menu(self):
        self.clear()
        botones_usuario= tk.Frame().pack()
        btn1=tk.Button(botones_usuario, text="Vehículo", command=self.vehiculo).pack()
        btn2=tk.Button(botones_usuario, text="Salida", command=self.salida).pack()
        btn3=tk.Button(botones_usuario, text="Activos", command=self.activos).pack()
        btn4=tk.Button(botones_usuario, text="Tarifa", command=self.tarifa).pack()
        botones_admin= tk.Frame()
        btn5=tk.Button(botones_admin, text="Ver Usuarios", command=self.ver_usuarios).pack()
        btn6=tk.Button(botones_admin, text="Ver Vehículos", command=self.ver_vehiculos).pack()
        btn7=tk.Button(botones_admin, text="Bitácora", command=self.bitacora).pack()
        btn8=tk.Button(botones_admin, text="Reportes", command=self.reportes).pack()
        
        if self.rol == "admin":
           botones_admin.pack()
           
        btn9=tk.Button(self.root, text="Cerrar sesión", command=self.cerrar_sesion).pack(pady=10)
           
    # ---------------- VEHICULO ----------------
    def vehiculo(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Registrar Vehículo")
        ventana.geometry("300x200")

        tk.Label(ventana, text="Placa:").pack()
        entrada_placa = tk.Entry(ventana)
        entrada_placa.pack()

        tk.Label(ventana, text="Tipo de vehículo:").pack()
        entrada_tipo = tk.Entry(ventana)
        entrada_tipo.pack()

        def mayuscula(event):
            texto = entrada_placa.get().upper()
            entrada_placa.delete(0, tk.END)
            entrada_placa.insert(0, texto)

        entrada_placa.bind("<KeyRelease>", mayuscula)

        def registrar():
            placa = entrada_placa.get().upper()
            tipo = entrada_tipo.get()

            if not placa or not tipo:
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return

            try:
                Vehiculo(placa, tipo)
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return

            resultado = self.sistema.registrar_vehiculo(placa, tipo)
            entrada = self.sistema.registrar_entrada(placa)

            messagebox.showinfo("Resultado", f"{resultado}\n{entrada}")
            ventana.destroy()

        tk.Button(ventana, text="Registrar entrada", command=registrar).pack(pady=5)
        tk.Button(ventana, text="Salir", command=ventana.destroy).pack(pady=5)

    # ---------------- SALIDA ----------------
    def salida(self):
        placa = simpledialog.askstring("Salida", "Ingrese la placa:")

        if not placa:
            return

        placa = placa.upper()
        resultado = self.sistema.registrar_salida(placa)
        messagebox.showinfo("Salida", resultado)

    # ---------------- OTROS ----------------
    def ver_usuarios(self):
        if self.rol != "admin":
            messagebox.showerror("Error", "Solo admin")
            return

        data = "".join(self.sistema.obtener_usuarios())
        messagebox.showinfo("Usuarios", data)

    def ver_vehiculos(self):
        data = "\n".join(self.sistema.obtener_vehiculos())
        messagebox.showinfo("Vehículos", data)

    def activos(self):
        data = "\n".join(self.sistema.vehiculos_activos())
        messagebox.showinfo("Activos", data)

    def tarifa(self):
        messagebox.showinfo("Tarifa", f"Q{self.sistema.obtener_tarifa()}")

    def reportes(self):
        datos = self.sistema.reporte_movimientos()
        txt = "\n".join([f"{a}: {c}" for a, c in datos])
        messagebox.showinfo("Reportes", txt)

    def bitacora(self):
        txt = "".join(self.sistema.ver_bitacora())
        messagebox.showinfo("Bitácora", txt)

    def cerrar_sesion(self):
        if self.sistema.usuario_actual:
            self.sistema.log("Cierre de sesion")

        self.usuario = None
        self.rol = None
        self.sistema.usuario_actual = None

        messagebox.showinfo("Sesión", "Sesión cerrada correctamente")
        self.login_view()
    
