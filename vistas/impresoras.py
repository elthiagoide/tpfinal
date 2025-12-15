import customtkinter as ctk
from tkinter import messagebox
import sys
import os
import config # Importamos para los colores

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database

# --- DICCIONARIO DE MARCAS Y MODELOS ---
DATOS_IMPRESORAS = {
    "Creality": ["Ender 3", "Ender 3 V2", "Ender 5", "K1", "CR-10", "OTROS"],
    "Bambu Lab": ["X1 Carbon", "P1S", "P1P", "A1 Mini", "A1", "OTROS"],
    "Anycubic": ["Kobra 2", "Vyper", "Photon Mono", "Mega X", "Kobra Neo", "OTROS"],
    "Prusa": ["MK3S+", "MK4", "Mini+", "XL", "SL1S", "OTROS"],
    "Hellbot": ["Magna 2", "Magna SE", "Hidra", "Apolo", "Magna 1", "OTROS"],
    "OTROS": ["OTROS"] 
}

class VistaImpresoras(ctk.CTkFrame):
    def __init__(self, master, user_id, **kwargs):
        # 1. Configuración Inicial
        super().__init__(master, **kwargs)
        self.configure(fg_color=config.COLOR_FONDO_APP) # Fondo Oscuro General
        self.user_id = user_id
        
        # Título
        ctk.CTkLabel(self, text="Mis Impresoras", font=("Segoe UI", 24, "bold"), text_color="white").pack(pady=(20, 10))

        # --- CAJA DE AYUDA (Estilo Dark) ---
        if config.MODO_PRINCIPIANTE:
            self.mostrar_ayuda()

        # --- TARJETA DE FORMULARIO (Gris Oscuro) ---
        self.frame_add = ctk.CTkFrame(self, fg_color=config.COLOR_TARJETA, corner_radius=10)
        self.frame_add.pack(fill="x", padx=40, pady=10)

        # Subtítulo del formulario
        ctk.CTkLabel(self.frame_add, text="AGREGAR NUEVA", font=("Segoe UI", 12, "bold"), text_color=config.COLOR_VERDE_BAMBU).pack(anchor="w", padx=20, pady=(15, 5))

        # Fila 1: Nombre y Horas
        row1 = ctk.CTkFrame(self.frame_add, fg_color="transparent")
        row1.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(row1, text="Nombre:", text_color="#ccc").pack(side="left", padx=5)
        self.entry_nombre = ctk.CTkEntry(row1, placeholder_text="Ej: Impresora 1", fg_color="#1a1a1a", border_color="#444", text_color="white")
        self.entry_nombre.pack(side="left", padx=5, expand=True, fill="x")
        
        # Nombre por defecto
        cantidad = database.contar_impresoras(self.user_id)
        self.entry_nombre.insert(0, f"Impresora {cantidad + 1}")

        ctk.CTkLabel(row1, text="Horas uso:", text_color="#ccc").pack(side="left", padx=(15, 5))
        self.entry_horas = ctk.CTkEntry(row1, placeholder_text="0", width=80, fg_color="#1a1a1a", border_color="#444", text_color="white")
        self.entry_horas.pack(side="left", padx=5)
        self.entry_horas.insert(0, "0") 

        # Fila 2: Marca y Modelo
        row2 = ctk.CTkFrame(self.frame_add, fg_color="transparent")
        row2.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(row2, text="Marca:", text_color="#ccc").pack(side="left", padx=5)
        self.combo_marca = ctk.CTkComboBox(row2, values=list(DATOS_IMPRESORAS.keys()), command=self.evento_cambio_marca, width=150, fg_color="#1a1a1a", button_color="#444", text_color="white", dropdown_fg_color="#333")
        self.combo_marca.pack(side="left", padx=5)
        
        ctk.CTkLabel(row2, text="Modelo:", text_color="#ccc").pack(side="left", padx=(15,5))
        self.combo_modelo = ctk.CTkComboBox(row2, values=["Seleccione Marca"], command=self.evento_cambio_modelo, width=150, fg_color="#1a1a1a", button_color="#444", text_color="white", dropdown_fg_color="#333")
        self.combo_modelo.pack(side="left", padx=5)

        # Fila 3: Campos Manuales (Ocultos por defecto)
        self.row_manual = ctk.CTkFrame(self.frame_add, fg_color="transparent")
        self.entry_marca_manual = ctk.CTkEntry(self.row_manual, placeholder_text="Escriba la Marca", fg_color="#1a1a1a", border_color="#444", text_color="white")
        self.entry_modelo_manual = ctk.CTkEntry(self.row_manual, placeholder_text="Escriba el Modelo", fg_color="#1a1a1a", border_color="#444", text_color="white")

        # Botón Guardar
        self.btn_guardar = ctk.CTkButton(self.frame_add, text="GUARDAR IMPRESORA", fg_color=config.COLOR_VERDE_BAMBU, hover_color=config.COLOR_VERDE_HOVER, font=("Segoe UI", 13, "bold"), command=self.guardar_impresora)
        self.btn_guardar.pack(pady=20, padx=20, fill="x")

        # --- LISTA DE IMPRESORAS ---
        ctk.CTkLabel(self, text="LISTADO", font=("Segoe UI", 12, "bold"), text_color="gray").pack(anchor="w", padx=40, pady=(10,0))
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent") # Transparente para ver el fondo negro
        self.scroll_frame.pack(fill="both", expand=True, padx=30, pady=10)

        # Inicialización de datos
        self.cargar_lista()
        self.evento_cambio_marca(self.combo_marca.get())

    # --- FUNCIONES DE LÓGICA ---

    def mostrar_ayuda(self):
        frame_ayuda = ctk.CTkFrame(self, fg_color=config.COLOR_FONDO_AYUDA, border_width=1, border_color=config.COLOR_BORDE_AYUDA, corner_radius=6)
        frame_ayuda.pack(fill="x", padx=40, pady=(0, 15))
        
        ctk.CTkLabel(frame_ayuda, text="ℹ️ TIPS PARA AGREGAR IMPRESORAS", text_color=config.COLOR_TITULO_AYUDA, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
        
        texto_guia = "• MARCA/MODELO: Selecciona de la lista. Si usas una marca genérica, elige 'OTROS'.\n• HORAS DE USO: Sirve para calcular el mantenimiento. Si es nueva, déjalo en 0."
        ctk.CTkLabel(frame_ayuda, text=texto_guia, text_color="#cccccc", justify="left", anchor="w", font=("Segoe UI", 11)).pack(padx=15, pady=(0, 10))

    def evento_cambio_marca(self, marca_seleccionada):
        modelos = DATOS_IMPRESORAS.get(marca_seleccionada, ["OTROS"])
        self.combo_modelo.configure(values=modelos)
        self.combo_modelo.set(modelos[0])
        self.chequear_manuales()

    def evento_cambio_modelo(self, modelo_seleccionado):
        self.chequear_manuales()

    def chequear_manuales(self):
        self.row_manual.pack_forget()
        self.entry_marca_manual.pack_forget()
        self.entry_modelo_manual.pack_forget()

        marca = self.combo_marca.get()
        modelo = self.combo_modelo.get()
        mostrar_fila = False

        if marca == "OTROS":
            self.entry_marca_manual.pack(side="left", padx=5, expand=True, fill="x")
            self.entry_modelo_manual.pack(side="left", padx=5, expand=True, fill="x")
            mostrar_fila = True
        elif modelo == "OTROS":
            self.entry_modelo_manual.pack(side="left", padx=5, expand=True, fill="x")
            mostrar_fila = True

        if mostrar_fila:
            self.row_manual.pack(fill="x", padx=15, pady=5, after=self.frame_add.winfo_children()[2]) # Indice ajustado

    def guardar_impresora(self):
        nombre = self.entry_nombre.get()
        horas_str = self.entry_horas.get()
        
        seleccion_marca = self.combo_marca.get()
        seleccion_modelo = self.combo_modelo.get()
        
        marca_final = seleccion_marca
        modelo_final = seleccion_modelo

        if seleccion_marca == "OTROS":
            marca_final = self.entry_marca_manual.get()
            modelo_final = self.entry_modelo_manual.get()
        elif seleccion_modelo == "OTROS":
            modelo_final = self.entry_modelo_manual.get()

        if not nombre or not marca_final or not modelo_final:
            messagebox.showwarning("Atención", "Completa todos los campos")
            return

        if not horas_str: horas_str = "0"

        try:
            horas = float(horas_str)
            if database.agregar_impresora(nombre, marca_final, modelo_final, horas, self.user_id):
                messagebox.showinfo("Éxito", "Impresora guardada")
                self.cargar_lista()
                
                # Reset
                cantidad = database.contar_impresoras(self.user_id)
                self.entry_nombre.delete(0, 'end')
                self.entry_nombre.insert(0, f"Impresora {cantidad + 1}")
                self.entry_horas.delete(0, 'end')
                self.entry_horas.insert(0, "0")
                self.entry_marca_manual.delete(0, 'end')
                self.entry_modelo_manual.delete(0, 'end')
                self.combo_marca.set("Creality")
                self.evento_cambio_marca("Creality")
            else:
                messagebox.showerror("Error", "No se pudo guardar")
        except ValueError:
            messagebox.showerror("Error", "Las horas deben ser un número")

    def cargar_lista(self):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()

        lista = database.obtener_impresoras(self.user_id)
        if not lista:
             ctk.CTkLabel(self.scroll_frame, text="No tienes impresoras registradas.", text_color="gray").pack(pady=20)
             return

        for imp in lista:
            id_imp, nombre, marca, modelo, estado, horas = imp[0], imp[1], imp[2], imp[3], imp[4], imp[5]

            # TARJETA OSCURA (Estilo Bambu)
            card = ctk.CTkFrame(self.scroll_frame, fg_color=config.COLOR_TARJETA, corner_radius=8, border_width=1, border_color="#333")
            card.pack(fill="x", pady=5, padx=5)

            # Icono
            ctk.CTkLabel(card, text="🖨️", font=("Segoe UI", 20)).pack(side="left", padx=15)
            
            # Textos
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", padx=5, pady=10)
            
            ctk.CTkLabel(info_frame, text=nombre, font=("Segoe UI", 14, "bold"), text_color="white").pack(anchor="w")
            ctk.CTkLabel(info_frame, text=f"{marca} {modelo} | {horas} hs", font=("Segoe UI", 12), text_color="gray").pack(anchor="w")

            # Botón Eliminar
            ctk.CTkButton(card, text="✕", width=30, height=30, fg_color="transparent", text_color="gray", hover_color=config.COLOR_ROJO,
                          command=lambda id=id_imp: self.evento_eliminar(id)).pack(side="right", padx=15)

    def evento_eliminar(self, id_impresora):
        if messagebox.askyesno("Confirmar", "¿Borrar impresora?"):
            database.eliminar_impresora(id_impresora)
            self.cargar_lista()
            
            cantidad = database.contar_impresoras(self.user_id)
            self.entry_nombre.delete(0, 'end')
            self.entry_nombre.insert(0, f"Impresora {cantidad + 1}")