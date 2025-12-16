import customtkinter as ctk
from tkinter import messagebox
import sys
import os
import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database

# Datos precargados para los dropdowns
DATOS_IMPRESORAS = {
    "Creality": ["Ender 3", "Ender 3 V2", "Ender 3 S1", "K1", "K1 Max", "CR-10", "OTROS"],
    "Bambu Lab": ["X1 Carbon", "P1S", "P1P", "A1 Mini", "A1", "OTROS"],
    "Prusa": ["MK3S+", "MK4", "Mini+", "XL", "OTROS"],
    "Artillery": ["Sidewinder X1", "Sidewinder X2", "Genius", "Hornet", "OTROS"],
    "Elegoo": ["Neptune 3", "Neptune 4", "Neptune 4 Pro", "OTROS"],
    "Anycubic": ["Kobra 2", "Kobra Neo", "Vyper", "Mega S", "OTROS"],
    "Voron": ["V0.1", "V2.4", "Trident", "Switchwire", "OTROS"],
    "OTROS": ["Genérica / Custom"] 
}

class VistaImpresoras(ctk.CTkFrame):
    def __init__(self, master, user_id, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=config.COLOR_FONDO_APP)
        self.user_id = user_id
        
        # Fuentes y colores (defensivo)
        FONT_TITULO = getattr(config, 'FONT_TITULO', ("Segoe UI", 24, "bold"))
        FONT_SUBTITULO = getattr(config, 'FONT_SUBTITULO', ("Segoe UI", 16, "bold"))
        FONT_TEXTO = getattr(config, 'FONT_TEXTO', ("Segoe UI", 13, "bold")) # Todo Bold como pediste
        BORDER_COLOR = getattr(config, 'COLOR_ACENTO', "#00965e")
        if isinstance(BORDER_COLOR, tuple): BORDER_COLOR = BORDER_COLOR[1]

        # Título Principal
        ctk.CTkLabel(self, text="Mis Impresoras", font=FONT_TITULO, text_color=config.COLOR_TEXTO_BLANCO).pack(pady=(10, 5))

        # --- 1. TIPS (Panel Superior) ---
        self.frame_tips = ctk.CTkFrame(self, fg_color="transparent", border_width=1, border_color=BORDER_COLOR, corner_radius=10)
        self.frame_tips.pack(fill="x", padx=20, pady=10)
        
        lbl_tip_title = ctk.CTkLabel(self.frame_tips, text="📄 TIPS PARA AGREGAR IMPRESORAS", font=("Segoe UI", 12, "bold"), text_color=BORDER_COLOR)
        lbl_tip_title.pack(anchor="w", padx=15, pady=(10, 2))
        
        lbl_tip_text = ctk.CTkLabel(self.frame_tips, text="• MARCA/MODELO: Selecciona de la lista. Si usas una marca genérica, elige 'OTROS'.\n• HORAS DE USO: Sirve para calcular el mantenimiento. Si es nueva, déjalo en 0.", 
                                    font=("Segoe UI", 11), text_color="gray", justify="left")
        lbl_tip_text.pack(anchor="w", padx=15, pady=(0, 10))

        # --- GRID PRINCIPAL (2 Columnas) ---
        self.main_grid = ctk.CTkFrame(self, fg_color="transparent")
        self.main_grid.pack(fill="both", expand=True, padx=20, pady=5)
        self.main_grid.grid_columnconfigure(0, weight=4) # Formulario (40%)
        self.main_grid.grid_columnconfigure(1, weight=6) # Lista (60%)
        self.main_grid.grid_rowconfigure(0, weight=1)

        # --- 2. FORMULARIO (Izquierda) ---
        self.panel_form = ctk.CTkFrame(self.main_grid, fg_color=config.COLOR_TARJETA, corner_radius=15,
                                       border_width=2, border_color=BORDER_COLOR)
        self.panel_form.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)

        ctk.CTkLabel(self.panel_form, text="AGREGAR NUEVA", font=FONT_SUBTITULO, text_color=BORDER_COLOR).pack(anchor="w", padx=20, pady=(20, 15))

        # Nombre
        ctk.CTkLabel(self.panel_form, text="Nombre:", font=FONT_TEXTO, text_color="gray").pack(anchor="w", padx=20)
        self.entry_nombre = ctk.CTkEntry(self.panel_form, placeholder_text="Ej: Ender 3 Pro", height=35, font=FONT_TEXTO, border_color=BORDER_COLOR)
        self.entry_nombre.pack(fill="x", padx=20, pady=(5, 10))

        # Fila Doble: Horas y Consumo
        row_specs = ctk.CTkFrame(self.panel_form, fg_color="transparent")
        row_specs.pack(fill="x", padx=20, pady=5)
        
        # Horas
        frame_horas = ctk.CTkFrame(row_specs, fg_color="transparent")
        frame_horas.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(frame_horas, text="Horas uso:", font=FONT_TEXTO, text_color="gray").pack(anchor="w")
        self.entry_horas = ctk.CTkEntry(frame_horas, placeholder_text="0", height=35, font=FONT_TEXTO, border_color=BORDER_COLOR)
        self.entry_horas.pack(fill="x")

        # Consumo
        frame_kw = ctk.CTkFrame(row_specs, fg_color="transparent")
        frame_kw.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(frame_kw, text="Consumo (kW):", font=FONT_TEXTO, text_color="gray").pack(anchor="w")
        self.entry_kw = ctk.CTkEntry(frame_kw, placeholder_text="0.30", height=35, font=FONT_TEXTO, border_color=BORDER_COLOR)
        self.entry_kw.pack(fill="x")

        # Marca
        ctk.CTkLabel(self.panel_form, text="Marca:", font=FONT_TEXTO, text_color="gray").pack(anchor="w", padx=20, pady=(10, 0))
        self.combo_marca = ctk.CTkComboBox(self.panel_form, values=list(DATOS_IMPRESORAS.keys()), height=35, 
                                           font=FONT_TEXTO, border_color=BORDER_COLOR, button_color=BORDER_COLOR,
                                           command=self.actualizar_modelos)
        self.combo_marca.pack(fill="x", padx=20, pady=5)

        # Modelo
        ctk.CTkLabel(self.panel_form, text="Modelo:", font=FONT_TEXTO, text_color="gray").pack(anchor="w", padx=20, pady=(10, 0))
        self.combo_modelo = ctk.CTkComboBox(self.panel_form, values=["Seleccione Marca"], height=35, 
                                            font=FONT_TEXTO, border_color=BORDER_COLOR, button_color=BORDER_COLOR)
        self.combo_modelo.pack(fill="x", padx=20, pady=5)

        # Botón Guardar
        ctk.CTkButton(self.panel_form, text="GUARDAR IMPRESORA", height=45, 
                      fg_color=BORDER_COLOR, hover_color=config.COLOR_ACENTO_HOVER, 
                      font=FONT_SUBTITULO, text_color="white",
                      command=self.guardar).pack(fill="x", padx=20, pady=30)

        # --- 3. LISTA (Derecha) ---
        self.scroll_lista = ctk.CTkScrollableFrame(self.main_grid, fg_color="transparent")
        self.scroll_lista.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)

        self.actualizar_modelos("Creality") # Init combos
        self.cargar_lista()

    # --- LÓGICA ---

    def actualizar_modelos(self, marca):
        modelos = DATOS_IMPRESORAS.get(marca, ["OTROS"])
        self.combo_modelo.configure(values=modelos)
        self.combo_modelo.set(modelos[0])

    def guardar(self):
        nombre = self.entry_nombre.get()
        marca = self.combo_marca.get()
        modelo = self.combo_modelo.get()
        
        # Validaciones
        if not nombre:
            messagebox.showwarning("Faltan datos", "El nombre es obligatorio.")
            return

        try:
            horas = float(self.entry_horas.get()) if self.entry_horas.get() else 0.0
            kw = float(self.entry_kw.get()) if self.entry_kw.get() else 0.0
        except ValueError:
            messagebox.showerror("Error", "Horas y Consumo deben ser números.")
            return

        # Guardar en DB
        if database.agregar_impresora(nombre, marca, modelo, horas, self.user_id, kw):
            messagebox.showinfo("Éxito", "Impresora guardada correctamente.")
            self.cargar_lista()
            # Limpiar campos
            self.entry_nombre.delete(0, 'end')
            self.entry_horas.delete(0, 'end')
            self.entry_kw.delete(0, 'end')
        else:
            messagebox.showerror("Error", "No se pudo guardar en la base de datos.")

    def cargar_lista(self):
        # Limpiar
        for widget in self.scroll_lista.winfo_children():
            widget.destroy()

        impresoras = database.obtener_impresoras(self.user_id)
        
        if not impresoras:
            ctk.CTkLabel(self.scroll_lista, text="No tienes impresoras registradas.", text_color="gray").pack(pady=20)
            return

        # Border color
        BORDER = getattr(config, 'COLOR_ACENTO', "#00965e")
        if isinstance(BORDER, tuple): BORDER = BORDER[1]

        for imp in impresoras:
            # imp: id, nombre, marca, modelo, estado, horas, power_kw
            iid = imp[0]
            nombre = imp[1]
            detalle = f"{imp[2]} {imp[3]} | {imp[5]:.0f} hs"
            consumo = f"Consumo: {imp[6]} kW" if len(imp) > 6 else "Consumo: 0 kW"

            # Tarjeta
            card = ctk.CTkFrame(self.scroll_lista, fg_color=config.COLOR_TARJETA, corner_radius=10,
                                border_width=1, border_color=BORDER)
            card.pack(fill="x", pady=5)

            # Icono Izquierda
            ctk.CTkLabel(card, text="🖨️", font=("Arial", 30)).pack(side="left", padx=15, pady=10)

            # Info Centro
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, pady=5)
            
            ctk.CTkLabel(info_frame, text=nombre, font=("Segoe UI", 14, "bold"), text_color="white", anchor="w").pack(fill="x")
            ctk.CTkLabel(info_frame, text=detalle, font=("Segoe UI", 12), text_color="gray", anchor="w").pack(fill="x")
            ctk.CTkLabel(info_frame, text=consumo, font=("Segoe UI", 12), text_color="white", anchor="w").pack(fill="x")

            # Botón Eliminar Derecha
            btn_del = ctk.CTkButton(card, text="✕", width=40, height=40, fg_color="transparent", 
                                    hover_color="#333", text_color="gray", font=("Arial", 16),
                                    command=lambda x=iid: self.eliminar(x))
            btn_del.pack(side="right", padx=10)

    def eliminar(self, id_imp):
        if messagebox.askyesno("Confirmar", "¿Eliminar esta impresora?"):
            database.eliminar_impresora(id_imp)
            self.cargar_lista()