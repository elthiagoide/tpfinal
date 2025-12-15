import customtkinter as ctk
import webbrowser
import random
import config # Importamos tus colores

# Lista de "Ofertas" simuladas (Puedes agregar las que quieras)
OFERTAS_DISPONIBLES = [
    {
        "titulo": "🔥 OFERTA RELÁMPAGO: Ender 3 V3 SE",
        "desc": "¡La impresora más vendida con nivelación automática a un precio histórico!",
        "precio": "$350.000",
        "link": "https://listado.mercadolibre.com.ar/ender-3-v3-se"
    },
    {
        "titulo": "🧵 PACK FILAMENTOS PLA x4",
        "desc": "Llevate 4 rollos de Grilon3 (Colores a elección) con envío gratis.",
        "precio": "$45.999",
        "link": "https://listado.mercadolibre.com.ar/filamento-pla-pack"
    },
    {
        "titulo": "💧 Resina Creality Standard 1L",
        "desc": "Alta precisión y bajo olor. Ideal para tus impresiones en 4K.",
        "precio": "$28.500",
        "link": "https://listado.mercadolibre.com.ar/resina-creality"
    }
]

class VentanaAnuncio(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        
        # Configuración de la ventana flotante
        self.title("¡Oportunidad!")
        self.geometry("400x300")
        self.resizable(False, False)
        self.configure(fg_color=config.COLOR_FONDO_APP)
        
        # Hacemos que la ventana aparezca siempre arriba
        self.attributes("-topmost", True)

        # Elegir una oferta al azar
        oferta = random.choice(OFERTAS_DISPONIBLES)

        # --- DISEÑO ---
        
        # Etiqueta "ANUNCIO"
        ctk.CTkLabel(self, text="📢 OPORTUNIDAD DEL DÍA", 
                     font=("Segoe UI", 12, "bold"), 
                     text_color=config.COLOR_VERDE_BAMBU).pack(pady=(20, 5))

        # Título del producto
        ctk.CTkLabel(self, text=oferta["titulo"], 
                     font=("Segoe UI", 18, "bold"), 
                     text_color="white", wraplength=350).pack(pady=(0, 10))

        # Descripción
        ctk.CTkLabel(self, text=oferta["desc"], 
                     font=("Segoe UI", 13), 
                     text_color="#ccc", wraplength=350).pack(pady=5)

        # Precio Gigante
        ctk.CTkLabel(self, text=oferta["precio"], 
                     font=("Segoe UI", 30, "bold"), 
                     text_color="white").pack(pady=15)

        # Botón de Compra
        ctk.CTkButton(self, text="VER EN LA WEB 🛒", 
                      fg_color=config.COLOR_VERDE_BAMBU, 
                      hover_color=config.COLOR_VERDE_HOVER,
                      font=("Segoe UI", 14, "bold"),
                      width=200, height=40,
                      command=lambda: self.abrir_link(oferta["link"])).pack(pady=10)

        # Botón Cerrar (Discreto)
        ctk.CTkButton(self, text="No me interesa", 
                      fg_color="transparent", text_color="gray", hover_color="#222",
                      command=self.destroy).pack(side="bottom", pady=10)

    def abrir_link(self, link):
        webbrowser.open(link)
        self.destroy() # Cierra la ventana al hacer clic