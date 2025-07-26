"""
Módulo de análisis de comparación jugador vs grupo
Club Atlético Colón
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

from config.settings import (
	COLORES, METRICAS_POR_SECCION, Z_SCORE_METRICAS, 
	ESCUDO_PATH, CACHE_TTL
)
from utils.data_utils import (
	preparar_datos_jugador, procesar_datos_categoria,
	calcular_estadisticas_categoria
)
from utils.ui_utils import get_base64_image
from visualizations.charts import crear_grafico_multifuerza, crear_radar_zscore


@st.cache_data(ttl=CACHE_TTL['graficos'], show_spinner=False)
def crear_grafico_comparacion_multifuerza(df, jugador_data, categoria, jugador_nombre, metricas_seleccionadas):
	"""
	Crea gráfico de comparación jugador vs grupo con el mismo estilo del individual
	"""
	# Configuración de métricas
	metricas_columnas = {
		"CUAD 70°": ("CUAD 70° Der", "CUAD 70° Izq"),
		"ISQ Wollin": ("ISQ Wollin Der", "ISQ Wollin Izq"),
		"IMTP": ("IMTP F. Der (N)", "IMTP F. Izq (N)"),
		"CMJ": ("CMJ F. Der (N)", "CMJ F. Izq (N)")
	}
	
	# Datos del jugador individual
	columnas_tabla = METRICAS_POR_SECCION["Fuerza"]
	datos_jugador = preparar_datos_jugador(jugador_data, columnas_tabla)
	
	# Datos del grupo (estadísticas)
	datos_grupo = procesar_datos_categoria(df, categoria)
	media_dict, std_dict = calcular_estadisticas_categoria(datos_grupo, columnas_tabla)
	
	# Preparar datos para el gráfico combinado
	barras_jugador_der, barras_jugador_izq = [], []
	barras_grupo_der, barras_grupo_izq = [], []
	std_grupo_der, std_grupo_izq = [], []
	nombres = []
	lsi_labels = {}
	
	for metrica in metricas_seleccionadas:
		if metrica == "CMJ":
			# CMJ Propulsiva
			val_jug_der_prop = datos_jugador.get("CMJ F. Der (N)", 0)
			val_jug_izq_prop = datos_jugador.get("CMJ F. Izq (N)", 0)
			val_grupo_der_prop = media_dict.get("CMJ F. Der (N)", 0)
			val_grupo_izq_prop = media_dict.get("CMJ F. Izq (N)", 0)
			std_der_prop = std_dict.get("CMJ F. Der (N)", 0)
			std_izq_prop = std_dict.get("CMJ F. Izq (N)", 0)
			lsi_fp = jugador_data.get("CMJ FP LSI (%) I/D", None)
			
			barras_jugador_der.append(val_jug_der_prop)
			barras_jugador_izq.append(val_jug_izq_prop)
			barras_grupo_der.append(val_grupo_der_prop)
			barras_grupo_izq.append(val_grupo_izq_prop)
			std_grupo_der.append(std_der_prop)
			std_grupo_izq.append(std_izq_prop)
			nombres.append("CMJ Prop")
			lsi_labels["CMJ Prop"] = lsi_fp
			
			# CMJ Frenado
			val_jug_der_fren = datos_jugador.get("CMJ F. Der (N).1", 0)
			val_jug_izq_fren = datos_jugador.get("CMJ F. Izq (N).1", 0)
			val_grupo_der_fren = media_dict.get("CMJ F. Der (N).1", 0)
			val_grupo_izq_fren = media_dict.get("CMJ F. Izq (N).1", 0)
			std_der_fren = std_dict.get("CMJ F. Der (N).1", 0)
			std_izq_fren = std_dict.get("CMJ F. Izq (N).1", 0)
			lsi_ff = jugador_data.get("CMJ FF LSI (%) I/D", None)
			
			barras_jugador_der.append(val_jug_der_fren)
			barras_jugador_izq.append(val_jug_izq_fren)
			barras_grupo_der.append(val_grupo_der_fren)
			barras_grupo_izq.append(val_grupo_izq_fren)
			std_grupo_der.append(std_der_fren)
			std_grupo_izq.append(std_izq_fren)
			nombres.append("CMJ Fren")
			lsi_labels["CMJ Fren"] = lsi_ff
		else:
			col_der, col_izq = metricas_columnas[metrica]
			val_jug_der = datos_jugador.get(col_der, 0)
			val_jug_izq = datos_jugador.get(col_izq, 0)
			val_grupo_der = media_dict.get(col_der, 0)
			val_grupo_izq = media_dict.get(col_izq, 0)
			std_der = std_dict.get(col_der, 0)
			std_izq = std_dict.get(col_izq, 0)
			
			barras_jugador_der.append(val_jug_der)
			barras_jugador_izq.append(val_jug_izq)
			barras_grupo_der.append(val_grupo_der)
			barras_grupo_izq.append(val_grupo_izq)
			std_grupo_der.append(std_der)
			std_grupo_izq.append(std_izq)
			nombres.append(metrica)
	
	# Crear figura con el mismo estilo del gráfico individual
	fig = go.Figure()
	
	# Barras del JUGADOR (Derecho) - Estilo idéntico al gráfico grupal
	fig.add_trace(go.Bar(
		x=nombres,
		y=barras_jugador_der,
		name=f"🔴 {jugador_nombre} (Der)",
		marker=dict(
			color=COLORES['rojo_colon'],
			pattern=dict(
				shape="",
				bgcolor="rgba(220, 38, 38, 0.3)",
				fgcolor="rgba(220, 38, 38, 1)"
			),
			opacity=0.9
		),
		text=[f"{v:.0f} N" for v in barras_jugador_der],
		textposition="outside",
		textfont=dict(size=13, color="white", family="Roboto", weight="bold"),
		hovertemplate=f'<b>🔴 {jugador_nombre} (Derecho)</b><br>%{{x}}: %{{y:.0f}} N<br><i>👤 VALOR INDIVIDUAL</i><extra></extra>',
		offsetgroup=1,
		hoverlabel=dict(
			bgcolor="rgba(220, 38, 38, 0.9)",
			bordercolor="rgba(220, 38, 38, 1)",
			font=dict(color="white", family="Roboto")
		)
	))
	
	# Barras del JUGADOR (Izquierdo) - Estilo idéntico al gráfico grupal
	fig.add_trace(go.Bar(
		x=nombres,
		y=barras_jugador_izq,
		name=f"⚫ {jugador_nombre} (Izq)",
		marker=dict(
			color=COLORES['negro_colon'],
			pattern=dict(
				shape="",
				bgcolor="rgba(31, 41, 55, 0.3)",
				fgcolor="rgba(31, 41, 55, 1)"
			),
			opacity=0.9
		),
		text=[f"{v:.0f} N" for v in barras_jugador_izq],
		textposition="outside",
		textfont=dict(size=13, color="white", family="Roboto", weight="bold"),
		hovertemplate=f'<b>⚫ {jugador_nombre} (Izquierdo)</b><br>%{{x}}: %{{y:.0f}} N<br><i>👤 VALOR INDIVIDUAL</i><extra></extra>',
		offsetgroup=2,
		hoverlabel=dict(
			bgcolor="rgba(31, 41, 55, 0.9)",
			bordercolor="rgba(31, 41, 55, 1)",
			font=dict(color="white", family="Roboto")
		)
	))
	
	# Barras del GRUPO (Derecho) - Estilo idéntico al gráfico grupal con barras de error
	fig.add_trace(go.Bar(
		x=nombres,
		y=barras_grupo_der,
		error_y=dict(type='data', array=std_grupo_der, visible=True, color='rgba(255,255,255,0.3)', thickness=0),
		name=f"🔴 {categoria} Promedio (Der)",
		marker=dict(
			color=COLORES['rojo_colon'],
			pattern=dict(
				shape="",
				bgcolor="rgba(220, 38, 38, 0.3)",
				fgcolor="rgba(220, 38, 38, 1)"
			),
			opacity=0.9
		),
		text=[f"{v:.0f} N" for v in barras_grupo_der],
		textposition="outside",
		textfont=dict(size=13, color="white", family="Roboto", weight="bold"),
		hovertemplate=f'<b>🔴 {categoria} (Derecho)</b><br>%{{x}}: %{{y:.0f}} N<br><i>👥 PROMEDIO GRUPAL ± %{{error_y.array:.0f}}</i><extra></extra>',
		offsetgroup=3,
		hoverlabel=dict(
			bgcolor="rgba(220, 38, 38, 0.8)",
			bordercolor="rgba(220, 38, 38, 1)",
			font=dict(color="white", family="Roboto")
		)
	))
	
	# Barras del GRUPO (Izquierdo) - Estilo idéntico al gráfico grupal con barras de error
	fig.add_trace(go.Bar(
		x=nombres,
		y=barras_grupo_izq,
		error_y=dict(type='data', array=std_grupo_izq, visible=True, color='rgba(255,255,255,0.3)', thickness=0),
		name=f"⚫ {categoria} Promedio (Izq)",
		marker=dict(
			color=COLORES['negro_colon'],
			pattern=dict(
				shape="",
				bgcolor="rgba(31, 41, 55, 0.3)",
				fgcolor="rgba(31, 41, 55, 1)"
			),
			opacity=0.9
		),
		text=[f"{v:.0f} N" for v in barras_grupo_izq],
		textposition="outside",
		textfont=dict(size=13, color="white", family="Roboto", weight="bold"),
		hovertemplate=f'<b>⚫ {categoria} (Izquierdo)</b><br>%{{x}}: %{{y:.0f}} N<br><i>👥 PROMEDIO GRUPAL ± %{{error_y.array:.0f}}</i><extra></extra>',
		offsetgroup=4,
		hoverlabel=dict(
			bgcolor="rgba(31, 41, 55, 0.8)",
			bordercolor="rgba(31, 41, 55, 1)",
			font=dict(color="white", family="Roboto")
		)
	))
	
	# Anotaciones LSI (igual que en el gráfico individual)
	for name in nombres:
		if name == "CUAD 70°":
			lsi_val = jugador_data.get("CUAD LSI (%)", None)
		elif name == "ISQ Wollin":
			lsi_val = jugador_data.get("ISQUIO LSI (%)", None)
		elif name == "IMTP":
			lsi_val = jugador_data.get("IMTP LSI (%)", None)
		else:
			lsi_val = lsi_labels.get(name)
		
		if lsi_val and lsi_val > 0:
			idx = nombres.index(name)
			
			# Determinar color según rango LSI
			if 90 <= lsi_val <= 110:  # Zona óptima
				lsi_color = COLORES['verde_optimo']
				border_color = "rgba(50, 205, 50, 1)"
			elif 80 <= lsi_val < 90 or 110 < lsi_val <= 120:  # Zona de alerta
				lsi_color = COLORES['naranja_alerta']
				border_color = "rgba(255, 165, 0, 1)"
			else:  # Zona de riesgo
				lsi_color = COLORES['rojo_riesgo']
				border_color = "rgba(255, 69, 0, 1)"
			
			# Obtener la altura máxima para posicionar la anotación
			max_altura = max(
				barras_jugador_der[idx], 
				barras_jugador_izq[idx],
				barras_grupo_der[idx],
				barras_grupo_izq[idx]
			)
			
			fig.add_annotation(
				text=f"<b>LSI: {lsi_val:.1f}%</b>",
				x=name,
				y=max_altura * 1.4,
				showarrow=False,
				font=dict(size=11, color="white", family="Roboto", weight="bold"),
				xanchor="center",
				align="center",
				bgcolor=lsi_color,
				bordercolor=border_color,
				borderwidth=2,
				borderpad=8,
				opacity=0.95
			)
	
	# Configuración del layout - Exactamente igual que el gráfico grupal
	fig.update_layout(
		barmode="group",
		bargap=0.3,
		bargroupgap=0.1,
		title=dict(
			text=f"⚽ Comparación: {jugador_nombre} vs {categoria} – Atlético Colón ⚽<br><span style='font-size:16px; color:rgba(255,255,255,0.8);'>Individual vs Promedio Grupal – Métricas de Fuerza</span>",
			font=dict(size=18, family="Roboto", weight="bold", color="rgba(220, 38, 38, 1)"),
			y=0.94,
			x=0.5,
			xanchor="center"
		),
		xaxis=dict(
			title=dict(
				text="Métrica", 
				font=dict(size=14, family="Roboto"),
				standoff=20
			),
			tickfont=dict(size=12, family="Roboto"),
			showgrid=True,
			gridwidth=1,
			gridcolor="rgba(255,255,255,0.1)",
			tickangle=0,
			categoryorder="array",
			categoryarray=nombres
		),
		yaxis=dict(
			title=dict(
				text="Fuerza (N)", 
				font=dict(size=14, family="Roboto"),
				standoff=15
			),
			tickfont=dict(size=12, family="Roboto"),
			showgrid=True,
			gridwidth=1,
			gridcolor="rgba(255,255,255,0.1)",
			zeroline=True,
			zerolinewidth=2,
			zerolinecolor="rgba(255,255,255,0.3)"
		),
		legend=dict(
			orientation="h",
			yanchor="bottom",
			y=1.02,
			xanchor="center",
			x=0.5,
			font=dict(size=12, family="Roboto"),
			bgcolor="rgba(220, 38, 38, 0.2)",
			bordercolor="rgba(220, 38, 38, 0.5)",
			borderwidth=2
		),
		plot_bgcolor=COLORES['fondo_oscuro'],
		paper_bgcolor=COLORES['fondo_oscuro'],
		font=dict(color="white", family="Roboto"),
		height=650,
		margin=dict(t=140, b=60, l=60, r=60),
		showlegend=True,
		transition=dict(
			duration=800,
			easing="cubic-in-out"
		),
		hovermode='x unified'
	)
	
	# Logo como marca de agua - Misma posición que el gráfico grupal
	try:
		escudo_base64 = get_base64_image(ESCUDO_PATH)
		fig.add_layout_image(
			dict(
				source=f"data:image/png;base64,{escudo_base64}",
				xref="paper", yref="paper",
				x=0.95, y=0.05,
				sizex=0.15, sizey=0.15,
				xanchor="right", yanchor="bottom",
				opacity=0.1,
				layer="below"
			)
		)
	except:
		pass
	
	return fig


@st.cache_data(ttl=CACHE_TTL['graficos'], show_spinner=False)
def crear_radar_comparacion_zscore(df, jugador_data, categoria, jugador_nombre):
	"""
	Crea radar de comparación Z-Score jugador vs grupo
	"""
	# Datos del jugador
	datos_jugador = {}
	for col in Z_SCORE_METRICAS.keys():
		if col in jugador_data.index:
			valor = jugador_data[col]
			if pd.notna(valor) and isinstance(valor, (int, float)):
				datos_jugador[Z_SCORE_METRICAS[col]] = valor
	
	# Datos del grupo (promedios Z-Score)
	datos_grupo_filtrados = df[df["categoria"] == categoria]
	datos_grupo = {}
	for col in Z_SCORE_METRICAS.keys():
		if col in datos_grupo_filtrados.columns:
			valores_validos = datos_grupo_filtrados[col].dropna()
			valores_numericos = [v for v in valores_validos if isinstance(v, (int, float))]
			if valores_numericos:
				datos_grupo[Z_SCORE_METRICAS[col]] = np.mean(valores_numericos)
	
	# Crear figura con subplots
	fig = make_subplots(
		rows=1, cols=2,
		specs=[[{"type": "polar"}, {"type": "polar"}]],
		subplot_titles=(
			f"🔴 {jugador_nombre} (Z-Score Individual)",
			f"👥 {categoria} (Z-Score Promedio Grupal)"
		),
		horizontal_spacing=0.1
	)
	
	# Radar individual
	if datos_jugador:
		categorias_jugador = list(datos_jugador.keys())
		valores_jugador = list(datos_jugador.values())
		
		fig.add_trace(
			go.Scatterpolar(
				r=valores_jugador,
				theta=categorias_jugador,
				fill='toself',
				fillcolor='rgba(220, 38, 38, 0.25)',
				line=dict(color=COLORES['rojo_colon'], width=3),
				marker=dict(color=COLORES['rojo_colon'], size=8, line=dict(color="white", width=2)),
				name=f"{jugador_nombre}",
				showlegend=False,
				hovertemplate="<b>%{theta}</b><br>Z-Score: %{r:.2f}<extra></extra>"
			),
			row=1, col=1
		)
	
	# Radar grupal
	if datos_grupo:
		categorias_grupo = list(datos_grupo.keys())
		valores_grupo = list(datos_grupo.values())
		
		fig.add_trace(
			go.Scatterpolar(
				r=valores_grupo,
				theta=categorias_grupo,
				fill='toself',
				fillcolor='rgba(59, 130, 246, 0.25)',
				line=dict(color=COLORES['azul_zscore'], width=3),
				marker=dict(color=COLORES['azul_zscore'], size=8, line=dict(color="white", width=2)),
				name=f"{categoria} (Promedio)",
				showlegend=False,
				hovertemplate="<b>%{theta}</b><br>Z-Score Promedio: %{r:.2f}<extra></extra>"
			),
			row=1, col=2
		)
	
	# Configuración de layout
	fig.update_layout(
		title=dict(
			text="⚽ Comparación Z-Score: Jugador vs Grupo – Atlético Colón ⚽",
			x=0.5,
			font=dict(size=18, color="white", family="Roboto", weight="bold")
		),
		height=600,
		plot_bgcolor='rgba(0,0,0,0)',
		paper_bgcolor='rgba(0,0,0,0)',
		font=dict(family="Roboto", color="white"),
		margin=dict(l=50, r=50, t=80, b=50)
	)
	
	# Configurar polares
	for i in [1, 2]:
		fig.update_polars(
			radialaxis=dict(
				visible=True,
				range=[-3, 3],
				tickfont=dict(size=10, color="white"),
				gridcolor="rgba(255,255,255,0.3)",
				linecolor="rgba(255,255,255,0.3)"
			),
			angularaxis=dict(
				tickfont=dict(size=11, color="white", family="Roboto"),
				linecolor="rgba(255,255,255,0.3)",
				gridcolor="rgba(255,255,255,0.3)"
			),
			bgcolor="rgba(0,0,0,0)",
			subplot=f"polar{i}" if i > 1 else "polar"
		)
	
	# Leyenda interpretativa
	fig.add_annotation(
		text="<b>Interpretación Z-Score:</b><br>" +
			 "🟢 Excelente: > 1.5<br>" +
			 "🔵 Bueno: 0.5 a 1.5<br>" +
			 "🟡 Promedio: -0.5 a 0.5<br>" +
			 "🟠 Bajo promedio: -1.5 a -0.5<br>" +
			 "🔴 Deficiente: < -1.5",
		xref="paper", yref="paper",
		x=0.02, y=0.98,
		xanchor="left", yanchor="top",
		bgcolor="rgba(40, 40, 40, 0.9)",
		bordercolor=COLORES['azul_zscore'],
		borderwidth=2,
		font=dict(size=10, color="white", family="Roboto")
	)
	
	return fig


@st.cache_data(ttl=CACHE_TTL['estadisticas'], show_spinner=False)
def calcular_metricas_comparacion(df, jugador_data, categoria, jugador_nombre):
	"""
	Calcula métricas de comparación entre jugador y grupo
	"""
	# Obtener métricas de fuerza
	METRICAS_FUERZA = list(METRICAS_POR_SECCION["Fuerza"].keys())
	
	# Datos del grupo
	datos_grupo = procesar_datos_categoria(df, categoria)
	media_dict, std_dict = calcular_estadisticas_categoria(datos_grupo, columnas_tabla)
	
	# Datos del jugador
	columnas_tabla = METRICAS_POR_SECCION["Fuerza"]
	datos_jugador = preparar_datos_jugador(jugador_data, columnas_tabla)
	
	comparaciones = {}
	
	for metrica in METRICAS_FUERZA:
		if metrica in datos_jugador and metrica in media_dict:
			comparaciones[metrica] = {}
			
			# Lado derecho
			if metrica in datos_jugador:
				valor_jugador_der = datos_jugador[metrica]
				promedio_grupo_der = media_dict[metrica]
				std_grupo_der = std_dict[metrica]
				
				# Calcular diferencias para lado derecho
				diferencia_der = valor_jugador_der - promedio_grupo_der
				diferencia_porcentual_der = (diferencia_der / promedio_grupo_der) * 100 if promedio_grupo_der != 0 else 0
				z_score_relativo_der = diferencia_der / std_grupo_der if std_grupo_der != 0 else 0
				
				comparaciones[metrica]['Derecho'] = {
					'valor_jugador': valor_jugador_der,
					'promedio_grupo': promedio_grupo_der,
					'std_grupo': std_grupo_der,
					'diferencia': diferencia_der,
					'diferencia_porcentual': diferencia_porcentual_der,
					'z_score_relativo': z_score_relativo_der
				}
			
			# Lado izquierdo
			metrica_izq = columnas_tabla[metrica]
			if metrica_izq in datos_jugador:
				valor_jugador_izq = datos_jugador[metrica_izq]
				promedio_grupo_izq = media_dict[metrica_izq]
				std_grupo_izq = std_dict[metrica_izq]
				
				# Calcular diferencias para lado izquierdo
				diferencia_izq = valor_jugador_izq - promedio_grupo_izq
				diferencia_porcentual_izq = (diferencia_izq / promedio_grupo_izq) * 100 if promedio_grupo_izq != 0 else 0
				z_score_relativo_izq = diferencia_izq / std_grupo_izq if std_grupo_izq != 0 else 0
				
				comparaciones[metrica]['Izquierdo'] = {
					'valor_jugador': valor_jugador_izq,
					'promedio_grupo': promedio_grupo_izq,
					'std_grupo': std_grupo_izq,
					'diferencia': diferencia_izq,
					'diferencia_porcentual': diferencia_porcentual_izq,
					'z_score_relativo': z_score_relativo_izq
				}
	
	return comparaciones


def analizar_comparacion_fuerza(df, datos_jugador, jugador, categoria):
	"""
	Análisis completo de comparación jugador vs grupo para fuerza
	"""
	st.markdown(f"""
	<div style='background: linear-gradient(135deg, rgba(220, 38, 38, 0.2), rgba(59, 130, 246, 0.2)); 
				padding: 20px; border-radius: 15px; margin-bottom: 25px; 
				border-left: 5px solid rgba(220, 38, 38, 1);'>
		<h2 style='margin: 0; color: white; font-weight: bold;'>
			🔄 Comparación: {jugador} vs {categoria}
		</h2>
		<p style='margin: 5px 0 0 0; color: rgba(255,255,255,0.8); font-size: 16px;'>
			Análisis comparativo de rendimiento individual vs promedio grupal
		</p>
	</div>
	""", unsafe_allow_html=True)
	
	# Selección de métricas (igual que en el individual)
	metricas_disponibles = ["CUAD 70°", "ISQ Wollin", "IMTP", "CMJ"]
	metricas_seleccionadas = st.multiselect(
		"Selección de Métricas - Selecciona las evaluaciones de fuerza para la comparación:",
		metricas_disponibles,
		default=["CUAD 70°", "ISQ Wollin", "IMTP"]
	)
	
	if metricas_seleccionadas:
		st.markdown("### 📊 Comparación Individual vs Grupal")
		
		with st.spinner("Generando gráfico comparativo..."):
			fig_comparacion = crear_grafico_comparacion_multifuerza(df, datos_jugador, categoria, jugador, metricas_seleccionadas)
			st.plotly_chart(fig_comparacion, use_container_width=True, config={'displayModeBar': False})
		
		# Interpretación - Estilo idéntico al gráfico grupal
		st.markdown(f"""
		<div style='background: rgba(59, 130, 246, 0.1); padding: 15px; border-radius: 10px; margin-top: 20px;'>
			<h4 style='color: white; margin-top: 0;'>📖 Interpretación del Gráfico de Comparación</h4>
			<div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 10px;'>
				<div>
					<h5 style='color: #DC2626; margin: 0 0 8px 0;'>👤 JUGADOR INDIVIDUAL ({jugador})</h5>
					<ul style='color: rgba(255,255,255,0.9); margin: 0; font-size: 13px;'>
						<li><strong>Barras sólidas</strong> con estilo estándar</li>
						<li><strong>Valores exactos</strong> del jugador</li>
						<li><strong>LSI individual</strong> mostrado arriba</li>
						<li><strong>Mismo estilo</strong> que gráfico individual</li>
					</ul>
				</div>
				<div>
					<h5 style='color: #3B82F6; margin: 0 0 8px 0;'>👥 PROMEDIO GRUPAL ({categoria})</h5>
					<ul style='color: rgba(255,255,255,0.9); margin: 0; font-size: 13px;'>
						<li><strong>Mismo estilo</strong> que gráfico grupal</li>
						<li><strong>Barras de error</strong> muestran ±SD</li>
						<li><strong>Valores promedio</strong> del grupo</li>
						<li><strong>Consistencia visual</strong> total</li>
					</ul>
				</div>
			</div>
			<div style='margin-top: 15px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.2);'>
				<p style='color: rgba(255,255,255,0.8); margin: 0; font-size: 13px; text-align: center;'>
					<strong>Comparación:</strong> Estilo visual idéntico a los gráficos individuales y grupales para máxima consistencia
				</p>
			</div>
		</div>
		""")
	else:
		st.warning("⚠️ Selecciona al menos una métrica para mostrar la comparación.")
