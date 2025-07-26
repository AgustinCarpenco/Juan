"""
Utilidades para interfaz de usuario
"""

import base64
import streamlit as st
from functools import lru_cache
from config.settings import ESCUDO_PATH

@lru_cache(maxsize=32)
def get_base64_image(image_path):
	"""Convierte imagen a base64 con cache LRU"""
	with open(image_path, "rb") as img_file:
		encoded = base64.b64encode(img_file.read()).decode()
	return encoded

def inicializar_session_state():
	"""Inicializa variables del session state"""
	if 'df_cache' not in st.session_state:
		st.session_state.df_cache = None
	if 'ultimo_jugador' not in st.session_state:
		st.session_state.ultimo_jugador = None
	if 'ultima_categoria' not in st.session_state:
		st.session_state.ultima_categoria = None
	if 'metricas_cache' not in st.session_state:
		st.session_state.metricas_cache = {}

def aplicar_estilos_css():
	"""Aplica estilos CSS personalizados"""
	st.markdown("""
	<style>
	/* Animaciones para elementos de Streamlit */
	.stPlotlyChart {
		animation: fadeInUp 0.8s ease-out;
		transition: all 0.3s ease;
	}

	.stPlotlyChart:hover {
		transform: translateY(-2px);
		box-shadow: 0 8px 25px rgba(0,0,0,0.3);
	}

	/* Animación de carga progresiva */
	@keyframes fadeInUp {
		from {
			opacity: 0;
			transform: translateY(30px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	/* Animación para selectores */
	.stSelectbox, .stMultiSelect {
		animation: slideInLeft 0.6s ease-out;
	}

	@keyframes slideInLeft {
		from {
			opacity: 0;
			transform: translateX(-20px);
		}
		to {
			opacity: 1;
			transform: translateX(0);
		}
	}

	/* Efecto hover para sidebar */
	.css-1d391kg {
		transition: all 0.3s ease;
	}

	/* Animación para títulos */
	.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
		animation: fadeIn 1s ease-out;
	}

	@keyframes fadeIn {
		from { opacity: 0; }
		to { opacity: 1; }
	}

	/* Loading spinner personalizado */
	.stSpinner {
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}
	</style>
	""", unsafe_allow_html=True)

def crear_header_principal():
	"""Crea el header principal de la aplicación"""
	escudo_base64 = get_base64_image(ESCUDO_PATH)
	
	st.markdown(
		f"""
		<div style='background: linear-gradient(135deg, rgba(220, 38, 38, 0.9), rgba(17, 24, 39, 0.9)); 
					padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 30px;
					box-shadow: 0 8px 32px rgba(0,0,0,0.3); border: 2px solid rgba(220, 38, 38, 0.3);'>
			<div style='display: flex; align-items: center; justify-content: center; gap: 20px;'>
				<img src='data:image/png;base64,{escudo_base64}' width='80' style='filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));'/>
				<div>
					<h1 style='margin: 0; color: white; font-size: 28px; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);'>
						EVALUACIÓN FÍSICA INTEGRAL
					</h1>
					<h2 style='margin: 5px 0 0 0; color: rgba(255,255,255,0.9); font-size: 18px; font-weight: normal;'>
						Club Atlético Colón
					</h2>
				</div>
			</div>
		</div>
		""",
		unsafe_allow_html=True
	)

def crear_header_seccion(seccion, jugador, categoria):
	"""Crea header para sección específica"""
	st.markdown(f"""
	<div style='background: linear-gradient(90deg, rgba(220, 38, 38, 0.8), rgba(17, 24, 39, 0.8)); 
				padding: 15px; border-radius: 10px; margin: 20px 0;
				border-left: 5px solid rgba(220, 38, 38, 1);'>
		<h3 style='margin: 0; color: white; font-size: 22px;'>
			Análisis de {seccion}
		</h3>
		<h4 style='margin: 8px 0; color: rgba(255,255,255,1); font-size: 20px; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);'>
			{jugador}
		</h4>
		<p style='margin: 5px 0 0 0; color: rgba(255,255,255,0.8); font-size: 14px;'>
			Categoría: {categoria}<br>
			Evaluación: 1ra Fase
		</p>
	</div>
	""", unsafe_allow_html=True)

def crear_footer():
	"""Crea el footer de la aplicación"""
	st.markdown("<br><br>", unsafe_allow_html=True)
	st.markdown("""
	<div style='background: linear-gradient(135deg, rgba(220, 38, 38, 0.9), rgba(17, 24, 39, 0.9)); 
				padding: 15px; border-radius: 10px; text-align: center; margin-top: 40px;
				box-shadow: 0 4px 16px rgba(0,0,0,0.2);'>
		<p style='margin: 0; color: rgba(255,255,255,0.8); font-size: 12px;'>
			© 2025 Club Atlético Colón - Sistema desarrollado para el Staff Técnico | Evaluación Física Integral v1.0
		</p>
	</div>
	""", unsafe_allow_html=True)


