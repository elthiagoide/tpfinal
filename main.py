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
from vistas.agenda import VistaAgenda
from vistas.planificador import VistaPlanificador

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

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=config.COLOR_MENU_LATERAL)
        self.sidebar.pack(side="left", fill="y")

        # 1. Cabecera (Logo Casa + Nombre Empresa)
        frame_header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        frame_header.pack(fill="x", pady=(12, 6), padx=10)

        # Botón Inicio (Cuadrado Verde tipo MakerWorld)
        btn_home = ctk.CTkButton(frame_header, text="", image=self.icon_home, width=40, height=40,
                     fg_color=config.COLOR_VERDE_BAMBU, hover_color=config.COLOR_VERDE_HOVER,
                     corner_radius=4, command=self.ir_a_inicio)
        btn_home.pack(side="left")
        # Pequeña casilla junto a la casita que muestra/oculta el panel de control
        frame_header_pc = ctk.CTkFrame(frame_header, fg_color="transparent")
        frame_header_pc.pack(side='left', padx=(8,0))
        ctk.CTkLabel(frame_header_pc, text="Panel de Control", font=("Segoe UI", 11), text_color="white").pack(side='left', padx=(6,0))
        # 2. Perfil Usuario (dejamos espacio en header; perfil y logout se muestran en el pie)
        frame_perfil = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        frame_perfil.pack(fill="x", padx=10, pady=(5, 6))
        ctk.CTkLabel(frame_perfil, text="", fg_color="transparent").pack()

        ctk.CTkFrame(self.sidebar, height=1, fg_color=config.COLOR_SEPARADOR).pack(fill="x", pady=(0, 20))

        # 3. Botones del Menú (orden personalizado)
        self.crear_titulo_seccion("ACCIONES")
        # Orden según petición: Nueva Impresión, Historial, Planificación, Agenda, Mis Impresoras, Filamentos
        self.crear_boton_menu("Nueva Impresión", self.icon_add, self.ir_a_nueva_impresion, destacado=True)
        self.crear_boton_menu("Historial", self.icon_printer, self.ir_a_historial)
        self.crear_boton_menu("Planificador", None, self.ir_a_planificador)
        self.crear_boton_menu("Agenda", None, self.ir_a_agenda)

        # Mover items de biblioteca dentro de ACCIONES para simplificar
        self.crear_boton_menu("Mis Impresoras", self.icon_printer, self.ir_a_impresoras)
        self.crear_boton_menu("Filamentos", self.icon_filament, self.ir_a_bobinas)
        self.crear_titulo_seccion("WEB")
        self.crear_boton_menu("Comprar Máquinas", None, lambda: webbrowser.open("https://listado.mercadolibre.com.ar/impresion-3d-impresoras"))
        self.crear_boton_menu("Comprar Insumos", None, lambda: webbrowser.open("https://listado.mercadolibre.com.ar/impresion-3d-insumos"))

        # Panel de Control: tres opciones (aparecen entre 'Comprar Insumos' y el footer)
        self.panel_control = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.panel_control.pack(fill='x', padx=12, pady=(12,6))

        # Modo Guía (switch compacto, deseleccionado por defecto)
        row_guia = ctk.CTkFrame(self.panel_control, fg_color="transparent")
        row_guia.pack(fill='x', pady=4)
        self.switch_modo = ctk.CTkSwitch(row_guia, text="", progress_color=config.COLOR_VERDE_BAMBU, fg_color="#444", button_color="white", command=self.evento_cambiar_modo)
        self.switch_modo.deselect()
        self.switch_modo.pack(side='left')
        ctk.CTkLabel(row_guia, text="Modo Guía", text_color="white", font=("Segoe UI", 11)).pack(side='left', padx=8)

        # Modo Claro
        row_claro = ctk.CTkFrame(self.panel_control, fg_color="transparent")
        row_claro.pack(fill='x', pady=4)
        self.switch_modo_claro = ctk.CTkSwitch(row_claro, text="", progress_color=config.COLOR_VERDE_BAMBU, fg_color="#444", button_color="white", command=self.evento_modo_claro)
        self.switch_modo_claro.deselect()
        self.switch_modo_claro.pack(side='left')
        ctk.CTkLabel(row_claro, text="Modo Claro", text_color="white", font=("Segoe UI", 11)).pack(side='left', padx=8)

        # Negrita
        row_negrita = ctk.CTkFrame(self.panel_control, fg_color="transparent")
        row_negrita.pack(fill='x', pady=4)
        self.switch_negrita = ctk.CTkSwitch(row_negrita, text="", progress_color=config.COLOR_VERDE_BAMBU, fg_color="#444", button_color="white", command=self.evento_negrita)
        self.switch_negrita.deselect()
        self.switch_negrita.pack(side='left')
        ctk.CTkLabel(row_negrita, text="Negrita", text_color="white", font=("Segoe UI", 11)).pack(side='left', padx=8)

        # 4. Zona Inferior: perfil + logout, separador y switches
        frame_bottom = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        frame_bottom.pack(side="bottom", fill="x", pady=12, padx=10)

        # Perfil y Cerrar Sesión juntos al pie
        bottom_profile = ctk.CTkFrame(frame_bottom, fg_color="transparent")
        bottom_profile.pack(fill='x', pady=(4,8))
        empresa_text = (self.usuario_empresa[:18] + '..') if self.usuario_empresa and len(self.usuario_empresa) > 18 else (self.usuario_empresa or "Mi Taller")
        ctk.CTkLabel(bottom_profile, text=f"👤  {self.usuario_nombre} - {empresa_text}", text_color="white", font=("Segoe UI", 13, "bold")).pack(side='left')
        ctk.CTkButton(bottom_profile, text="Cerrar Sesión", fg_color="transparent", text_color=config.COLOR_ROJO, hover_color="#3a2a2a", command=self.mostrar_login).pack(side='right')

        # Separador
        ctk.CTkFrame(frame_bottom, height=1, fg_color=config.COLOR_SEPARADOR).pack(fill="x", pady=(2, 8))

        # Área Principal
        self.main_area = ctk.CTkFrame(self, fg_color=config.COLOR_FONDO_APP)
        self.main_area.pack(side="right", fill="both", expand=True)

        # Aplicar tema actual luego de construir la UI
        try:
            self._apply_current_theme()
        except Exception:
            pass

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

    def evento_modo_claro(self):
        try:
            if self.switch_modo_claro.get():
                ctk.set_appearance_mode("Light")
                # colores claros aproximados
                sidebar_bg = "#F0F2F4"
                main_bg = "#FFFFFF"
                text_color = "black"
                self._show_mode_toast("Modo Claro activado")
            else:
                ctk.set_appearance_mode("Dark")
                sidebar_bg = config.COLOR_MENU_LATERAL
                main_bg = config.COLOR_FONDO_APP
                text_color = "white"
                self._show_mode_toast("Modo Oscuro activado")

            # Actualizar colores de contenedores principales
            try:
                if hasattr(self, 'sidebar') and self.sidebar is not None:
                    self.sidebar.configure(fg_color=sidebar_bg)
                if hasattr(self, 'main_area') and self.main_area is not None:
                    self.main_area.configure(fg_color=main_bg)
            except Exception:
                pass

            # Aplicar tema de forma recursiva a contenedores y widgets comunes
            def apply_recursively(container, sidebar_mode=False):
                if not container: return
                for w in container.winfo_children():
                    try:
                        # Ajustes por tipo
                        if isinstance(w, ctk.CTkLabel):
                            w.configure(text_color=text_color)
                        elif isinstance(w, ctk.CTkButton):
                            try: w.configure(text_color=text_color)
                            except Exception: pass
                        elif isinstance(w, ctk.CTkEntry):
                            try: w.configure(fg_color=main_bg, text_color=text_color)
                            except Exception: pass
                        # No tocar CTkFrame internos para preservar estilos de tarjetas y recuadros
                        elif isinstance(w, ctk.CTkFrame):
                            pass
                        elif isinstance(w, ctk.CTkSwitch):
                            # Los switches tienen apariencia propia; ajustar label si hay uno al lado
                            try: 
                                # muchos switches están acompañados por un Label sibling
                                pass
                            except Exception: pass
                    except Exception:
                        pass
                    # Recurse
                    try:
                        apply_recursively(w, sidebar_mode=sidebar_mode)
                    except Exception:
                        pass

            try:
                apply_recursively(self.sidebar, sidebar_mode=True)
                apply_recursively(self.main_area, sidebar_mode=False)
                try:
                    if self.vista_actual:
                        apply_recursively(self.vista_actual, sidebar_mode=False)
                except Exception:
                    pass
                # also ensure the stored panel_control label/switches reflect the change
                try:
                    if hasattr(self, 'panel_control') and self.panel_control:
                        apply_recursively(self.panel_control, sidebar_mode=True)
                except Exception:
                    pass
                # and the small checkbox/label in header
                try:
                    if hasattr(self, 'checkbox_panel') and self.checkbox_panel:
                        # label sibling
                        parent = self.checkbox_panel.master
                        for w in parent.winfo_children():
                            try:
                                if isinstance(w, ctk.CTkLabel):
                                    w.configure(text_color=text_color)
                            except Exception:
                                pass
                except Exception:
                    pass
            except Exception:
                pass
        except Exception:
            pass

    def _show_mode_toast(self, text):
        # pequeña confirmación visual en la vista principal
        try:
            toast = ctk.CTkLabel(self.main_area, text=text, fg_color=config.COLOR_TARJETA, corner_radius=6, text_color="white")
            toast.place(relx=0.5, rely=0.02, anchor='n')
            self.after(1200, toast.destroy)
        except Exception:
            pass

    def evento_negrita(self):
        try:
            enabled = bool(self.switch_negrita.get())
            # Delegar a la vista actual si soporta el cambio
            if self.vista_actual and hasattr(self.vista_actual, 'apply_negrita'):
                try:
                    self.vista_actual.apply_negrita(enabled)
                except Exception:
                    pass
            # Aplicar de forma más global: sidebar y main_area
            try:
                def apply_font_to_widget(w):
                    try:
                        if hasattr(w, 'cget'):
                            f = w.cget('font')
                            if not f:
                                return
                            # normalizar a lista
                            if isinstance(f, str):
                                parts = f.split()
                            else:
                                parts = list(f)
                            # si está habilitado, asegurarse de 'bold' en estilos
                            if enabled:
                                if 'bold' not in [str(x).lower() for x in parts]:
                                    parts.append('bold')
                            else:
                                parts = [p for p in parts if str(p).lower() != 'bold']
                            try:
                                w.configure(font=tuple(parts))
                            except Exception:
                                pass
                    except Exception:
                        pass

                for container in (self.sidebar, self.main_area):
                    try:
                        for w in container.winfo_children():
                            apply_font_to_widget(w)
                            # algunos contenedores tienen hijos adicionales
                            try:
                                for c in w.winfo_children():
                                    apply_font_to_widget(c)
                            except Exception:
                                pass
                    except Exception:
                        pass
            except Exception:
                pass
        except Exception:
            pass

    def cambiar_vista(self, clase_vista, **kwargs):
        if self.vista_actual is not None: self.vista_actual.destroy()
        
        # El callback ahora apunta a ir_a_nueva_impresion
        if clase_vista == VistaInicio:
            self.vista_actual = clase_vista(self.main_area, user_id=self.usuario_id, callback_nueva_impresion=self.ir_a_nueva_impresion, **kwargs)
        else:
            self.vista_actual = clase_vista(self.main_area, user_id=self.usuario_id, **kwargs)
        self.vista_actual.pack(fill="both", expand=True)
        # Reaplicar tema actual por si la nueva vista necesita ajustes
        try:
            self._apply_current_theme()
        except Exception:
            pass

    def _apply_current_theme(self):
        # Aplica los colores actuales según ctk.get_appearance_mode()
        try:
            mode = ctk.get_appearance_mode()
        except Exception:
            mode = 'Dark'
        if mode == 'Light':
            sidebar_bg = "#F0F2F4"
            main_bg = "#FFFFFF"
            text_color = "black"
        else:
            sidebar_bg = config.COLOR_MENU_LATERAL
            main_bg = config.COLOR_FONDO_APP
            text_color = "white"

        # ajustar contenedores principales
        try:
            if hasattr(self, 'sidebar') and self.sidebar:
                self.sidebar.configure(fg_color=sidebar_bg)
            if hasattr(self, 'main_area') and self.main_area:
                self.main_area.configure(fg_color=main_bg)
        except Exception:
            pass

        # aplicar recursivamente
        def apply_recursively(container, sidebar_mode=False):
            if not container: return
            for w in container.winfo_children():
                try:
                    if isinstance(w, ctk.CTkLabel):
                        w.configure(text_color=text_color)
                    elif isinstance(w, ctk.CTkButton):
                        try: w.configure(text_color=text_color)
                        except Exception: pass
                    elif isinstance(w, ctk.CTkEntry):
                        try: w.configure(fg_color=main_bg, text_color=text_color)
                        except Exception: pass
                    elif isinstance(w, ctk.CTkFrame):
                        # preservar fg_color de frames internos (tarjetas), no forzar
                        pass
                except Exception:
                    pass
                try:
                    apply_recursively(w, sidebar_mode=sidebar_mode)
                except Exception:
                    pass

        try:
            apply_recursively(self.sidebar, sidebar_mode=True)
            apply_recursively(self.main_area, sidebar_mode=False)
            if hasattr(self, 'vista_actual') and self.vista_actual:
                try: apply_recursively(self.vista_actual, sidebar_mode=False)
                except Exception: pass
        except Exception:
            pass

    # Rutas
    def ir_a_inicio(self): self.cambiar_vista(VistaInicio)
    def ir_a_impresoras(self): self.cambiar_vista(VistaImpresoras)
    def ir_a_bobinas(self): self.cambiar_vista(VistaBobinas)
    
    # NUEVAS RUTAS
    def ir_a_historial(self): self.cambiar_vista(VistaHistorial)
    def ir_a_nueva_impresion(self): self.cambiar_vista(VistaNuevaImpresion)
    def ir_a_agenda(self, pid=None): self.cambiar_vista(VistaAgenda, selected_pid=pid)
    def ir_a_planificador(self): self.cambiar_vista(VistaPlanificador)
    def ir_a_planificador(self): self.cambiar_vista(VistaPlanificador)

if __name__ == "__main__":
    app = App()
    app.mainloop()