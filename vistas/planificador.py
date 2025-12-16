import customtkinter as ctk
from tkinter import messagebox
import sys
import os
import config
import json
from datetime import datetime, timedelta

# Intentar importar calendario
try:
    from tkcalendar import DateEntry
    CALENDARIO_DISPONIBLE = True
except ImportError:
    CALENDARIO_DISPONIBLE = False

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database

# --- VENTANA POPUP 1: RESULTADO ---
class VentanaResultado(ctk.CTkToplevel):
    def __init__(self, parent, datos, on_yes):
        super().__init__(parent)
        self.on_yes = on_yes
        
        self.overrideredirect(True) 
        self.attributes('-topmost', True)
        
        bg_color = config.COLOR_FONDO_APP
        if isinstance(bg_color, tuple): bg_color = bg_color[1]
        self.configure(fg_color=bg_color) 

        w, h = 500, 480
        x = (self.winfo_screenwidth()/2) - (w/2)
        y = (self.winfo_screenheight()/2) - (h/2)
        self.geometry(f"{w}x{h}+{int(x)}+{int(y)}")

        self.frame = ctk.CTkFrame(self, fg_color=bg_color, 
                                  border_width=2, border_color=config.COLOR_ACENTO, corner_radius=0)
        self.frame.pack(fill="both", expand=True)

        header = ctk.CTkFrame(self.frame, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 5))
        ctk.CTkLabel(header, text="Resultado", font=("Segoe UI", 22, "bold"), text_color=config.COLOR_TEXTO_BLANCO).pack(side="left")
        ctk.CTkButton(header, text="✕", width=40, height=40, fg_color="transparent", hover_color="#333", text_color="gray", font=("Arial", 18), command=self.destroy).pack(side="right")

        ctk.CTkLabel(self.frame, text="✓", font=("Arial", 65, "bold"), text_color=config.COLOR_ACENTO).pack(pady=(0, 5))
        ctk.CTkLabel(self.frame, text="ESTRATEGIA CALCULADA", font=("Segoe UI", 16, "bold"), text_color=config.COLOR_TEXTO_BLANCO).pack(pady=(0, 15))

        content_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=50)
        for linea in datos:
            color_texto = config.COLOR_TEXTO_GRIS
            if "⚠️" in linea: color_texto = "#e74c3c"
            elif "$" in linea: color_texto = "#f1c40f"
            ctk.CTkLabel(content_frame, text=f"• {linea}", font=("Segoe UI", 14), text_color=color_texto, anchor="w", justify="left").pack(fill="x", pady=2)

        ctk.CTkLabel(self.frame, text="¿Deseas guardar esto en la Agenda?", font=("Segoe UI", 14), text_color="gray").pack(pady=(25, 15))

        btn_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=40, pady=10)
        ctk.CTkButton(btn_frame, text="Sí", height=45, fg_color=config.COLOR_ACENTO, hover_color=config.COLOR_ACENTO_HOVER, font=("Segoe UI", 14, "bold"), text_color="white", command=self.confirmar).pack(side="left", expand=True, fill="x", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="No", height=45, fg_color="transparent", border_width=2, border_color="#444", text_color="gray", hover_color="#333", font=("Segoe UI", 14, "bold"), command=self.destroy).pack(side="right", expand=True, fill="x", padx=(10, 0))

    def confirmar(self):
        self.destroy()
        self.on_yes()

# --- VENTANA POPUP 2: CALENDARIO ---
class VentanaFecha(ctk.CTkToplevel):
    def __init__(self, parent, on_confirm_date):
        super().__init__(parent)
        self.on_confirm_date = on_confirm_date
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        bg_color = config.COLOR_FONDO_APP
        if isinstance(bg_color, tuple): bg_color = bg_color[1]
        self.configure(fg_color=bg_color)
        w, h = 400, 320
        x = (self.winfo_screenwidth()/2) - (w/2)
        y = (self.winfo_screenheight()/2) - (h/2)
        self.geometry(f"{w}x{h}+{int(x)}+{int(y)}")
        self.frame = ctk.CTkFrame(self, fg_color=bg_color, border_width=2, border_color=config.COLOR_ACENTO, corner_radius=0)
        self.frame.pack(fill="both", expand=True)
        ctk.CTkLabel(self.frame, text="Agendar Entrega", font=("Segoe UI", 20, "bold"), text_color=config.COLOR_TEXTO_BLANCO).pack(pady=(20, 5))
        ctk.CTkLabel(self.frame, text="Selecciona la fecha límite:", font=("Segoe UI", 14), text_color="gray").pack(pady=(0, 10))
        self.cal_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.cal_frame.pack(pady=10)
        if CALENDARIO_DISPONIBLE:
            self.cal = DateEntry(self.cal_frame, width=16, background='#00965e', foreground='white', borderwidth=2, font=("Arial", 12))
            self.cal.pack(padx=10, pady=10)
        else:
            ctk.CTkLabel(self.cal_frame, text="Formato: AAAA-MM-DD", text_color="gray").pack()
            self.entry_date = ctk.CTkEntry(self.cal_frame, placeholder_text="2025-12-31")
            self.entry_date.pack(pady=5)
        btn_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=40, pady=20)
        ctk.CTkButton(btn_frame, text="Guardar", height=40, fg_color=config.COLOR_ACENTO, hover_color=config.COLOR_ACENTO_HOVER, text_color="white", font=("Segoe UI", 12, "bold"), command=self.guardar).pack(side="left", expand=True, fill="x", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Cancelar", height=40, fg_color="transparent", border_width=2, border_color="#444", text_color="gray", hover_color="#333", font=("Segoe UI", 12, "bold"), command=self.destroy).pack(side="right", expand=True, fill="x", padx=(10, 0))

    def guardar(self):
        if CALENDARIO_DISPONIBLE:
            fecha_str = self.cal.get_date().strftime("%Y-%m-%d")
        else:
            fecha_str = self.entry_date.get()
            if not fecha_str: fecha_str = datetime.now().strftime("%Y-%m-%d")
        self.destroy()
        self.on_confirm_date(fecha_str)

# --- VENTANA EXITO ---
class VentanaExito(ctk.CTkToplevel):
    def __init__(self, parent, mensaje):
        super().__init__(parent)
        self.overrideredirect(True) 
        self.attributes('-topmost', True)
        bg_color = config.COLOR_FONDO_APP
        if isinstance(bg_color, tuple): bg_color = bg_color[1]
        self.configure(fg_color=bg_color) 
        w, h = 400, 250
        x = (self.winfo_screenwidth()/2) - (w/2)
        y = (self.winfo_screenheight()/2) - (h/2)
        self.geometry(f"{w}x{h}+{int(x)}+{int(y)}")
        self.frame = ctk.CTkFrame(self, fg_color=bg_color, border_width=2, border_color=config.COLOR_ACENTO, corner_radius=0)
        self.frame.pack(fill="both", expand=True)
        ctk.CTkLabel(self.frame, text="✓", font=("Arial", 60, "bold"), text_color=config.COLOR_ACENTO).pack(pady=(30, 10))
        ctk.CTkLabel(self.frame, text="¡OPERACIÓN EXITOSA!", font=("Segoe UI", 16, "bold"), text_color="white").pack()
        ctk.CTkLabel(self.frame, text=mensaje, font=("Segoe UI", 13), text_color="gray", wraplength=350).pack(pady=(5, 20))
        ctk.CTkButton(self.frame, text="Aceptar", height=40, width=150, fg_color=config.COLOR_ACENTO, hover_color=config.COLOR_ACENTO_HOVER, font=("Segoe UI", 13, "bold"), text_color="white", command=self.destroy).pack(pady=10)


# --- VISTA PLANIFICADOR ---
class VistaPlanificador(ctk.CTkFrame):
    def __init__(self, master, user_id, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=config.COLOR_FONDO_APP)
        self.user_id = user_id
        
        self.filas_materiales = [] 
        self.flota_seleccionada = [] 
        self.ultima_estrategia = None
        self.stock_agrupado = {}

        # Fuentes
        FONT_TITULO = getattr(config, 'FONT_TITULO', ("Segoe UI", 24, "bold"))
        FONT_SUBTITULO = getattr(config, 'FONT_SUBTITULO', ("Segoe UI", 18, "bold"))
        FONT_TEXTO = getattr(config, 'FONT_TEXTO', ("Segoe UI", 13, "normal"))
        FONT_BOTON = getattr(config, 'FONT_BOTON', ("Segoe UI", 12, "bold"))
        BORDER_COLOR = getattr(config, 'COLOR_ACENTO', "#00965e")
        if isinstance(BORDER_COLOR, tuple): BORDER_COLOR = BORDER_COLOR[1]

        # Título
        ctk.CTkLabel(self, text="Planificador Masivo", font=FONT_TITULO, text_color=config.COLOR_TEXTO_BLANCO).pack(pady=(10, 5))

        # Grid
        self.main_grid = ctk.CTkFrame(self, fg_color="transparent")
        self.main_grid.pack(fill="both", expand=True, padx=20, pady=5)
        self.main_grid.grid_columnconfigure(0, weight=1); self.main_grid.grid_columnconfigure(1, weight=1)
        self.main_grid.grid_rowconfigure(0, weight=3); self.main_grid.grid_rowconfigure(1, weight=1)

        # --- 1) PANEL IZQUIERDO ---
        self.panel_obj = ctk.CTkFrame(self.main_grid, fg_color=config.COLOR_TARJETA, corner_radius=15, border_width=2, border_color=BORDER_COLOR)
        self.panel_obj.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)
        
        ctk.CTkLabel(self.panel_obj, text="1) Objetivo y Materiales", font=FONT_SUBTITULO, text_color="white").pack(anchor="w", padx=20, pady=(15, 10))
        
        # Inputs Nombre y Meta
        ctk.CTkLabel(self.panel_obj, text="Nombre del Proyecto:", font=FONT_BOTON, text_color=config.COLOR_TEXTO_GRIS).pack(anchor="w", padx=20)
        self.entry_nombre = ctk.CTkEntry(self.panel_obj, placeholder_text="Ej: Jarra", height=35, font=FONT_TEXTO, border_color=BORDER_COLOR, text_color=config.COLOR_TEXTO_BLANCO)
        self.entry_nombre.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(self.panel_obj, text="Meta total (unidades):", font=FONT_BOTON, text_color=config.COLOR_TEXTO_GRIS).pack(anchor="w", padx=20)
        self.entry_meta = ctk.CTkEntry(self.panel_obj, placeholder_text="100", width=120, height=35, font=FONT_TEXTO, border_color=BORDER_COLOR, text_color=config.COLOR_TEXTO_BLANCO)
        self.entry_meta.pack(anchor="w", padx=20, pady=(0, 10))

        # --- CAMBIO AQUI: CABECERA DE MATERIALES CON BOTÓN ---
        frame_header_mat = ctk.CTkFrame(self.panel_obj, fg_color="transparent")
        frame_header_mat.pack(fill="x", padx=20, pady=(5, 5))
        
        ctk.CTkLabel(frame_header_mat, text="Materiales por unidad:", font=FONT_BOTON, text_color=config.COLOR_TEXTO_GRIS).pack(side="left")
        
        # BOTÓN AÑADIR COLOR AHORA ESTÁ ARRIBA
        ctk.CTkButton(frame_header_mat, text="+ Añadir", width=80, height=25, fg_color="transparent", 
                      border_width=1, border_color=BORDER_COLOR, text_color=config.COLOR_TEXTO_BLANCO, 
                      font=("Segoe UI", 11, "bold"), command=self.agregar_fila_material).pack(side="right")

        # Scroll de materiales (Ahora abajo del botón, así no lo empuja)
        self.scroll_mat = ctk.CTkScrollableFrame(self.panel_obj, fg_color="transparent", height=150)
        self.scroll_mat.pack(fill="both", expand=True, padx=10, pady=5)


        # --- 2) PANEL DERECHO ---
        self.panel_flota = ctk.CTkFrame(self.main_grid, fg_color=config.COLOR_TARJETA, corner_radius=15, border_width=2, border_color=BORDER_COLOR)
        self.panel_flota.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)
        ctk.CTkLabel(self.panel_flota, text="2) Flota / Recursos", font=FONT_SUBTITULO, text_color="white").pack(anchor="w", padx=20, pady=(15, 10))

        ctk.CTkLabel(self.panel_flota, text="Impresora (seleccionar):", font=FONT_BOTON, text_color=config.COLOR_TEXTO_GRIS).pack(anchor="w", padx=20)
        self.combo_impresoras = ctk.CTkComboBox(self.panel_flota, values=["Cargando..."], height=35, font=FONT_TEXTO, border_color=BORDER_COLOR, button_color=BORDER_COLOR, text_color=config.COLOR_TEXTO_BLANCO)
        self.combo_impresoras.pack(fill="x", padx=20, pady=(0, 10))

        frame_time = ctk.CTkFrame(self.panel_flota, fg_color="transparent")
        frame_time.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(frame_time, text="Tiempo unidad:", font=FONT_BOTON, text_color=config.COLOR_TEXTO_GRIS).pack(side="left")
        self.entry_hs = ctk.CTkEntry(frame_time, placeholder_text="Hs", width=60, border_color=BORDER_COLOR, text_color=config.COLOR_TEXTO_BLANCO)
        self.entry_hs.pack(side="left", padx=5)
        ctk.CTkLabel(frame_time, text=":", text_color=config.COLOR_TEXTO_BLANCO).pack(side="left")
        self.entry_min = ctk.CTkEntry(frame_time, placeholder_text="Min", width=60, border_color=BORDER_COLOR, text_color=config.COLOR_TEXTO_BLANCO)
        self.entry_min.pack(side="left", padx=5)

        ctk.CTkButton(self.panel_flota, text="Agregar a Flota", width=150, fg_color="#3498db", hover_color="#2980b9", font=FONT_BOTON, text_color="white", command=self.agregar_a_flota).pack(pady=10)

        ctk.CTkLabel(self.panel_flota, text="Máquinas añadidas:", font=FONT_BOTON, text_color=config.COLOR_TEXTO_GRIS).pack(anchor="w", padx=20)
        self.scroll_flota = ctk.CTkScrollableFrame(self.panel_flota, fg_color="#1a1a1a", corner_radius=5)
        self.scroll_flota.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        # --- 3) PANEL RESULTADOS ---
        self.panel_res = ctk.CTkFrame(self.main_grid, fg_color=config.COLOR_TARJETA, corner_radius=15, border_width=2, border_color=BORDER_COLOR)
        self.panel_res.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(15, 0))
        ctk.CTkLabel(self.panel_res, text="3) Resultados y Estrategia", font=FONT_SUBTITULO, text_color="white").pack(anchor="w", padx=20, pady=(15, 5))

        frame_bottom = ctk.CTkFrame(self.panel_res, fg_color="transparent")
        frame_bottom.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(frame_bottom, text="Horas de trabajo por día:", font=config.FONT_BOTON, text_color=config.COLOR_TEXTO_GRIS).pack(side="left")
        self.entry_jor = ctk.CTkEntry(frame_bottom, placeholder_text="8", width=60, border_color=BORDER_COLOR, text_color=config.COLOR_TEXTO_BLANCO)
        self.entry_jor.pack(side="left", padx=10)
        self.entry_jor.insert(0, "8")

        ctk.CTkButton(self.panel_res, text="CALCULAR ESTRATEGIA", height=50, fg_color=config.COLOR_VERDE_BAMBU, hover_color=config.COLOR_VERDE_HOVER, font=("Segoe UI", 16, "bold"), text_color="white", command=self.calcular).pack(fill="x", padx=20, pady=20)

        self.cargar_datos()
        self.agregar_fila_material()

    # --- LÓGICA ---
    def cargar_datos(self):
        imps = database.obtener_impresoras(self.user_id)
        self.mapa_imp = {f"{i[1]} ({i[2]})": i[0] for i in imps}
        if self.mapa_imp:
            self.combo_impresoras.configure(values=list(self.mapa_imp.keys()))
            self.combo_impresoras.set(list(self.mapa_imp.keys())[0])
        else: self.combo_impresoras.configure(values=["Sin máquinas"])

        bobs = database.obtener_bobinas(self.user_id)
        # Agrupar stock por Material - Color
        self.stock_agrupado = {}
        for b in bobs:
            mat_col = f"{b[2]} - {b[3]}" # Material - Color
            self.stock_agrupado[mat_col] = self.stock_agrupado.get(mat_col, 0) + b[4]
        
        self.list_materiales_disponibles = sorted(list(self.stock_agrupado.keys()))

    def agregar_fila_material(self):
        row = ctk.CTkFrame(self.scroll_mat, fg_color="transparent")
        row.pack(fill="x", pady=2)
        
        vals = self.list_materiales_disponibles if self.list_materiales_disponibles else ["Sin Stock"]
        cb = ctk.CTkComboBox(row, values=vals, width=180, font=config.FONT_TEXTO)
        cb.pack(side="left", fill="x", expand=True)
        if vals: cb.set(vals[0])
        
        en = ctk.CTkEntry(row, placeholder_text="gr/u", width=60)
        en.pack(side="left", padx=5)
        
        btn = ctk.CTkButton(row, text="✕", width=30, fg_color=config.COLOR_ROJO, hover_color="#c0392b", command=lambda f=row: self.eliminar_fila(f))
        btn.pack(side="right")
        self.filas_materiales.append({"frame": row, "combo": cb, "entry": en})

    def eliminar_fila(self, frame):
        frame.destroy()
        self.filas_materiales = [f for f in self.filas_materiales if f["frame"] != frame]

    def agregar_a_flota(self):
        nombre = self.combo_impresoras.get()
        hs = self.entry_hs.get()
        mins = self.entry_min.get()
        try:
            h = float(hs) if hs else 0
            m = float(mins) if mins else 0
            total_h = h + (m/60)
            if total_h <= 0: return
            imp_id = self.mapa_imp.get(nombre)
            power = 0.3 
            self.flota_seleccionada.append({"nombre": nombre, "tiempo": total_h, "power": power, "id": imp_id})
            lbl = ctk.CTkLabel(self.scroll_flota, text=f"• {nombre} ({h:.0f}h {m:.0f}m)", anchor="w", text_color="white", font=config.FONT_SMALL)
            lbl.pack(fill="x", padx=5)
        except: pass

    def calcular(self):
        try:
            meta = int(self.entry_meta.get())
            jornada = float(self.entry_jor.get())
        except:
            messagebox.showerror("Error", "Meta y Jornada deben ser números")
            return
        if not self.flota_seleccionada:
            messagebox.showwarning("Error", "Agrega máquinas a la flota")
            return
        
        materiales_necesarios = {}
        alertas_stock = []
        
        for fila in self.filas_materiales:
            col_tipo = fila["combo"].get()
            try: g_u = float(fila["entry"].get())
            except: continue
            
            total_nec = g_u * meta
            materiales_necesarios[col_tipo] = materiales_necesarios.get(col_tipo, 0) + total_nec

        # Verificar stock
        for tipo, cantidad in materiales_necesarios.items():
            stock_real = self.stock_agrupado.get(tipo, 0)
            if stock_real < cantidad:
                faltante = cantidad - stock_real
                alertas_stock.append(f"⚠️ Falta {tipo}: {faltante:.0f}g")

        unidades_por_dia = 0
        for maq in self.flota_seleccionada:
            unidades_por_dia += jornada / maq["tiempo"]
        dias_totales = meta / unidades_por_dia if unidades_por_dia > 0 else 0
        horas_totales_reloj = dias_totales * jornada 
        
        costo_energia_total = 0
        costo_kw = getattr(config, 'COSTO_KW', 0.2)
        for maq in self.flota_seleccionada:
            costo_energia_total += (maq['power'] * horas_totales_reloj) * costo_kw
        
        self.ultima_estrategia = {
            'nombre': self.entry_nombre.get(),
            'meta': meta,
            'materiales': materiales_necesarios,
            'flota': self.flota_seleccionada,
            'tiempo_hs': horas_totales_reloj,
            'costo_energia': costo_energia_total
        }
        
        datos_mostrar = [
            f"Producción Diaria: {unidades_por_dia:.1f} unidades",
            f"Tiempo Total: {dias_totales:.1f} días laborales",
            f"Costo Energía Est.: ${costo_energia_total:.2f}"
        ]
        
        if alertas_stock:
            datos_mostrar.append("--- FALTANTES ---")
            datos_mostrar.extend(alertas_stock)
        else:
            datos_mostrar.append("✅ Stock suficiente.")

        VentanaResultado(self, datos_mostrar, self.abrir_selector_fecha)

    def abrir_selector_fecha(self):
        VentanaFecha(self, self.guardar_final_db)

    def guardar_final_db(self, fecha_entrega):
        if not self.ultima_estrategia: return
        import json
        mat_json = json.dumps(self.ultima_estrategia['materiales'])
        flota_simple = [{"id": m.get('id'), "nombre": m['nombre']} for m in self.ultima_estrategia['flota']]
        flota_json = json.dumps(flota_simple)
        ok = database.guardar_proyecto_agenda(
            self.user_id,
            self.ultima_estrategia['nombre'],
            self.ultima_estrategia['meta'],
            mat_json,
            flota_json,
            self.ultima_estrategia['tiempo_hs'],
            self.ultima_estrategia['costo_energia'],
            0, fecha_entrega, 0
        )
        if ok: 
            VentanaExito(self, "Proyecto guardado en la Agenda con éxito.")
        else: 
            messagebox.showerror("Error", "No se pudo guardar en la base de datos")