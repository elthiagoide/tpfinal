import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
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

class VistaImpresiones(ctk.CTkFrame):
    def __init__(self, master, user_id, **kwargs):
        
        super().__init__(master, **kwargs)
        self.user_id = user_id

        self.mapa_impresoras = {}
        self.mapa_bobinas = {}

        self.label = ctk.CTkLabel(self, text="Nueva Impresión", font=("Roboto", 24, "bold"))
        self.label.pack(pady=(20, 10))

        # --- PANEL DE CARGA (FORMULARIO) ---
        self.frame_form = ctk.CTkFrame(self)
        self.frame_form.pack(fill="x", padx=20, pady=10)

        # Fila 1: Nombre de la pieza
        self.entry_nombre = ctk.CTkEntry(self.frame_form, placeholder_text="Nombre de la pieza (Ej: Groot)")
        self.entry_nombre.pack(fill="x", padx=10, pady=10)

        # Fila 2: Selectores (Impresora y Bobina)
        row_selects = ctk.CTkFrame(self.frame_form, fg_color="transparent")
        row_selects.pack(fill="x", padx=5, pady=5)

        self.combo_impresora = ctk.CTkComboBox(row_selects, values=["Cargando..."], width=200)
        self.combo_impresora.pack(side="left", padx=5, expand=True)
        self.combo_impresora.set("Seleccionar Impresora")

        self.combo_bobina = ctk.CTkComboBox(row_selects, values=["Cargando..."], width=200)
        self.combo_bobina.pack(side="left", padx=5, expand=True)
        self.combo_bobina.set("Seleccionar Filamento")

        # Fila 3: Datos numéricos (Peso y Tiempo dividido)
        row_nums = ctk.CTkFrame(self.frame_form, fg_color="transparent")
        row_nums.pack(fill="x", padx=5, pady=5)

        # Entrada de PESO
        self.entry_peso = ctk.CTkEntry(row_nums, placeholder_text="Peso usado (g)", width=120)
        self.entry_peso.pack(side="left", padx=5)

        # --- CAMBIO AQUÍ: DOS ENTRADAS PARA EL TIEMPO ---
        
        # Etiqueta decorativa (opcional, o usamos placeholders)
        ctk.CTkLabel(row_nums, text="Tiempo:").pack(side="left", padx=(10, 2))

        self.entry_horas = ctk.CTkEntry(row_nums, placeholder_text="Hs", width=50)
        self.entry_horas.pack(side="left", padx=2)
        
        ctk.CTkLabel(row_nums, text=":").pack(side="left")

        self.entry_minutos = ctk.CTkEntry(row_nums, placeholder_text="Min", width=50)
        self.entry_minutos.pack(side="left", padx=2)

        ctk.CTkLabel(row_nums, text="Cantidad:").pack(side="left", padx=(10,2))
        self.entry_cantidad = ctk.CTkEntry(row_nums, placeholder_text="1", width=80)
        self.entry_cantidad.pack(side="left", padx=2)

        # Botón Registrar
        self.btn_registrar = ctk.CTkButton(self.frame_form, text="✅ Registrar Impresión", 
                                           fg_color="green", height=40,
                                           command=self.registrar)
        self.btn_registrar.pack(fill="x", padx=10, pady=15)

        # --- SEPARADOR ---
        ctk.CTkLabel(self, text="Historial de Trabajos", font=("Roboto", 18, "bold")).pack(pady=(20, 5))

        # --- LISTA HISTORIAL ---
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Inicialización
        self.cargar_datos_combos()
        self.cargar_historial()
        if config.MODO_PRINCIPIANTE:
            self.mostrar_ayuda()
    def mostrar_ayuda(self):
        frame_ayuda = ctk.CTkFrame(self, fg_color=config.COLOR_FONDO_AYUDA, border_width=1, border_color=config.COLOR_BORDE_AYUDA, corner_radius=6)
        frame_ayuda.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(frame_ayuda, text="ℹ️ CÁLCULO DE COSTOS", text_color=config.COLOR_TITULO_AYUDA, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
        
        texto_guia = (
            "• PESO: Usa el valor que te da tu laminador (Cura/BambuStudio) en gramos.\n"
            "• TIEMPO: El sistema descontará material y sumará desgaste a la máquina automáticamente."
        )
        ctk.CTkLabel(frame_ayuda, text=texto_guia, text_color="#cccccc", justify="left", anchor="w", font=("Segoe UI", 11)).pack(padx=15, pady=(0, 10))
    def cargar_datos_combos(self):
        # 1. Impresoras
        impresoras = database.obtener_impresoras(self.user_id)
        nombres_imp = []
        self.mapa_impresoras = {}
        for imp in impresoras:
            nombre_str = f"{imp[1]} ({imp[2]})"
            nombres_imp.append(nombre_str)
            self.mapa_impresoras[nombre_str] = imp[0]
        
        if nombres_imp:
            self.combo_impresora.configure(values=nombres_imp)
            self.combo_impresora.set(nombres_imp[0])
        else:
            self.combo_impresora.configure(values=["Sin impresoras"])
            self.combo_impresora.set("Sin impresoras")

        # 2. Bobinas
        bobinas = database.obtener_bobinas(self.user_id)
        nombres_bob = []
        self.mapa_bobinas = {}
        for bob in bobinas:
            nombre_str = f"{bob[1]} {bob[2]} {bob[3]} ({bob[4]}g)"
            nombres_bob.append(nombre_str)
            self.mapa_bobinas[nombre_str] = bob[0]
            
        if nombres_bob:
            self.combo_bobina.configure(values=nombres_bob)
            self.combo_bobina.set(nombres_bob[0])
        else:
            self.combo_bobina.configure(values=["Sin filamentos"])
            self.combo_bobina.set("Sin filamentos")

    def registrar(self):
        # Obtener valores
        nombre_pieza = self.entry_nombre.get()
        seleccion_imp = self.combo_impresora.get()
        seleccion_bob = self.combo_bobina.get()
        peso_str = self.entry_peso.get()
        
        # Obtenemos horas y minutos por separado
        horas_str = self.entry_horas.get()
        minutos_str = self.entry_minutos.get()

        # Validaciones básicas
        if not nombre_pieza or not peso_str:
            messagebox.showwarning("Faltan datos", "Completa el nombre y el peso.")
            return

        # Si dejan el tiempo vacío, asumimos 0
        if not horas_str: horas_str = "0"
        if not minutos_str: minutos_str = "0"
        
        if seleccion_imp == "Sin impresoras" or seleccion_bob == "Sin filamentos":
            messagebox.showerror("Error", "Necesitas tener impresoras y bobinas registradas.")
            return

        id_impresora = self.mapa_impresoras.get(seleccion_imp)
        id_bobina = self.mapa_bobinas.get(seleccion_bob)

        try:
                peso = float(peso_str)
            
                # --- CONVERSIÓN DE TIEMPO ---
                horas = float(horas_str)
                minutos = float(minutos_str)
                tiempo_unit = horas + (minutos / 60)
                cantidad = int(self.entry_cantidad.get() or 1)
                if tiempo_unit == 0:
                    messagebox.showwarning("Atención", "El tiempo por unidad no puede ser 0.")
                    return

                # Fecha entrega y precio
                fecha_entrega = None
                precio_unit = 0.0
                if TKCAL_AVAILABLE:
                    # no hay control en esta vista por simplicidad; se puede ampliar
                    fecha_entrega = None
                try:
                    precio_unit = float(self.entry_peso.get()) if self.entry_peso.get() else 0.0
                except Exception:
                    precio_unit = 0.0

                # Llamar a la base de datos (enviamos tiempo por unidad y cantidad)
                exito, mensaje = database.registrar_impresion(
                    nombre_pieza, peso, tiempo_unit, id_impresora, id_bobina, self.user_id, cantidad=cantidad, delivery_date=fecha_entrega, precio_unit=precio_unit
                )

            if exito:
                # Modal estilizado
                dlg = ctk.CTkToplevel(self)
                dlg.title("¡Éxito!")
                dlg.geometry("380x140")
                ctk.CTkLabel(dlg, text=mensaje, wraplength=340).pack(pady=(20,8))
                ctk.CTkButton(dlg, text="Aceptar", command=dlg.destroy, fg_color="green").pack(pady=8)
                self.entry_nombre.delete(0, 'end')
                self.entry_peso.delete(0, 'end')
                # Limpiamos los campos de tiempo
                self.entry_horas.delete(0, 'end')
                self.entry_minutos.delete(0, 'end')
                
                self.cargar_historial()
                self.cargar_datos_combos()
            else:
                messagebox.showerror("Error", mensaje)

        except ValueError:
            messagebox.showerror("Error", "Peso, Horas y Minutos deben ser números.")

    def cargar_historial(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        historial = database.obtener_historial(self.user_id)
        
        if not historial:
            ctk.CTkLabel(self.scroll_frame, text="Aún no has registrado impresiones.", text_color="gray").pack(pady=20)
            return

        for trabajo in historial:
            # trabajo: (id, pieza, fecha, costo, peso, cantidad, delivery_date, precio_unit, ganancia, impresora, bob_marca, bob_color)
            id_trabajo = trabajo[0]
            pieza = trabajo[1]
            fecha = trabajo[2]
            costo = trabajo[3]
            cantidad = trabajo[5]
            delivery = trabajo[6]
            ganancia = trabajo[8]

            card = ctk.CTkFrame(self.scroll_frame)
            card.pack(fill="x", pady=5)

            # Checkbox
            chk = ctk.CTkCheckBox(card, text="", width=20)
            chk_var = tk.IntVar(value=0)
            chk.configure(variable=chk_var)
            chk.pack(side="left", padx=12)
            if not hasattr(self, 'seleccionados'):
                self.seleccionados = {}
            self.seleccionados[id_trabajo] = chk_var

            info_main = f"📦 {pieza}  |  💲 Costo: ${costo:.2f} | Cant: {cantidad}"
            ctk.CTkLabel(card, text=info_main, font=("Roboto", 14, "bold"), anchor="w").pack(side="left", padx=10, pady=(5,0))
            
            info_sub = f"📅 {fecha}  |  Entrega: {delivery or '-'} | Ganancia: ${ganancia if ganancia is not None else 0:.2f}"
            ctk.CTkLabel(card, text=info_sub, font=("Roboto", 11), text_color="gray", anchor="w").pack(side="left", padx=10, pady=(0,5))
            
            # Ganancia destacada
            ctk.CTkLabel(card, text=f"${ganancia if ganancia is not None else 0:.2f}", text_color="#9ee59e", font=("Roboto", 12, "bold")).pack(side="right", padx=12)
            btns = ctk.CTkFrame(card, fg_color="transparent")
            btns.pack(side="right", padx=10)
            ctk.CTkButton(btns, text="Ver detalle", width=120, command=lambda t=trabajo: self.mostrar_detalle(t)).pack(side="left", padx=6)
            ctk.CTkButton(btns, text="Eliminar", fg_color="red", width=60, command=lambda i=id_trabajo: self.eliminar(i)).pack(side="left", padx=6)

    def mostrar_detalle(self, trabajo):
        top = ctk.CTkToplevel(self)
        top.title(f"Detalle - {trabajo[1]}")
        top.geometry("520x320")
        ctk.CTkLabel(top, text=trabajo[1], font=("Segoe UI", 16, "bold"), text_color="white").pack(pady=(12,6))
        info = (
            f"Fecha: {trabajo[2]}\n"
            f"Costo total: ${trabajo[3]:.2f}\n"
            f"Peso por unidad: {trabajo[4]} g\n"
            f"Cantidad: {trabajo[5]}\n"
            f"Fecha entrega: {trabajo[6] or '-'}\n"
            f"Precio/u: ${trabajo[7] if trabajo[7] is not None else 0:.2f}\n"
            f"Ganancia: ${trabajo[8] if trabajo[8] is not None else 0:.2f}\n"
            f"Impresora: {trabajo[9]}\n"
            f"Bobina: {trabajo[10]} {trabajo[11]}\n"
        )
        ctk.CTkLabel(top, text=info, text_color="gray", justify="left").pack(padx=12, pady=8)
        ctk.CTkButton(top, text="Cerrar", command=top.destroy, fg_color=config.COLOR_VERDE_BAMBU).pack(pady=12)

    def eliminar(self, id_trabajo):
        if messagebox.askyesno("Borrar", "¿Borrar del historial?"):
            database.eliminar_impresion(id_trabajo)
            self.cargar_historial()