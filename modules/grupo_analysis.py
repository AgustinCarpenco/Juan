"""
Módulo de análisis grupal
"""

import streamlit as st
import pandas as pd
from visualizations.charts import crear_grafico_multifuerza_grupo, crear_radar_zscore_grupo
from utils.data_utils import procesar_datos_categoria, calcular_estadisticas_grupo, preparar_datos_grupo
from config.settings import PLOTLY_CONFIG

def analizar_fuerza_grupo(df, categoria):
	"""Realiza el análisis completo de fuerza para el grupo/categoría"""
	
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
		"Selección de Métricas - Selecciona las evaluaciones de fuerza para el análisis grupal:",
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
		# Obtener datos del grupo
		datos_grupo = df[df["categoria"] == categoria]
		
		# Generar gráfico grupal con cache optimizado
		fig_multifuerza_grupo = crear_grafico_multifuerza_grupo(
			datos_grupo, 
			tuple(metricas_seleccionadas), 
			metricas_columnas,
			categoria
		)
		
		# Mostrar gráfico con animación
		st.markdown("""
		<div style="animation: fadeInUp 0.8s ease-out;">
		""", unsafe_allow_html=True)
		
		st.plotly_chart(fig_multifuerza_grupo, use_container_width=True, config=PLOTLY_CONFIG)
		
		st.markdown("</div>", unsafe_allow_html=True)
		
		# === TABLA DE ESTADÍSTICAS GRUPALES ===
		st.markdown("---")
		st.markdown(f"### 📊 Tabla Estadísticas - {categoria}")
		
		# Calcular estadísticas con cache
		estadisticas = calcular_estadisticas_grupo(datos_grupo, tuple(metricas_seleccionadas), metricas_columnas)
		
		# Preparar datos para la tabla
		filas_tabla = []
		indices_tabla = []
		
		for metrica in metricas_seleccionadas:
			if metrica == "CMJ":
				# CMJ Propulsiva
				stats_prop = estadisticas.get(f"{metrica}_Prop", {})
				filas_tabla.append([
					stats_prop.get('media', 0),
					stats_prop.get('mediana', 0),
					stats_prop.get('std', 0),
					stats_prop.get('min', 0),
					stats_prop.get('max', 0)
				])
				indices_tabla.append("CMJ Propulsiva (N)")
				
				# CMJ Frenado
				stats_fren = estadisticas.get(f"{metrica}_Fren", {})
				filas_tabla.append([
					stats_fren.get('media', 0),
					stats_fren.get('mediana', 0),
					stats_fren.get('std', 0),
					stats_fren.get('min', 0),
					stats_fren.get('max', 0)
				])
				indices_tabla.append("CMJ Frenado (N)")
			else:
				stats = estadisticas.get(metrica, {})
				unidad = " (N)" if metrica in ["IMTP"] else ""
				filas_tabla.append([
					stats.get('media', 0),
					stats.get('mediana', 0),
					stats.get('std', 0),
					stats.get('min', 0),
					stats.get('max', 0)
				])
				indices_tabla.append(f"{metrica}{unidad}")
		
		# Crear DataFrame de estadísticas grupales
		df_estadisticas_grupo = pd.DataFrame(
			filas_tabla,
			columns=["Media", "Mediana", "Desv. Est.", "Mínimo", "Máximo"],
			index=indices_tabla
		)
		df_estadisticas_grupo.index.name = "Métrica"
		
		# Mostrar tabla con estilo similar al perfil del jugador
		st.dataframe(
			df_estadisticas_grupo.style.format("{:.1f}").apply(
				lambda x: [
					'background-color: rgba(220, 38, 38, 0.15); font-weight: bold;',  # Columna Media
					'background-color: rgba(255, 255, 255, 0.08);',  # Columna Mediana
					'background-color: rgba(59, 130, 246, 0.15);',   # Columna Desv. Est.
					'background-color: rgba(16, 185, 129, 0.15);',   # Columna Mínimo
					'background-color: rgba(245, 158, 11, 0.15);'    # Columna Máximo
				], axis=1
			).set_table_styles([
				{'selector': 'th.col_heading', 'props': 'background-color: rgba(220, 38, 38, 0.3); color: white; font-weight: bold;'},
				{'selector': 'th.row_heading', 'props': 'background-color: rgba(31, 41, 55, 0.8); color: white; font-weight: bold; text-align: left;'},
				{'selector': 'td', 'props': 'text-align: center; padding: 8px;'}
			]),
			use_container_width=True
		)
		
		# === Análisis Z-Score Grupal ===
		st.markdown("---")
		st.markdown("### 🎯 Análisis Z-Score del Grupo")
		
		# Crear radar Z-Score grupal
		fig_radar_grupo = crear_radar_zscore_grupo(datos_grupo, categoria)
		
		if fig_radar_grupo:
			st.plotly_chart(fig_radar_grupo, use_container_width=True, config=PLOTLY_CONFIG)
		else:
			st.warning("No hay suficientes datos Z-Score para mostrar el radar grupal.")
			
	else:
		st.warning("⚠️ Selecciona al menos una métrica para visualizar el análisis grupal.")
