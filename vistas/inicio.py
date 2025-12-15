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
        frame_dinero.pack(pady=40, ipadx=20, ipady=10)
        
        ctk.CTkLabel(frame_dinero, text="COSTO TOTAL DE PRODUCCIÓN", font=("Segoe UI", 12, "bold"), text_color="gray").pack()
        ctk.CTkLabel(frame_dinero, text=f"${gasto_total:,.2f}", font=("Segoe UI", 32, "bold"), text_color="white").pack()

        # Botón de Acción Principal
        ctk.CTkButton(self, text="✨ NUEVA IMPRESIÓN", width=250, height=50, 
                      font=("Segoe UI", 14, "bold"),
                      fg_color=config.COLOR_VERDE_BAMBU, hover_color=config.COLOR_VERDE_HOVER,
                      command=self.callback_nueva_impresion).pack(pady=10)

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