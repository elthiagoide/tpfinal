import customtkinter as ctk
from tkinter import messagebox
import sys
import os
import config # Importamos para los colores

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database

class VistaBobinas(ctk.CTkFrame):
    def __init__(self, master, user_id, **kwargs):
        # 1. Configuración Inicial (OBLIGATORIO PRIMERO)
        super().__init__(master, **kwargs)
        self.configure(fg_color=config.COLOR_FONDO_APP) # Fondo oscuro general
        self.user_id = user_id

        # Título
        ctk.CTkLabel(self, text="Stock de Filamentos", font=("Segoe UI", 24, "bold"), text_color="white").pack(pady=(20, 10))

        # --- AYUDA (Estilo Dark) ---
        if config.MODO_PRINCIPIANTE:
            self.mostrar_ayuda()

        # --- TARJETA FORMULARIO (Gris Oscuro) ---
        self.frame_add = ctk.CTkFrame(self, fg_color=config.COLOR_TARJETA, corner_radius=10)
        self.frame_add.pack(fill="x", padx=40, pady=10)

        # Subtítulo
        ctk.CTkLabel(self.frame_add, text="AGREGAR NUEVO ROLLO", font=("Segoe UI", 12, "bold"), text_color=config.COLOR_VERDE_BAMBU).pack(anchor="w", padx=20, pady=(15, 5))

        # Fila 1: Marca y Color
        row1 = ctk.CTkFrame(self.frame_add, fg_color="transparent")
        row1.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(row1, text="Marca:", text_color="#ccc").pack(side="left", padx=5)
        self.combo_marca = ctk.CTkComboBox(row1, 
                                           values=["PRINTALOT", "GST", "HELLBOT", "GRILON3", "CREALITY", "ELEGOO", "OTROS"],
                                           command=self.evento_cambio_marca,
                                           width=150, fg_color="#1a1a1a", button_color="#444", text_color="white", dropdown_fg_color="#333")
        self.combo_marca.pack(side="left", padx=5)

        # Campo manual Marca (oculto)
        self.entry_marca_manual = ctk.CTkEntry(row1, placeholder_text="Escriba la marca...", fg_color="#1a1a1a", border_color="#444", text_color="white")

        ctk.CTkLabel(row1, text="Color:", text_color="#ccc").pack(side="left", padx=(15, 5))
        self.entry_color = ctk.CTkEntry(row1, placeholder_text="Ej: Rojo", width=120, fg_color="#1a1a1a", border_color="#444", text_color="white")
        self.entry_color.pack(side="left", padx=5)

        # Fila 2: Material
        row2 = ctk.CTkFrame(self.frame_add, fg_color="transparent")
        row2.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(row2, text="Material:", text_color="#ccc").pack(side="left", padx=5)
        self.combo_material = ctk.CTkComboBox(row2, 
                                              values=["PLA", "PETG", "ABS", "TPU", "OTROS"],
                                              command=self.evento_cambio_material,
                                              width=150, fg_color="#1a1a1a", button_color="#444", text_color="white", dropdown_fg_color="#333")
        self.combo_material.pack(side="left", padx=5)

        # Campo manual Material (oculto)
        self.entry_mat_manual = ctk.CTkEntry(row2, placeholder_text="Escriba el material...", fg_color="#1a1a1a", border_color="#444", text_color="white")

        # Fila 3: Peso y Costo
        row3 = ctk.CTkFrame(self.frame_add, fg_color="transparent")
        row3.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(row3, text="Peso (g):", text_color="#ccc").pack(side="left", padx=5)
        self.entry_peso = ctk.CTkEntry(row3, placeholder_text="1000", width=80, fg_color="#1a1a1a", border_color="#444", text_color="white")
        self.entry_peso.pack(side="left", padx=5)
        
        ctk.CTkLabel(row3, text="Costo ($):", text_color="#ccc").pack(side="left", padx=(15, 5))
        self.entry_costo = ctk.CTkEntry(row3, placeholder_text="0.00", width=80, fg_color="#1a1a1a", border_color="#444", text_color="white")
        self.entry_costo.pack(side="left", padx=5)

        # Botón Guardar
        self.btn_guardar = ctk.CTkButton(self.frame_add, text="GUARDAR BOBINA", fg_color=config.COLOR_VERDE_BAMBU, hover_color=config.COLOR_VERDE_HOVER, font=("Segoe UI", 13, "bold"), command=self.guardar)
        self.btn_guardar.pack(pady=20, padx=20, fill="x")

        # --- LISTA ---
        ctk.CTkLabel(self, text="INVENTARIO", font=("Segoe UI", 12, "bold"), text_color="gray").pack(anchor="w", padx=40, pady=(10,0))
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=30, pady=10)

        self.cargar_lista()

    # --- LÓGICA VISUAL ---

    def mostrar_ayuda(self):
        frame_ayuda = ctk.CTkFrame(self, fg_color=config.COLOR_FONDO_AYUDA, border_width=1, border_color=config.COLOR_BORDE_AYUDA, corner_radius=6)
        frame_ayuda.pack(fill="x", padx=40, pady=(0, 15))
        
        ctk.CTkLabel(frame_ayuda, text="ℹ️ TIPS DE MATERIALES", text_color=config.COLOR_TITULO_AYUDA, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
        
        texto_guia = "• COSTO: Ingresa el valor real del rollo. Vital para calcular ganancias.\n• PESO: Normalmente 1000g. Si es muestra, pon la cantidad real."
        ctk.CTkLabel(frame_ayuda, text=texto_guia, text_color="#cccccc", justify="left", anchor="w", font=("Segoe UI", 11)).pack(padx=15, pady=(0, 10))

    def evento_cambio_marca(self, seleccion):
        if seleccion == "OTROS":
            self.entry_marca_manual.pack(side="left", padx=5, expand=True, fill="x")
        else:
            self.entry_marca_manual.pack_forget()

    def evento_cambio_material(self, seleccion):
        if seleccion == "OTROS":
            self.entry_mat_manual.pack(side="left", padx=5, expand=True, fill="x")
        else:
            self.entry_mat_manual.pack_forget()

    # --- LÓGICA BASE DE DATOS ---

    def guardar(self):
        seleccion_marca = self.combo_marca.get()
        if seleccion_marca == "OTROS":
            marca_final = self.entry_marca_manual.get().strip()
        else:
            marca_final = seleccion_marca

        seleccion_mat = self.combo_material.get()
        if seleccion_mat == "OTROS":
            material_final = self.entry_mat_manual.get().strip()
        else:
            material_final = seleccion_mat

        if not marca_final or not material_final:
            messagebox.showwarning("Atención", "Si eliges 'OTROS', escribe el nombre.")
            return

        col = self.entry_color.get()
        pes = self.entry_peso.get()
        cos = self.entry_costo.get()

        if marca_final and material_final and col and pes and cos:
            try:
                peso_float = float(pes)
                costo_float = float(cos)
                
                if database.agregar_bobina(marca_final, material_final, col, peso_float, costo_float, self.user_id):
                    messagebox.showinfo("Éxito", "Bobina guardada")
                    
                    # Resetear
                    self.entry_color.delete(0, 'end')
                    self.entry_peso.delete(0, 'end')
                    self.entry_costo.delete(0, 'end')
                    self.entry_marca_manual.delete(0, 'end')
                    self.entry_mat_manual.delete(0, 'end')
                    self.combo_marca.set("PRINTALOT")
                    self.evento_cambio_marca("PRINTALOT")
                    self.combo_material.set("PLA")
                    self.evento_cambio_material("PLA")
                    
                    self.cargar_lista()
                else:
                    messagebox.showerror("Error", "Error en BD")
            except ValueError:
                messagebox.showerror("Error", "Peso y Costo deben ser números")
        else:
            messagebox.showwarning("Atención", "Completa todos los campos")

    def cargar_lista(self):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()

        lista = database.obtener_bobinas(self.user_id)
        if not lista:
             ctk.CTkLabel(self.scroll_frame, text="No hay bobinas en stock.", text_color="gray").pack(pady=20)
             return

        for bob in lista:
            id_bob, marca, mat, col, peso, cos = bob[0], bob[1], bob[2], bob[3], bob[4], bob[5]
            
            # Tarjeta Estilo Dark
            card = ctk.CTkFrame(self.scroll_frame, fg_color=config.COLOR_TARJETA, corner_radius=8)
            card.pack(fill="x", pady=5, padx=5)
            
            # Icono
            ctk.CTkLabel(card, text="🧵", font=("Segoe UI", 20)).pack(side="left", padx=15)

            # Info
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", padx=5, pady=10)

            texto_main = f"{marca} {mat} {col}"
            ctk.CTkLabel(info_frame, text=texto_main, font=("Segoe UI", 14, "bold"), text_color="white").pack(anchor="w")
            
            texto_sub = f"⚖️ {peso}g  |  💲${cos}"
            ctk.CTkLabel(info_frame, text=texto_sub, font=("Segoe UI", 12), text_color="gray").pack(anchor="w")
            
            # Botón Eliminar
            ctk.CTkButton(card, text="✕", width=30, height=30, fg_color="transparent", text_color="gray", hover_color=config.COLOR_ROJO,
                          command=lambda i=id_bob: self.eliminar(i)).pack(side="right", padx=15)

    def eliminar(self, id_bobina):
        if messagebox.askyesno("Confirmar", "¿Borrar bobina?"):
            database.eliminar_bobina(id_bobina)
            self.cargar_lista()