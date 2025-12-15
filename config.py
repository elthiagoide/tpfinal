# config.py - CONFIGURACIÓN DE COLORES Y MODOS

# --- PALETA ESTILO MAKERWORLD / BAMBU STUDIO ---

# 1. Fondos Principales
COLOR_FONDO_APP = "#181b1f"       # Fondo principal oscuro
COLOR_MENU_LATERAL = "#222b32"    # Fondo de la barra lateral
COLOR_SEPARADOR = "#333b42"       # <--- ESTA ES LA QUE TE FALTABA
COLOR_TARJETA = "#2c2c2c"         # Fondo de las tarjetas de impresoras/bobinas

# 2. Acentos (Verdes)
COLOR_VERDE_BAMBU = "#00965e"     # Verde principal
COLOR_VERDE_HOVER = "#00b06f"     # Verde más claro al pasar mouse

# 3. Acciones / Estados
COLOR_ROJO = "#e74c3c"            # Para eliminar o cerrar sesión
COLOR_ROJO_HOVER = "#ff6b6b"

# 4. Textos
COLOR_TEXTO_BLANCO = "#ffffff"
COLOR_TEXTO_GRIS = "#9e9e9e"
COLOR_HOVER_BTN = "#2a3640"       # Fondo gris al pasar mouse por botones del menú

# --- CONFIGURACIÓN DE MODOS (PRINCIPIANTE/GUÍA) ---
MODO_PRINCIPIANTE = True          # Arranca activado por defecto

# Colores para la caja de Ayuda
COLOR_FONDO_AYUDA = "#2a3036"
COLOR_BORDE_AYUDA = "#00965e"
COLOR_TITULO_AYUDA = "#00965e"
# --- CONFIGURACIÓN ENERGÉTICA ---
# Costo por kW-h (valor por defecto, el usuario podrá cambiarlo en la UI)
COSTO_KW = 0.20
# Mostrar cálculo de consumo energético en el dashboard por defecto
MOSTRAR_CONSUMO = True

# Tarifas por zona (ejemplos). El usuario puede seleccionar una zona o ingresar un costo manual.
ZONAS_COSTO = {
	'Zona urbana (tarifa baja)': 0.15,
	'Zona estándar': 0.20,
	'Zona industrial (tarifa alta)': 0.28
}