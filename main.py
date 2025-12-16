import customtkinter as ctk
from tkinter import messagebox, filedialog
import database
import webbrowser
import os
import shutil # Para copiar la imagen
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
        self.usuario_avatar_path = None # Variable nueva para guardar ruta
        self.vista_actual = None
        
        # Variable temporal para el registro
        self.ruta_avatar_temporal = None 

        self.crear_carpetas()
        self.cargar_imagenes_base()

        self.var_modo_claro = ctk.BooleanVar(value=False)
        self.var_modo_guia = ctk.BooleanVar(value=config.MODO_PRINCIPIANTE)

        usuarios = database.obtener_todos_usuarios()
        if usuarios: self.mostrar_seleccion_perfil(usuarios)
        else: self.mostrar_login_clasico()

    def crear_carpetas(self):
        # Crear carpeta para guardar avatares si no existe
        self.path_avatars = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets", "avatars")
        if not os.path.exists(self.path_avatars):
            os.makedirs(self.path_avatars)

    def cargar_imagenes_base(self):
        self.path_assets = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")
        self.icon_home = None; self.icon_printer = None; self.icon_filament = None; self.icon_add = None
        # Imagen default si no tiene avatar
        self.img_default = None 
        try:
            if os.path.exists(os.path.join(self.path_assets, "home.png")): self.icon_home = ctk.CTkImage(Image.open(os.path.join(self.path_assets, "home.png")), size=(20, 20))
            if os.path.exists(os.path.join(self.path_assets, "printer.png")): self.icon_printer = ctk.CTkImage(Image.open(os.path.join(self.path_assets, "printer.png")), size=(20, 20))
            if os.path.exists(os.path.join(self.path_assets, "filament.png")): self.icon_filament = ctk.CTkImage(Image.open(os.path.join(self.path_assets, "filament.png")), size=(20, 20))
            if os.path.exists(os.path.join(self.path_assets, "add.png")): self.icon_add = ctk.CTkImage(Image.open(os.path.join(self.path_assets, "add.png")), size=(20, 20))
            if os.path.exists(os.path.join(self.path_assets, "logo.png")): 
                self.img_default = ctk.CTkImage(Image.open(os.path.join(self.path_assets, "logo.png")), size=(80, 80))
        except: pass

    # --- HELPER: Cargar Avatar de Usuario ---
    def obtener_avatar_usuario(self, path_relativo, size=(80, 80)):
        """Carga la imagen desde la ruta guardada en DB, o usa default si falla"""
        if path_relativo and os.path.exists(path_relativo):
            try:
                return ctk.CTkImage(Image.open(path_relativo), size=size)
            except:
                pass # Si falla (archivo corrupto/borrado), usa default
        
        # Si no hay path o falló, usa el logo default con el tamaño pedido
        if self.img_default:
            # Reabrir para redimensionar (un poco ineficiente pero seguro)
            try:
                return ctk.CTkImage(Image.open(os.path.join(self.path_assets, "logo.png")), size=size)
            except: return None
        return None

    # --- PANTALLA 1: PERFILES (NETFLIX STYLE) ---
    def mostrar_seleccion_perfil(self, lista_usuarios):
        for w in self.winfo_children(): w.destroy()
        self.configure(fg_color=config.COLOR_FONDO_APP)

        ctk.CTkLabel(self, text="¿Quién está imprimiendo hoy?", font=config.FONT_TITULO, text_color=config.COLOR_TEXTO_BLANCO).pack(pady=(60, 40))

        frame_perfiles = ctk.CTkFrame(self, fg_color="transparent")
        frame_perfiles.pack()

        for usuario in lista_usuarios:
            # usuario = (username, empresa, avatar_path)
            username = usuario[0]
            avatar_path = usuario[2] if len(usuario) > 2 else None
            
            card = ctk.CTkFrame(frame_perfiles, fg_color="transparent")
            card.pack(side="left", padx=25)

            # Cargar imagen específica (ajustada para rellenar el interior del recuadro 140x140 con border 2)
            img_user = self.obtener_avatar_usuario(avatar_path, size=(136, 136))

            # Marco cuadrado verde que no sobresalga (sin corner radius)
            avatar_frame = ctk.CTkFrame(card, fg_color=config.COLOR_TARJETA, width=140, height=140, corner_radius=0, border_width=2, border_color=config.COLOR_ACENTO)
            avatar_frame.pack_propagate(False)
            avatar_frame.pack()

            if img_user:
                lbl = ctk.CTkLabel(avatar_frame, text="", image=img_user)
                lbl.pack(expand=True)
                lbl.bind("<Button-1>", lambda e, u=username: self.mostrar_login_password(u))
            else:
                lbl = ctk.CTkLabel(avatar_frame, text="👤", font=("Arial", 36), text_color="gray")
                lbl.pack(expand=True)
                lbl.bind("<Button-1>", lambda e, u=username: self.mostrar_login_password(u))

            ctk.CTkLabel(card, text=username, font=config.FONT_SUBTITULO, text_color=config.COLOR_TEXTO_GRIS).pack(pady=15)

        ctk.CTkButton(self, text="+ Agregar Cuenta", fg_color="transparent", text_color="gray", 
                      font=config.FONT_TEXTO, hover_color="#222",
                      command=self.mostrar_login_clasico).pack(pady=80)

    # --- PANTALLA 2: PASSWORD ---
    def mostrar_login_password(self, prefill_user):
        for w in self.winfo_children(): w.destroy()
        card = ctk.CTkFrame(self, fg_color=config.COLOR_TARJETA, corner_radius=20, border_width=1, border_color="#333")
        card.place(relx=0.5, rely=0.5, anchor="center")

        # Buscar avatar de este usuario para mostrarlo arriba
        # (Hacemos una query rápida o pasamos el dato, query es más seguro aquí)
        conn = database.get_connection()
        c = conn.cursor()
        c.execute("SELECT avatar_path FROM usuarios WHERE username=?", (prefill_user,))
        res = c.fetchone()
        conn.close()
        path_actual = res[0] if res else None
        
        img = self.obtener_avatar_usuario(path_actual, size=(80, 80))
        # Marco cuadrado verde alrededor del avatar en pantalla de contraseña
        avatar_frame = ctk.CTkFrame(card, fg_color=config.COLOR_TARJETA, width=84, height=84, corner_radius=0, border_width=2, border_color=config.COLOR_ACENTO)
        avatar_frame.pack_propagate(False)
        avatar_frame.pack(pady=(20, 10))
        if img:
            lbl = ctk.CTkLabel(avatar_frame, text="", image=img)
            lbl.pack(expand=True)
        else:
            ctk.CTkLabel(avatar_frame, text="👤", font=("Arial", 30), text_color="gray").pack(expand=True)

        ctk.CTkLabel(card, text=f"Hola, {prefill_user}", font=config.FONT_SUBTITULO, text_color=config.COLOR_TEXTO_BLANCO).pack(pady=(0, 20), padx=60)
        
        self.entry_pass = ctk.CTkEntry(card, placeholder_text="Contraseña", show="*", width=260, height=45, fg_color=config.COLOR_FONDO_APP, border_color="#333", text_color=config.COLOR_TEXTO_BLANCO, font=config.FONT_TEXTO)
        self.entry_pass.pack(pady=10)
        self.entry_pass.focus()
        self.entry_pass.bind("<Return>", lambda event: self.evento_login_rapido(prefill_user))

        ctk.CTkButton(card, text="INGRESAR", width=260, height=45, fg_color=config.COLOR_ACENTO, hover_color=config.COLOR_ACENTO_HOVER, font=config.FONT_BOTON, command=lambda: self.evento_login_rapido(prefill_user)).pack(pady=20)
        ctk.CTkButton(card, text="← Cambiar usuario", fg_color="transparent", text_color="gray", hover_color="#222", font=config.FONT_SMALL, command=lambda: self.mostrar_seleccion_perfil(database.obtener_todos_usuarios())).pack(pady=(0,20))

    def evento_login_rapido(self, user):
        pwd = self.entry_pass.get()
        res = database.login_usuario(user, pwd)
        if res:
            # res = (id, user, empresa, avatar)
            self.usuario_id = res[0]
            self.usuario_nombre = res[1]
            self.usuario_empresa = res[2]
            self.usuario_avatar_path = res[3] # Guardamos la ruta
            self.mostrar_menu_principal()
        else:
            messagebox.showerror("Error", "Contraseña incorrecta")

    # --- PANTALLA 3: REGISTRO (CON FOTO) ---
    def mostrar_login_clasico(self):
        for w in self.winfo_children(): w.destroy()
        self.configure(fg_color=config.COLOR_FONDO_APP)
        self.ruta_avatar_temporal = None # Reset

        card = ctk.CTkFrame(self, fg_color=config.COLOR_TARJETA, corner_radius=20)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card, text="NUEVA CUENTA", font=config.FONT_TITULO, text_color=config.COLOR_TEXTO_BLANCO).pack(pady=(25, 15), padx=60)
        
        # Botón Circular para Subir Foto
        self.btn_foto = ctk.CTkButton(card, text="📷 Subir Logo", width=120, height=120, corner_radius=60, 
                                      fg_color="#333", hover_color="#444", border_width=2, border_color=config.COLOR_ACENTO,
                                      command=self.seleccionar_avatar)
        self.btn_foto.pack(pady=10)
        self.lbl_foto_status = ctk.CTkLabel(card, text="", font=config.FONT_SMALL, text_color="gray")
        self.lbl_foto_status.pack()

        self.entry_reg_user = ctk.CTkEntry(card, placeholder_text="Usuario", width=280, height=40, fg_color=config.COLOR_FONDO_APP, text_color=config.COLOR_TEXTO_BLANCO, font=config.FONT_TEXTO)
        self.entry_reg_user.pack(pady=5)
        self.entry_reg_empresa = ctk.CTkEntry(card, placeholder_text="Nombre del Taller", width=280, height=40, fg_color=config.COLOR_FONDO_APP, text_color=config.COLOR_TEXTO_BLANCO, font=config.FONT_TEXTO)
        self.entry_reg_empresa.pack(pady=5)
        self.entry_reg_pass = ctk.CTkEntry(card, placeholder_text="Contraseña", show="*", width=280, height=40, fg_color=config.COLOR_FONDO_APP, text_color=config.COLOR_TEXTO_BLANCO, font=config.FONT_TEXTO)
        self.entry_reg_pass.pack(pady=5)

        ctk.CTkButton(card, text="CREAR CUENTA", width=280, height=45, fg_color=config.COLOR_ACENTO, font=config.FONT_BOTON, command=self.evento_registro).pack(pady=20)
        
        if database.obtener_todos_usuarios():
             ctk.CTkButton(card, text="Cancelar", fg_color="transparent", text_color="gray", hover_color="#222", font=config.FONT_SMALL, command=lambda: self.mostrar_seleccion_perfil(database.obtener_todos_usuarios())).pack(pady=10)

    def seleccionar_avatar(self):
        filename = filedialog.askopenfilename(title="Seleccionar Avatar", filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")])
        if filename:
            self.ruta_avatar_temporal = filename
            self.btn_foto.configure(text="✅ Foto Lista", fg_color=config.COLOR_ACENTO)
            self.lbl_foto_status.configure(text=os.path.basename(filename))

    def evento_registro(self):
        u, p, e = self.entry_reg_user.get(), self.entry_reg_pass.get(), self.entry_reg_empresa.get()
        if not u or not p:
            messagebox.showwarning("Error", "Faltan datos")
            return 
        
        # Procesar Imagen
        path_final = None
        if self.ruta_avatar_temporal:
            try:
                # Copiar la imagen a la carpeta assets/avatars con el nombre del usuario
                ext = os.path.splitext(self.ruta_avatar_temporal)[1] # .jpg, .png
                nombre_archivo = f"avatar_{u}{ext}"
                destino = os.path.join(self.path_avatars, nombre_archivo)
                shutil.copy(self.ruta_avatar_temporal, destino)
                path_final = destino
            except Exception as err:
                print(f"Error copiando imagen: {err}")

        if database.registrar_usuario(u, p, e, path_final):
            self.mostrar_seleccion_perfil(database.obtener_todos_usuarios())
        else: 
            messagebox.showerror("Error", "El usuario ya existe")

    def cambiar_avatar_usuario(self):
        """Permite al usuario cambiar el avatar desde el sidebar."""
        if not self.usuario_id:
            messagebox.showwarning("Atención", "No hay usuario logueado")
            return
        filename = filedialog.askopenfilename(title="Seleccionar Avatar", filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")])
        if not filename: return

        try:
            ext = os.path.splitext(filename)[1]
            nombre_archivo = f"avatar_user_{self.usuario_id}{ext}"
            destino = os.path.join(self.path_avatars, nombre_archivo)
            shutil.copy(filename, destino)
            # Actualizar en la DB
            try:
                database.actualizar_avatar_usuario(self.usuario_id, destino)
            except:
                pass
            # Actualizar en memoria y re-renderizar sidebar
            self.usuario_avatar_path = destino
            self.mostrar_menu_principal(navigate=False)
            messagebox.showinfo("Avatar", "Avatar actualizado correctamente.")
        except Exception as e:
            print(f"Error cambiando avatar: {e}")
            messagebox.showerror("Error", "No se pudo actualizar la imagen")

    # --- MENÚ LATERAL ---
    def mostrar_menu_principal(self, navigate=True):
        vista_actual_class = VistaInicio
        if not navigate and self.vista_actual: vista_actual_class = self.vista_actual.__class__

        for widget in self.winfo_children(): widget.destroy()
        
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=config.COLOR_MENU_LATERAL)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # 1. PERFIL (CON FOTO PERSONALIZADA)
        profile_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        profile_box.pack(fill="x", padx=20, pady=(30, 10))

        # Cargar avatar actual (tamaño reducido para sidebar)
        img = self.obtener_avatar_usuario(self.usuario_avatar_path, size=(56, 56))

        # Marco verde alrededor de la foto: recuadro sin esquinas redondeadas
        avatar_frame = ctk.CTkFrame(profile_box, fg_color="transparent", width=60, height=60, corner_radius=0, border_width=2, border_color=config.COLOR_ACENTO)
        avatar_frame.pack_propagate(False)
        avatar_frame.pack(side="left", padx=(0, 12), pady=(4, 0))

        # Usar etiqueta clicable (sin efecto hover grande) para evitar sobresalto visual
        if img:
            avatar_label = ctk.CTkLabel(avatar_frame, text="", image=img)
            avatar_label.pack(expand=True)
            avatar_label.bind("<Button-1>", lambda e: self.cambiar_avatar_usuario())
        else:
            avatar_label = ctk.CTkLabel(avatar_frame, text="👤", font=("Arial", 22), text_color="gray")
            avatar_label.pack(expand=True)
            avatar_label.bind("<Button-1>", lambda e: self.cambiar_avatar_usuario())

        # Información a la derecha del avatar: mantener same-gap y alineación superior
        info_box = ctk.CTkFrame(profile_box, fg_color="transparent")
        info_box.pack(side="left", fill="x", pady=(4, 0))

        # Nombre de usuario y botón cerrar sesión alineados (mismo espacio respecto a la foto)
        ctk.CTkLabel(info_box, text=self.usuario_nombre, font=config.FONT_BOTON, text_color=config.COLOR_TEXTO_BLANCO, anchor="w").pack(fill="x")
        ctk.CTkButton(info_box, text="Cerrar Sesión", height=18, width=0,
                      fg_color="transparent", text_color=config.COLOR_ROJO, hover_color="#333",
                      font=config.FONT_SMALL, anchor="w",
                      command=self.salir).pack(fill="x", pady=(2, 0))

        # 2. TALLER
        taller_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        taller_box.pack(fill="x", padx=20, pady=(6, 10))
        # Mostrar nombre del taller centrado, en verde y más grande
        nombre_taller = (self.usuario_empresa or "Mi Taller").upper()
        ctk.CTkLabel(taller_box, text=nombre_taller, font=("Segoe UI", 12, "bold"), text_color=config.COLOR_ACENTO, anchor="center").pack(fill="x")
        ctk.CTkFrame(self.sidebar, height=1, fg_color=config.COLOR_SEPARADOR).pack(fill="x", padx=20, pady=5)

        # 3. MENU
        self.menu_scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.menu_scroll.pack(fill="both", expand=True)

        self.crear_titulo("INICIO")
        self.crear_boton("Dashboard", self.icon_home, self.ir_a_inicio)
        self.crear_titulo("PRODUCCIÓN")
        self.crear_boton("Nueva Impresión", self.icon_add, self.ir_a_nueva_impresion, destacado=True)
        self.crear_boton("Planificador", None, self.ir_a_planificador)
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

        self.main_area = ctk.CTkFrame(self, fg_color=config.COLOR_FONDO_APP)
        self.main_area.pack(side="right", fill="both", expand=True, padx=30, pady=30)
        
        if navigate:
            self.ir_a_inicio()
            # Proteger la apertura del anuncio en caso de error en la vista
            try:
                self.after(1000, lambda: VentanaAnuncio(self))
            except Exception as e:
                print(f"Error mostrando anuncio: {e}")
        else:
            if vista_actual_class == VistaInicio:
                self.cambiar_vista(vista_actual_class, callback_nueva_impresion=self.ir_a_nueva_impresion)
            else:
                self.cambiar_vista(vista_actual_class)

    # --- HELPERS ---
    def crear_titulo(self, txt):
        ctk.CTkLabel(self.menu_scroll, text=txt, font=config.FONT_BOTON, text_color=config.COLOR_TEXTO_GRIS, anchor="w").pack(fill="x", padx=25, pady=(15,5))

    def crear_boton(self, txt, icon, cmd, destacado=False):
        fg = "transparent"
        if destacado: fg = config.COLOR_ACENTO
        col_txt = "white" if destacado else config.COLOR_TEXTO_BLANCO
        ctk.CTkButton(self.menu_scroll, text=f"  {txt}", image=icon, compound="left", anchor="w", fg_color=fg, hover_color=config.COLOR_HOVER_BTN, text_color=col_txt, font=config.FONT_BOTON, height=38, command=cmd).pack(fill="x", padx=15, pady=2)

    def crear_switch(self, txt, var, cmd):
        frame = ctk.CTkFrame(self.menu_scroll, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=2)
        ctk.CTkSwitch(frame, text=txt, variable=var, command=cmd, text_color=config.COLOR_TEXTO_BLANCO, progress_color=config.COLOR_ACENTO, font=config.FONT_SMALL).pack(anchor="w")

    # --- EVENTOS ---
    def toggle_tema(self):
        if self.var_modo_claro.get(): ctk.set_appearance_mode("Light")
        else: ctk.set_appearance_mode("Dark")
        self.mostrar_menu_principal(navigate=False)

    def toggle_guia(self): config.MODO_PRINCIPIANTE = self.var_modo_guia.get()
    
    def salir(self):
        self.usuario_id = None
        self.usuario_avatar_path = None
        self.mostrar_seleccion_perfil(database.obtener_todos_usuarios())
    
    def destroy(self):
        try: plt.close('all')
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
        if self.vista_actual:
            try: self.vista_actual.destroy()
            except: pass
        try:
            self.vista_actual = clase_vista(self.main_area, user_id=self.usuario_id, **kwargs)
            self.vista_actual.pack(fill="both", expand=True)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            print(f"Error cargando vista {clase_vista}: {e}\n{tb}")
            # Mostrar placeholder para evitar pantalla negra
            for w in self.main_area.winfo_children():
                try: w.destroy()
                except: pass
            err_frame = ctk.CTkFrame(self.main_area, fg_color=config.COLOR_TARJETA, corner_radius=15, border_width=2, border_color=config.COLOR_ACENTO)
            err_frame.pack(fill="both", expand=True, padx=20, pady=20)
            ctk.CTkLabel(err_frame, text="Error al cargar la vista", font=config.FONT_SUBTITULO, text_color="white").pack(pady=20)
            ctk.CTkLabel(err_frame, text=tb, font=config.FONT_TEXTO, text_color="gray", wraplength=600).pack(pady=10)

if __name__ == "__main__":
    app = App()
    app.mainloop()