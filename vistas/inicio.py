import customtkinter as ctk
import sys
import os
import config # Importamos para usar los colores

# Importar database
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database

class VistaInicio(ctk.CTkFrame):
    def __init__(self, master, user_id, callback_nueva_impresion, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=config.COLOR_FONDO_APP) # Fondo oscuro general
        self.user_id = user_id
        self.callback_nueva_impresion = callback_nueva_impresion

        # Título
        ctk.CTkLabel(self, text="Panel de Control", font=("Segoe UI", 24, "bold"), text_color="white").pack(pady=(30, 5))
        ctk.CTkLabel(self, text="Resumen de actividad", font=("Segoe UI", 14), text_color="gray").pack(pady=(0, 30))

        # --- TARJETAS DE ESTADÍSTICAS (GRID) ---
        # Usamos un Grid para que se ordenen mejor
        frame_stats = ctk.CTkFrame(self, fg_color="transparent")
        frame_stats.pack(fill="x", padx=40)
        
        # Configuración de columnas para que se centren
        frame_stats.grid_columnconfigure(0, weight=1)
        frame_stats.grid_columnconfigure(1, weight=1)
        frame_stats.grid_columnconfigure(2, weight=1)

        # Datos
        cant_impresoras = database.contar_impresoras(self.user_id)
        cant_bobinas = database.contar_bobinas(self.user_id)
        cant_trabajos = database.contar_trabajos(self.user_id)
        gasto_total = database.calcular_gasto_total(self.user_id)

        # Tarjetas "Dark Mode"
        # Azul Cyan para Impresoras, Naranja para Bobinas, Verde para Trabajos
        self.crear_tarjeta_pro(frame_stats, 0, "IMPRESORAS", str(cant_impresoras), "#3498db", "🖨️")
        self.crear_tarjeta_pro(frame_stats, 1, "BOBINAS", str(cant_bobinas), "#e67e22", "🧵")
        self.crear_tarjeta_pro(frame_stats, 2, "TRABAJOS", str(cant_trabajos), "#2ecc71", "✅")
        
        # --- SECCIÓN DINERO ---
        frame_dinero = ctk.CTkFrame(self, fg_color=config.COLOR_TARJETA, corner_radius=10)
        # Mantener mismo margen horizontal que otras secciones
        frame_dinero.pack(pady=40, ipadx=20, ipady=10, fill='x', padx=40)

        # Controles de consumo energético en el dashboard
        opts = ctk.CTkFrame(self, fg_color="transparent")
        opts.pack(padx=10, pady=(10,0))
        self.switch_mostrar = ctk.CTkSwitch(opts, text="Incluir costo energético", progress_color=config.COLOR_VERDE_BAMBU, command=self.toggle_consumo)
        if config.MOSTRAR_CONSUMO:
            self.switch_mostrar.select()
        else:
            self.switch_mostrar.deselect()
        self.switch_mostrar.pack(side="left", padx=(0,10))

        ctk.CTkLabel(opts, text="Costo kW-h:", text_color="gray").pack(side="left")
        self.entry_costokw = ctk.CTkEntry(opts, placeholder_text=str(config.COSTO_KW), width=120, fg_color="#1a1a1a", border_color="#444", text_color="white")
        self.entry_costokw.pack(side="left", padx=6)
        # removido botón 'Aplicar' (no requerido). Mostrar valor actual en el entry
        try:
            self.entry_costokw.insert(0, str(config.COSTO_KW))
        except Exception:
            pass

        # (Los switches de modo y accesibilidad están en la barra lateral)

        # Centered small box containing only the two big cards (Costo + Ganancia)
        center_box = ctk.CTkFrame(frame_dinero, fg_color="transparent")
        # limitar ancho para que no ocupe todo el espacio
        center_box.configure(width=900)
        center_box.pack(pady=8)
        center_box.pack_propagate(False)
        # usar grid para que ambas tarjetas queden alineadas
        center_box.grid_columnconfigure(0, weight=1)
        center_box.grid_columnconfigure(1, weight=1)

        card_cost = ctk.CTkFrame(center_box, fg_color=config.COLOR_TARJETA, corner_radius=8, width=420)
        card_cost.grid(row=0, column=0, padx=24, pady=12, sticky='n')
        ctk.CTkLabel(card_cost, text="COSTO TOTAL DE PRODUCCIÓN", font=("Segoe UI", 12, "bold"), text_color="gray").pack()
        self.label_gasto_total = ctk.CTkLabel(card_cost, text=f"${gasto_total:,.2f}", font=("Segoe UI", 32, "bold"), text_color="white")
        self.label_gasto_total.pack(pady=(2,8))
        # detalles energéticos (no empaquetados por defecto)
        self.label_energy_hour = ctk.CTkLabel(card_cost, text="", text_color="gray")
        self.label_energy_acum = ctk.CTkLabel(card_cost, text="", text_color="gray")
        self.label_combined = ctk.CTkLabel(card_cost, text="", font=("Segoe UI", 14, "bold"), text_color="white")

        card_gain = ctk.CTkFrame(center_box, fg_color=config.COLOR_TARJETA, corner_radius=8, width=420)
        card_gain.grid(row=0, column=1, padx=24, pady=12, sticky='n')
        ctk.CTkLabel(card_gain, text="GANANCIA TOTAL", font=("Segoe UI", 12, "bold"), text_color="gray").pack()
        self.label_ganancia_total = ctk.CTkLabel(card_gain, text="$0.00", font=("Segoe UI", 32, "bold"), text_color="#9ee59e")
        self.label_ganancia_total.pack(pady=(2,8))
        self.label_ganancia_detail = ctk.CTkLabel(card_gain, text="", text_color="gray")
        self.label_ganancia_detail.pack()

        # Preview area moved OUTSIDE the big frame; create placeholder here and pack later
        # (we'll create a separate preview block after the frame_dinero)
        self.preview_container = None

        # Actualizar valores con lo que haya en la DB
        self.actualizar_consumo_dashboard()

        # --- Sección PREVIEWS fuera del cuadro grande ---
        preview_outer = ctk.CTkFrame(self, fg_color="transparent")
        preview_outer.pack(fill='x', padx=40)
        preview_frame = ctk.CTkFrame(preview_outer, fg_color=config.COLOR_TARJETA, corner_radius=8)
        preview_frame.pack(padx=6, pady=6, fill='x')
        ctk.CTkLabel(preview_frame, text="Últimas agendas", font=("Segoe UI", 12, "bold"), text_color="white").pack(pady=(6,4))
        # Header con botón único para ver todas las agendas
        header_row = ctk.CTkFrame(preview_frame, fg_color="transparent")
        header_row.pack(fill='x', padx=6)
        ctk.CTkLabel(header_row, text="Últimas agendas", font=("Segoe UI", 12, "bold"), text_color="white").pack(side='left', pady=(6,4))
        ctk.CTkButton(header_row, text="Ver agendas", width=120, command=self._ver_todas_las_agendas).pack(side='right', pady=(6,4))

        # Contenedor con dos columnas para up to 2 previews
        self.preview_container = ctk.CTkFrame(preview_frame, fg_color="transparent")
        self.preview_container.pack(padx=6, pady=4, fill='x')
        self.preview_container.grid_columnconfigure(0, weight=1)
        self.preview_container.grid_columnconfigure(1, weight=1)

        # Cargar previews iniciales
        try:
            self.actualizar_previews_y_stats()
        except Exception:
            pass

        # Nota: removido botón flotante "Nueva Impresión" para evitar comportamiento inconsistente

    def crear_tarjeta_pro(self, parent, col_idx, titulo, numero, color_acento, icono):
        # La tarjeta es GRIS OSCURO, no del color
        card = ctk.CTkFrame(parent, fg_color=config.COLOR_TARJETA, corner_radius=10, border_width=1, border_color="#333")
        card.grid(row=0, column=col_idx, padx=10, sticky="ew")
        
        # Icono y Título
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(pady=(15, 5))
        
        ctk.CTkLabel(header, text=icono, font=("Segoe UI", 20)).pack(side="left", padx=5)
        ctk.CTkLabel(header, text=titulo, font=("Segoe UI", 12, "bold"), text_color="gray").pack(side="left")

        # El Número es el que lleva el COLOR
        ctk.CTkLabel(card, text=numero, font=("Segoe UI", 40, "bold"), text_color=color_acento).pack(pady=(0, 15))

    def aplicar_costo(self):
        try:
            v = float(self.entry_costokw.get())
            config.COSTO_KW = v
            self.actualizar_consumo_dashboard()
        except ValueError:
            pass

    def toggle_consumo(self):
        config.MOSTRAR_CONSUMO = bool(self.switch_mostrar.get())
        self.actualizar_consumo_dashboard()

    def actualizar_consumo_dashboard(self):
        # recalcula el consumo total y muestra/oculta etiquetas según config
        try:
            costo = float(config.COSTO_KW)
        except:
            costo = 0.0

        # obtener impresoras y sumar
        impresoras = database.obtener_impresoras(self.user_id)
        total_kw = 0.0
        total_energy_cost_acum = 0.0
        for imp in impresoras:
            # imp: id, nombre, marca, modelo, estado, horas_uso, power_kw?
            horas = imp[5] if len(imp) > 5 else 0.0
            power_kw = imp[6] if len(imp) > 6 else 0.0
            total_kw += power_kw
            total_energy_cost_acum += (power_kw * horas) * costo

        costo_por_hora = total_kw * costo

        gasto_total = database.calcular_gasto_total(self.user_id) or 0.0
        ingresos_total = database.calcular_ingresos_total(self.user_id) or 0.0

        # Mostrar u ocultar detalles energéticos según toggle
        if config.MOSTRAR_CONSUMO:
            # actualizar textos
            try:
                self.label_energy_hour.configure(text=f"Consumo total por hora: {total_kw:.2f} kW -> Costo/h: {costo_por_hora:.2f}")
                self.label_energy_acum.configure(text=f"Costo energético acumulado (según horas registradas): {total_energy_cost_acum:.2f}")
                self.label_gasto_total.configure(text=f"${gasto_total:,.2f}")
                self.label_combined.configure(text=f"Costo total estimado (material + energía): ${gasto_total + total_energy_cost_acum:.2f}")
            except Exception:
                pass
            # pack energy labels si no están visibles
            try:
                if not self.label_energy_hour.winfo_ismapped():
                    self.label_energy_hour.pack()
                if not self.label_energy_acum.winfo_ismapped():
                    self.label_energy_acum.pack()
                if not self.label_combined.winfo_ismapped():
                    self.label_combined.pack(pady=(6,0))
            except Exception:
                pass

            # ganancia = ingresos - (gasto + energia)
            gan_total = ingresos_total - (gasto_total + total_energy_cost_acum)
            self.label_ganancia_total.configure(text=f"${gan_total:,.2f}")
            self.label_ganancia_detail.configure(text=f"Ingresos: ${ingresos_total:,.2f} | Antes energía: ${ingresos_total - gasto_total:,.2f}")
        else:
            # ocultar etiquetas energéticas si estaban visibles
            try:
                if self.label_energy_hour.winfo_ismapped():
                    self.label_energy_hour.pack_forget()
                if self.label_energy_acum.winfo_ismapped():
                    self.label_energy_acum.pack_forget()
                if self.label_combined.winfo_ismapped():
                    self.label_combined.pack_forget()
            except Exception:
                pass

            # ganancia simple: preferir columna ganancia o fallback ingresos - gastos
            try:
                gan_stored = database.calcular_ganancia_total(self.user_id) or 0.0
                if gan_stored == 0.0:
                    gan_calc = ingresos_total - gasto_total
                else:
                    gan_calc = gan_stored
            except Exception:
                gan_calc = ingresos_total - gasto_total
            self.label_ganancia_total.configure(text=f"${gan_calc:,.2f}")
            self.label_ganancia_detail.configure(text=f"Ingresos: ${ingresos_total:,.2f}")

    def actualizar_previews_y_stats(self):
        # actualizar las últimas 3 agendas en preview_container y contadores laterales
        try:
            proyectos = database.obtener_ultimas_agendas(self.user_id, limit=2)
        except Exception:
            proyectos = []

        # limpiar contenedor
        for w in self.preview_container.winfo_children():
            w.destroy()

        # mostrar hasta 2 en columnas (izq / der)
        for idx, p in enumerate(proyectos[:2]):
            # p: id, nombre, meta, materiales, flota, tiempo_hs, costo_energia, precio_unit, delivery_date, ganancia, created_at
            pid = p[0]
            nombre = p[1] if len(p) > 1 else 'Proyecto'
            meta = p[2] if len(p) > 2 else ''
            card = ctk.CTkFrame(self.preview_container, fg_color=config.COLOR_TARJETA, corner_radius=6)
            card.grid(row=0, column=idx, sticky='nsew', padx=6, pady=8)
            ctk.CTkLabel(card, text=f"{nombre}", font=("Segoe UI", 11, "bold"), text_color="white").pack(anchor='w', padx=8, pady=(6,2))
            ctk.CTkLabel(card, text=f"Meta: {meta}", text_color='gray').pack(anchor='w', padx=8, pady=(0,6))
            # detalle breve
            ctk.CTkLabel(card, text=f"Fecha: {p[8]}", text_color='gray').pack(anchor='w', padx=8, pady=(0,6))

        # si hay menos de 2, llenar el otro lado con espacio para mantener layout
        if len(proyectos) < 2:
            for empty_idx in range(len(proyectos), 2):
                placeholder = ctk.CTkFrame(self.preview_container, fg_color="transparent")
                placeholder.grid(row=0, column=empty_idx, sticky='nsew', padx=6, pady=8)

    def apply_negrita(self, enabled: bool):
        """Aplicar modo de texto aumentado/negrita en la vista (llamado desde `main`)."""
        try:
            if enabled:
                self.label_gasto_total.configure(font=("Segoe UI", 36, "bold"))
                self.label_ganancia_total.configure(font=("Segoe UI", 36, "bold"))
            else:
                self.label_gasto_total.configure(font=("Segoe UI", 32, "bold"))
                self.label_ganancia_total.configure(font=("Segoe UI", 32, "bold"))
        except Exception:
            pass

    def _abrir_en_agenda(self, pid):
        # simple helper: si el master tiene método para cambiar vista a Agenda, usarlo
        try:
            if hasattr(self.master, 'mostrar_agenda'):
                self.master.mostrar_agenda(pid)
        except Exception:
            pass

    def _ver_todas_las_agendas(self):
        try:
            if hasattr(self.master, 'ir_a_agenda'):
                # navegar a vista Agenda
                self.master.ir_a_agenda()
        except Exception:
            pass