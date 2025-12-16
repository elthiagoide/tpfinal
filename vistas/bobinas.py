import customtkinter as ctk
from tkinter import messagebox
import sys
import os
import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database

# Materiales comunes para el dropdown
MATERIALES_COMUNES = ["PLA", "PLA+", "PETG", "ABS", "ASA", "TPU", "NYLON", "RESINA", "OTROS"]

class VistaBobinas(ctk.CTkFrame):
    def __init__(self, master, user_id, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=config.COLOR_FONDO_APP)
        self.user_id = user_id
        
        # Fuentes y colores (defensivo)
        FONT_TITULO = getattr(config, 'FONT_TITULO', ("Segoe UI", 24, "bold"))
        FONT_SUBTITULO = getattr(config, 'FONT_SUBTITULO', ("Segoe UI", 16, "bold"))
        FONT_TEXTO = getattr(config, 'FONT_TEXTO', ("Segoe UI", 13, "bold"))
        BORDER_COLOR = getattr(config, 'COLOR_ACENTO', "#00965e")
        if isinstance(BORDER_COLOR, tuple): BORDER_COLOR = BORDER_COLOR[1]

        # Título Principal
        ctk.CTkLabel(self, text="Mis Filamentos", font=FONT_TITULO, text_color=config.COLOR_TEXTO_BLANCO).pack(pady=(10, 5))

        # --- 1. TIPS (Panel Superior) ---
        self.frame_tips = ctk.CTkFrame(self, fg_color="transparent", border_width=1, border_color=BORDER_COLOR, corner_radius=10)
        self.frame_tips.pack(fill="x", padx=20, pady=10)
        
        lbl_tip_title = ctk.CTkLabel(self.frame_tips, text="🧵 TIPS DE GESTIÓN DE STOCK", font=("Segoe UI", 12, "bold"), text_color=BORDER_COLOR)
        lbl_tip_title.pack(anchor="w", padx=15, pady=(10, 2))
        
        lbl_tip_text = ctk.CTkLabel(self.frame_tips, text="• PESO ACTUAL: Ingresa el peso neto (filamento sin carrete). Un rollo nuevo suele tener 1000g.\n• COSTO: Precio de reposición del rollo completo. Se usará para calcular costos por gramo.", 
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

        ctk.CTkLabel(self.panel_form, text="AGREGAR NUEVO", font=FONT_SUBTITULO, text_color=BORDER_COLOR).pack(anchor="w", padx=20, pady=(20, 15))

        # Marca
        ctk.CTkLabel(self.panel_form, text="Marca:", font=FONT_TEXTO, text_color="gray").pack(anchor="w", padx=20)
        self.entry_marca = ctk.CTkEntry(self.panel_form, placeholder_text="Ej: Grilon3", height=35, font=FONT_TEXTO, border_color=BORDER_COLOR)
        self.entry_marca.pack(fill="x", padx=20, pady=(5, 10))

        # Material (Dropdown)
        ctk.CTkLabel(self.panel_form, text="Material:", font=FONT_TEXTO, text_color="gray").pack(anchor="w", padx=20)
        self.combo_material = ctk.CTkComboBox(self.panel_form, values=MATERIALES_COMUNES, height=35, 
                                              font=FONT_TEXTO, border_color=BORDER_COLOR, button_color=BORDER_COLOR)
        self.combo_material.set("PLA")
        self.combo_material.pack(fill="x", padx=20, pady=(5, 10))

        # Color
        ctk.CTkLabel(self.panel_form, text="Color:", font=FONT_TEXTO, text_color="gray").pack(anchor="w", padx=20)
        self.entry_color = ctk.CTkEntry(self.panel_form, placeholder_text="Ej: Rojo Fuego", height=35, font=FONT_TEXTO, border_color=BORDER_COLOR)
        self.entry_color.pack(fill="x", padx=20, pady=(5, 10))

        # Fila Doble: Peso y Costo
        row_specs = ctk.CTkFrame(self.panel_form, fg_color="transparent")
        row_specs.pack(fill="x", padx=20, pady=5)
        
        # Peso
        frame_peso = ctk.CTkFrame(row_specs, fg_color="transparent")
        frame_peso.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(frame_peso, text="Peso (g):", font=FONT_TEXTO, text_color="gray").pack(anchor="w")
        self.entry_peso = ctk.CTkEntry(frame_peso, placeholder_text="1000", height=35, font=FONT_TEXTO, border_color=BORDER_COLOR)
        self.entry_peso.pack(fill="x")

        # Costo
        frame_costo = ctk.CTkFrame(row_specs, fg_color="transparent")
        frame_costo.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(frame_costo, text="Costo ($):", font=FONT_TEXTO, text_color="gray").pack(anchor="w")
        self.entry_costo = ctk.CTkEntry(frame_costo, placeholder_text="20000", height=35, font=FONT_TEXTO, border_color=BORDER_COLOR)
        self.entry_costo.pack(fill="x")

        # Botón Guardar
        ctk.CTkButton(self.panel_form, text="GUARDAR FILAMENTO", height=45, 
                      fg_color=BORDER_COLOR, hover_color=config.COLOR_ACENTO_HOVER, 
                      font=FONT_SUBTITULO, text_color="white",
                      command=self.guardar).pack(fill="x", padx=20, pady=30)

        # --- 3. LISTA (Derecha) ---
        self.scroll_lista = ctk.CTkScrollableFrame(self.main_grid, fg_color="transparent")
        self.scroll_lista.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)

        self.cargar_lista()

    # --- LÓGICA ---

    def guardar(self):
        marca = self.entry_marca.get()
        mat = self.combo_material.get()
        col = self.entry_color.get()
        
        # Validaciones
        if not marca or not col:
            messagebox.showwarning("Faltan datos", "Marca y Color son obligatorios.")
            return

        try:
            peso = float(self.entry_peso.get()) if self.entry_peso.get() else 1000.0
            costo = float(self.entry_costo.get()) if self.entry_costo.get() else 0.0
        except ValueError:
            messagebox.showerror("Error", "Peso y Costo deben ser números.")
            return

        # Guardar en DB
        if database.agregar_bobina(marca, mat, col, peso, costo, self.user_id):
            messagebox.showinfo("Éxito", "Filamento agregado correctamente.")
            self.cargar_lista()
            # Limpiar campos
            self.entry_marca.delete(0, 'end')
            self.entry_color.delete(0, 'end')
            self.entry_peso.delete(0, 'end')
            self.entry_peso.insert(0, "1000")
            self.entry_costo.delete(0, 'end')
        else:
            messagebox.showerror("Error", "No se pudo guardar en la base de datos.")

    def cargar_lista(self):
        # Limpiar
        for widget in self.scroll_lista.winfo_children():
            widget.destroy()

        bobinas = database.obtener_bobinas(self.user_id)
        
        if not bobinas:
            ctk.CTkLabel(self.scroll_lista, text="No tienes filamentos registrados.", text_color="gray").pack(pady=20)
            return

        # Border color
        BORDER = getattr(config, 'COLOR_ACENTO', "#00965e")
        if isinstance(BORDER, tuple): BORDER = BORDER[1]

        for bob in bobinas:
            # bob: id, marca, material, color, peso_actual, costo, user_id
            bid = bob[0]
            titulo = f"{bob[1]} {bob[2]} - {bob[3]}"
            detalle = f"Stock: {bob[4]:.0f}g | Costo: ${bob[5]:.0f}"
            
            # Tarjeta
            card = ctk.CTkFrame(self.scroll_lista, fg_color=config.COLOR_TARJETA, corner_radius=10,
                                border_width=1, border_color=BORDER)
            card.pack(fill="x", pady=5)

            # Icono Izquierda (Rollo)
            ctk.CTkLabel(card, text="🧵", font=("Arial", 26)).pack(side="left", padx=15, pady=10)

            # Info Centro
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, pady=5)
            
            ctk.CTkLabel(info_frame, text=titulo, font=("Segoe UI", 14, "bold"), text_color="white", anchor="w").pack(fill="x")
            ctk.CTkLabel(info_frame, text=detalle, font=("Segoe UI", 12), text_color="gray", anchor="w").pack(fill="x")

            # Botón Eliminar Derecha
            btn_del = ctk.CTkButton(card, text="✕", width=35, height=35, fg_color="transparent", 
                                    hover_color="#333", text_color="gray", font=("Arial", 16),
                                    command=lambda x=bid: self.eliminar(x))
            btn_del.pack(side="right", padx=10)

    def eliminar(self, id_bob):
        if messagebox.askyesno("Confirmar", "¿Eliminar este filamento del stock?"):
            database.eliminar_bobina(id_bob)
            self.cargar_lista()