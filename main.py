import customtkinter as ctk
from tkinter import messagebox
import database
import webbrowser
import os
from PIL import Image
import config
from vistas.anuncio import VentanaAnuncio
# Importamos las vistas
from vistas.impresoras import VistaImpresoras
from vistas.bobinas import VistaBobinas
from vistas.historial import VistaHistorial
from vistas.nueva_impresion import VistaNuevaImpresion
from vistas.inicio import VistaInicio

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestión Taller 3D")
        self.geometry("1100x700")
        
        self.vista_actual = None
        self.usuario_id = None
        self.usuario_nombre = "Usuario"
        self.usuario_empresa = "Mi Taller"

        # --- CARGA DE IMÁGENES SEGURA ---
        self.cargar_imagenes()
        
        # Iniciamos
        self.mostrar_login()

    def cargar_imagenes(self):
        """Intenta cargar imagenes, si fallan usa None para no romper el programa"""
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")
        self.logo_image = None
        self.logo_menu = None
        self.icon_home = None
        self.icon_printer = None
        self.icon_filament = None
        self.icon_add = None

        try:
            # Solo cargamos si el archivo existe
            if os.path.exists(os.path.join(image_path, "logo.png")):
                self.logo_image = ctk.CTkImage(Image.open(os.path.join(image_path, "logo.png")), size=(100, 100))
                self.logo_menu = ctk.CTkImage(Image.open(os.path.join(image_path, "logo.png")), size=(30, 30))
            
            if os.path.exists(os.path.join(image_path, "home.png")):
                self.icon_home = ctk.CTkImage(Image.open(os.path.join(image_path, "home.png")), size=(20, 20))
                
            if os.path.exists(os.path.join(image_path, "printer.png")):
                self.icon_printer = ctk.CTkImage(Image.open(os.path.join(image_path, "printer.png")), size=(20, 20))
                
            if os.path.exists(os.path.join(image_path, "filament.png")):
                self.icon_filament = ctk.CTkImage(Image.open(os.path.join(image_path, "filament.png")), size=(20, 20))
                
            if os.path.exists(os.path.join(image_path, "add.png")):
                self.icon_add = ctk.CTkImage(Image.open(os.path.join(image_path, "add.png")), size=(20, 20))
                
        except Exception as e:
            print(f"Advertencia: No se pudieron cargar algunas imágenes ({e})")

    # --- PANTALLA LOGIN ---
    def mostrar_login(self):
        for widget in self.winfo_children(): widget.destroy()
        self.configure(fg_color=config.COLOR_FONDO_APP)

        frame = ctk.CTkFrame(self, fg_color=config.COLOR_MENU_LATERAL, corner_radius=15)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        if self.logo_image:
            ctk.CTkLabel(frame, text="", image=self.logo_image).pack(pady=(40, 10), padx=50)
        
        ctk.CTkLabel(frame, text="BIENVENIDO", font=("Segoe UI", 24, "bold"), text_color="white").pack(pady=(0, 20))

        self.entry_user = ctk.CTkEntry(frame, placeholder_text="Usuario", width=250, height=40)
        self.entry_user.pack(pady=10, padx=40)
        self.entry_pass = ctk.CTkEntry(frame, placeholder_text="Contraseña", show="*", width=250, height=40)
        self.entry_pass.pack(pady=10, padx=40)

        ctk.CTkButton(frame, text="INICIAR SESIÓN", width=250, height=40, fg_color=config.COLOR_VERDE_BAMBU, hover_color=config.COLOR_VERDE_HOVER, font=("Segoe UI", 14, "bold"), command=self.evento_login).pack(pady=20)
        
        ctk.CTkFrame(frame, height=1, width=200, fg_color=config.COLOR_SEPARADOR).pack(pady=10)
        
        ctk.CTkLabel(frame, text="¿No tienes cuenta?", text_color="gray").pack()
        ctk.CTkButton(frame, text="Crear Cuenta Nueva", fg_color="transparent", text_color=config.COLOR_VERDE_BAMBU, hover_color="#333", command=self.mostrar_registro).pack(pady=(0, 30))

    # --- PANTALLA REGISTRO ---
    def mostrar_registro(self):
        for widget in self.winfo_children(): widget.destroy()
        self.configure(fg_color=config.COLOR_FONDO_APP)

        frame = ctk.CTkFrame(self, fg_color=config.COLOR_MENU_LATERAL, corner_radius=15)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="CREAR CUENTA", font=("Segoe UI", 24, "bold"), text_color="white").pack(pady=(40, 20), padx=50)

        self.entry_reg_user = ctk.CTkEntry(frame, placeholder_text="Nombre de Usuario", width=250, height=40)
        self.entry_reg_user.pack(pady=10, padx=40)
        
        self.entry_reg_empresa = ctk.CTkEntry(frame, placeholder_text="Nombre de tu Taller / Empresa", width=250, height=40)
        self.entry_reg_empresa.pack(pady=10, padx=40)

        self.entry_reg_pass = ctk.CTkEntry(frame, placeholder_text="Contraseña", show="*", width=250, height=40)
        self.entry_reg_pass.pack(pady=10, padx=40)

        ctk.CTkButton(frame, text="REGISTRARSE", width=250, height=40, fg_color=config.COLOR_VERDE_BAMBU, hover_color=config.COLOR_VERDE_HOVER, font=("Segoe UI", 14, "bold"), command=self.evento_registro).pack(pady=20)
        ctk.CTkButton(frame, text="Volver al Login", fg_color="transparent", text_color="gray", hover_color="#333", command=self.mostrar_login).pack(pady=(0, 30))

    # --- EVENTOS LOGIN/REGISTRO ---
    def evento_login(self):
        user = self.entry_user.get()
        password = self.entry_pass.get()
        res = database.login_usuario(user, password)
        if res:
            self.usuario_id, self.usuario_nombre, self.usuario_empresa = res
            self.mostrar_menu_principal()
        else:
            messagebox.showerror("Error", "Datos incorrectos.")

    def evento_registro(self):
        user, pwd, emp = self.entry_reg_user.get(), self.entry_reg_pass.get(), self.entry_reg_empresa.get()
        if not user or not pwd or not emp:
            messagebox.showwarning("Atención", "Completa todos los campos.")
            return
        if database.registrar_usuario(user, pwd, emp):
            messagebox.showinfo("Éxito", "Cuenta creada.")
            self.mostrar_login()
        else:
            messagebox.showerror("Error", "Usuario existente.")

    # --- MENÚ PRINCIPAL ---
    def mostrar_menu_principal(self):
        for widget in self.winfo_children(): widget.destroy()

        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=config.COLOR_MENU_LATERAL)
        self.sidebar.pack(side="left", fill="y")

        # 1. Cabecera (Logo Casa + Nombre Empresa)
        frame_header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        frame_header.pack(fill="x", pady=(20, 5), padx=10)
        
        # Botón Inicio (Cuadrado Verde tipo MakerWorld)
        btn_home = ctk.CTkButton(frame_header, text="", image=self.icon_home, width=40, height=40, 
                                 fg_color=config.COLOR_VERDE_BAMBU, hover_color=config.COLOR_VERDE_HOVER, 
                                 corner_radius=4, command=self.ir_a_inicio)
        btn_home.pack(side="left")
        
        empresa_text = (self.usuario_empresa[:15] + '..') if self.usuario_empresa and len(self.usuario_empresa) > 15 else (self.usuario_empresa or "MI TALLER")
        ctk.CTkLabel(frame_header, text=f"  {empresa_text.upper()}", font=("Segoe UI", 14, "bold"), text_color="white").pack(side="left")

        # 2. Perfil Usuario
        frame_perfil = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        frame_perfil.pack(fill="x", padx=10, pady=(5, 15))
        # Icono circular simulado
        ctk.CTkLabel(frame_perfil, text="👤", font=("Segoe UI", 16)).pack(side="left", padx=(5,0))
        ctk.CTkLabel(frame_perfil, text=f" {self.usuario_nombre}", text_color="gray", font=("Segoe UI", 12)).pack(side="left")

        ctk.CTkFrame(self.sidebar, height=1, fg_color=config.COLOR_SEPARADOR).pack(fill="x", pady=(0, 20))

        # 3. Botones del Menú
        self.crear_titulo_seccion("BIBLIOTECA")
        #self.crear_boton_menu("Panel Inicio", self.icon_home, self.ir_a_inicio)
        self.crear_boton_menu("Mis Impresoras", self.icon_printer, self.ir_a_impresoras)
        self.crear_boton_menu("Filamentos", self.icon_filament, self.ir_a_bobinas)
        self.crear_boton_menu("Historial", self.icon_printer, self.ir_a_historial) # <--- Apunta a historial

        self.crear_titulo_seccion("ACCIONES")
        self.crear_boton_menu("Nueva Impresión", self.icon_add, self.ir_a_nueva_impresion, destacado=True)
        self.crear_titulo_seccion("WEB")
        self.crear_boton_menu("Comprar Máquinas", None, lambda: webbrowser.open("https://listado.mercadolibre.com.ar/impresion-3d-impresoras"))
        self.crear_boton_menu("Comprar Insumos", None, lambda: webbrowser.open("https://listado.mercadolibre.com.ar/impresion-3d-insumos"))

        # 4. Zona Inferior
        frame_bottom = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        frame_bottom.pack(side="bottom", fill="x", pady=20, padx=10)

        self.switch_modo = ctk.CTkSwitch(frame_bottom, text="Modo Guía", font=("Segoe UI", 12), text_color="white",
                                         progress_color=config.COLOR_VERDE_BAMBU, fg_color="#444", button_color="white",
                                         command=self.evento_cambiar_modo)
        if config.MODO_PRINCIPIANTE: self.switch_modo.select()
        else: self.switch_modo.deselect()
        self.switch_modo.pack(pady=(0, 15), padx=5)

        ctk.CTkFrame(frame_bottom, height=1, fg_color=config.COLOR_SEPARADOR).pack(fill="x", pady=(0, 10))
        
        ctk.CTkButton(frame_bottom, text=" Cerrar Sesión", image=self.logo_menu, compound="left", anchor="w",
                      fg_color="transparent", text_color=config.COLOR_ROJO, hover_color="#3a2a2a",
                      command=self.mostrar_login).pack(fill="x")

        # Área Principal
        self.main_area = ctk.CTkFrame(self, fg_color=config.COLOR_FONDO_APP)
        self.main_area.pack(side="right", fill="both", expand=True)

        self.ir_a_inicio()
        self.after(1000, self.mostrar_anuncio)
    def crear_titulo_seccion(self, texto):
        ctk.CTkLabel(self.sidebar, text=texto, font=("Segoe UI", 11, "bold"), text_color=config.COLOR_TEXTO_GRIS, anchor="w").pack(fill="x", padx=15, pady=(15, 5))
    def mostrar_anuncio(self):
    # Solo mostramos si no hay ya una ventana abierta (opcional)
        VentanaAnuncio(self)
    def crear_boton_menu(self, texto, icono, comando, destacado=False):
        color_texto, color_hover, color_fg = "#FFFFFF", "#3A3A3A", "transparent"
        if destacado:
            color_fg, color_hover = config.COLOR_VERDE_BAMBU, config.COLOR_VERDE_HOVER
        
        # Protección por si la imagen es None
        img = icono if icono else None
        
        btn = ctk.CTkButton(self.sidebar, text=f"  {texto}", image=img, compound="left", anchor="w",
                            height=35, corner_radius=6, font=("Segoe UI", 13),
                            fg_color=color_fg, text_color=color_texto, hover_color=color_hover,
                            command=comando)
        btn.pack(fill="x", padx=10, pady=2)
    
    def evento_cambiar_modo(self):
        config.MODO_PRINCIPIANTE = bool(self.switch_modo.get())
        # Actualizamos la vista actual si corresponde
        if isinstance(self.vista_actual, VistaImpresoras): self.ir_a_impresoras()
        elif isinstance(self.vista_actual, VistaBobinas): self.ir_a_bobinas()
        elif isinstance(self.vista_actual, VistaNuevaImpresion): self.ir_a_nueva_impresion() # <--- Cambio aquí

    def cambiar_vista(self, clase_vista, **kwargs):
        if self.vista_actual is not None: self.vista_actual.destroy()
        
        # El callback ahora apunta a ir_a_nueva_impresion
        if clase_vista == VistaInicio:
            self.vista_actual = clase_vista(self.main_area, user_id=self.usuario_id, callback_nueva_impresion=self.ir_a_nueva_impresion)
        else:
            self.vista_actual = clase_vista(self.main_area, user_id=self.usuario_id)
        self.vista_actual.pack(fill="both", expand=True)

    # Rutas
    def ir_a_inicio(self): self.cambiar_vista(VistaInicio)
    def ir_a_impresoras(self): self.cambiar_vista(VistaImpresoras)
    def ir_a_bobinas(self): self.cambiar_vista(VistaBobinas)
    
    # NUEVAS RUTAS
    def ir_a_historial(self): self.cambiar_vista(VistaHistorial)
    def ir_a_nueva_impresion(self): self.cambiar_vista(VistaNuevaImpresion)

if __name__ == "__main__":
    app = App()
    app.mainloop()