"""
Aplicación principal - Reporte de lesiones - Atlético Colón
Club Atlético Colón - Base limpia para desarrollo
"""

import streamlit as st
from utils.ui_utils import aplicar_estilos_css, crear_header_principal, crear_footer, configurar_tema_oscuro
from components.filters_ui import mostrar_filtros_principales
from modules.kpi_cards import mostrar_kpi_cantidad_lesiones, mostrar_kpi_dias_lesionado, mostrar_kpi_dias_lesion_seleccionada, mostrar_kpi_lesiones_activas
from modules.grafico_evolutivo import mostrar_grafico_evolutivo
from modules.grafico_ranking_lesionados import mostrar_grafico_ranking_lesionados
from modules.grafico_region_lesiones import mostrar_grafico_region_lesiones

# ========= CONFIGURACIÓN DE PÁGINA ==========
st.set_page_config(
	page_title="Reporte de lesiones - Atlético Colón",
	#page_icon="⚽",
	layout="wide",
	initial_sidebar_state="expanded"
)

def main():
	"""Función principal de la aplicación - Base limpia"""
	
	# Header principal - Lo más arriba posible para ganar espacio
	crear_header_principal()
	
	# Configurar tema oscuro
	configurar_tema_oscuro()
	aplicar_estilos_css()
	
	# ===== GRÁFICO EVOLUTIVO (PRIMERO) =====
	# Separador visual para el gráfico evolutivo
	st.markdown(
		"""
		<p style='
			color:#9ca3af;
			font-size:13px;
			text-transform:uppercase;
			letter-spacing:1px;
			margin-top:10px;
			margin-bottom:4px;
			text-align:left;
		'>
			Análisis temporal
		</p>
		<hr style='
			border:none;
			height:2px;
			background:linear-gradient(to right, #dc2626, #1f2937);
			margin:8px 0 25px 0;
			border-radius:2px;
		'>
		""",
		unsafe_allow_html=True
	)
	
	# Gráfico evolutivo de lesiones (sin depender de filtros)
	mostrar_grafico_evolutivo()
	
	# ===== FILTROS (DESPUÉS DEL GRÁFICO) =====
	# Mostrar filtros principales (jugador, evento de lesión y tipo informativo)
	selected_player, selected_event, tipo_lesion, fecha_inicio, fecha_fin = mostrar_filtros_principales()
	
	# ===== INDICADORES DEL JUGADOR =====
	# Separador visual entre filtros y KPIs
	st.markdown(
		"""
		<p style='
			color:#9ca3af;
			font-size:13px;
			text-transform:uppercase;
			letter-spacing:1px;
			margin-top:30px;
			margin-bottom:4px;
			text-align:left;
		'>
			Indicadores del jugador
		</p>
		<hr style='
			border:none;
			height:2px;
			background:linear-gradient(to right, #dc2626, #1f2937);
			margin:8px 0 25px 0;
			border-radius:2px;
		'>
		""",
		unsafe_allow_html=True
	)
	
	# Mostrar nombre del jugador seleccionado centrado y más grande
	if selected_player:
		st.markdown(
			f"<h1 style='text-align:center; color:white; font-size:40px; margin-top:25px; margin-bottom:40px;'>{selected_player}</h1>",
			unsafe_allow_html=True
		)
	
	# Primera fila de KPIs (2 columnas)
	col1, col2 = st.columns(2)
	
	with col1:
		mostrar_kpi_cantidad_lesiones(selected_player)
	
	with col2:
		mostrar_kpi_dias_lesionado(selected_player)
	
	# Segunda fila de KPIs (2 columnas)
	col3, col4 = st.columns(2)
	
	with col3:
		mostrar_kpi_dias_lesion_seleccionada(selected_player, selected_event)
	
	with col4:
		mostrar_kpi_lesiones_activas(selected_player)
	
	# ===== GRÁFICOS COMPARATIVOS =====
	# Separador visual para gráficos comparativos
	st.markdown(
		"""
		<p style='
			color:#9ca3af;
			font-size:13px;
			text-transform:uppercase;
			letter-spacing:1px;
			margin-top:40px;
			margin-bottom:4px;
			text-align:left;
		'>
			Comparativa general de lesiones
		</p>
		<hr style='
			border:none;
			height:2px;
			background:linear-gradient(to right, #dc2626, #1f2937);
			margin:8px 0 25px 0;
			border-radius:2px;
		'>
		""",
		unsafe_allow_html=True
	)
	
	# Gráficos en dos columnas
	col1, col2 = st.columns(2)
	
	with col1:
		mostrar_grafico_ranking_lesionados()
	
	with col2:
		mostrar_grafico_region_lesiones()
	
	# Sidebar vacío
	with st.sidebar:
		pass
	
	# Footer
	crear_footer()

if __name__ == "__main__":
	main()
