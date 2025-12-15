import customtkinter as ctk
from tkinter import messagebox, filedialog
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

        # Cabecera con Título y Botón Exportar
        frame_header = ctk.CTkFrame(self, fg_color="transparent")
        frame_header.pack(fill="x", padx=30, pady=(20, 10))

        ctk.CTkLabel(frame_header, text="Historial de Trabajos", font=("Segoe UI", 24, "bold"), text_color="white").pack(side="left")

        # BOTÓN EXPORTAR
        ctk.CTkButton(frame_header, text="📄 Exportar a Excel", 
                      width=150, fg_color=config.COLOR_VERDE_BAMBU, hover_color=config.COLOR_VERDE_HOVER,
                      command=self.exportar_csv).pack(side="right")

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

    def cargar_historial(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        historial = database.obtener_historial(self.user_id)
        
        if not historial:
            ctk.CTkLabel(self.scroll_frame, text="No hay trabajos registrados.", text_color="gray").pack(pady=20)
            return

        for trabajo in historial:
            # trabajo: (id, pieza, fecha, costo, peso, imp_nombre, bob_marca, bob_color)
            id_trabajo = trabajo[0]
            pieza = trabajo[1]
            fecha = trabajo[2]
            costo = trabajo[3]
            
            # Tarjeta Estilo Dark
            card = ctk.CTkFrame(self.scroll_frame, fg_color=config.COLOR_TARJETA, corner_radius=8)
            card.pack(fill="x", pady=5, padx=5)

            # Icono
            ctk.CTkLabel(card, text="✅", font=("Segoe UI", 18)).pack(side="left", padx=15)

            # Info
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", padx=5, pady=10)
            
            ctk.CTkLabel(info_frame, text=pieza, font=("Segoe UI", 14, "bold"), text_color="white").pack(anchor="w")
            
            detalle = f"{fecha} | 💲${costo:.2f} | 🖨️ {trabajo[5]}"
            ctk.CTkLabel(info_frame, text=detalle, font=("Segoe UI", 12), text_color="gray").pack(anchor="w")
            
            # Botón Eliminar
            ctk.CTkButton(card, text="✕", width=30, height=30, fg_color="transparent", text_color="gray", hover_color=config.COLOR_ROJO,
                          command=lambda i=id_trabajo: self.eliminar(i)).pack(side="right", padx=15)

    def eliminar(self, id_trabajo):
        if messagebox.askyesno("Borrar", "¿Borrar del historial permanentemente?"):
            database.eliminar_impresion(id_trabajo)
            self.cargar_historial()