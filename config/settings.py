"""
Configuración general de la aplicación
"""

# ========= CONFIGURACIÓN DE RUTAS ==========
DATA_PATH = "/Users/agustin/Documents/Agustin_2025/Juan Colon/data/1ra evaluación.xlsx"
ESCUDO_PATH = "/Users/agustin/Documents/Agustin_2025/Juan Colon/data/escudo.png"

# ========= CONFIGURACIÓN DE CACHE ==========
CACHE_TTL = {
	'datos_principales': 3600,  # 1 hora
	'graficos': 1800,          # 30 minutos
	'estadisticas': 900,       # 15 minutos
	'selecciones': 300,        # 5 minutos
	'preparacion_datos': 600,  # 10 minutos
	'jugadores_categoria': 1800 # 30 minutos
}

# ========= CONFIGURACIÓN DE MÉTRICAS ==========
METRICAS_POR_SECCION = {
	"Fuerza": {
		"CUAD 70° Der": "CUAD 70° Izq",
		"ISQ Wollin Der": "ISQ Wollin Izq", 
		"IMTP F. Der (N)": "IMTP F. Izq (N)",
		"CMJ F. Der (N)": "CMJ F. Izq (N)"
	},
	"Movilidad": {
		"Flexión Cadera Der": "Flexión Cadera Izq",
		"Extensión Cadera Der": "Extensión Cadera Izq",
		"Flexión Rodilla Der": "Flexión Rodilla Izq",
		"Extensión Rodilla Der": "Extensión Rodilla Izq",
		"Flexión Tobillo Der": "Flexión Tobillo Izq",
		"Extensión Tobillo Der": "Extensión Tobillo Izq"
	},
	"Funcionalidad": {
		"Overhead Squat Der": "Overhead Squat Izq",
		"Single Leg Squat Der": "Single Leg Squat Izq",
		"In-Line Lunge Der": "In-Line Lunge Izq",
		"Shoulder Mobility Der": "Shoulder Mobility Izq",
		"Active SLR Der": "Active SLR Izq",
		"T. S. Der": "T. S. Izq"
	}
}

# ========= CONFIGURACIÓN DE COLORES ==========
COLORES = {
	'rojo_colon': 'rgba(220, 38, 38, 0.85)',
	'negro_colon': 'rgba(31, 41, 55, 0.85)',
	'fondo_oscuro': 'rgba(17, 24, 39, 1)',
	'azul_zscore': 'rgba(59, 130, 246, 0.8)',
	'verde_optimo': 'rgba(50, 205, 50, 0.9)',
	'naranja_alerta': 'rgba(255, 165, 0, 0.9)',
	'rojo_riesgo': 'rgba(255, 69, 0, 0.9)'
}

# ========= CONFIGURACIÓN DE Z-SCORES ==========
Z_SCORE_METRICAS = {
	'Z SCORE CUAD Der': 'CUAD Der',
	'Z SCORE CUAD Izq': 'CUAD Izq',
	'Z SCORE ISQ Der': 'ISQ Der',
	'Z SCORE ISQ Izq': 'ISQ Izq',
	'Z SCORE IMTP Der': 'IMTP Der',
	'Z SCORE IMTP Izq': 'IMTP Izq',
	'Z SCORE CMJ FP Der': 'CMJ FP Der',
	'Z SCORE CMJ FP Izq': 'CMJ FP Izq',
	'Z SCORE CMJ FF Der': 'CMJ FF Der',
	'Z SCORE CMJ FF Izq': 'CMJ FF Izq'
}

# ========= CONFIGURACIÓN DE PLOTLY ==========
PLOTLY_CONFIG = {
	'displayModeBar': True,
	'displaylogo': False,
	'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
	'toImageButtonOptions': {
		'format': 'png',
		'height': 620,
		'width': 1000,
		'scale': 2
	}
}
