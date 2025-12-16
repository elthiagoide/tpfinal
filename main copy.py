import customtkinter as ctk
from tkinter import messagebox
import database
import webbrowser
import os
from PIL import Image
import config
from vistas.anuncio import VentanaAnuncio

# Importar vistas
from vistas.impresoras import VistaImpresoras
from vistas.bobinas import VistaBobinas
from vistas.historial import VistaHistorial
from vistas.nueva_impresion import VistaNuevaImpresion
from vistas.inicio import VistaInicio
from vistas.agenda import VistaAgenda
from vistas.planificador import VistaPlanificador

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LayerHub | Gestión Profesional")
        self.geometry("1280x800")
        
        try: self.state('zoomed') 
        except: pass

        self.usuario_id = None
        self.usuario_nombre = ""
        self.usuario_empresa = ""
        self.vista_actual = None

        self.cargar_imagenes()

        # Variables de Configuración
        self.var_modo_claro = ctk.BooleanVar(value=False)
        self.var_modo_guia = ctk.BooleanVar(value=config.MODO_PRINCIPIANTE)

        # Lógica de Inicio
        usuarios = database.obtener_todos_usuarios()
        if usuarios:
            self.mostrar_seleccion_perfil(usuarios)
        else:
            self.mostrar_login_clasico()

    def cargar_imagenes(self):
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")
        self.icon_home = None; self.icon_printer = None; self.icon_filament = None; self.icon_add = None; self.img_avatar = None
        try:
            if os.path.exists(os.path.join(image_path, "home.png")): self.icon_home = ctk.CTkImage(Image.open(os.path.join(image_path, "home.png")), size=(20, 20))
            if os.path.exists(os.path.join(image_path, "printer.png")): self.icon_printer = ctk.CTkImage(Image.open(os.path.join(image_path, "printer.png")), size=(20, 20))
            if os.path.exists(os.path.join(image_path, "filament.png")): self.icon_filament = ctk.CTkImage(Image.open(os.path.join(image_path, "filament.png")), size=(20, 20))
            if os.path.exists(os.path.join(image_path, "add.png")): self.icon_add = ctk.CTkImage(Image.open(os.path.join(image_path, "add.png")), size=(20, 20))
            if os.path.exists(os.path.join(image_path, "logo.png")): self.img_avatar = ctk.CTkImage(Image.open(os.path.join(image_path, "logo.png")), size=(50, 50))
        except: pass

    # --- PANTALLA 1: SELECCIÓN DE PERFIL ---
    def mostrar_seleccion_perfil(self, lista_usuarios):
        for w in self.winfo_children(): w.destroy()
        self.configure(fg_color=config.COLOR_FONDO_APP)

        ctk.CTkLabel(self, text="¿Quién está imprimiendo hoy?", font=config.FONT_TITULO, text_color=config.COLOR_TEXTO_BLANCO).pack(pady=(80, 50))

        frame_perfiles = ctk.CTkFrame(self, fg_color="transparent")
        frame_perfiles.pack()

        for usuario in lista_usuarios:
            username = usuario[0]
            card = ctk.CTkFrame(frame_perfiles, fg_color="transparent")
            card.pack(side="left", padx=30)

            img_sel = ctk.CTkImage(Image.open(os.path.join("assets", "logo.png")), size=(120, 120)) if self.img_avatar else None
            
            btn = ctk.CTkButton(card, text="", width=140, height=140, 
                                image=img_sel, 
                                fg_color=config.COLOR_TARJETA, 
                                hover_color=config.COLOR_ACENTO,
                                corner_radius=20,
                                command=lambda u=username: self.mostrar_login_password(u))
            btn.pack()
            ctk.CTkLabel(card, text=username, font=config.FONT_SUBTITULO, text_color=config.COLOR_TEXTO_GRIS).pack(pady=15)

        ctk.CTkButton(self, text="+ Agregar Cuenta", fg_color="transparent", text_color="gray", 
                      font=config.FONT_TEXTO, hover_color="#222",
                      command=self.mostrar_login_clasico).pack(pady=80)

    # --- PANTALLA 2: PASSWORD ---
    def mostrar_login_password(self, prefill_user):
        for w in self.winfo_children(): w.destroy()
        
        card = ctk.CTkFrame(self, fg_color=config.COLOR_TARJETA, corner_radius=20, border_width=1, border_color="#333")
        card.place(relx=0.5, rely=0.5, anchor="center")

        if self.img_avatar:
            ctk.CTkLabel(card, text="", image=self.img_avatar).pack(pady=(30, 10))

        ctk.CTkLabel(card, text=f"Hola, {prefill_user}", font=config.FONT_SUBTITULO, text_color=config.COLOR_TEXTO_BLANCO).pack(pady=(0, 20), padx=60)
        
        self.entry_pass = ctk.CTkEntry(card, placeholder_text="Contraseña", show="*", width=260, height=45, 
                                     fg_color=config.COLOR_FONDO_APP, border_color="#333", text_color=config.COLOR_TEXTO_BLANCO, font=config.FONT_TEXTO)
        self.entry_pass.pack(pady=10)
        self.entry_pass.focus()
        self.entry_pass.bind("<Return>", lambda event: self.evento_login_rapido(prefill_user))

        ctk.CTkButton(card, text="INGRESAR", width=260, height=45, 
                      fg_color=config.COLOR_ACENTO, hover_color=config.COLOR_ACENTO_HOVER, 
                      font=config.FONT_BOTON,
                      command=lambda: self.evento_login_rapido(prefill_user)).pack(pady=20)
        
        ctk.CTkButton(card, text="← Cambiar usuario", fg_color="transparent", text_color="gray", hover_color="#222", font=config.FONT_SMALL,
                      command=lambda: self.mostrar_seleccion_perfil(database.obtener_todos_usuarios())).pack(pady=(0,20))

    def evento_login_rapido(self, user):
        pwd = self.entry_pass.get()
        res = database.login_usuario(user, pwd)
        if res:
            self.usuario_id, self.usuario_nombre, self.usuario_empresa = res
            self.mostrar_menu_principal()
        else:
            messagebox.showerror("Error", "Contraseña incorrecta")

    # --- PANTALLA 3: LOGIN CLÁSICO ---
    def mostrar_login_clasico(self):
        for w in self.winfo_children(): w.destroy()
        self.configure(fg_color=config.COLOR_FONDO_APP)
        
        card = ctk.CTkFrame(self, fg_color=config.COLOR_TARJETA, corner_radius=20)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card, text="NUEVA CUENTA", font=config.FONT_TITULO, text_color=config.COLOR_TEXTO_BLANCO).pack(pady=(30, 20), padx=60)
        
        self.entry_reg_user = ctk.CTkEntry(card, placeholder_text="Usuario", width=280, height=40, fg_color=config.COLOR_FONDO_APP, text_color=config.COLOR_TEXTO_BLANCO, font=config.FONT_TEXTO)
        self.entry_reg_user.pack(pady=5)
        self.entry_reg_empresa = ctk.CTkEntry(card, placeholder_text="Nombre del Taller", width=280, height=40, fg_color=config.COLOR_FONDO_APP, text_color=config.COLOR_TEXTO_BLANCO, font=config.FONT_TEXTO)
        self.entry_reg_empresa.pack(pady=5)
        self.entry_reg_pass = ctk.CTkEntry(card, placeholder_text="Contraseña", show="*", width=280, height=40, fg_color=config.COLOR_FONDO_APP, text_color=config.COLOR_TEXTO_BLANCO, font=config.FONT_TEXTO)
        self.entry_reg_pass.pack(pady=5)

        ctk.CTkButton(card, text="CREAR CUENTA", width=280, height=45, fg_color=config.COLOR_ACENTO, font=config.FONT_BOTON, command=self.evento_registro).pack(pady=20)
        
        if database.obtener_todos_usuarios():
             ctk.CTkButton(card, text="Cancelar", fg_color="transparent", text_color="gray", hover_color="#222", font=config.FONT_SMALL,
                           command=lambda: self.mostrar_seleccion_perfil(database.obtener_todos_usuarios())).pack(pady=10)

    def evento_registro(self):
        u, p, e = self.entry_reg_user.get(), self.entry_reg_pass.get(), self.entry_reg_empresa.get()
        if not u or not p:
            messagebox.showwarning("Error", "Faltan datos")
            return 
        if database.registrar_usuario(u, p, e):
            self.mostrar_seleccion_perfil(database.obtener_todos_usuarios())
        else: 
            messagebox.showerror("Error", "El usuario ya existe")

    # --- MENÚ LATERAL ---
    def mostrar_menu_principal(self, navigate=True):
        # Detectar qué vista estamos mostrando para recargarla si hace falta
        vista_actual_class = VistaInicio 
        if not navigate and self.vista_actual:
            vista_actual_class = self.vista_actual.__class__

        for widget in self.winfo_children(): widget.destroy()
        
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=config.COLOR_MENU_LATERAL)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # 1. PERFIL COMPACTO
        profile_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        profile_box.pack(fill="x", padx=20, pady=(30, 10))

        if self.img_avatar:
            avatar = ctk.CTkLabel(profile_box, text="", image=self.img_avatar) 
            avatar.pack(side="left", padx=(0, 12))
        else:
            ctk.CTkLabel(profile_box, text="👤", font=("Arial", 30), text_color="gray").pack(side="left", padx=(0, 12))
        
        info_box = ctk.CTkFrame(profile_box, fg_color="transparent")
        info_box.pack(side="left", fill="x")
        
        ctk.CTkLabel(info_box, text=self.usuario_nombre, font=config.FONT_BOTON, 
                     text_color=config.COLOR_TEXTO_BLANCO, anchor="w").pack(fill="x")
        
        btn_salir = ctk.CTkButton(info_box, text="Cerrar Sesión", height=18, width=0, 
                                  fg_color="transparent", text_color=config.COLOR_ROJO, hover_color="#333",
                                  font=config.FONT_SMALL, anchor="w",
                                  command=self.salir)
        btn_salir.pack(fill="x", pady=(2, 0))

        # 2. TALLER
        taller_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        taller_box.pack(fill="x", padx=20, pady=(0, 10))
        taller = self.usuario_empresa if self.usuario_empresa else "Mi Taller"
        ctk.CTkLabel(taller_box, text=taller.upper(), font=config.FONT_SMALL, text_color="gray", anchor="w").pack(fill="x")
        
        ctk.CTkFrame(self.sidebar, height=1, fg_color=config.COLOR_SEPARADOR).pack(fill="x", padx=20, pady=5)

        # 3. MENU SCROLL
        self.menu_scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.menu_scroll.pack(fill="both", expand=True)

        self.crear_titulo("INICIO")
        self.crear_boton("Dashboard", self.icon_home, self.ir_a_inicio)
        
        self.crear_titulo("PRODUCCIÓN")
        self.crear_boton("Nueva Impresión", self.icon_add, self.ir_a_nueva_impresion, destacado=True)
        self.crear_boton("Planificador Masivo", None, self.ir_a_planificador)
        self.crear_boton("Agenda", None, self.ir_a_agenda)
        self.crear_boton("Historial", self.icon_printer, self.ir_a_historial)
        
        self.crear_titulo("INVENTARIO")
        self.crear_boton("Impresoras", self.icon_printer, self.ir_a_impresoras)
        self.crear_boton("Filamentos", self.icon_filament, self.ir_a_bobinas)

        self.crear_titulo("TIENDA ONLINE")
        self.crear_boton("Comprar Máquinas", None, lambda: webbrowser.open("https://listado.mercadolibre.com.ar/impresion-3d-impresoras"))
        self.crear_boton("Comprar Insumos", None, lambda: webbrowser.open("https://listado.mercadolibre.com.ar/impresion-3d-insumos"))

        self.crear_titulo("AJUSTES")
        self.crear_switch("Modo Claro", self.var_modo_claro, self.toggle_tema)
        self.crear_switch("Ayuda Guiada", self.var_modo_guia, self.toggle_guia)

        # 4. AREA PRINCIPAL
        self.main_area = ctk.CTkFrame(self, fg_color=config.COLOR_FONDO_APP)
        self.main_area.pack(side="right", fill="both", expand=True, padx=30, pady=30)
        
        # Lógica de carga de vista (CORREGIDA)
        if navigate:
            self.ir_a_inicio()
            self.after(1000, lambda: VentanaAnuncio(self))
        else:
            # Si solo estamos refrescando (cambio de tema), mantenemos la vista
            if vista_actual_class == VistaInicio:
                self.cambiar_vista(vista_actual_class, callback_nueva_impresion=self.ir_a_nueva_impresion)
            else:
                self.cambiar_vista(vista_actual_class)

    # --- HELPERS ---
    def crear_titulo(self, txt):
        ctk.CTkLabel(self.menu_scroll, text=txt, font=config.FONT_BOTON, 
                     text_color=config.COLOR_TEXTO_GRIS, anchor="w").pack(fill="x", padx=25, pady=(15,5))

    def crear_boton(self, txt, icon, cmd, destacado=False):
        fg = "transparent"
        if destacado: fg = config.COLOR_ACENTO
        col_txt = "white" if destacado else config.COLOR_TEXTO_BLANCO
        
        ctk.CTkButton(self.menu_scroll, text=f"  {txt}", image=icon, compound="left", anchor="w", 
                      fg_color=fg, hover_color=config.COLOR_HOVER_BTN, 
                      text_color=col_txt, font=config.FONT_BOTON,
                      height=38, command=cmd).pack(fill="x", padx=15, pady=2)

    def crear_switch(self, txt, var, cmd):
        frame = ctk.CTkFrame(self.menu_scroll, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=2)
        ctk.CTkSwitch(frame, text=txt, variable=var, command=cmd, 
                      text_color=config.COLOR_TEXTO_BLANCO,
                      progress_color=config.COLOR_ACENTO, font=config.FONT_SMALL).pack(anchor="w")

    # --- EVENTOS ---
    def toggle_tema(self):
        if self.var_modo_claro.get():
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")
        self.mostrar_menu_principal(navigate=False)

    def toggle_guia(self): config.MODO_PRINCIPIANTE = self.var_modo_guia.get()
    
    def salir(self):
        self.usuario_id = None
        self.mostrar_seleccion_perfil(database.obtener_todos_usuarios())
    
    def destroy(self):
        try:
            import matplotlib.pyplot as plt
            plt.close('all')
        except: pass
        try:
            if self.vista_actual: self.vista_actual.destroy()
        except: pass
        super().destroy()

    def ir_a_inicio(self): self.cambiar_vista(VistaInicio, callback_nueva_impresion=self.ir_a_nueva_impresion)
    def ir_a_impresoras(self): self.cambiar_vista(VistaImpresoras)
    def ir_a_bobinas(self): self.cambiar_vista(VistaBobinas)
    def ir_a_historial(self): self.cambiar_vista(VistaHistorial)
    def ir_a_nueva_impresion(self): self.cambiar_vista(VistaNuevaImpresion)
    def ir_a_agenda(self): self.cambiar_vista(VistaAgenda)
    def ir_a_planificador(self): self.cambiar_vista(VistaPlanificador)

    def cambiar_vista(self, clase_vista, **kwargs):
        if self.vista_actual: self.vista_actual.destroy()
        self.vista_actual = clase_vista(self.main_area, user_id=self.usuario_id, **kwargs)
        self.vista_actual.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()