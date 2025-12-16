import customtkinter as ctk
from tkinter import messagebox, filedialog
import tkinter as tk
import sys
import os
import config
import csv            # <--- NUEVO
from datetime import datetime # <--- NUEVO

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database

class VistaHistorial(ctk.CTkFrame):
    def __init__(self, master, user_id, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=config.COLOR_FONDO_APP)
        self.user_id = user_id

        # Cabecera con Título, Orden y Botón Exportar
        frame_header = ctk.CTkFrame(self, fg_color="transparent")
        frame_header.pack(fill="x", padx=30, pady=(20, 10))

        ctk.CTkLabel(frame_header, text="Historial de Trabajos", font=("Segoe UI", 24, "bold"), text_color="white").pack(side="left")

        # Selector de orden
        self.combo_orden = ctk.CTkComboBox(frame_header, values=["Fecha ↓", "Fecha ↑", "Ganancia ↓", "Ganancia ↑"], width=160)
        self.combo_orden.set("Fecha ↓")
        self.combo_orden.pack(side="right", padx=8)
        self.combo_orden.bind("<<ComboboxSelected>>", lambda e: self.cargar_historial())

        # BOTÓN EXPORTAR y Marcar todo
        ctk.CTkButton(frame_header, text="📄 Exportar a Excel", 
              width=150, fg_color=config.COLOR_VERDE_BAMBU, hover_color=config.COLOR_VERDE_HOVER,
              command=self.exportar_csv).pack(side="right", padx=8)
        ctk.CTkButton(frame_header, text="Exportar seleccionados", 
              width=180, fg_color="#4a90e2", hover_color="#3a78c2",
              command=self.exportar_seleccionados).pack(side="right", padx=8)
        # Marcar todo como checkbox (visual claro junto a controles)
        import tkinter as _tk
        self.chk_all_var = _tk.IntVar(value=0)
        self.chk_all_cb = ctk.CTkCheckBox(frame_header, text="Marcar todo", variable=self.chk_all_var, command=self.toggle_marcar_todo)
        self.chk_all_cb.pack(side="right", padx=8)

        # Lista Scrollable
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=30, pady=10)

        self.cargar_historial()

    def exportar_csv(self):
        # 1. Pedir datos
        historial = database.obtener_historial(self.user_id)
        if not historial:
            messagebox.showwarning("Vacío", "No hay datos para exportar.")
            return

        # 2. Generar nombre de archivo con fecha
        fecha_hoy = datetime.now().strftime("%Y-%m-%d_%H-%M")
        nombre_default = f"reporte_impresiones_{fecha_hoy}.csv"

        # 3. Preguntar dónde guardar
        try:
            archivo = filedialog.asksaveasfilename(
                defaultextension=".csv",
                initialfile=nombre_default,
                filetypes=[("Archivos CSV", "*.csv"), ("Todos", "*.*")],
                title="Guardar Reporte"
            )

            if archivo:
                with open(archivo, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=';') # Usamos ; para que Excel lo abra directo en latam
                    
                    # Encabezados
                    writer.writerow(["ID", "Pieza", "Fecha", "Costo ($)", "Peso (g)", "Impresora", "Bobina Marca", "Bobina Color"])
                    
                    # Datos
                    for fila in historial:
                        # fila: (id, pieza, fecha, costo, peso, imp_nombre, bob_marca, bob_color)
                        writer.writerow(fila)
                
                messagebox.showinfo("Éxito", f"Reporte guardado en:\n{archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {e}")

    def exportar_seleccionados(self):
        # exportar solo los seleccionados en self.seleccionados
        sel = [pid for pid, var in getattr(self, 'seleccionados', {}).items() if var.get() == 1]
        if not sel:
            messagebox.showwarning("Sin selección", "No hay elementos seleccionados para exportar.")
            return
        historial = database.obtener_historial(self.user_id)
        filas = [h for h in historial if h[0] in sel]
        # usar misma lógica que exportar_csv pero con filas filtradas
        try:
            fecha_hoy = datetime.now().strftime("%Y-%m-%d_%H-%M")
            nombre_default = f"reporte_impresiones_seleccion_{fecha_hoy}.csv"
            archivo = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=nombre_default, filetypes=[("Archivos CSV", "*.csv")])
            if archivo:
                with open(archivo, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=';')
                    writer.writerow(["ID", "Pieza", "Fecha", "Costo ($)", "Peso (g)", "Cant", "Entrega", "Precio/u", "Ganancia", "Impresora", "Bobina Marca", "Bobina Color"])
                    for fila in filas:
                        writer.writerow(fila)
                messagebox.showinfo("Éxito", f"Reporte guardado en:\n{archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {e}")

    def toggle_marcar_todo(self):
        # si checkbox header está marcado -> marcar todos, sino desmarcar todos
        try:
            target = 1 if getattr(self, 'chk_all_var', None) and self.chk_all_var.get() == 1 else 0
            for pid, var in getattr(self, 'seleccionados', {}).items():
                var.set(target)
        except Exception:
            pass

    def cargar_historial(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        historial = database.obtener_historial(self.user_id)
        
        if not historial:
            ctk.CTkLabel(self.scroll_frame, text="No hay trabajos registrados.", text_color="gray").pack(pady=20)
            return

        # Aplicar orden local según selector
        orden = self.combo_orden.get() if hasattr(self, 'combo_orden') else "Fecha ↓"
        try:
            if orden == "Fecha ↑":
                historial = sorted(historial, key=lambda x: x[2])
            elif orden == "Ganancia ↓":
                historial = sorted(historial, key=lambda x: (x[8] if x[8] is not None else 0), reverse=False)
            elif orden == "Ganancia ↑":
                historial = sorted(historial, key=lambda x: (x[8] if x[8] is not None else 0), reverse=True)
            else:
                historial = sorted(historial, key=lambda x: x[2], reverse=True)
        except Exception:
            pass

        for trabajo in historial:
            # Trabajos pueden venir con esquemas distintos; extraer defensivamente
            def g(i, default=None):
                try:
                    return trabajo[i]
                except Exception:
                    return default

            id_trabajo = g(0, 0)
            pieza = g(1, "(sin nombre)")
            fecha = g(2, "")
            costo = g(3, 0.0) or 0.0
            peso = g(4, 0.0) or 0.0

            # Soporte para varias versiones de esquema
            if len(trabajo) >= 12:
                cantidad = g(5, 1)
                delivery = g(6, None)
                precio_unit = g(7, None)
                ganancia = g(8, 0.0) or 0.0
                impresora = g(9, "-")
                bob_marca = g(10, "-")
                bob_color = g(11, "-")
            elif len(trabajo) == 9:
                # Formato seleccionado en database.obtener_historial
                cantidad = 1
                delivery = None
                precio_unit = None
                ganancia = g(5, 0.0) or 0.0
                impresora = g(6, "-")
                bob_marca = g(7, "-")
                bob_color = g(8, "-")
            else:
                cantidad = g(5, 1) or 1
                delivery = g(6, None)
                precio_unit = g(7, None)
                ganancia = g(8, 0.0) or 0.0
                impresora = g(9, "-")
                bob_marca = g(10, "-")
                bob_color = g(11, "-")

            # Tarjeta Estilo Dark
            card = ctk.CTkFrame(self.scroll_frame, fg_color=config.COLOR_TARJETA, corner_radius=8)
            card.pack(fill="x", pady=5, padx=5)

            # Checkbox
            chk_var = tk.IntVar(value=0)
            cb = ctk.CTkCheckBox(card, variable=chk_var, text="", width=20)
            cb.pack(side="left", padx=12)
            # store selection state
            try:
                if not hasattr(self, 'seleccionados'):
                    self.seleccionados = {}
                self.seleccionados[id_trabajo] = chk_var
            except Exception:
                pass

            # (removed decorative icon) -- checkbox used for selection

            # Info
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", padx=5, pady=10, expand=True)
            
            ctk.CTkLabel(info_frame, text=pieza, font=("Segoe UI", 14, "bold"), text_color="white").pack(anchor="w")
            
            try:
                detalle = f"{fecha} | 💲${float(costo):.2f} | Cant: {cantidad} | Entrega: {delivery or '-'}"
            except Exception:
                detalle = f"{fecha} | 💲${costo} | Cant: {cantidad} | Entrega: {delivery or '-'}"
            ctk.CTkLabel(info_frame, text=detalle, font=("Segoe UI", 12), text_color="gray").pack(anchor="w")

            # Ganancia destacada y botones Ver detalle/Eliminar
            ctk.CTkLabel(card, text=f"Ganancia: ${ganancia if ganancia is not None else 0:.2f}", text_color="#9ee59e", font=("Segoe UI", 12, "bold")).pack(side="right", padx=12)
            btns_right = ctk.CTkFrame(card, fg_color="transparent")
            btns_right.pack(side="right", padx=6)
            ctk.CTkButton(btns_right, text="Ver detalle", width=120, command=lambda t=trabajo: self.mostrar_detalle(t)).pack(side="left", padx=6)
            ctk.CTkButton(btns_right, text="Eliminar", width=110, fg_color=config.COLOR_ROJO, hover_color=config.COLOR_ROJO_HOVER, command=lambda i=id_trabajo: self.eliminar(i)).pack(side="left", padx=6)

    def mostrar_detalle(self, trabajo):
        # Mostrar detalle de forma defensiva según esquema
        top = ctk.CTkToplevel(self)
        top.title(f"Detalle - {g(1, '(sin nombre)')}")
        top.geometry("520x360")
        try:
            top.lift()
            top.grab_set()
        except:
            pass
        ctk.CTkLabel(top, text=g(1, '(sin nombre)'), font=("Segoe UI", 16, "bold"), text_color="white").pack(pady=(12,6))
        # Reusar los campos ya calculados si es posible
        try:
            pieza = trabajo[1]
        except: pieza = g(1, '(sin nombre)')
        try:
            fecha = trabajo[2]
        except: fecha = g(2, '')
        try:
            costo = float(trabajo[3])
        except: costo = g(3, 0.0)
        try:
            peso = trabajo[4]
        except: peso = g(4, 0.0)

        # Extract other fields defensively
        if len(trabajo) >= 12:
            cantidad = g(5, 1)
            delivery = g(6, None)
            precio_unit = g(7, None)
            ganancia = g(8, 0.0)
            impresora = g(9, '-')
            bob_marca = g(10, '-')
            bob_color = g(11, '-')
        elif len(trabajo) == 9:
            cantidad = 1
            delivery = None
            precio_unit = None
            ganancia = g(5, 0.0)
            impresora = g(6, '-')
            bob_marca = g(7, '-')
            bob_color = g(8, '-')
        else:
            cantidad = g(5, 1)
            delivery = g(6, None)
            precio_unit = g(7, None)
            ganancia = g(8, 0.0)
            impresora = g(9, '-')
            bob_marca = g(10, '-')
            bob_color = g(11, '-')

        info = (
            f"Fecha: {fecha}\n"
            f"Costo total: ${float(costo) if isinstance(costo, (int,float)) else costo}\n"
            f"Peso por unidad: {peso} g\n"
            f"Cantidad: {cantidad}\n"
            f"Fecha entrega: {delivery or '-'}\n"
            f"Precio/u: ${precio_unit if precio_unit is not None else 0}\n"
            f"Ganancia: ${ganancia if ganancia is not None else 0}\n"
            f"Impresora: {impresora}\n"
            f"Bobina: {bob_marca} {bob_color}\n"
        )
        ctk.CTkLabel(top, text=info, text_color="gray", justify="left").pack(padx=12, pady=8)
        ctk.CTkButton(top, text="Cerrar", command=top.destroy, fg_color=config.COLOR_VERDE_BAMBU).pack(pady=12)

    def eliminar(self, id_trabajo):
        if messagebox.askyesno("Borrar", "¿Borrar del historial permanentemente?"):
            database.eliminar_impresion(id_trabajo)
            self.cargar_historial()