import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from src.modelo.vehiculo import Vehiculo


class App:
    def __init__(self, sistema):
        self.sistema = sistema
        self.root = tk.Tk()
        self.root.title("Sistema Parqueo")
        self.root.geometry("980x620")
        self.root.minsize(900, 560)
        self.root.config(bg="#0F172A")

        self.usuario = None
        self.rol = None
        self.frame_principal = None
        self.tabla_activos = None
        self.label_estado = None

        self._configurar_estilos()

        self.login_view()

    def run(self):
        self.root.mainloop()

    def _configurar_estilos(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("Modern.TFrame", background="#111827")
        estilo.configure("Card.TFrame", background="#1F2937")
        estilo.configure("Sidebar.TFrame", background="#0B1220")
        estilo.configure(
            "Title.TLabel",
            background="#111827",
            foreground="#F9FAFB",
            font=("Segoe UI", 20, "bold")
        )
        estilo.configure(
            "Subtitle.TLabel",
            background="#111827",
            foreground="#9CA3AF",
            font=("Segoe UI", 10)
        )
        estilo.configure(
            "CardTitle.TLabel",
            background="#1F2937",
            foreground="#F9FAFB",
            font=("Segoe UI", 12, "bold")
        )
        estilo.configure(
            "Modern.TLabel",
            background="#111827",
            foreground="#E5E7EB",
            font=("Segoe UI", 10)
        )
        estilo.configure(
            "Modern.TButton",
            font=("Segoe UI", 10),
            padding=8,
            borderwidth=0
        )
        estilo.map(
            "Modern.TButton",
            background=[("active", "#334155"), ("!active", "#2563EB")],
            foreground=[("disabled", "#9CA3AF"), ("!disabled", "#FFFFFF")]
        )
        estilo.configure(
            "Menu.TButton",
            font=("Segoe UI", 10),
            padding=10,
            anchor="w",
            borderwidth=0
        )
        estilo.map(
            "Menu.TButton",
            background=[("active", "#1E293B"), ("!active", "#0B1220")],
            foreground=[("!disabled", "#E5E7EB")]
        )
        estilo.configure(
            "Treeview",
            background="#0F172A",
            fieldbackground="#0F172A",
            foreground="#E5E7EB",
            rowheight=30,
            borderwidth=0
        )
        estilo.configure(
            "Treeview.Heading",
            background="#334155",
            foreground="#F9FAFB",
            font=("Segoe UI", 10, "bold"),
            relief="flat"
        )
        estilo.map("Treeview", background=[("selected", "#2563EB")])

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def _crear_card(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=16)
        return card

    # ---------------- LOGIN ----------------
    def login_view(self):
        self.clear()
        contenedor = ttk.Frame(self.root, style="Modern.TFrame", padding=24)
        contenedor.pack(fill="both", expand=True)

        ttk.Label(contenedor, text="Sistema de Parqueo", style="Title.TLabel").pack(pady=(40, 4))
        ttk.Label(
            contenedor,
            text="Gestiona accesos, vehículos activos y movimientos",
            style="Subtitle.TLabel"
        ).pack(pady=(0, 20))

        card = self._crear_card(contenedor)
        card.pack(pady=12)

        ttk.Label(card, text="Iniciar sesión", style="CardTitle.TLabel").grid(
            row=0, column=0, columnspan=2, pady=(0, 12), sticky="w"
        )

        ttk.Label(card, text="Usuario", style="Modern.TLabel").grid(row=1, column=0, sticky="w", pady=6)
        self.u = ttk.Entry(card, width=28)
        self.u.grid(row=1, column=1, pady=6, padx=(10, 0))

        ttk.Label(card, text="Contraseña", style="Modern.TLabel").grid(row=2, column=0, sticky="w", pady=6)
        self.p = ttk.Entry(card, show="*", width=28)
        self.p.grid(row=2, column=1, pady=6, padx=(10, 0))

        ttk.Button(card, text="Acceder", style="Modern.TButton", command=self.login).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(14, 6)
        )
        ttk.Button(card, text="Crear una cuenta", style="Modern.TButton", command=self.registro).grid(
            row=4, column=0, columnspan=2, sticky="ew"
        )
        recuperar = tk.Label(
            card,
            text="¿Has olvidado la contraseña?",
            bg="#1F2937",
            fg="#93C5FD",
            cursor="hand2",
            font=("Segoe UI", 10, "underline")
        )
        recuperar.grid(row=5, column=0, columnspan=2, pady=(10, 0))
        recuperar.bind("<Button-1>", lambda e: self.recuperar_password_view())

    def login(self):
        ok, rol = self.sistema.login(self.u.get(), self.p.get())

        if ok:
            self.rol = rol
            self.menu()
            self.activos()
        else:
            mensaje = self.sistema.ultimo_error_login or "Login incorrecto"
            messagebox.showerror("Error", mensaje)

    def registro(self):
        self.clear()

        contenedor = ttk.Frame(self.root, style="Modern.TFrame", padding=24)
        contenedor.pack(fill="both", expand=True)

        ttk.Label(contenedor, text="Creación de usuario", style="Title.TLabel").pack(pady=(20, 14))
        v = self._crear_card(contenedor)
        v.pack()

        ttk.Label(v, text="Nombre", style="Modern.TLabel").grid(row=0, column=0, sticky="w", pady=6)
        u = ttk.Entry(v, width=30)
        u.grid(row=0, column=1, pady=6, padx=(10, 0))

        ttk.Label(v, text="Rol", style="Modern.TLabel").grid(row=1, column=0, sticky="w", pady=6)
        r = ttk.Combobox(v, width=27, state="readonly", values=["usuario", "admin"])
        r.grid(row=1, column=1, pady=6, padx=(10, 0))
        r.set("usuario")

        ttk.Label(v, text="Contraseña", style="Modern.TLabel").grid(row=2, column=0, sticky="w", pady=6)
        p = ttk.Entry(v, width=30, show="*")
        p.grid(row=2, column=1, pady=6, padx=(10, 0))

        ttk.Label(v, text="Confirmación", style="Modern.TLabel").grid(row=3, column=0, sticky="w", pady=6)
        c = ttk.Entry(v, width=30, show="*")
        c.grid(row=3, column=1, pady=6, padx=(10, 0))

        def guardar():
            label_informacion.config(text="")
            rol = r.get().strip().lower()
            if rol == "admin":
                val = self.sistema.Es_admin(simpledialog.askstring("Contraseña", "Ingrese la contraseña de admin:"))
                if  val == False:
                    label_informacion.config(text="ha ingresado una contraseña de admin no valida")
                    return
                
            mensaje = self.sistema.registrar_usuario(u.get(), p.get(), c.get(), rol)
            label_informacion.config(text=mensaje)
            
            if mensaje =="verifique su contraseña":
                return
            elif mensaje=="verifique sus datos":
                return
            else: 
                messagebox.showinfo("Info", mensaje)
                self.login_view()           

        ttk.Button(v, text="Guardar", style="Modern.TButton", command=guardar).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(12, 6)
        )
        label_informacion = ttk.Label(v, style="Subtitle.TLabel")
        label_informacion.grid(row=5, column=0, columnspan=2, pady=(0, 6))
        ttk.Button(v, text="Volver", style="Modern.TButton", command=self.login_view).grid(
            row=6, column=0, columnspan=2, sticky="ew"
        )

    def recuperar_password_view(self):
        self.clear()

        contenedor = ttk.Frame(self.root, style="Modern.TFrame", padding=24)
        contenedor.pack(fill="both", expand=True)

        ttk.Label(contenedor, text="Recuperar contraseña", style="Title.TLabel").pack(pady=(20, 14))
        v = self._crear_card(contenedor)
        v.pack()

        ttk.Label(v, text="Usuario", style="Modern.TLabel").grid(row=0, column=0, sticky="w", pady=6)
        u = ttk.Entry(v, width=30)
        u.grid(row=0, column=1, pady=6, padx=(10, 0))

        ttk.Label(v, text="Nueva contraseña", style="Modern.TLabel").grid(row=1, column=0, sticky="w", pady=6)
        p = ttk.Entry(v, width=30, show="*")
        p.grid(row=1, column=1, pady=6, padx=(10, 0))

        ttk.Label(v, text="Confirmación", style="Modern.TLabel").grid(row=2, column=0, sticky="w", pady=6)
        c = ttk.Entry(v, width=30, show="*")
        c.grid(row=2, column=1, pady=6, padx=(10, 0))

        label_info = ttk.Label(v, style="Subtitle.TLabel")
        label_info.grid(row=4, column=0, columnspan=2, pady=(4, 6))

        def guardar():
            mensaje = self.sistema.recuperar_contrasena(u.get(), p.get(), c.get())
            label_info.config(text=mensaje)
            if mensaje == "Contraseña actualizada":
                messagebox.showinfo("Recuperación", mensaje)
                self.login_view()

        ttk.Button(v, text="Actualizar contraseña", style="Modern.TButton", command=guardar).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(12, 6)
        )
        ttk.Button(v, text="Volver", style="Modern.TButton", command=self.login_view).grid(
            row=5, column=0, columnspan=2, sticky="ew"
        )

    # ---------------- MENU ----------------
    def menu(self):
        self.clear()

        principal = ttk.Frame(self.root, style="Modern.TFrame")
        principal.pack(fill="both", expand=True)

        self.frame_principal = ttk.Frame(principal, style="Modern.TFrame", padding=18)
        self.frame_principal.pack(side="left", fill="both", expand=True)

        frame_menu = ttk.Frame(principal, style="Sidebar.TFrame", padding=10)
        frame_menu.pack(side="right", fill="y")

        ttk.Label(
            frame_menu,
            text="Menú",
            background="#0B1220",
            foreground="#F9FAFB",
            font=("Segoe UI", 12, "bold")
        ).pack(fill="x", pady=(6, 12))

        ttk.Button(frame_menu, text="Vehículos activos", style="Menu.TButton", command=self.activos).pack(
            fill="x", pady=2
        )
        ttk.Button(frame_menu, text="Tarifa", style="Menu.TButton", command=self.tarifa).pack(fill="x", pady=2)
        ttk.Button(frame_menu, text="Cerrar sesión", style="Menu.TButton", command=self.cerrar_sesion).pack(
            fill="x", pady=(2, 14)
        )

        botones_admin = ttk.Frame(frame_menu, style="Sidebar.TFrame")
        ttk.Button(botones_admin, text="Ver usuarios", style="Menu.TButton", command=self.ver_usuarios).pack(
            fill="x", pady=2
        )
        ttk.Button(botones_admin, text="Ver vehículos", style="Menu.TButton", command=self.ver_vehiculos).pack(
            fill="x", pady=2
        )
        ttk.Button(botones_admin, text="Bitácora", style="Menu.TButton", command=self.bitacora).pack(
            fill="x", pady=2
        )
        ttk.Button(botones_admin, text="Reportes", style="Menu.TButton", command=self.reportes).pack(
            fill="x", pady=2
        )

        if self.rol == "admin":
            botones_admin.pack(fill="x")

    # ---------------- ACTIVOS ----------------
    def _obtener_tipo_vehiculo(self, placa):
        ruta = f"data/vehiculos/{placa}.txt"
        try:
            with open(ruta, "r") as f:
                for linea in f:
                    if linea.lower().startswith("tipo:"):
                        return linea.split(":", 1)[1].strip()
        except FileNotFoundError:
            return "No registrado"
        return "No registrado"

    def activos(self):
        for widget in self.frame_principal.winfo_children():
            widget.destroy()

        ttk.Label(self.frame_principal, text="Vehículos activos", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            self.frame_principal,
            text="Selecciona una fila para registrar su salida",
            style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(0, 12))

        barra = ttk.Frame(self.frame_principal, style="Modern.TFrame")
        barra.pack(fill="x", pady=(0, 10))
        ttk.Button(barra, text="Agregar vehículo", style="Modern.TButton", command=self.vehiculo).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(
            barra,
            text="Registrar salida del seleccionado",
            style="Modern.TButton",
            command=self.salida_desde_tabla
        ).pack(side="left")

        card = self._crear_card(self.frame_principal)
        card.pack(fill="both", expand=True)

        columnas = ("placa", "tipo", "estado")
        self.tabla_activos = ttk.Treeview(card, columns=columnas, show="headings")
        self.tabla_activos.heading("placa", text="Placa")
        self.tabla_activos.heading("tipo", text="Tipo")
        self.tabla_activos.heading("estado", text="Estado")
        self.tabla_activos.column("placa", width=180, anchor="center")
        self.tabla_activos.column("tipo", width=220, anchor="center")
        self.tabla_activos.column("estado", width=180, anchor="center")

        scroll = ttk.Scrollbar(card, orient="vertical", command=self.tabla_activos.yview)
        self.tabla_activos.configure(yscrollcommand=scroll.set)
        self.tabla_activos.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        activos = self.sistema.vehiculos_activos() or []
        for placa in activos:
            tipo = self._obtener_tipo_vehiculo(placa)
            self.tabla_activos.insert("", "end", values=(placa, tipo, "Dentro del parqueo"))

        self.label_estado = ttk.Label(self.frame_principal, text="", style="Subtitle.TLabel")
        self.label_estado.pack(anchor="w", pady=(8, 0))
        if not activos:
            self.label_estado.config(text="No hay vehículos activos en este momento.")
                
    def vehiculo(self):
        for widget in self.frame_principal.winfo_children():
            widget.destroy()

        ttk.Label(self.frame_principal, text="Registrar vehículo", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            self.frame_principal,
            text="Se registrará el vehículo y su entrada de inmediato",
            style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(0, 12))

        card = self._crear_card(self.frame_principal)
        card.pack(anchor="w")

        ttk.Label(card, text="Placa:", style="Modern.TLabel").grid(row=0, column=0, sticky="w", pady=6)
        entrada_placa = ttk.Entry(card, width=30)
        entrada_placa.grid(row=0, column=1, pady=6, padx=(10, 0))

        ttk.Label(card, text="Tipo de vehículo:", style="Modern.TLabel").grid(row=1, column=0, sticky="w", pady=6)
        entrada_tipo = ttk.Combobox(card, width=27, state="readonly", values=["carro", "moto"])
        entrada_tipo.grid(row=1, column=1, pady=6, padx=(10, 0))
        entrada_tipo.set("carro")

        def mayuscula(event):
            texto = entrada_placa.get().upper()
            entrada_placa.delete(0, tk.END)
            entrada_placa.insert(0, texto)

        entrada_placa.bind("<KeyRelease>", mayuscula)

        def registrar():
            placa = entrada_placa.get().upper()
            tipo = entrada_tipo.get().strip().lower()

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

        ttk.Button(card, text="Registrar entrada", style="Modern.TButton", command=registrar).grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(10, 6)
        )
        ttk.Button(card, text="Volver a activos", style="Modern.TButton", command=self.activos).grid(
            row=3, column=0, columnspan=2, sticky="ew"
        )

    # ---------------- SALIDA ----------------
    def salida_desde_tabla(self):
        if not self.tabla_activos:
            return
        seleccion = self.tabla_activos.selection()
        if not seleccion:
            messagebox.showwarning("Salida", "Selecciona un vehículo en la tabla.")
            return
        placa = self.tabla_activos.item(seleccion[0], "values")[0]
        self.salida(placa)

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

        ttk.Label(self.frame_principal, text="Tarifa", style="Title.TLabel").pack(anchor="w")
        contenido = f"La tarifa actual es de Q{self.sistema.obtener_tarifa()}"
        card = self._crear_card(self.frame_principal)
        card.pack(fill="x", pady=(12, 0))
        ttk.Label(card, text=contenido, style="CardTitle.TLabel").pack(anchor="w")
        ttk.Button(card, text="Regresar", style="Modern.TButton", command=self.activos).pack(
            anchor="w", pady=(10, 0)
        )
        
    def ver_usuarios(self):
        for widget in self.frame_principal.winfo_children():
            widget.destroy()

        ttk.Label(self.frame_principal, text="Usuarios registrados", style="Title.TLabel").pack(anchor="w")
        data = "".join(self.sistema.obtener_usuarios()) or "Sin usuarios registrados."
        card = self._crear_card(self.frame_principal)
        card.pack(fill="both", expand=True, pady=(12, 0))
        tk.Label(card, text=data, bg="#1F2937", fg="#E5E7EB", justify="left").pack(anchor="w")
        ttk.Button(card, text="Regresar", style="Modern.TButton", command=self.activos).pack(
            anchor="w", pady=(10, 0)
        )

    def ver_vehiculos(self):
        for widget in self.frame_principal.winfo_children():
            widget.destroy()

        ttk.Label(self.frame_principal, text="Vehículos registrados", style="Title.TLabel").pack(anchor="w")
        data = "\n".join(self.sistema.obtener_vehiculos()) or "Sin vehículos registrados."
        card = self._crear_card(self.frame_principal)
        card.pack(fill="both", expand=True, pady=(12, 0))
        tk.Label(card, text=data, bg="#1F2937", fg="#E5E7EB", justify="left").pack(anchor="w")
        ttk.Button(card, text="Regresar", style="Modern.TButton", command=self.activos).pack(
            anchor="w", pady=(10, 0)
        )
        
    def bitacora(self):
        for widget in self.frame_principal.winfo_children():
            widget.destroy()

        ttk.Label(self.frame_principal, text="Bitácora", style="Title.TLabel").pack(anchor="w")
        txt = "".join(self.sistema.ver_bitacora())
        card = self._crear_card(self.frame_principal)
        card.pack(fill="both", expand=True, pady=(12, 0))
        contenedor_texto = tk.Frame(card, bg="#1F2937")
        contenedor_texto.pack(fill="both", expand=True)

        scroll = ttk.Scrollbar(contenedor_texto, orient="vertical")
        scroll.pack(side="right", fill="y")

        area = tk.Text(
            contenedor_texto,
            wrap="word",
            bg="#1F2937",
            fg="#E5E7EB",
            insertbackground="#E5E7EB",
            relief="flat",
            yscrollcommand=scroll.set
        )
        area.pack(side="left", fill="both", expand=True)
        scroll.config(command=area.yview)

        area.insert("1.0", txt or "Bitácora vacía.")
        area.config(state="disabled")
        ttk.Button(card, text="Regresar", style="Modern.TButton", command=self.activos).pack(
            anchor="w", pady=(10, 0)
        )
        
    def reportes(self):
        for widget in self.frame_principal.winfo_children():
            widget.destroy()

        ttk.Label(self.frame_principal, text="Reportes", style="Title.TLabel").pack(anchor="w")
        datos = self.sistema.reporte_movimientos()
        card = self._crear_card(self.frame_principal)
        card.pack(fill="both", expand=True, pady=(12, 0))

        if not datos:
            tk.Label(
                card,
                text="Sin datos para reportes.",
                bg="#1F2937",
                fg="#E5E7EB",
                justify="left"
            ).pack(anchor="w")
            return

        panel_izquierdo = tk.Frame(card, bg="#1F2937")
        panel_izquierdo.pack(side="left", fill="y", padx=(0, 12))

        panel_derecho = tk.Frame(card, bg="#1F2937")
        panel_derecho.pack(side="left", fill="both", expand=True)

        ttk.Label(
            panel_izquierdo,
            text="Archivos de movimiento",
            background="#1F2937",
            foreground="#F9FAFB",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 8))

        columnas = ("archivo", "registros")
        tabla_reportes = ttk.Treeview(panel_izquierdo, columns=columnas, show="headings", height=18)
        tabla_reportes.heading("archivo", text="Archivo")
        tabla_reportes.heading("registros", text="Líneas")
        tabla_reportes.column("archivo", width=250, anchor="w")
        tabla_reportes.column("registros", width=80, anchor="center")
        tabla_reportes.pack(side="left", fill="y")

        scroll_tabla = ttk.Scrollbar(panel_izquierdo, orient="vertical", command=tabla_reportes.yview)
        scroll_tabla.pack(side="right", fill="y")
        tabla_reportes.configure(yscrollcommand=scroll_tabla.set)

        for archivo, cantidad in datos:
            tabla_reportes.insert("", "end", values=(archivo, cantidad))

        scroll_texto = ttk.Scrollbar(panel_derecho, orient="vertical")
        scroll_texto.pack(side="right", fill="y")

        area = tk.Text(
            panel_derecho,
            wrap="word",
            bg="#111827",
            fg="#E5E7EB",
            insertbackground="#E5E7EB",
            relief="flat",
            yscrollcommand=scroll_texto.set
        )
        area.pack(side="left", fill="both", expand=True)
        scroll_texto.config(command=area.yview)

        def mostrar_reporte(event=None):
            seleccion = tabla_reportes.selection()
            if not seleccion:
                return
            archivo = tabla_reportes.item(seleccion[0], "values")[0]
            contenido = self.sistema.leer_reporte_movimiento(archivo)
            area.config(state="normal")
            area.delete("1.0", tk.END)
            area.insert("1.0", contenido or "Archivo vacío.")
            area.config(state="disabled")

        tabla_reportes.bind("<<TreeviewSelect>>", mostrar_reporte)
        primera_fila = tabla_reportes.get_children()
        if primera_fila:
            tabla_reportes.selection_set(primera_fila[0])
            mostrar_reporte()
        ttk.Button(self.frame_principal, text="Regresar", style="Modern.TButton", command=self.activos).pack(
            anchor="w", pady=(10, 0)
        )

    def cerrar_sesion(self):
        if self.sistema.usuario_actual:
            self.sistema.log("Cierre de sesion")

        self.usuario = None
        self.rol = None
        self.sistema.usuario_actual = None

        messagebox.showinfo("Sesión", "Sesión cerrada correctamente")
        self.login_view()
    
