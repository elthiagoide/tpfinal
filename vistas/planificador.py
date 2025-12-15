import customtkinter as ctk
from tkinter import messagebox
import sys
import os
import webbrowser
import config
import json
from datetime import datetime, timedelta

# intentar importar DateEntry
try:
    from tkcalendar import DateEntry
    TKCAL_AVAILABLE = True
except Exception:
    TKCAL_AVAILABLE = False

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database


class VistaPlanificador(ctk.CTkFrame):
    """Planificador Masivo: simulador que NO escribe en la BD.
    Sigue la Lógica de Unidad Pura: usuario define 1 unidad, meta total,
    asigna máquinas con tiempo por unidad; el cálculo usa producción
    paralela (throughput sum of speeds).
    """
    def __init__(self, master, user_id, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=config.COLOR_FONDO_APP)
        self.user_id = user_id

        # fuentes defensivas (usar las de config si existen)
        FONT_TITULO = getattr(config, 'FONT_TITULO', ("Segoe UI", 20, "bold"))
        FONT_SECCION = getattr(config, 'FONT_SECCION', ("Segoe UI", 12, "bold"))

        ctk.CTkLabel(self, text="Planificador Masivo", font=FONT_TITULO, text_color="white").pack(pady=(18,6))

        # Contenedor principal con desplazamiento (para mostrar todo en pantallas pequeñas)
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=8)
        container = ctk.CTkFrame(scroll, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=12, pady=8)

        # --- LAYOUT: Secciones 1 y 2 en una fila, sección 3 debajo ---
        top_row = ctk.CTkFrame(container, fg_color="transparent")
        top_row.pack(fill="x", pady=(0,12))

        # --- SECCIÓN 1: Objetivo y Materiales por unidad (izquierda) ---
        sec1 = ctk.CTkFrame(top_row, fg_color=config.COLOR_TARJETA, corner_radius=8)
        sec1.pack(side="left", fill="both", expand=True, padx=(0,6))
        ctk.CTkLabel(sec1, text="1) Objetivo y Materiales por Unidad", font=FONT_SECCION, text_color=config.COLOR_VERDE_BAMBU).pack(anchor="w", padx=12, pady=(8,4))

        f_obj = ctk.CTkFrame(sec1, fg_color="transparent")
        f_obj.pack(fill="x", padx=12, pady=(0,8))
        ctk.CTkLabel(f_obj, text="Nombre del Proyecto:", text_color="gray").pack(anchor="w")
        self.entry_nombre = ctk.CTkEntry(f_obj, placeholder_text="Ej: Jarra colorida", fg_color="#1a1a1a", border_color="#444", text_color="white")
        self.entry_nombre.pack(fill="x", pady=6)

        row_meta = ctk.CTkFrame(f_obj, fg_color="transparent")
        row_meta.pack(fill="x")
        ctk.CTkLabel(row_meta, text="Meta total (unidades):", text_color="gray").pack(side="left")
        self.entry_meta = ctk.CTkEntry(row_meta, placeholder_text="100", width=120, fg_color="#1a1a1a", border_color="#444", text_color="white")
        self.entry_meta.pack(side="left", padx=8)

        # Materiales dinámicos (multicolor)
        ctk.CTkLabel(sec1, text="Materiales por unidad (multicolor):", text_color="gray").pack(anchor="w", padx=12)
        self.frame_materiales = ctk.CTkFrame(sec1, fg_color="transparent")
        self.frame_materiales.pack(fill="x", padx=12, pady=6)

        btns_mat = ctk.CTkFrame(sec1, fg_color="transparent")
        btns_mat.pack(fill="x", padx=12, pady=(0,10))
        ctk.CTkButton(btns_mat, text="+ Añadir color", command=self.agregar_material, width=140).pack(side="left")

        # lista interna de filas: (frame, entry_color, entry_gramos, btn_quitar)
        self.material_rows = []
        self.agregar_material()  # una fila por defecto

        # --- SECCIÓN 2: Definición de la Flota (derecha) ---
        sec2 = ctk.CTkFrame(top_row, fg_color=config.COLOR_TARJETA, corner_radius=8)
        sec2.pack(side="right", fill="both", expand=True, padx=(6,0))
        ctk.CTkLabel(sec2, text="2) Flota / Recursos (máquinas)", font=FONT_SECCION, text_color=config.COLOR_VERDE_BAMBU).pack(anchor="w", padx=12, pady=(8,4))

        f_flot = ctk.CTkFrame(sec2, fg_color="transparent")
        f_flot.pack(fill="x", padx=12, pady=(0,8))

        # Combo impresora desde DB
        ctk.CTkLabel(f_flot, text="Impresora (seleccionar):", text_color="gray").pack(anchor="w")
        self.combo_imp = ctk.CTkComboBox(f_flot, values=["Cargando..."], width=300, fg_color="#1a1a1a", button_color="#444", text_color="white")
        self.combo_imp.pack(fill="x", pady=6)

        # Tiempo por unidad para esta impresora
        row_time = ctk.CTkFrame(f_flot, fg_color="transparent")
        row_time.pack(fill="x")
        ctk.CTkLabel(row_time, text="Tiempo por unidad:", text_color="gray").pack(side="left")
        self.entry_hs = ctk.CTkEntry(row_time, placeholder_text="Hs", width=80, fg_color="#1a1a1a", border_color="#444", text_color="white")
        self.entry_hs.pack(side="left", padx=4)
        ctk.CTkLabel(row_time, text=":", text_color="gray").pack(side="left")
        self.entry_min = ctk.CTkEntry(row_time, placeholder_text="Min", width=80, fg_color="#1a1a1a", border_color="#444", text_color="white")
        self.entry_min.pack(side="left", padx=4)

        ctk.CTkButton(f_flot, text="Agregar a Flota", command=self.agregar_maquina, width=160).pack(pady=8)

        # Lista visual de máquinas añadidas
        ctk.CTkLabel(sec2, text="Máquinas añadidas (sesión):", text_color="gray").pack(anchor="w", padx=12)
        self.frame_flota = ctk.CTkScrollableFrame(sec2, fg_color="transparent", height=120)
        self.frame_flota.pack(fill="x", padx=12, pady=6)
        self.flota = []  # lista de dicts: {id,nombre,marca,modelo,power_kw,hs,min,velocidad}

        # cargar datos iniciales
        self.cargar_bobinas()
        self.cargar_impresoras()

        # --- SECCIÓN 3: Resultados (debajo, ancho completo) ---
        sec3 = ctk.CTkFrame(container, fg_color=config.COLOR_TARJETA, corner_radius=8)
        sec3.pack(fill="both", expand=True, pady=(6,0))
        ctk.CTkLabel(sec3, text="3) Resultados y Estrategia", font=FONT_SECCION, text_color=config.COLOR_VERDE_BAMBU).pack(anchor="w", padx=12, pady=(8,4))

        # Horas laborales por día (para cálculo de días necesarios)
        hrow = ctk.CTkFrame(sec3, fg_color="transparent")
        hrow.pack(fill="x", padx=12, pady=(0,6))
        ctk.CTkLabel(hrow, text="Horas de trabajo por día:", text_color="gray").pack(side="left")
        self.entry_horas_por_dia = ctk.CTkEntry(hrow, placeholder_text="8", width=100, fg_color="#1a1a1a", border_color="#444", text_color="white")
        self.entry_horas_por_dia.pack(side="left", padx=8)

        ctk.CTkButton(sec3, text="Calcular Estrategia", fg_color=config.COLOR_VERDE_BAMBU, hover_color=config.COLOR_VERDE_HOVER, command=self.calcular_estrategia).pack(padx=12, pady=(0,8))

        self.result_frame = ctk.CTkScrollableFrame(sec3, fg_color="transparent")
        self.result_frame.pack(fill="both", expand=True, padx=12, pady=6)
        self.label_result = ctk.CTkLabel(self.result_frame, text="", justify="left", text_color="gray")
        self.label_result.pack(anchor="w")
        # botón guardar (se mostrará luego de calcular)
        self.btn_guardar = None
        self.ultima_estrategia = None
        self.fecha_entrega = None
        self.precio_unit = None

    # ------------------ helpers UI ------------------
    def agregar_material(self):
        """Fila dinámica: color (texto) + gramos por unidad"""
        row = ctk.CTkFrame(self.frame_materiales, fg_color=config.COLOR_TARJETA, corner_radius=6)
        row.pack(fill="x", pady=6)

        entry_color = ctk.CTkEntry(row, placeholder_text="Color (ej: rojo)", width=260, fg_color="#1a1a1a", border_color="#444", text_color="white")
        entry_color.pack(side="left", padx=6, pady=6)
        entry_g = ctk.CTkEntry(row, placeholder_text="g por unidad", width=140, fg_color="#1a1a1a", border_color="#444", text_color="white")
        entry_g.pack(side="left", padx=6)
        btn = ctk.CTkButton(row, text="Quitar", width=80, fg_color=config.COLOR_ROJO, hover_color=config.COLOR_ROJO_HOVER, command=lambda r=row: self.quitar_material(r))
        btn.pack(side="right", padx=6)

        self.material_rows.append((row, entry_color, entry_g))

    def quitar_material(self, row):
        for i, (r, c, e) in enumerate(self.material_rows):
            if r == row:
                r.destroy()
                self.material_rows.pop(i)
                return

    def cargar_bobinas(self):
        """Carga bobinas para uso interno (stock por color). No se muestra en la UI aquí."""
        try:
            lista = database.obtener_bobinas(self.user_id)
            # bobinas_map por color sensible en minúsculas -> lista de pesos disponibles
            self.bobinas_map = {}
            for b in lista:
                # b: id, marca, material, color, peso_actual, costo, user_id
                bid, marca, material, color, peso, costo = b[0], b[1], b[2], b[3], b[4], b[5]
                key = (color or '').strip().lower()
                self.bobinas_map.setdefault(key, []).append({'id': bid, 'marca': marca, 'material': material, 'peso': float(peso), 'costo': float(costo)})
        except Exception:
            self.bobinas_map = {}

    # no es necesario _llenar_bobinas_en_combos porque ahora pedimos color directamente

    def cargar_impresoras(self):
        try:
            lista = database.obtener_impresoras(self.user_id)
            vals = []
            self.imp_map = {}
            for imp in lista:
                # imp: id, nombre, marca, modelo, estado, horas_uso, power_kw?
                iid, nombre, marca, modelo = imp[0], imp[1], imp[2], imp[3]
                power = imp[6] if len(imp) > 6 else 0.0
                display = f"{nombre} ({marca} {modelo}) - {power:.2f} kW"
                vals.append(display)
                self.imp_map[display] = {'id': iid, 'power': power, 'marca': marca, 'modelo': modelo}
            if vals:
                self.combo_imp.configure(values=vals)
                self.combo_imp.set(vals[0])
            else:
                self.combo_imp.configure(values=["Sin impresoras"])
                self.combo_imp.set("Sin impresoras")
        except Exception:
            self.combo_imp.configure(values=["Sin impresoras"])
            self.combo_imp.set("Sin impresoras")

    def agregar_maquina(self):
        sel = self.combo_imp.get()
        if not sel or sel == "Sin impresoras":
            messagebox.showwarning("Atención", "Selecciona una impresora válida.")
            return

        try:
            hs = float(self.entry_hs.get() or 0)
            mn = float(self.entry_min.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Horas y minutos deben ser números.")
            return

        tiempo_horas = hs + (mn / 60.0)
        if tiempo_horas <= 0:
            messagebox.showwarning("Atención", "El tiempo por unidad debe ser mayor que 0.")
            return

        info = self.imp_map.get(sel, None)
        if not info:
            messagebox.showerror("Error", "No se encontró la impresora seleccionada.")
            return

        velocidad = 1.0 / tiempo_horas
        maquina = {
            'display': sel,
            'id': info['id'],
            'marca': info['marca'],
            'modelo': info['modelo'],
            'power': float(info.get('power', 0.0)),
            'tiempo_unidad': tiempo_horas,
            'velocidad': velocidad
        }

        # agregar visual
        row = ctk.CTkFrame(self.frame_flota, fg_color=config.COLOR_TARJETA, corner_radius=6)
        row.pack(fill="x", pady=6)
        ctk.CTkLabel(row, text=maquina['display'], text_color="white").pack(side="left", padx=8)
        ctk.CTkLabel(row, text=f"Vel: {maquina['velocidad']:.3f} u/h | Consumo: {maquina['power']:.2f} kW", text_color="gray").pack(side="left", padx=8)
        btn = ctk.CTkButton(row, text="Quitar", width=80, fg_color=config.COLOR_ROJO, hover_color=config.COLOR_ROJO_HOVER, command=lambda r=row: self.quitar_maquina(r, maquina))
        btn.pack(side="right", padx=8)

        self.flota.append(maquina)

    def quitar_maquina(self, row, maquina):
        for i, m in enumerate(self.flota):
            if m is maquina:
                self.flota.pop(i)
                row.destroy()
                return

    # ------------------ Cálculo ------------------
    def calcular_estrategia(self):
        # Validaciones
        try:
            meta = int(self.entry_meta.get())
        except Exception:
            messagebox.showerror("Error", "Meta total inválida. Ingresa un entero.")
            return

        if meta <= 0:
            messagebox.showwarning("Atención", "La meta total debe ser mayor que 0.")
            return

        if not self.flota:
            messagebox.showwarning("Atención", "Agrega al menos una máquina a la flota.")
            return

        # Materiales: sumar gramos por unidad * meta, agrupado por color indicado
        materiales_totales = {}
        for (_, entry_color, entry_g) in self.material_rows:
            color = (entry_color.get() or '').strip()
            if not color:
                continue
            try:
                gramos = float(entry_g.get())
            except Exception:
                messagebox.showerror("Error", "Ingrese gramos válidos en materiales.")
                return

            key = color
            materiales_totales[key] = materiales_totales.get(key, 0.0) + gramos * meta

        # Tiempo (throughput)
        total_vel = 0.0
        for m in self.flota:
            total_vel += m['velocidad']

        if total_vel <= 0:
            messagebox.showerror("Error", "Velocidad combinada inválida.")
            return

        tiempo_total_hs = meta / total_vel  # horas

        dias = int(tiempo_total_hs // 24)
        horas_rest = tiempo_total_hs - dias * 24
        horas_ent = int(horas_rest)
        minutos_ent = int(round((horas_rest - horas_ent) * 60))

        # Consumo energético: cada máquina trabaja tiempo_total_hs horas (ver lógica matemática)
        costo_kw = getattr(config, 'COSTO_KW', 0.0)
        detalle_consumo = []
        total_power_sum = 0.0
        for m in self.flota:
            power = float(m.get('power', 0.0))
            consumo_kwh = power * tiempo_total_hs
            costo = consumo_kwh * float(costo_kw)
            detalle_consumo.append((m['display'], power, consumo_kwh, costo))
            total_power_sum += power

        costo_total_energia = sum(x[3] for x in detalle_consumo)
        # Preparar y mostrar resultados en secciones estéticas
        shortages = []
        for k, v in materiales_totales.items():
            # comparar con stock disponible por color (case-insensitive)
            key = k.strip().lower()
            available = 0.0
            if hasattr(self, 'bobinas_map') and key in self.bobinas_map:
                for b in self.bobinas_map[key]:
                    available += float(b.get('peso', 0.0))
            if available <= 0.0 and hasattr(self, 'bobinas_map'):
                for colname, items in self.bobinas_map.items():
                    if key in colname and key:
                        for b in items:
                            available += float(b.get('peso', 0.0))

            if available < v:
                shortages.append((k, v, available))

        # limpiar frame de resultados
        for w in self.result_frame.winfo_children():
            w.destroy()

        # Mostrar resumen condensado y botón Agendar
        # resumen grande: mostrar costo total y tiempo como lo más importante
        total_cost = costo_total_energia
        # estimar costo de materiales
        costo_materiales = 0.0
        try:
            for color, gramos in materiales_totales.items():
                key = color.strip().lower()
                if hasattr(self, 'bobinas_map') and key in self.bobinas_map and self.bobinas_map[key]:
                    b = self.bobinas_map[key][0]
                    precio_por_gramo = float(b.get('costo', 0.0)) / max(1.0, float(b.get('peso', 1000.0)))
                    costo_materiales += gramos * precio_por_gramo
        except Exception:
            costo_materiales = 0.0

        total_cost += costo_materiales

        # mostrar en grande
        top_summary = ctk.CTkFrame(self.result_frame, fg_color=config.COLOR_TARJETA, corner_radius=8)
        top_summary.pack(fill="x", pady=8, padx=6)
        ctk.CTkLabel(top_summary, text=f"Costo total estimado: {total_cost:.2f}", font=("Segoe UI", 18, "bold"), text_color="#ffd966").pack(anchor="w", padx=12, pady=(8,4))
        ctk.CTkLabel(top_summary, text=f" - Materiales: {costo_materiales:.2f} | Energía: {costo_total_energia:.2f}", text_color="gray").pack(anchor="w", padx=12, pady=(0,8))
        tiempo_text = f"Tiempo estimado: {tiempo_total_hs:.2f} hs -> {dias}d {horas_ent}h {minutos_ent}m"
        # calcular días laborales si el usuario definió horas por día
        dias_trabajo_msg = ""
        try:
            horas_por_dia = float(self.entry_horas_por_dia.get() or 0)
            if horas_por_dia > 0:
                from math import ceil
                dias_trabajo = ceil(tiempo_total_hs / horas_por_dia)
                dias_trabajo_msg = f" | Días laborales (@{horas_por_dia}h/d): {dias_trabajo}"
        except Exception:
            dias_trabajo_msg = ""

        ctk.CTkLabel(top_summary, text=tiempo_text + dias_trabajo_msg, text_color="gray").pack(anchor="w", padx=12, pady=(0,8))

        # mostrar botón Agendar
        if self.btn_guardar:
            try:
                self.btn_guardar.destroy()
            except Exception:
                pass
        self.btn_guardar = ctk.CTkButton(self.result_frame, text="Agendar (definir fecha y precio)", fg_color=config.COLOR_VERDE_BAMBU, hover_color=config.COLOR_VERDE_HOVER, command=lambda: self.dialog_agendar(materiales_totales, detalle_consumo, total_cost, costo_materiales, tiempo_total_hs))
        self.btn_guardar.pack(pady=(10,12))

        # almacenar última estrategia para poder guardarla en agenda
        self.ultima_estrategia = {
            'nombre': self.entry_nombre.get() or 'Sin nombre',
            'meta': meta,
            'materiales': materiales_totales,
            'flota': self.flota,
            'tiempo_hs': tiempo_total_hs,
            'costo_energia': costo_total_energia,
            'shortages': shortages
        }

        # mostrar botón Guardar en Agenda
        if self.btn_guardar:
            try:
                self.btn_guardar.destroy()
            except Exception:
                pass
        # botón para agregar fecha/ precio antes de guardar
        ctk.CTkButton(self.result_frame, text="Agregar fecha de entrega / Precio unidad", fg_color="#6aa84f", hover_color="#5b7e3a", command=self.agregar_fecha_entrega_dialog).pack(pady=(6,4))

        self.info_fecha_lbl = ctk.CTkLabel(self.result_frame, text="", text_color="#cfcfcf")
        self.info_fecha_lbl.pack(anchor="w", pady=(2,6))

        self.btn_guardar = ctk.CTkButton(self.result_frame, text="Guardar en agenda", fg_color="#3a7bd5", hover_color="#2f6bb0", command=self.guardar_en_agenda)
        self.btn_guardar.pack(pady=(6,12))

    def abrir_tienda(self):
        # abrir link de compra (puede modificarse)
        webbrowser.open("https://listado.mercadolibre.com.ar/filamento-3d")

    def agregar_fecha_entrega_dialog(self, on_ok_callback=None):
        top = ctk.CTkToplevel(self)
        top.title("Agregar fecha de entrega y precio")
        top.geometry("420x180")
        # fecha por defecto: hoy + 7 días
        default = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

        ctk.CTkLabel(top, text="Fecha de entrega (YYYY-MM-DD):", text_color="gray").pack(anchor="w", padx=12, pady=(12,4))
        if TKCAL_AVAILABLE:
            try:
                entry_fecha = DateEntry(top, date_pattern='yyyy-mm-dd')
                entry_fecha.set_date(default)
                entry_fecha.pack(fill="x", padx=12)
            except Exception:
                entry_fecha = ctk.CTkEntry(top, placeholder_text=default)
                entry_fecha.insert(0, default)
                entry_fecha.pack(fill="x", padx=12)
        else:
            entry_fecha = ctk.CTkEntry(top, placeholder_text=default)
            entry_fecha.insert(0, default)
            entry_fecha.pack(fill="x", padx=12)

        ctk.CTkLabel(top, text="Precio de venta por unidad (moneda):", text_color="gray").pack(anchor="w", padx=12, pady=(8,4))
        entry_precio = ctk.CTkEntry(top, placeholder_text="Ej: 25.5")
        if self.precio_unit:
            entry_precio.insert(0, str(self.precio_unit))
        entry_precio.pack(fill="x", padx=12)

        def on_ok():
            fecha = entry_fecha.get().strip()
            precio = entry_precio.get().strip() or "0"
            # validar fecha simple
            try:
                datetime.strptime(fecha, '%Y-%m-%d')
            except Exception:
                messagebox.showerror("Error", "Fecha inválida. Usa formato YYYY-MM-DD.")
                return
            try:
                precio_f = float(precio)
            except Exception:
                messagebox.showerror("Error", "Precio inválido.")
                return

            self.fecha_entrega = fecha
            self.precio_unit = precio_f
            # actualizar etiqueta en resultados
            try:
                self.info_fecha_lbl.configure(text=f"Entrega: {self.fecha_entrega} | Precio/u: {self.precio_unit:.2f}")
            except Exception:
                pass
            top.destroy()
            # si hay un callback (por ejemplo: reintentar guardar), llamarlo
            try:
                if on_ok_callback:
                    on_ok_callback()
            except Exception:
                pass

        btns = ctk.CTkFrame(top, fg_color='transparent')
        btns.pack(fill='x', pady=12, padx=12)
        ctk.CTkButton(btns, text="Cancelar", fg_color="#999", command=top.destroy).pack(side='right', padx=6)
        ctk.CTkButton(btns, text="OK", fg_color=config.COLOR_VERDE_BAMBU, command=on_ok).pack(side='right')

    def dialog_agendar(self, materiales_totales, detalle_consumo, total_cost, costo_materiales, tiempo_total_hs):
        top = ctk.CTkToplevel(self)
        top.title("Agendar y fijar precio")
        top.geometry("720x520")
        top.lift(); top.focus_force()

        # Panel de desglose
        left = ctk.CTkFrame(top, fg_color="transparent")
        left.pack(side='left', fill='both', expand=True, padx=12, pady=12)
        right = ctk.CTkFrame(top, fg_color="transparent")
        right.pack(side='right', fill='y', padx=12, pady=12)

        ctk.CTkLabel(left, text="Desglose de Costos", font=("Segoe UI", 14, "bold"), text_color="white").pack(anchor='w')

        sec_mat = ctk.CTkFrame(left, fg_color=config.COLOR_TARJETA, corner_radius=8)
        sec_mat.pack(fill='x', pady=8)
        ctk.CTkLabel(sec_mat, text="Materiales (estimación)", font=("Segoe UI", 12, "bold"), text_color=config.COLOR_VERDE_BAMBU).pack(anchor='w', padx=8, pady=6)
        try:
            for k, v in materiales_totales.items():
                # intentar estimar costo por color
                costo_k = 0.0
                key = k.strip().lower()
                if hasattr(self, 'bobinas_map') and key in self.bobinas_map and self.bobinas_map[key]:
                    b = self.bobinas_map[key][0]
                    precio_por_gramo = float(b.get('costo', 0.0)) / max(1.0, float(b.get('peso', 1000.0)))
                    costo_k = v * precio_por_gramo
                ctk.CTkLabel(sec_mat, text=f" - {k}: {v:.2f} g -> Costo estimado: {costo_k:.2f}", text_color="gray").pack(anchor='w', padx=10)
        except Exception:
            ctk.CTkLabel(sec_mat, text="No se pudo estimar costo de materiales.", text_color="gray").pack(anchor='w', padx=10)

        sec_energy = ctk.CTkFrame(left, fg_color=config.COLOR_TARJETA, corner_radius=8)
        sec_energy.pack(fill='x', pady=8)
        ctk.CTkLabel(sec_energy, text="Consumo por máquina (kWh) y costo", font=("Segoe UI", 12, "bold"), text_color=config.COLOR_VERDE_BAMBU).pack(anchor='w', padx=8, pady=6)
        for d in detalle_consumo:
            ctk.CTkLabel(sec_energy, text=f" - {d[0]}: {d[2]:.2f} kWh -> Costo: {d[3]:.2f}", text_color="gray").pack(anchor='w', padx=10)

        # resumen grande
        resumen = ctk.CTkFrame(left, fg_color=config.COLOR_TARJETA, corner_radius=8)
        resumen.pack(fill='x', pady=8)
        ctk.CTkLabel(resumen, text=f"Costo total estimado: {total_cost:.2f}", font=("Segoe UI", 16, "bold"), text_color="#ffd966").pack(anchor='w', padx=10, pady=8)
        ctk.CTkLabel(resumen, text=f" - Materiales: {costo_materiales:.2f} | Energía: {total_cost - costo_materiales:.2f}", text_color="gray").pack(anchor='w', padx=10, pady=(0,8))

        # lado derecho: zona, fecha, precio y acciones
        ctk.CTkLabel(right, text="Configuración", font=("Segoe UI", 12, "bold"), text_color="white").pack(anchor='w')

        ctk.CTkLabel(right, text="Zona / tarifa eléctrica:", text_color="gray").pack(anchor='w', pady=(8,2))
        zonas = list(getattr(config, 'ZONAS_COSTO', {}).keys())
        self.combo_zona = ctk.CTkComboBox(right, values=zonas, width=260)
        if zonas:
            self.combo_zona.set(zonas[0])
        self.combo_zona.pack(anchor='w')

        ctk.CTkLabel(right, text="Costo kW-h (override):", text_color="gray").pack(anchor='w', pady=(8,2))
        entry_costo_kw = ctk.CTkEntry(right, placeholder_text=str(getattr(config, 'COSTO_KW', 0.0)))
        entry_costo_kw.pack(anchor='w')

        ctk.CTkLabel(right, text="Fecha de entrega (YYYY-MM-DD):", text_color="gray").pack(anchor='w', pady=(12,2))
        fecha_default = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        if TKCAL_AVAILABLE:
            try:
                entry_fecha = DateEntry(right, date_pattern='yyyy-mm-dd')
                entry_fecha.set_date(fecha_default)
                entry_fecha.pack()
            except Exception:
                entry_fecha = ctk.CTkEntry(right)
                entry_fecha.insert(0, fecha_default)
                entry_fecha.pack()
        else:
            entry_fecha = ctk.CTkEntry(right)
            entry_fecha.insert(0, fecha_default)
            entry_fecha.pack()

        ctk.CTkLabel(right, text="Precio de venta por unidad:", text_color="gray").pack(anchor='w', pady=(12,2))
        entry_precio_unit = ctk.CTkEntry(right)
        entry_precio_unit.pack(anchor='w')

        resultado_lbl = ctk.CTkLabel(right, text="", text_color="#ffd966", wraplength=260)
        resultado_lbl.pack(pady=(12,4))

        def calcular_ganancia_local():
            try:
                precio_u = float(entry_precio_unit.get())
            except Exception:
                messagebox.showerror("Error", "Precio por unidad inválido")
                return
            unidades = int(self.entry_meta.get() or 0)
            ingresos = precio_u * unidades
            energia_cost = sum(x[3] for x in detalle_consumo)
            # si el usuario seleccionó zona, ajustar tarifa
            tarifa = None
            try:
                sel = self.combo_zona.get()
                tarifa = config.ZONAS_COSTO.get(sel)
            except Exception:
                tarifa = None
            try:
                override = entry_costo_kw.get().strip()
                if override:
                    tarifa = float(override)
            except Exception:
                pass
            # recalcular energia cost if tarifa changed
            if tarifa is not None:
                energia_cost = 0.0
                new_det = []
                for d in detalle_consumo:
                    consumo_kwh = d[2]
                    costo_d = consumo_kwh * tarifa
                    new_det.append((d[0], d[1], consumo_kwh, costo_d))
                    energia_cost += costo_d

            costo_mat = costo_materiales
            total_costo_local = energia_cost + costo_mat
            gan_total = ingresos - total_costo_local
            resultado_lbl.configure(text=f"Ingresos: {ingresos:.2f}\nCosto materiales: {costo_mat:.2f}\nCosto energía: {energia_cost:.2f}\nCosto total: {total_costo_local:.2f}\nGanancia total: {gan_total:.2f}")
            return gan_total, tarifa

        def guardar_final():
            # validar fecha y precio
            try:
                fecha = entry_fecha.get().strip()
                datetime.strptime(fecha, '%Y-%m-%d')
            except Exception:
                messagebox.showerror("Error", "Fecha inválida")
                return
            try:
                precio_u = float(entry_precio_unit.get())
            except Exception:
                messagebox.showerror("Error", "Precio inválido")
                return

            # recalcular tarifa y costos antes de guardar
            tarifa = None
            try:
                sel = self.combo_zona.get()
                tarifa = config.ZONAS_COSTO.get(sel)
            except Exception:
                tarifa = None
            try:
                override = entry_costo_kw.get().strip()
                if override:
                    tarifa = float(override)
            except Exception:
                pass

            energia_cost = 0.0
            if tarifa is not None:
                for d in detalle_consumo:
                    energia_cost += d[2] * tarifa
            else:
                energia_cost = sum(x[3] for x in detalle_consumo)

            costo_mat = costo_materiales
            unidades = int(self.entry_meta.get() or 0)
            ingresos = precio_u * unidades
            gan_total = ingresos - (energia_cost + costo_mat)

            # normalizar flota
            flota_lista = []
            for m in self.ultima_estrategia.get('flota', []):
                flota_lista.append({
                    'id': m.get('id'),
                    'display': m.get('display'),
                    'marca': m.get('marca'),
                    'modelo': m.get('modelo'),
                    'power': m.get('power'),
                    'tiempo_unidad': m.get('tiempo_unidad'),
                    'velocidad': m.get('velocidad')
                })

            ok = database.guardar_proyecto_agenda(self.user_id, self.ultima_estrategia.get('nombre'), self.ultima_estrategia.get('meta'), json.dumps(materiales_totales), json.dumps(flota_lista), tiempo_total_hs, energia_cost, precio_u, entry_fecha.get().strip(), gan_total)
            if ok:
                dlg = ctk.CTkToplevel(self)
                dlg.title("Guardado")
                dlg.geometry("360x140")
                ctk.CTkLabel(dlg, text="Proyecto agendado correctamente.", font=("Segoe UI", 12)).pack(pady=(20,8))
                ctk.CTkButton(dlg, text="Aceptar", command=lambda: (dlg.destroy(), top.destroy()), fg_color=config.COLOR_VERDE_BAMBU).pack(pady=12)
            else:
                dlg = ctk.CTkToplevel(self)
                dlg.title("Error")
                dlg.geometry("360x120")
                ctk.CTkLabel(dlg, text="No se pudo guardar el proyecto.", text_color="red").pack(pady=20)
                ctk.CTkButton(dlg, text="Cerrar", command=dlg.destroy).pack(pady=8)

        ctk.CTkButton(right, text="Calcular Ganancia", fg_color=config.COLOR_VERDE_BAMBU, command=calcular_ganancia_local).pack(pady=(8,6))
        ctk.CTkButton(right, text="Guardar y Agendar", fg_color="#3a7bd5", command=guardar_final).pack()

    def guardar_en_agenda(self):
        if not self.ultima_estrategia:
            messagebox.showwarning("Atención", "No hay estrategia calculada para guardar.")
            return

        # Si no se definió precio por unidad, pedirlo antes de guardar
        try:
            if not self.precio_unit or float(self.precio_unit) <= 0:
                # abrir diálogo para que el usuario ingrese fecha y precio, luego reintentar guardar
                self.agregar_fecha_entrega_dialog(on_ok_callback=self.guardar_en_agenda)
                return
        except Exception:
            # en caso de error al interpretar, pedir igualmente
            self.agregar_fecha_entrega_dialog(on_ok_callback=self.guardar_en_agenda)
            return

        try:
            # serializar materiales y flota
            materiales_json = json.dumps(self.ultima_estrategia.get('materiales', {}))
            # flota contiene objetos no serializables (objetos CTk). Normalizar lista con campos útiles
            flota_lista = []
            for m in self.ultima_estrategia.get('flota', []):
                flota_lista.append({
                    'id': m.get('id'),
                    'display': m.get('display'),
                    'marca': m.get('marca'),
                    'modelo': m.get('modelo'),
                    'power': m.get('power'),
                    'tiempo_unidad': m.get('tiempo_unidad'),
                    'velocidad': m.get('velocidad')
                })
            flota_json = json.dumps(flota_lista)

            # calcular ganancia estimada: ingresos - (energia + materiales)
            meta = int(self.ultima_estrategia.get('meta', 0))
            precio_unit = float(self.precio_unit) if self.precio_unit else 0.0
            ingresos = precio_unit * meta
            energia_cost = float(self.ultima_estrategia.get('costo_energia', 0.0))
            # estimar costo de materiales si hay datos en bobinas_map
            costo_materiales = 0.0
            try:
                for color, gramos in self.ultima_estrategia.get('materiales', {}).items():
                    key = color.strip().lower()
                    if hasattr(self, 'bobinas_map') and key in self.bobinas_map and self.bobinas_map[key]:
                        # usar el primer item para estimar precio por gramo
                        b = self.bobinas_map[key][0]
                        precio_por_gramo = float(b.get('costo', 0.0)) / max(1.0, float(b.get('peso', 1000.0)))
                        costo_materiales += gramos * precio_por_gramo
            except Exception:
                costo_materiales = 0.0

            ganancia = ingresos - energia_cost - costo_materiales

            ok = database.guardar_proyecto_agenda(
                self.user_id,
                self.ultima_estrategia.get('nombre'),
                meta,
                materiales_json,
                flota_json,
                float(self.ultima_estrategia.get('tiempo_hs', 0.0)),
                energia_cost,
                precio_unit,
                self.fecha_entrega,
                ganancia
            )

            if ok:
                dlg = ctk.CTkToplevel(self)
                dlg.title("Guardado")
                dlg.geometry("360x140")
                ctk.CTkLabel(dlg, text="Estrategia guardada en la agenda correctamente.", font=("Segoe UI", 12)).pack(pady=(20,8))
                ctk.CTkButton(dlg, text="Aceptar", command=dlg.destroy, fg_color=config.COLOR_VERDE_BAMBU).pack(pady=12)
            else:
                dlg = ctk.CTkToplevel(self)
                dlg.title("Error")
                dlg.geometry("360x120")
                ctk.CTkLabel(dlg, text="No se pudo guardar la estrategia en la agenda.", text_color="red").pack(pady=20)
                ctk.CTkButton(dlg, text="Cerrar", command=dlg.destroy).pack(pady=8)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al guardar: {e}")
