import customtkinter as ctk
import sys
import os
import config
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.interpolate import make_interp_spline
import webbrowser
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database

class VistaInicio(ctk.CTkFrame):
    def __init__(self, master, user_id, callback_nueva_impresion, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=config.COLOR_FONDO_APP)
        self.user_id = user_id
        self.callback_nueva_impresion = callback_nueva_impresion # Callback para navegar
        self.loop_id = None

        # Layout Principal
        self.grid_columnconfigure(0, weight=7)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=6)
        self.grid_rowconfigure(1, weight=4)

        # ============================================================
        # 1. GRÁFICO (Arriba Izquierda)
        # ============================================================
        self.frame_graph = ctk.CTkFrame(self, fg_color=config.COLOR_TARJETA, corner_radius=15, 
                                        border_width=2, border_color=config.COLOR_ACENTO)
        self.frame_graph.grid(row=0, column=0, padx=(0, 10), pady=(0, 10), sticky="nsew")
        
        h_graph = ctk.CTkFrame(self.frame_graph, fg_color="transparent")
        h_graph.pack(fill="x", padx=20, pady=(15, 5))
        
        # AQUI ESTÁ EL CAMBIO: Usamos config.FONT_SUBTITULO en vez de ("Arial", 20)
        ctk.CTkLabel(h_graph, text="Balance Financiero (7 Días)", 
                     font=config.FONT_SUBTITULO, text_color=config.COLOR_TEXTO_BLANCO).pack(side="left")
        
        self.plot_container = ctk.CTkFrame(self.frame_graph, fg_color="transparent")
        self.plot_container.pack(fill="both", expand=True, padx=10, pady=10)
        self.inicializar_grafico()

        # ============================================================
        # 2. CARRUSEL (Arriba Derecha)
        # ============================================================
        self.frame_carousel = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_carousel.grid(row=0, column=1, padx=(10, 0), pady=(0, 10), sticky="nsew")
        
        self.btn_anuncio = ctk.CTkButton(self.frame_carousel, text="", 
                                         fg_color=config.COLOR_ACENTO, corner_radius=15, 
                                         cursor="hand2", border_width=2, border_color=config.COLOR_ACENTO, 
                                         command=self.click_anuncio)
        self.btn_anuncio.pack(fill="both", expand=True)
        
        # CAMBIO: Fuente dinámica para el texto del anuncio
        self.lbl_anuncio_text = ctk.CTkLabel(self.frame_carousel, text="", 
                                             font=config.FONT_TITULO, text_color="white", 
                                             bg_color=config.COLOR_ACENTO, cursor="hand2")
        self.lbl_anuncio_text.place(relx=0.5, rely=0.5, anchor="center")
        self.lbl_anuncio_text.bind("<Button-1>", lambda e: self.click_anuncio())
        
        self.idx_anuncio = 0
        ruta_assets = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "anuncios")
        
        self.anuncios = [
            # Pon el nombre exacto de tus archivos aquí
            {"img": os.path.join(ruta_assets, "anuncio1.png"), "url": "https://mercadolibre.com.ar"},
            {"img": os.path.join(ruta_assets, "anuncio2.png"), "url": "https://google.com"},
            {"img": os.path.join(ruta_assets, "anuncio3.png"), "url": "https://youtube.com"}
        ]
        self.animar_carrusel()

        # ============================================================
        # 3. LISTA (Abajo Izquierda)
        # ============================================================
        self.frame_lista = ctk.CTkFrame(self, fg_color=config.COLOR_TARJETA, corner_radius=15, 
                                        border_width=2, border_color=config.COLOR_ACENTO)
        self.frame_lista.grid(row=1, column=0, padx=(0, 10), pady=(10, 0), sticky="nsew")

        h_lista = ctk.CTkFrame(self.frame_lista, fg_color="transparent")
        h_lista.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(h_lista, text="Próximas Entregas", 
                     font=config.FONT_SUBTITULO, text_color=config.COLOR_TEXTO_BLANCO).pack(side="left")
        
        ctk.CTkButton(h_lista, text="Ver Agenda ➔", width=100, height=25, 
                      fg_color=config.COLOR_TEXTO_BLANCO, text_color=config.COLOR_FONDO_APP, 
                      hover_color="gray", font=config.FONT_SMALL, 
                      command=lambda: master.master.ir_a_agenda()).pack(side="right")

        self.scroll_lista = ctk.CTkScrollableFrame(self.frame_lista, fg_color="transparent")
        self.scroll_lista.pack(fill="both", expand=True, padx=10, pady=5)
        self.cargar_lista_entregas()

        # ============================================================
        # 4. KPI (Abajo Derecha)
        # ============================================================
        self.frame_kpi = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_kpi.grid(row=1, column=1, padx=(10, 0), pady=(10, 0), sticky="nsew")
        self.frame_kpi.grid_columnconfigure(0, weight=1); self.frame_kpi.grid_columnconfigure(1, weight=1)
        self.frame_kpi.grid_rowconfigure(0, weight=1); self.frame_kpi.grid_rowconfigure(1, weight=1)

        ingresos = database.calcular_ingresos_total(self.user_id)
        costos = database.calcular_gasto_total(self.user_id)
        
        self.crear_kpi(0, 0, "Ganancia", f"${(ingresos-costos):,.0f}", config.COLOR_ACENTO, "💰")
        self.crear_kpi(0, 1, "Costos", f"${costos:,.0f}", config.COLOR_ROJO, "📉")
        self.crear_kpi(1, 0, "Pendientes", str(database.contar_proyectos_agenda(self.user_id)), "#3498db", "⏳")
        self.crear_kpi(1, 1, "Realizados", str(database.contar_trabajos(self.user_id)), "#95a5a6", "✅")

    # --- MÉTODOS ---
    def obtener_color_hex(self, color_var):
        modo = ctk.get_appearance_mode()
        if isinstance(color_var, tuple): return color_var[0] if modo == "Light" else color_var[1]
        return color_var

    def inicializar_grafico(self):
        raw_data = database.obtener_balance_ultimos_dias(self.user_id)
        if not raw_data or len(raw_data) < 2: 
            ctk.CTkLabel(self.plot_container, text="Faltan datos", font=config.FONT_TEXTO, text_color="gray").pack(expand=True)
            return

        fechas = [d[0][5:] for d in raw_data]; costos = [d[1] for d in raw_data]; ingresos = [d[2] for d in raw_data]
        bg = self.obtener_color_hex(config.COLOR_TARJETA)
        text = "black" if ctk.get_appearance_mode() == "Light" else "white"
        grid = "#cccccc" if ctk.get_appearance_mode() == "Light" else "#444444"
        acento = self.obtener_color_hex(config.COLOR_ACENTO)
        rojo = self.obtener_color_hex(config.COLOR_ROJO)

        x = np.arange(len(fechas))
        x_smooth = np.linspace(x.min(), x.max(), 300)
        try:
            y_costos = [max(0,v) for v in make_interp_spline(x, costos, k=3)(x_smooth)]
            y_ing = [max(0,v) for v in make_interp_spline(x, ingresos, k=3)(x_smooth)]
        except: x_smooth, y_costos, y_ing = x, costos, ingresos

        if ctk.get_appearance_mode() == "Light": plt.style.use('default')
        else: plt.style.use('dark_background')

        fig, ax = plt.subplots(figsize=(6, 3), dpi=100)
        fig.patch.set_facecolor(bg); ax.set_facecolor(bg)
        for spine in ax.spines.values(): spine.set_visible(False)
        ax.tick_params(left=False, bottom=False, labelcolor=text, labelsize=8)
        ax.grid(axis='y', color=grid, linestyle='--', linewidth=0.5, alpha=0.5)
        
        ax.plot(x_smooth, y_costos, color=rojo, linestyle='--', alpha=0.8)
        ax.fill_between(x_smooth, y_costos, color=rojo, alpha=0.1)
        ax.plot(x_smooth, y_ing, color=acento, linewidth=2.5)
        ax.fill_between(x_smooth, y_ing, color=acento, alpha=0.2)
        if len(fechas) > 0:
            ax.set_xticks(x); ax.set_xticklabels(fechas, color=text)

        canvas = FigureCanvasTkAgg(fig, master=self.plot_container)
        canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True)

    def animar_carrusel(self):
        if not self.winfo_exists(): return
        
        # Obtener datos del anuncio actual
        dato = self.anuncios[self.idx_anuncio]
        
        try:
            # 1. Cargar la imagen
            # Size=(500, 600) fuerza a que se vea bien en ese cuadro
            imagen_ctk = ctk.CTkImage(Image.open(dato["img"]), size=(300, 380))
            
            # 2. Ponerla en el botón
            self.btn_anuncio.configure(image=imagen_ctk, fg_color="transparent")
            
            # 3. Borrar el texto superpuesto (porque la imagen ya debería tener el texto publicitario)
            self.lbl_anuncio_text.configure(text="") 
            
        except Exception as e:
            print(f"Error cargando imagen: {e}")
            # Si falla, poner un color de respaldo
            self.btn_anuncio.configure(image=None, fg_color=config.COLOR_ACENTO)

        # Avanzar al siguiente
        self.idx_anuncio = (self.idx_anuncio + 1) % len(self.anuncios)
        self.loop_id = self.after(4000, self.animar_carrusel)

    def click_anuncio(self):
        idx = (self.idx_anuncio - 1) % len(self.anuncios)
        webbrowser.open(self.anuncios[idx]["url"])

    def crear_kpi(self, r, c, t, v, col, icon):
        # KPI con borde verde
        card = ctk.CTkFrame(self.frame_kpi, fg_color=config.COLOR_TARJETA, corner_radius=15, 
                            border_width=2, border_color=config.COLOR_ACENTO)
        card.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(card, text=icon, font=("Segoe UI", 16)).pack(anchor="w", padx=15, pady=(10,0))
        
        # CAMBIO: Usamos FONT_TITULO y FONT_SMALL
        ctk.CTkLabel(card, text=v, font=config.FONT_TITULO, text_color=config.COLOR_TEXTO_BLANCO).pack(anchor="w", padx=15)
        ctk.CTkLabel(card, text=t, font=config.FONT_SMALL, text_color=config.COLOR_TEXTO_GRIS).pack(anchor="w", padx=15, pady=(0,10))

    def cargar_lista_entregas(self):
        agendas = database.obtener_ultimas_agendas(self.user_id, limit=5)
        if not agendas: return
        for ped in agendas:
            bg_row = ("#e1e5ea", "#252a36") 
            row = ctk.CTkFrame(self.scroll_lista, fg_color=bg_row, corner_radius=8)
            row.pack(fill="x", pady=4)
            fecha = ped[8] if ped[8] else "S/F"
            # CAMBIO: Fuentes dinámicas en la lista también
            ctk.CTkLabel(row, text=fecha[:5], font=config.FONT_SMALL, width=45, text_color="gray").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=ped[1], font=config.FONT_BOTON, text_color=config.COLOR_TEXTO_BLANCO).pack(side="left")
            ctk.CTkLabel(row, text="Pendiente", font=config.FONT_SMALL, text_color="#e67e22").pack(side="right", padx=10)

    def destroy(self):
        if self.loop_id: 
            try: self.after_cancel(self.loop_id)
            except: pass
        try: plt.close('all')
        except: pass
        super().destroy()