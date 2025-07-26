"""
Aplicación principal refactorizada - Evaluación Física Integral
Club Atlético Colón
"""

import streamlit as st

# Importar módulos refactorizados
from config.settings import DATA_PATH
from utils.ui_utils import inicializar_session_state, aplicar_estilos_css, crear_header_principal, crear_header_seccion, crear_footer
from utils.data_utils import cargar_datos_optimizado
from components.sidebar import crear_sidebar
from modules.fuerza_analysis import analizar_fuerza

# ========= CONFIGURACIÓN DE PÁGINA ==========
st.set_page_config(
	page_title="Evaluación Física Integral - Atlético Colón",
	page_icon="⚽",
	layout="wide",
	initial_sidebar_state="expanded"
)

def main():
	"""Función principal de la aplicación"""
	
	# Inicializar configuración
	inicializar_session_state()
	aplicar_estilos_css()
	
	# Cargar datos
	df = cargar_datos_optimizado(DATA_PATH)
	
	# Crear sidebar y obtener selecciones
	categoria, jugador, vista, seccion, exportar = crear_sidebar(df)
	
	# Crear header principal
	crear_header_principal()
	
	# ========= CONTENIDO PRINCIPAL ==========
	if vista == "Perfil del Jugador":
		# Header de sección
		crear_header_seccion(seccion, jugador, categoria)
		
		# Obtener datos del jugador seleccionado
		datos_jugador = df[(df["categoria"] == categoria) & (df["Deportista"] == jugador)].iloc[0]
		
		# Análisis por sección
		if seccion == "Fuerza":
			analizar_fuerza(df, datos_jugador, jugador, categoria)
			
		elif seccion == "Movilidad":
			st.markdown("### 🔧 Módulo en Desarrollo")
			st.info("El análisis de movilidad estará disponible próximamente.")
			
		elif seccion == "Funcionalidad":
			st.markdown("### 🔧 Módulo en Desarrollo") 
			st.info("El análisis de funcionalidad estará disponible próximamente.")
	
	elif vista == "Perfil del Grupo":
		st.markdown("### 🔧 Módulo en Desarrollo")
		st.info("El análisis de grupo estará disponible próximamente.")
		
	elif vista == "Comparación Jugador vs Grupo":
		st.markdown("### 🔧 Módulo en Desarrollo")
		st.info("La comparación jugador vs grupo estará disponible próximamente.")
	
	else:
		st.warning("Esta visualización detallada está disponible solo en el modo 'Perfil del Jugador'.")
	
	# Footer
	crear_footer()
	
	# Manejo del botón exportar
	if exportar:
		st.success("🔧 Funcionalidad de exportación en desarrollo")

if __name__ == "__main__":
	main()
