"""
Configuración general de la aplicación - Solo elementos visuales
"""

# ========= CONFIGURACIÓN DE RUTAS ==========
import os

# Rutas básicas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESCUDO_PATH = os.path.join(BASE_DIR, "data", "escudo.png")

# ========= CONFIGURACIÓN DE COLORES CORPORATIVOS ==========
COLORES = {
	'rojo_colon': 'rgba(220, 38, 38, 0.85)',
	'negro_colon': 'rgba(31, 41, 55, 0.85)',
	'fondo_oscuro': 'rgba(17, 24, 39, 1)',
	'azul_zscore': 'rgba(59, 130, 246, 0.8)',
	'verde_optimo': 'rgba(50, 205, 50, 0.9)',
	'naranja_alerta': 'rgba(255, 165, 0, 0.9)',
	'rojo_riesgo': 'rgba(255, 69, 0, 0.9)'
}
