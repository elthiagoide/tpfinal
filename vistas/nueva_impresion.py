import customtkinter as ctk
from tkinter import messagebox
import sys
import os
import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database

class VistaNuevaImpresion(ctk.CTkFrame):
    def __init__(self, master, user_id, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=config.COLOR_FONDO_APP)
        self.user_id = user_id
        self.filas_materiales = [] 

        # Título Principal
        ctk.CTkLabel(self, text="Nueva Impresión", font=config.FONT_TITULO, text_color=config.COLOR_TEXTO_BLANCO).pack(pady=(15, 10))

        # --- CONTENEDOR PRINCIPAL (GRID 2 COLUMNAS) ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=5)
        
        self.main_container.grid_columnconfigure(0, weight=1) # Izquierda 50%
        self.main_container.grid_columnconfigure(1, weight=1) # Derecha 50%
        self.main_container.grid_rowconfigure(0, weight=1)    # Alto expandible

        # ============================================================
        # PANEL IZQUIERDO: INFORMACIÓN DEL TRABAJO
        # ============================================================
        self.panel_info = ctk.CTkFrame(self.main_container, fg_color=config.COLOR_TARJETA, corner_radius=15,
                                       border_width=2, border_color=config.COLOR_ACENTO)
        self.panel_info.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)

        # Título Panel Info
        ctk.CTkLabel(self.panel_info, text="Información del Trabajo", font=config.FONT_SUBTITULO, text_color="white").pack(anchor="w", padx=20, pady=(20, 15))

        # Campo 1: Nombre (Con Icono)
        ctk.CTkLabel(self.panel_info, text="👤 Nombre del Archivo / Pieza", font=config.FONT_BOTON, text_color=config.COLOR_TEXTO_GRIS).pack(anchor="w", padx=20)
        self.entry_nombre = ctk.CTkEntry(self.panel_info, placeholder_text="Ej: Casco_V1", height=40, 
                                         font=config.FONT_TEXTO, border_color=config.COLOR_ACENTO)
        self.entry_nombre.pack(fill="x", padx=20, pady=(5, 15))

        # Campo 2: Impresora
        ctk.CTkLabel(self.panel_info, text="🖨️ Impresora Utilizada", font=config.FONT_BOTON, text_color=config.COLOR_TEXTO_GRIS).pack(anchor="w", padx=20)
        self.combo_impresora = ctk.CTkComboBox(self.panel_info, values=["Cargando..."], height=40, 
                                               font=config.FONT_TEXTO, dropdown_font=config.FONT_TEXTO, border_color=config.COLOR_ACENTO, button_color=config.COLOR_ACENTO)
        self.combo_impresora.pack(fill="x", padx=20, pady=(5, 15))

        # Campo 3: Tiempo
        ctk.CTkLabel(self.panel_info, text="🕒 Tiempo de Impresión (Horas)", font=config.FONT_BOTON, text_color=config.COLOR_TEXTO_GRIS).pack(anchor="w", padx=20)
        self.entry_tiempo = ctk.CTkEntry(self.panel_info, placeholder_text="Ej: 4.5", height=40, 
                                         font=config.FONT_TEXTO, border_color=config.COLOR_ACENTO)
        self.entry_tiempo.pack(fill="x", padx=20, pady=(5, 20))


        # ============================================================
        # PANEL DERECHO: MATERIALES UTILIZADOS
        # ============================================================
        self.panel_mat = ctk.CTkFrame(self.main_container, fg_color=config.COLOR_TARJETA, corner_radius=15,
                                      border_width=2, border_color=config.COLOR_ACENTO)
        self.panel_mat.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)

        ctk.CTkLabel(self.panel_mat, text="Materiales Utilizados", font=config.FONT_SUBTITULO, text_color="white").pack(anchor="w", padx=20, pady=(20, 15))

        # Área Scrollable para las filas
        self.scroll_materiales = ctk.CTkScrollableFrame(self.panel_mat, fg_color="transparent")
        self.scroll_materiales.pack(fill="both", expand=True, padx=10, pady=5)

        # Botón "+ Agregar otro color" (Estilo Outline)
        self.btn_add_color = ctk.CTkButton(self.panel_mat, text="+ Agregar otro color", 
                                           fg_color="transparent", border_width=1, border_color=config.COLOR_ACENTO, 
                                           text_color=config.COLOR_TEXTO_BLANCO, hover_color=config.COLOR_HOVER_BTN,
                                           command=self.agregar_fila_material)
        self.btn_add_color.pack(pady=20)


        # ============================================================
        # BOTÓN GIGANTE "REGISTRAR" (Abajo del todo)
        # ============================================================
        self.btn_save = ctk.CTkButton(self, text="REGISTRAR TRABAJO", height=55, 
                                      fg_color=config.COLOR_ACENTO, hover_color=config.COLOR_ACENTO_HOVER, 
                                      font=("Segoe UI", 16, "bold"), text_color="white",
                                      command=self.guardar)
        self.btn_save.pack(fill="x", padx=20, pady=(0, 20))

        # Cargar datos iniciales
        self.cargar_datos_db()
        self.agregar_fila_material() # Una fila por defecto

    # --- LÓGICA (IGUAL QUE ANTES) ---

    def cargar_datos_db(self):
        imps = database.obtener_impresoras(self.user_id)
        self.mapa_impresoras = {f"{i[1]} ({i[2]})": i[0] for i in imps}
        if self.mapa_impresoras:
            self.combo_impresora.configure(values=list(self.mapa_impresoras.keys()))
            self.combo_impresora.set(list(self.mapa_impresoras.keys())[0])
        else:
            self.combo_impresora.configure(values=["Sin Impresoras"])

        bobs = database.obtener_bobinas(self.user_id)
        self.lista_nombres_bobinas = [f"{b[1]} {b[2]} - {b[3]}" for b in bobs]
        self.mapa_bobinas = {f"{b[1]} {b[2]} - {b[3]}": b[0] for b in bobs}

    def agregar_fila_material(self):
        # Fila visual
        row_frame = ctk.CTkFrame(self.scroll_materiales, fg_color="transparent")
        row_frame.pack(fill="x", pady=5)

        # Combo
        combo = ctk.CTkComboBox(row_frame, values=self.lista_nombres_bobinas if self.lista_nombres_bobinas else ["Sin Filamento"], 
                                width=200, height=35, font=config.FONT_TEXTO, border_color=config.COLOR_ACENTO, button_color=config.COLOR_ACENTO)
        combo.pack(side="left", padx=(0, 10), fill="x", expand=True)
        if self.lista_nombres_bobinas: combo.set(self.lista_nombres_bobinas[0])

        # Entry Gramos
        entry_g = ctk.CTkEntry(row_frame, placeholder_text="Grs", width=70, height=35, 
                               font=config.FONT_TEXTO, border_color=config.COLOR_ACENTO)
        entry_g.pack(side="left", padx=5)
        
        # Botón X
        btn_del = ctk.CTkButton(row_frame, text="✕", width=30, height=35, fg_color="transparent", 
                                text_color=config.COLOR_ROJO, hover_color=config.COLOR_HOVER_BTN,
                                command=lambda f=row_frame: self.eliminar_fila(f))
        btn_del.pack(side="right", padx=5)

        self.filas_materiales.append({"frame": row_frame, "combo": combo, "entry": entry_g})

    def eliminar_fila(self, frame_borrar):
        if len(self.filas_materiales) <= 1: return
        frame_borrar.destroy()
        self.filas_materiales = [f for f in self.filas_materiales if f["frame"] != frame_borrar]

    def guardar(self):
        nombre = self.entry_nombre.get()
        t_str = self.entry_tiempo.get()
        imp_name = self.combo_impresora.get()

        if not nombre or not t_str:
            messagebox.showwarning("Faltan Datos", "Completa nombre y tiempo.")
            return

        try: tiempo = float(t_str)
        except:
            messagebox.showerror("Error", "Tiempo debe ser número")
            return

        lista_final = []
        for fila in self.filas_materiales:
            nom_bob = fila["combo"].get()
            g_str = fila["entry"].get()
            if nom_bob == "Sin Filamento": continue
            try:
                g = float(g_str)
                id_bob = self.mapa_bobinas.get(nom_bob)
                if id_bob: lista_final.append((id_bob, g))
            except:
                messagebox.showerror("Error", "El peso debe ser número")
                return

        if not lista_final:
            messagebox.showwarning("Error", "Agrega al menos un material con peso")
            return

        id_imp = self.mapa_impresoras.get(imp_name)
        exito, msg = database.registrar_impresion(nombre, tiempo, lista_final, id_imp, self.user_id)
        
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.entry_nombre.delete(0, 'end')
            self.entry_tiempo.delete(0, 'end')
            for f in self.filas_materiales: f["frame"].destroy()
            self.filas_materiales = []
            self.agregar_fila_material()
        else:
            messagebox.showerror("Error", msg)