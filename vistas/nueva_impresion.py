import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
try:
    from tkcalendar import DateEntry
    TKCAL_AVAILABLE = True
except Exception:
    TKCAL_AVAILABLE = False
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
        
        # LISTA TEMPORAL (Se borra al salir de esta pantalla)
        self.sesion_actual = [] 

        self.mapa_impresoras = {}
        self.mapa_bobinas = {}

        ctk.CTkLabel(self, text="Nueva Impresión", font=("Segoe UI", 24, "bold"), text_color="white").pack(pady=(20, 10))

        # Ayuda
        if config.MODO_PRINCIPIANTE:
            self.mostrar_ayuda()

        # --- FORMULARIO ---
        self.frame_form = ctk.CTkFrame(self, fg_color=config.COLOR_TARJETA, corner_radius=10)
        self.frame_form.pack(fill="x", padx=40, pady=10)

        # Fila 1: Nombre
        ctk.CTkLabel(self.frame_form, text="NOMBRE PIEZA:", font=("Segoe UI", 11, "bold"), text_color=config.COLOR_VERDE_BAMBU).pack(anchor="w", padx=20, pady=(15, 0))
        self.entry_nombre = ctk.CTkEntry(self.frame_form, placeholder_text="Ej: Groot", fg_color="#1a1a1a", border_color="#444", text_color="white")
        self.entry_nombre.pack(fill="x", padx=20, pady=(5, 10))

        # Fila 2: Selectores
        row_selects = ctk.CTkFrame(self.frame_form, fg_color="transparent")
        row_selects.pack(fill="x", padx=15, pady=5)

        self.combo_impresora = ctk.CTkComboBox(row_selects, values=["Cargando..."], width=200, fg_color="#1a1a1a", button_color="#444", text_color="white")
        self.combo_impresora.pack(side="left", padx=5, expand=True)
        self.combo_bobina = ctk.CTkComboBox(row_selects, values=["Cargando..."], width=200, fg_color="#1a1a1a", button_color="#444", text_color="white")
        self.combo_bobina.pack(side="left", padx=5, expand=True)

        # Fila 3: Datos
        row_nums = ctk.CTkFrame(self.frame_form, fg_color="transparent")
        row_nums.pack(fill="x", padx=15, pady=10)

        self.entry_peso = ctk.CTkEntry(row_nums, placeholder_text="Peso (g)", width=100, fg_color="#1a1a1a", border_color="#444", text_color="white")
        self.entry_peso.pack(side="left", padx=5)

        ctk.CTkLabel(row_nums, text="Tiempo:", text_color="gray").pack(side="left", padx=(15, 2))
        self.entry_horas = ctk.CTkEntry(row_nums, placeholder_text="Hs", width=50, fg_color="#1a1a1a", border_color="#444", text_color="white")
        self.entry_horas.pack(side="left", padx=2)
        ctk.CTkLabel(row_nums, text=":", text_color="gray").pack(side="left")
        self.entry_minutos = ctk.CTkEntry(row_nums, placeholder_text="Min", width=50, fg_color="#1a1a1a", border_color="#444", text_color="white")
        self.entry_minutos.pack(side="left", padx=2)

        # Cantidad de piezas
        ctk.CTkLabel(row_nums, text="Cantidad:", text_color="gray").pack(side="left", padx=(12,2))
        self.entry_cantidad = ctk.CTkEntry(row_nums, placeholder_text="1", width=80, fg_color="#1a1a1a", border_color="#444", text_color="white")
        self.entry_cantidad.pack(side="left", padx=2)

        # Fecha de entrega y precio (opcional)
        row_extra = ctk.CTkFrame(self.frame_form, fg_color="transparent")
        row_extra.pack(fill="x", padx=15, pady=(8,0))
        ctk.CTkLabel(row_extra, text="Fecha entrega:", text_color="gray").pack(side="left", padx=(5,2))
        if TKCAL_AVAILABLE:
            self.entry_fecha_entrega = DateEntry(row_extra, date_pattern='yyyy-mm-dd')
            self.entry_fecha_entrega.pack(side="left", padx=4)
        else:
            self.entry_fecha_entrega = ctk.CTkEntry(row_extra, placeholder_text=(datetime.now().strftime('%Y-%m-%d')))
            self.entry_fecha_entrega.pack(side="left", padx=4)

        ctk.CTkLabel(row_extra, text="Precio/u:", text_color="gray").pack(side="left", padx=(12,2))
        self.entry_precio_unit = ctk.CTkEntry(row_extra, placeholder_text="0.0", width=120, fg_color="#1a1a1a", border_color="#444", text_color="white")
        self.entry_precio_unit.pack(side="left", padx=4)

        # Botón
        self.btn_registrar = ctk.CTkButton(self.frame_form, text="REGISTRAR PIEZA", fg_color=config.COLOR_VERDE_BAMBU, hover_color=config.COLOR_VERDE_HOVER, font=("Segoe UI", 13, "bold"), command=self.registrar)
        self.btn_registrar.pack(fill="x", padx=20, pady=20)

        # --- LISTA TEMPORAL ---
        ctk.CTkLabel(self, text="AÑADIDO RECIENTEMENTE (SESIÓN ACTUAL)", font=("Segoe UI", 12, "bold"), text_color="gray").pack(anchor="w", padx=40, pady=(20,0))
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=30, pady=10)

        # Inicialización
        self.cargar_datos_combos()

    def mostrar_ayuda(self):
        frame_ayuda = ctk.CTkFrame(self, fg_color=config.COLOR_FONDO_AYUDA, border_width=1, border_color=config.COLOR_BORDE_AYUDA, corner_radius=6)
        frame_ayuda.pack(fill="x", padx=40, pady=(0, 15))
        ctk.CTkLabel(frame_ayuda, text="ℹ️ REGISTRAR TRABAJO", text_color=config.COLOR_TITULO_AYUDA, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
        texto = "• PESO: Gramos usados según el Slicer.\n• LISTA: Aquí abajo verás solo lo que añadas ahora. Para ver todo ve a 'Historial'."
        ctk.CTkLabel(frame_ayuda, text=texto, text_color="#ccc", justify="left", anchor="w", font=("Segoe UI", 11)).pack(padx=15, pady=(0, 10))

    def cargar_datos_combos(self):
        # (Misma lógica que tenías antes para cargar combos)
        impresoras = database.obtener_impresoras(self.user_id)
        nombres_imp = []
        self.mapa_impresoras = {}
        for imp in impresoras:
            nombre = f"{imp[1]} ({imp[2]})"
            nombres_imp.append(nombre)
            self.mapa_impresoras[nombre] = imp[0]
        
        if nombres_imp:
            self.combo_impresora.configure(values=nombres_imp)
            self.combo_impresora.set(nombres_imp[0])
        else:
            self.combo_impresora.configure(values=["Sin impresoras"])
            self.combo_impresora.set("Sin impresoras")

        bobinas = database.obtener_bobinas(self.user_id)
        nombres_bob = []
        self.mapa_bobinas = {}
        for bob in bobinas:
            nombre = f"{bob[1]} {bob[2]} ({bob[4]}g)"
            nombres_bob.append(nombre)
            self.mapa_bobinas[nombre] = bob[0]
            
        if nombres_bob:
            self.combo_bobina.configure(values=nombres_bob)
            self.combo_bobina.set(nombres_bob[0])
        else:
            self.combo_bobina.configure(values=["Sin bobinas"])
            self.combo_bobina.set("Sin bobinas")

    def registrar(self):
        nombre = self.entry_nombre.get()
        sel_imp = self.combo_impresora.get()
        sel_bob = self.combo_bobina.get()
        peso_str = self.entry_peso.get()
        hs_str = self.entry_horas.get()
        min_str = self.entry_minutos.get()

        if not nombre or not peso_str:
            messagebox.showwarning("Faltan datos", "Nombre y peso obligatorios.")
            return

        id_imp = self.mapa_impresoras.get(sel_imp)
        id_bob = self.mapa_bobinas.get(sel_bob)

        if not id_imp or not id_bob:
            messagebox.showerror("Error", "Selecciona impresora y bobina válidas.")
            return

        if not hs_str: hs_str = "0"
        if not min_str: min_str = "0"
        cantidad_str = self.entry_cantidad.get() or "1"
        fecha_entrega = None
        if TKCAL_AVAILABLE:
            try:
                fecha_entrega = self.entry_fecha_entrega.get_date().strftime('%Y-%m-%d')
            except Exception:
                fecha_entrega = self.entry_fecha_entrega.get()
        else:
            fecha_entrega = self.entry_fecha_entrega.get().strip() or None
        precio_unit_str = self.entry_precio_unit.get() or "0"

        try:
            peso = float(peso_str)
            tiempo_unit = float(hs_str) + (float(min_str) / 60)
            cantidad = int(float(cantidad_str))
            # tiempo total para stock/impresora: acumulamos tiempo total de la corrida
            tiempo_total = tiempo_unit * max(1, cantidad)
            precio_unit = float(precio_unit_str)
            
            exito, mensaje = database.registrar_impresion(nombre, peso, tiempo_unit, id_imp, id_bob, self.user_id, cantidad=cantidad, delivery_date=fecha_entrega, precio_unit=precio_unit)

            if exito:
                # 1. Agregamos a la lista TEMPORAL (mostrar detalle enriquecido)
                nueva_pieza = {
                    "nombre": nombre,
                    "detalle": f"Cant: {cantidad} | Peso/u: {peso}g | Tiempo total: {tiempo_total:.2f} hs | {mensaje} | Entrega: {fecha_entrega or '-'} | Precio/u: {precio_unit:.2f}"
                }
                self.sesion_actual.insert(0, nueva_pieza) # Agregamos al principio
                
                # 2. Refrescamos la lista visual
                self.actualizar_lista_sesion()
                
                # 3. Limpiamos campos
                self.entry_nombre.delete(0, 'end')
                self.entry_peso.delete(0, 'end')
                self.entry_horas.delete(0, 'end')
                self.entry_minutos.delete(0, 'end')
                self.cargar_datos_combos() # Actualizar stock combos
                
                # Mostrar diálogo estilizado en lugar del messagebox estándar
                dlg = ctk.CTkToplevel(self)
                dlg.title("Guardado")
                dlg.geometry("380x140")
                ctk.CTkLabel(dlg, text="Pieza añadida a la sesión.", font=("Segoe UI", 12)).pack(pady=(20,8))
                ctk.CTkLabel(dlg, text=f"{nombre} — {cantidad} unidad(es)", text_color="gray").pack()
                ctk.CTkButton(dlg, text="Aceptar", command=dlg.destroy, fg_color=config.COLOR_VERDE_BAMBU).pack(pady=12)
            else:
                messagebox.showerror("Error", mensaje)

        except ValueError:
            messagebox.showerror("Error", "Números inválidos.")

    def actualizar_lista_sesion(self):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()

        if not self.sesion_actual:
            ctk.CTkLabel(self.scroll_frame, text="No has añadido nada en esta sesión.", text_color="gray").pack(pady=20)
            return

        for pieza in self.sesion_actual:
            card = ctk.CTkFrame(self.scroll_frame, fg_color=config.COLOR_TARJETA, corner_radius=6)
            card.pack(fill="x", pady=5, padx=5)
            
            ctk.CTkLabel(card, text="✨", font=("Segoe UI", 16)).pack(side="left", padx=10)
            
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", padx=5, pady=5)
            ctk.CTkLabel(info, text=pieza['nombre'], font=("Segoe UI", 12, "bold"), text_color="white").pack(anchor="w")
            ctk.CTkLabel(info, text=pieza['detalle'], font=("Segoe UI", 11), text_color="gray").pack(anchor="w")