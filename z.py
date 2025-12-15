import customtkinter as ctk
import webbrowser
from tkinter import messagebox
import database # Importamos el archivo database.py que acabamos de crear

# Configuración inicial de diseño
ctk.set_appearance_mode("System")  # Opciones: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gestión de Impresión 3D - Taller")
        self.geometry("900x600")

        # Inicializamos mostrando el Login
        self.mostrar_login()

    def mostrar_login(self):
        """Muestra la pantalla de inicio de sesión"""
        # Limpiamos la ventana por si había algo antes
        for widget in self.winfo_children():
            widget.destroy()

        self.frame_login = ctk.CTkFrame(self)
        self.frame_login.pack(pady=50, padx=50, fill="both", expand=True)

        ctk.CTkLabel(self.frame_login, text="Bienvenido al Taller", font=("Roboto", 24, "bold")).pack(pady=30)

        self.entry_user = ctk.CTkEntry(self.frame_login, placeholder_text="Usuario", width=300)
        self.entry_user.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(self.frame_login, placeholder_text="Contraseña", show="*", width=300)
        self.entry_pass.pack(pady=10)

        ctk.CTkButton(self.frame_login, text="Iniciar Sesión", command=self.evento_login, width=300).pack(pady=20)
        
        ctk.CTkButton(self.frame_login, text="Registrar Nuevo Usuario", 
                      fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), 
                      command=self.evento_registro, width=300).pack(pady=5)

    def mostrar_menu_principal(self):
        """Esta pantalla aparece DESPUÉS de loguearse"""
        # Borramos el login
        for widget in self.winfo_children():
            widget.destroy()

        # --- Menú Lateral (Sidebar) ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="MENÚ", font=("Roboto", 20, "bold")).pack(pady=20)
        
        ctk.CTkButton(self.sidebar, text="Mis Impresoras", command=self.mostrar_impresoras).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Bobinas / Stock", command=lambda: print("Ir a Bobinas")).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Nueva Impresión", fg_color="green", command=lambda: print("Nueva Impresión")).pack(pady=10, padx=20)
        
        ctk.CTkButton(self.sidebar, text="Cerrar Sesión", fg_color="red", command=self.mostrar_login).pack(side="bottom", pady=20, padx=20)

        # --- Área Principal ---
        self.main_area = ctk.CTkFrame(self)
        self.main_area.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.main_area, text="Panel de Control", font=("Roboto", 24)).pack(pady=20)
        ctk.CTkLabel(self.main_area, text="Selecciona una opción del menú para empezar.").pack()

        label_compras = ctk.CTkLabel(self.sidebar, text="COMPRAS / WEB", font=("Roboto", 16, "bold"), text_color="gray")
        label_compras.pack(pady=(20, 10))

        ctk.CTkButton(self.sidebar, text="Comprar Impresoras", 
                      fg_color="transparent", border_width=1, text_color=("gray10", "gray90"),
                      command=lambda: webbrowser.open("https://listado.mercadolibre.com.ar/impresion-3d-impresoras")).pack(pady=5, padx=20)

        ctk.CTkButton(self.sidebar, text="Comprar Filamentos", 
                      fg_color="transparent", border_width=1, text_color=("gray10", "gray90"),
                      command=lambda: webbrowser.open("https://listado.mercadolibre.com.ar/impresion-3d-insumos")).pack(pady=5, padx=20)
        
    def mostrar_impresoras(self):
        """Muestra la lista de impresoras y formulario para agregar"""
        # 1. Limpiamos el panel derecho (borramos lo que había antes)
        for widget in self.main_area.winfo_children():
            widget.destroy()

        # 2. Título
        ctk.CTkLabel(self.main_area, text="Gestión de Impresoras", font=("Roboto", 24)).pack(pady=10)

        # 3. Formulario para agregar nueva (Un Frame chiquito arriba)
        frame_add = ctk.CTkFrame(self.main_area)
        frame_add.pack(fill="x", padx=20, pady=10)

        entry_nombre = ctk.CTkEntry(frame_add, placeholder_text="Nombre nueva impresora (Ej: Ender 3)")
        entry_nombre.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        def accion_guardar():
            nombre = entry_nombre.get()
            if nombre:
                if database.agregar_impresora(nombre):
                    messagebox.showinfo("Éxito", "Impresora guardada")
                    self.mostrar_impresoras() # Recargamos la pantalla para ver la nueva
                else:
                    messagebox.showerror("Error", "No se pudo guardar")
            else:
                messagebox.showwarning("Atención", "Escribí un nombre primero")

        ctk.CTkButton(frame_add, text="Guardar", fg_color="green", command=accion_guardar).pack(side="right", padx=10)

        # 4. Lista de Impresoras (Usamos ScrollableFrame por si hay muchas)
        scroll_frame = ctk.CTkScrollableFrame(self.main_area)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        lista = database.obtener_impresoras()
        
        if not lista:
            ctk.CTkLabel(scroll_frame, text="No hay impresoras registradas aún.").pack(pady=20)
        else:
            for imp in lista:
                # imp es una tupla: (id, nombre, estado, horas)
                card = ctk.CTkFrame(scroll_frame)
                card.pack(fill="x", pady=5)
                
                # Datos a la izquierda
                texto_info = f"{imp[1]}\nEstado: {imp[2]} | Horas: {imp[3]}"
                ctk.CTkLabel(card, text=texto_info, anchor="w", justify="left").pack(side="left", padx=10, pady=5)
    # --- Lógica de Botones ---

    def evento_login(self):
        user = self.entry_user.get()
        password = self.entry_pass.get()

        if database.login_usuario(user, password):
            messagebox.showinfo("Éxito", f"Bienvenido, {user}!")
            self.mostrar_menu_principal() # ¡Vamos al menú!
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

    def evento_registro(self):
        user = self.entry_user.get()
        password = self.entry_pass.get()

        if not user or not password:
            messagebox.showwarning("Faltan datos", "Por favor completa usuario y contraseña.")
            return

        if database.registrar_usuario(user, password):
            messagebox.showinfo("Registro Exitoso", "Usuario creado. Ahora puedes iniciar sesión.")
        else:
            messagebox.showerror("Error", "El usuario ya existe.")

if __name__ == "__main__":
    app = App()
    app.mainloop()