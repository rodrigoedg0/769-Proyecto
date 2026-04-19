import tkinter as tk
from tkinter import messagebox, simpledialog
from src.modelo.vehiculo import Vehiculo


class App:
    def __init__(self, sistema):
        self.sistema = sistema
        self.root = tk.Tk()
        self.root.title("Sistema Parqueo")
        self.root.geometry("600x400")
        self.root.config(bg="#093059")

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
        frame_login= tk.Frame(self.root)
        frame_login.config(bg="#093059")
        frame_login.pack(expand=True)
        
        tk.Label(frame_login, text="LOGIN").pack()

        self.u = tk.Entry(frame_login)
        self.u.pack()

        self.p = tk.Entry(frame_login, show="*")
        self.p.pack()

        tk.Button(frame_login, text="Login", command=self.login).pack()
        tk.Button(frame_login, text="Registrar", command=self.registro).pack()

    def login(self):
        ok, rol = self.sistema.login(self.u.get(), self.p.get())

        if ok:
            self.rol = rol
            self.menu()
            self.activos()
        else:
            messagebox.showerror("Error", "Login incorrecto")

    def registro(self):
        self.clear()
        
        v = tk.Frame(self.root)
        v.config(bg="#093059")
        v.pack(expand=True)
        
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
        
        self.frame_principal = tk.Frame(bg="#093059")
        self.frame_principal.place(relwidth=0.8, relheight=1, relx=0)
        frame_menu = tk.Frame(bg="#093059")
        frame_menu.place(relwidth=0.2, relheight=1, relx=0.8)
        
        botones_usuario= tk.Frame(frame_menu, bg="#093059")
        botones_usuario.pack(fill="x")
        btn1=tk.Button(botones_usuario, text="cerrar sesion", command=self.cerrar_sesion).pack(fill="x", expand=True)
        btn2=tk.Button(botones_usuario, text="vehiculos activos", command=self.activos).pack(fill="x", expand=True)
        btn3=tk.Button(botones_usuario, text="Tarifa", command=self.tarifa).pack(fill="x", expand=True)
        botones_admin= tk.Frame(frame_menu, bg="#093059")
        btn4=tk.Button(botones_admin, text="Ver Usuarios", command=self.ver_usuarios).pack(fill="x", expand=True)
        btn5=tk.Button(botones_admin, text="Ver Vehículos", command=self.ver_vehiculos).pack(fill="x", expand=True)
        btn6=tk.Button(botones_admin, text="Bitácora", command=self.bitacora).pack(fill="x", expand=True)
        btn7=tk.Button(botones_admin, text="Reportes", command=self.reportes).pack(fill="x", expand=True)
        
        if self.rol == "admin":
           botones_admin.pack(fill="x")
           
    # ---------------- ACTIVOS ----------------
    def activos(self):
        for widget in self.frame_principal.winfo_children():
            widget.destroy()
            
        tk.Button(self.frame_principal, text="agregar vehiculo", command=self.vehiculo).pack()
        
        if self.sistema.vehiculos_activos() != None:
            for placa in self.sistema.vehiculos_activos():
                ruta = f"data/vehiculos/{placa}.txt"
                with open(ruta, "r") as f:
                    contenido = f.read()
                tk.Label(self.frame_principal, text=contenido).pack(pady=(5,0))
                tk.Button(self.frame_principal, text="Salida", command=lambda:self.salida(placa)).pack()
                
    def vehiculo(self):
        for widget in self.frame_principal.winfo_children():
            widget.destroy()

        tk.Label(self.frame_principal, text="Placa:").pack()
        entrada_placa = tk.Entry(self.frame_principal)
        entrada_placa.pack()

        tk.Label(self.frame_principal, text="Tipo de vehículo:").pack()
        entrada_tipo = tk.Entry(self.frame_principal)
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
            self.activos()

        tk.Button(self.frame_principal, text="Registrar entrada", command=registrar).pack(pady=5)

    # ---------------- SALIDA ----------------
    def salida(self, placa_a_salir):
        placa = placa_a_salir
        if not placa:
            return

        placa = placa.upper()
        resultado = self.sistema.registrar_salida(placa)
        messagebox.showinfo("Salida", resultado)
        self.activos()

    # ---------------- OTROS ----------------
    def tarifa(self):
        for widget in self.frame_principal.winfo_children():
            widget.destroy()
            
        contenido= f"La tarifa actual es de Q{self.sistema.obtener_tarifa()}"
        tk.Label(self.frame_principal, text=contenido, bg="#093059", fg="#FFFFFF").pack(fill="x", expand=True)
        
    def ver_usuarios(self):
        for widget in self.frame_principal.winfo_children():
            widget.destroy()
            
        data = "".join(self.sistema.obtener_usuarios())
        tk.Label(self.frame_principal, text=data, bg="#093059", fg="#FFFFFF").pack(fill="x", expand=True)

    def ver_vehiculos(self):
        for widget in self.frame_principal.winfo_children():
            widget.destroy()
            
        data = "\n".join(self.sistema.obtener_vehiculos())
        tk.Label(self.frame_principal, text=data, bg="#093059", fg="#FFFFFF").pack(fill="x", expand=True)
        
    def bitacora(self):
        for widget in self.frame_principal.winfo_children():
            widget.destroy()
            
        txt = "".join(self.sistema.ver_bitacora())
        tk.Label(self.frame_principal, text=txt, bg="#093059", fg="#FFFFFF").pack(fill="x", expand=True)
        
    def reportes(self):
        for widget in self.frame_principal.winfo_children():
            widget.destroy()
            
        datos = self.sistema.reporte_movimientos()
        txt = "\n".join([f"{a}: {c}" for a, c in datos])
        tk.Label(self.frame_principal, text=txt, bg="#093059", fg="#FFFFFF").pack(fill="x", expand=True)

    def cerrar_sesion(self):
        if self.sistema.usuario_actual:
            self.sistema.log("Cierre de sesion")

        self.usuario = None
        self.rol = None
        self.sistema.usuario_actual = None

        messagebox.showinfo("Sesión", "Sesión cerrada correctamente")
        self.login_view()
    
