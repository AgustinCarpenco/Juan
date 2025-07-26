"""
Módulo de análisis de fuerza
"""

import streamlit as st
import pandas as pd
from visualizations.charts import crear_grafico_multifuerza, crear_radar_zscore
from utils.data_utils import procesar_datos_categoria, calcular_estadisticas_categoria, preparar_datos_jugador

from config.settings import PLOTLY_CONFIG

def analizar_fuerza(df, datos_jugador, jugador, categoria):
	"""Realiza el análisis completo de fuerza"""
	
	# === Selección de métricas de fuerza ===
	metricas_disponibles = ["CUAD 70°", "ISQ Wollin", "IMTP", "CMJ"]
	metricas_display = ["CUAD 70°", "ISQ Wollin", "IMTP", "CMJ"]
	metricas_columnas = {
		"CUAD 70°": ("CUAD 70° Der", "CUAD 70° Izq"),
		"ISQ Wollin": ("ISQ Wollin Der", "ISQ Wollin Izq"),
		"IMTP": ("IMTP F. Der (N)", "IMTP F. Izq (N)"),
		"CMJ": ("CMJ F. Der (N)", "CMJ F. Izq (N)")
	}

	metricas_seleccionadas_display = st.multiselect(
		"Selección de Métricas - Selecciona las evaluaciones de fuerza para el análisis bilateral:",
		metricas_disponibles,
		default=["CUAD 70°", "ISQ Wollin", "IMTP"]
	)
	
	# Convertir de display a nombres reales
	metricas_seleccionadas = []
	for metrica_display in metricas_seleccionadas_display:
		for i, display in enumerate(metricas_disponibles):
			if metrica_display == display:
				metricas_seleccionadas.append(metricas_display[i])

	if metricas_seleccionadas:
		# Optimización con cache - crear hash del jugador
		datos_jugador_dict = datos_jugador.to_dict() if hasattr(datos_jugador, 'to_dict') else dict(datos_jugador)
		
		# Generar gráfico con cache optimizado
		fig_multifuerza = crear_grafico_multifuerza(datos_jugador_dict, tuple(metricas_seleccionadas), metricas_columnas)
		
		# Mostrar gráfico con animación
		st.markdown("""
		<div style="animation: fadeInUp 0.8s ease-out;">
		""", unsafe_allow_html=True)
		
		st.plotly_chart(fig_multifuerza, use_container_width=True, config=PLOTLY_CONFIG)
		
		st.markdown("</div>", unsafe_allow_html=True)
		
		# === RADAR CHART Z-SCORES ===
		st.markdown("<br>", unsafe_allow_html=True)
		
		# Header para el radar chart
		st.markdown(f"""
		<div style='background: linear-gradient(90deg, rgba(220, 38, 38, 0.8), rgba(17, 24, 39, 0.8));
					border-left: 4px solid rgba(220, 38, 38, 1);'>
			<h4 style='margin: 0; color: white; font-size: 18px;'>
				Análisis Z-Score 
			</h4>
		</div>
		""", unsafe_allow_html=True)
		
		# Generar radar chart con cache optimizado
		fig_radar = crear_radar_zscore(datos_jugador_dict, jugador)
		
		radar_config = PLOTLY_CONFIG.copy()
		radar_config['toImageButtonOptions'].update({
			'filename': f'radar_zscore_{jugador}_{categoria}',
			'height': 500,
			'width': 800
		})
		
		st.plotly_chart(fig_radar, use_container_width=True, config=radar_config)
		


		# === TABLA COMPARATIVA ===
		st.markdown(f"#### Tabla - {jugador}")

		# Usar función optimizada con cache para procesar datos
		df_categoria = procesar_datos_categoria(df, categoria)
		
		# Columnas de fuerza que queremos analizar
		columnas_tabla = {
			"CUAD 70° Der": "CUAD 70° Izq",
			"ISQ Wollin Der": "ISQ Wollin Izq",
			"IMTP F. Der (N)": "IMTP F. Izq (N)",
			"CMJ F. Der (N)": "CMJ F. Izq (N)"
		}

		# Usar funciones optimizadas con cache
		jugador_dict = preparar_datos_jugador(datos_jugador_dict, columnas_tabla)
		media_dict, std_dict = calcular_estadisticas_categoria(df_categoria, columnas_tabla)

		# Ordenar columnas como pares
		column_order = []
		for der, izq in columnas_tabla.items():
			column_order.extend([der, izq])

		# Crear DataFrame comparativo original
		df_comparativo = pd.DataFrame([
			jugador_dict,
			media_dict,
			std_dict
		])[column_order]
		df_comparativo.index = [f"{jugador}", f"Media {categoria}", f"Desv. Est. {categoria}"]
		
		# Transponer tabla para mejor visualización y exportación PDF
		df_transpuesto = df_comparativo.T
		df_transpuesto.index.name = "Métrica"
		
		# Mostrar tabla transpuesta con estilo optimizado
		st.dataframe(
			df_transpuesto.style.format("{:.1f}").apply(
				lambda x: [
					'background-color: rgba(220, 38, 38, 0.15); font-weight: bold;',  # Columna jugador
					'background-color: rgba(255, 255, 255, 0.08);',  # Columna media
					'background-color: rgba(59, 130, 246, 0.15);'    # Columna desv. est.
				], axis=1
			).set_table_styles([
				{'selector': 'th.col_heading', 'props': 'background-color: rgba(220, 38, 38, 0.3); color: white; font-weight: bold;'},
				{'selector': 'th.row_heading', 'props': 'background-color: rgba(31, 41, 55, 0.8); color: white; font-weight: bold; text-align: left;'},
				{'selector': 'td', 'props': 'text-align: center; padding: 8px;'}
			]),
			use_container_width=True
		)
		
	else:
		st.info("Selecciona al menos una métrica para visualizar el gráfico.")
