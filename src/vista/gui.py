import tkinter as tk
from tkinter import messagebox, simpledialog

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
            self.menu()
        else:
            messagebox.showerror("Error", "Login incorrecto")

    def registro(self):
        v = tk.Toplevel(self.root)

        u = tk.Entry(v); u.pack()
        p = tk.Entry(v); p.pack()
        r = tk.Entry(v); r.pack()

        def guardar():
            messagebox.showinfo("Info",
                self.sistema.registrar_usuario(u.get(), p.get(), r.get()))
            v.destroy()

        tk.Button(v, text="Guardar", command=guardar).pack()

    # ---------------- MENU ----------------
    def menu(self):
        self.clear()

        tk.Button(self.root, text="Vehículo", command=self.vehiculo).pack()
        tk.Button(self.root, text="Entrada", command=self.entrada).pack()
        tk.Button(self.root, text="Salida", command=self.salida).pack()
        tk.Button(self.root, text="Ver Usuarios", command=self.ver_usuarios).pack()
        tk.Button(self.root, text="Ver Vehículos", command=self.ver_vehiculos).pack()
        tk.Button(self.root, text="Activos", command=self.activos).pack()
        tk.Button(self.root, text="Tarifa", command=self.tarifa).pack()
        tk.Button(self.root, text="Reportes", command=self.reportes).pack()
        tk.Button(self.root, text="Bitácora", command=self.bitacora).pack()

    # ---------------- FUNCIONES ----------------
    def vehiculo(self):
        placa = simpledialog.askstring("Placa", "Placa:")
        tipo = simpledialog.askstring("Tipo", "Tipo:")
        messagebox.showinfo("Info",
            self.sistema.registrar_vehiculo(placa, tipo))

    def entrada(self):
        placa = simpledialog.askstring("Entrada", "Placa:")
        messagebox.showinfo("Info",
            self.sistema.registrar_entrada(placa))

    def salida(self):
        placa = simpledialog.askstring("Salida", "Placa:")
        messagebox.showinfo("Info",
            self.sistema.registrar_salida(placa))

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
        messagebox.showinfo("Tarifa",
            f"Q{self.sistema.obtener_tarifa()}")

    def reportes(self):
        datos = self.sistema.reporte_movimientos()
        txt = "\n".join([f"{a}: {c}" for a,c in datos])
        messagebox.showinfo("Reportes", txt)

    def bitacora(self):
        txt = "".join(self.sistema.ver_bitacora())
        messagebox.showinfo("Bitácora", txt)