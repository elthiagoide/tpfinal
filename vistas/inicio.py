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
        # Contenedor del anuncio: usar mismo estilo que otras tarjetas para mantener consistencia
        self.frame_carousel = ctk.CTkFrame(self, fg_color=config.COLOR_TARJETA, corner_radius=15,
                           border_width=2, border_color=config.COLOR_ACENTO)
        self.frame_carousel.grid(row=0, column=1, padx=(10, 0), pady=(0, 10), sticky="nsew")

        # Contenedor interno para que el borde del frame externo quede visible
        # y para poder controlar el padding interno donde irá la imagen.
        self.inner_carousel = ctk.CTkFrame(self.frame_carousel, fg_color=config.COLOR_TARJETA, corner_radius=13)
        self.inner_carousel.pack(fill="both", expand=True, padx=8, pady=8)

        # Botón interior: transparente y sin borde, heredando esquinas redondeadas
        # La imagen se colocará aquí y ocupará todo el espacio disponible.
        self.btn_anuncio = ctk.CTkButton(self.inner_carousel, text="",
                 fg_color="transparent", corner_radius=13,
                 cursor="hand2", border_width=0,
                 command=self.click_anuncio)
        self.btn_anuncio.pack(fill="both", expand=True)
        
        # CAMBIO: Fuente dinámica para el texto del anuncio
        self.lbl_anuncio_text = ctk.CTkLabel(self.frame_carousel, text="", 
                                             font=config.FONT_TITULO, text_color="white", 
                                             bg_color=config.COLOR_ACENTO, cursor="hand2")
        self.lbl_anuncio_text.place(relx=0.5, rely=0.5, anchor="center")
        self.lbl_anuncio_text.bind("<Button-1>", lambda e: self.click_anuncio())
        
        self.idx_anuncio = 0
        # Bandera para fijar tamaño interno del carrusel en la primera medición
        self._carousel_fixed_size_set = False
        ruta_assets = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "anuncios")
        
        self.anuncios = [
            # Pon el nombre exacto de tus archivos aquí
            {"img": os.path.join(ruta_assets, "anuncio1.png"), "url": "https://mercadolibre.com.ar"},
            {"img": os.path.join(ruta_assets, "anuncio2.png"), "url": "https://google.com"},
            {"img": os.path.join(ruta_assets, "anuncio3.png"), "url": "https://youtube.com"}
        ]
        # Llamar a la animación con un pequeño delay para que la geometría se establezca
        self.after(150, self.animar_carrusel)

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
        try:
            raw_data = database.obtener_balance_ultimos_dias(self.user_id)
        except Exception as e:
            print(f"Error al obtener balance: {e}")
            raw_data = None

        # TRACE temporales para depuración
        try:
            print(f"TRACE VistaInicio.user_id={self.user_id} raw_data_len={len(raw_data) if raw_data is not None else 0}")
            if raw_data:
                for r in raw_data[:10]:
                    print("TRACE ROW:", r)
        except Exception:
            pass

        if not raw_data or len(raw_data) < 2:
            ctk.CTkLabel(self.plot_container, text="Faltan datos", font=config.FONT_TEXTO, text_color="gray").pack(expand=True)
            return

        # Coerción segura: algunos valores pueden venir como floats o None, protegemos los accesos
        fechas = []
        costos = []
        ingresos = []
        for d in raw_data:
            try:
                dia = d[0]
                if dia is None:
                    fechas.append("")
                else:
                    dia_str = str(dia)
                    fechas.append(dia_str[5:] if len(dia_str) >= 5 else dia_str)
            except Exception:
                fechas.append("")
            try:
                costos.append(float(d[1]) if d[1] is not None else 0.0)
            except Exception:
                costos.append(0.0)
            try:
                ingresos.append(float(d[2]) if d[2] is not None else 0.0)
            except Exception:
                ingresos.append(0.0)
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
            # Intentamos adaptar la imagen al tamaño actual del botón para que rellene el contenedor
            w = self.btn_anuncio.winfo_width()
            h = self.btn_anuncio.winfo_height()
            # Si la geometría aún no está lista, reintentar dentro de 100ms
            if w < 10 or h < 10:
                self.after(100, self.animar_carrusel)
                return

            # Fijar el tamaño interno la primera vez para evitar que la imagen
            # cambie la geometría del widget en cada ciclo (feedback loop)
            if not self._carousel_fixed_size_set:
                try:
                    self.inner_carousel.configure(width=w, height=h)
                    # Evitamos que el contenido cambie el tamaño del contenedor
                    self.inner_carousel.pack_propagate(False)
                except:
                    pass
                self._carousel_fixed_size_set = True

            target_size = (max(1, w), max(1, h))
            corner = min(15, int(min(target_size) * 0.08))
            imagen_ctk = self._crear_imagen_redondeada(dato["img"], target_size, corner)

            # Ponerla en el botón, asegurando que ocupe todo el espacio interior
            if imagen_ctk:
                self.btn_anuncio.configure(image=imagen_ctk, fg_color="transparent")
                self.lbl_anuncio_text.configure(text="")
            else:
                self.btn_anuncio.configure(image=None, fg_color=config.COLOR_ACENTO)

        except Exception as e:
            print(f"Error cargando imagen: {e}")
            self.btn_anuncio.configure(image=None, fg_color=config.COLOR_ACENTO)

        # Avanzar al siguiente
        self.idx_anuncio = (self.idx_anuncio + 1) % len(self.anuncios)
        self.loop_id = self.after(4000, self.animar_carrusel)

    def click_anuncio(self):
        idx = (self.idx_anuncio - 1) % len(self.anuncios)
        webbrowser.open(self.anuncios[idx]["url"])

    def _crear_imagen_redondeada(self, ruta, size, radius):
        """Carga la imagen `ruta`, la redimensiona a `size` y aplica máscara de esquinas redondeadas.
        Devuelve un `CTkImage` listo para usar."""
        try:
            img = Image.open(ruta).convert("RGBA")
            img = img.resize(size, Image.LANCZOS)

            # Crear máscara redondeada
            mask = Image.new('L', size, 0)
            from PIL import ImageDraw
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle([(0,0), (size[0], size[1])], radius=radius, fill=255)

            # Aplicar máscara
            img.putalpha(mask)

            return ctk.CTkImage(img, size=size)
        except Exception as e:
            print(f"Error creando imagen redondeada: {e}")
            # Fallback simple
            try:
                return ctk.CTkImage(Image.open(ruta), size=(300, 380))
            except:
                return None

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
            row.pack(fill="x", pady=6, padx=6)

            # Extraer campos guardando contra índices faltantes
            nombre = str(ped[2]) if len(ped) > 2 and ped[2] else "(Sin nombre)"
            delivery = str(ped[9]) if len(ped) > 9 and ped[9] else "S/F"
            gan = ped[10] if len(ped) > 10 and ped[10] is not None else 0.0
            # En algunas bases antiguas la columna 'estado' quedó desplazada al índice 12
            estado = str(ped[12]) if len(ped) > 12 and ped[12] else (str(ped[11]) if len(ped) > 11 and ped[11] else "Pendiente")

            # Mostrar todo en una sola línea: Nombre | Fecha | Ganancia | Estado
            # Nombre (izquierda, expandible)
            ctk.CTkLabel(row, text=nombre, font=config.FONT_BOTON, text_color=config.COLOR_TEXTO_BLANCO).pack(side="left", fill="x", expand=True, padx=8)
            # Fecha (pequeña)
            ctk.CTkLabel(row, text=delivery, font=config.FONT_SMALL, width=120, text_color="gray").pack(side="left", padx=8)
            # Ganancia
            ctk.CTkLabel(row, text=f"${gan:,.2f}", font=config.FONT_BOTON, text_color=config.COLOR_ACENTO).pack(side="left", padx=8)
            # Estado (verde si 'Realizado' o similar)
            color_estado = ("#27ae60" if estado.lower().startswith("r") else "#e67e22")
            ctk.CTkLabel(row, text=estado, font=config.FONT_SMALL, text_color=color_estado).pack(side="left", padx=8)

    def destroy(self):
        if self.loop_id: 
            try: self.after_cancel(self.loop_id)
            except: pass
        try: plt.close('all')
        except: pass
        super().destroy()