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
	
	# Crear columnas extendidas que incluyan CMJ Frenado
	columnas_tabla = METRICAS_POR_SECCION["Fuerza"]
	columnas_extendidas = columnas_tabla.copy()
	columnas_extendidas["CMJ F. Der (N).1"] = "CMJ F. Izq (N).1"  # CMJ Frenado
	
	# Datos del jugador individual (con columnas extendidas)
	datos_jugador = preparar_datos_jugador(jugador_data, columnas_extendidas)
	
	# Datos del grupo (estadísticas)
	datos_grupo = procesar_datos_categoria(df, categoria)
	media_dict, std_dict = calcular_estadisticas_categoria(datos_grupo, columnas_extendidas)
	
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
			color=COLORES['rojo_colon'],  # Rojo para jugador derecho
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
		name=f"🔵 {categoria} Promedio (Der)",
		marker=dict(
			color="rgba(59, 130, 246, 1)",  # Azul para grupo derecho
			pattern=dict(
				shape="",
				bgcolor="rgba(59, 130, 246, 0.3)",
				fgcolor="rgba(59, 130, 246, 1)"
			),
			opacity=0.9
		),
		text=[f"{v:.0f} N" for v in barras_grupo_der],
		textposition="outside",
		textfont=dict(size=13, color="white", family="Roboto", weight="bold"),
		hovertemplate=f'<b>🔵 {categoria} (Derecho)</b><br>%{{x}}: %{{y:.0f}} N<br><i>👥 PROMEDIO GRUPAL ± %{{error_y.array:.0f}}</i><extra></extra>',
		offsetgroup=3,
		hoverlabel=dict(
			bgcolor="rgba(59, 130, 246, 0.8)",
			bordercolor="rgba(59, 130, 246, 1)",
			font=dict(color="white", family="Roboto")
		)
	))
	
	# Barras del GRUPO (Izquierdo) - Estilo idéntico al gráfico grupal con barras de error
	fig.add_trace(go.Bar(
		x=nombres,
		y=barras_grupo_izq,
		error_y=dict(type='data', array=std_grupo_izq, visible=True, color='rgba(255,255,255,0.3)', thickness=0),
		name=f"🟢 {categoria} Promedio (Izq)",
		marker=dict(
			color="rgba(16, 185, 129, 1)",  # Verde para grupo izquierdo
			pattern=dict(
				shape="",
				bgcolor="rgba(16, 185, 129, 0.3)",
				fgcolor="rgba(16, 185, 129, 1)"
			),
			opacity=0.9
		),
		text=[f"{v:.0f} N" for v in barras_grupo_izq],
		textposition="outside",
		textfont=dict(size=13, color="white", family="Roboto", weight="bold"),
		hovertemplate=f'<b>🟢 {categoria} (Izquierdo)</b><br>%{{x}}: %{{y:.0f}} N<br><i>👥 PROMEDIO GRUPAL ± %{{error_y.array:.0f}}</i><extra></extra>',
		offsetgroup=4,
		hoverlabel=dict(
			bgcolor="rgba(16, 185, 129, 0.8)",
			bordercolor="rgba(16, 185, 129, 1)",
			font=dict(color="white", family="Roboto")
		)
	))
	
	# Leyendas debajo de cada barra
	jugador_corto = jugador_nombre.split()[0] + " " + jugador_nombre.split()[1][0] + "." if len(jugador_nombre.split()) > 1 else jugador_nombre
	
	for i, name in enumerate(nombres):
		# Leyenda para barras del jugador (izquierda)
		fig.add_annotation(
			text=f"<b>{jugador_corto}</b>",
			x=i - 0.2,  # Posición ligeramente a la izquierda
			y=-50,  # Debajo del eje X
			showarrow=False,
			font=dict(size=10, color="white", family="Roboto", weight="bold"),
			xanchor="center",
			yanchor="top",
			xref="x",
			yref="y"
		)
		
		# Leyenda para barras del grupo (derecha)
		fig.add_annotation(
			text="<b>Promedio</b>",
			x=i + 0.2,  # Posición ligeramente a la derecha
			y=-50,  # Debajo del eje X
			showarrow=False,
			font=dict(size=10, color="white", family="Roboto", weight="bold"),
			xanchor="center",
			yanchor="top",
			xref="x",
			yref="y"
		)
	
	# Etiquetas D/I dentro de las barras - Posiciones corregidas
	for i, name in enumerate(nombres):
		# Calcular posiciones exactas según el barmode="group"
		# Con bargap=0.3 y bargroupgap=0.1, las posiciones son:
		pos_jugador_der = i - 0.225  # Barra jugador derecho
		pos_jugador_izq = i - 0.075  # Barra jugador izquierdo  
		pos_grupo_der = i + 0.075   # Barra grupo derecho
		pos_grupo_izq = i + 0.225   # Barra grupo izquierdo
		
		# D en barra del jugador (derecha) - Roja
		if barras_jugador_der[i] > 50:  # Solo si la barra es lo suficientemente alta
			fig.add_annotation(
				text="<b>D</b>",
				x=pos_jugador_der,
				y=barras_jugador_der[i] / 2,
				showarrow=False,
				font=dict(size=12, color="white", family="Roboto", weight="bold"),
				xanchor="center",
				yanchor="middle"
			)
		
		# I en barra del jugador (izquierda) - Negra
		if barras_jugador_izq[i] > 50:
			fig.add_annotation(
				text="<b>I</b>",
				x=pos_jugador_izq,
				y=barras_jugador_izq[i] / 2,
				showarrow=False,
				font=dict(size=12, color="white", family="Roboto", weight="bold"),
				xanchor="center",
				yanchor="middle"
			)
		
		# D en barra del grupo (derecha) - Azul
		if barras_grupo_der[i] > 50:
			fig.add_annotation(
				text="<b>D</b>",
				x=pos_grupo_der,
				y=barras_grupo_der[i] / 2,
				showarrow=False,
				font=dict(size=12, color="white", family="Roboto", weight="bold"),
				xanchor="center",
				yanchor="middle"
			)
		
		# I en barra del grupo (izquierda) - Verde
		if barras_grupo_izq[i] > 50:
			fig.add_annotation(
				text="<b>I</b>",
				x=pos_grupo_izq,
				y=barras_grupo_izq[i] / 2,
				showarrow=False,
				font=dict(size=12, color="white", family="Roboto", weight="bold"),
				xanchor="center",
				yanchor="middle"
			)
	
	# Configuración del layout - Exactamente igual que el gráfico grupal
	fig.update_layout(
		barmode="group",
		bargap=0.3,
		bargroupgap=0.1,
		title=dict(
			text=f"{jugador_nombre} vs Promedio del Grupo",
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
		margin=dict(t=140, b=90, l=60, r=60),  # Margen inferior aumentado para leyendas
		showlegend=False,  # Leyenda oculta para gráfico más limpio
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


@st.cache_data(ttl=CACHE_TTL['graficos'], show_spinner="Generando radar comparación Z-Score...")
def crear_radar_comparacion_zscore(df, jugador_data, categoria, jugador_nombre):
	"""
	Crea radar de comparación Z-Score jugador vs grupo en un solo gráfico - Estilo unificado
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
	
	# Obtener todas las métricas disponibles (unión de ambos conjuntos)
	metricas_disponibles = set(datos_jugador.keys()) | set(datos_grupo.keys())
	metricas_ordenadas = sorted(list(metricas_disponibles))
	
	# Preparar datos para ambas series
	valores_jugador = [datos_jugador.get(metrica, 0) for metrica in metricas_ordenadas]
	valores_grupo = [datos_grupo.get(metrica, 0) for metrica in metricas_ordenadas]
	
	# Crear figura polar única
	fig = go.Figure()
	
	# Agregar serie del jugador individual (estilo idéntico a módulos individuales)
	fig.add_trace(
		go.Scatterpolar(
			r=valores_jugador,
			theta=metricas_ordenadas,
			fill='toself',
			fillcolor='rgba(220, 38, 38, 0.25)',
			line=dict(color=COLORES['rojo_colon'], width=3),
			marker=dict(color=COLORES['rojo_colon'], size=8, line=dict(color="white", width=2)),
			name=f"👤 {jugador_nombre}",
			hovertemplate="<b>%{theta}</b><br>👤 Z-Score Individual: %{r:.2f}<extra></extra>"
		)
	)
	
	# Agregar serie del grupo promedio (estilo idéntico a módulos grupales)
	fig.add_trace(
		go.Scatterpolar(
			r=valores_grupo,
			theta=metricas_ordenadas,
			fill='toself',
			fillcolor='rgba(59, 130, 246, 0.25)',
			line=dict(color=COLORES['azul_zscore'], width=3),
			marker=dict(color=COLORES['azul_zscore'], size=8, line=dict(color="white", width=2)),
			name=f"👥 {categoria} (Promedio)",
			hovertemplate="<b>%{theta}</b><br>👥 Z-Score Promedio: %{r:.2f}<extra></extra>"
		)
	)
	
	# Agregar leyenda interpretativa integrada (estilo unificado)
	fig.add_annotation(
		text="<b>Interpretación Z-Score</b><br>" +
			 "<span style='color: #22c55e;'>Z > +1:</span> Superior al promedio<br>" +
			 "<span style='color: #fbbf24;'>Z = 0:</span> Rendimiento promedio<br>" +
			 "<span style='color: #ef4444;'>Z < -1:</span> Inferior al promedio",
		x=0.02,
		y=0.98,
		xref="paper",
		yref="paper",
		xanchor="left",
		yanchor="top",
		showarrow=False,
		font=dict(size=11, color="white", family="Roboto"),
		align="left",
		bgcolor="rgba(31, 41, 55, 0.9)",
		bordercolor="rgba(59, 130, 246, 0.8)",
		borderwidth=2,
		borderpad=10,
		opacity=0.95
	)
	
	# Configuración de layout (estilo unificado con otros módulos)
	fig.update_layout(
		polar=dict(
			radialaxis=dict(
				visible=True,
				range=[-3, 3],
				tickfont=dict(size=10, color="white"),
				gridcolor="rgba(255,255,255,0.3)",
				linecolor="rgba(255,255,255,0.5)"
			),
			angularaxis=dict(
				tickfont=dict(size=11, color="white", family="Roboto"),
				linecolor="rgba(255,255,255,0.5)",
				gridcolor="rgba(255,255,255,0.2)"
			),
			bgcolor=COLORES['fondo_oscuro']
		),
		showlegend=True,
		title=dict(
			text=f"Comparación Z-Score - {jugador_nombre} vs {categoria}",
			font=dict(size=16, color="white", family="Roboto", weight="bold"),
			x=0.5,
			xanchor="center"
		),
		plot_bgcolor=COLORES['fondo_oscuro'],
		paper_bgcolor=COLORES['fondo_oscuro'],
		font=dict(color="white", family="Roboto"),
		height=500,
		margin=dict(t=60, b=40, l=40, r=40),
		legend=dict(
			x=0.85, y=0.15,
			xanchor="left", yanchor="bottom",
			bgcolor="rgba(31, 41, 55, 0.9)",
			bordercolor="rgba(255,255,255,0.3)",
			borderwidth=1,
			font=dict(size=11, color="white", family="Roboto")
		)
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


def crear_tabla_comparacion_jugador_grupo(df, datos_jugador, categoria, jugador, metricas_seleccionadas):
	"""
	Crea una tabla comparativa entre el jugador y las estadísticas del grupo
	"""
	# Mapeo de métricas a columnas
	metricas_columnas = {
		"CUAD 70°": ("CUAD 70° Der", "CUAD 70° Izq"),
		"ISQ Wollin": ("ISQ Wollin Der", "ISQ Wollin Izq"),
		"IMTP": ("IMTP F. Der (N)", "IMTP F. Izq (N)"),
		"CMJ": ("CMJ F. Der (N)", "CMJ F. Izq (N)")
	}
	
	# Obtener datos del grupo (excluyendo al jugador actual para evitar sesgo)
	datos_grupo = df[(df["categoria"] == categoria) & (df["Deportista"] != jugador)]
	
	# Construir filas de la tabla
	filas_tabla = []
	indices_tabla = []
	
	for metrica in metricas_seleccionadas:
		if metrica in metricas_columnas:
			col_der, col_izq = metricas_columnas[metrica]
			
			# Valores del jugador - Convertir a numérico
			jugador_der = pd.to_numeric(datos_jugador[col_der], errors='coerce') if col_der in datos_jugador.index else 0
			jugador_izq = pd.to_numeric(datos_jugador[col_izq], errors='coerce') if col_izq in datos_jugador.index else 0
			
			# Estadísticas del grupo - Filtrar solo valores numéricos
			grupo_der = pd.to_numeric(datos_grupo[col_der], errors='coerce').dropna()
			grupo_izq = pd.to_numeric(datos_grupo[col_izq], errors='coerce').dropna()
			
			# Derecha
			if len(grupo_der) > 0 and pd.notna(jugador_der):
				media_grupo_der = grupo_der.mean()
				std_grupo_der = grupo_der.std()
				filas_tabla.append([jugador_der, media_grupo_der, std_grupo_der])
				indices_tabla.append(f"{metrica} Der")
			
			# Izquierda
			if len(grupo_izq) > 0 and pd.notna(jugador_izq):
				media_grupo_izq = grupo_izq.mean()
				std_grupo_izq = grupo_izq.std()
				filas_tabla.append([jugador_izq, media_grupo_izq, std_grupo_izq])
				indices_tabla.append(f"{metrica} Izq")
	
	# Crear DataFrame
	df_comparativo = pd.DataFrame(
		filas_tabla,
		columns=[f"{jugador}", f"Media {categoria}", f"Desv. Est. {categoria}"],
		index=indices_tabla
	)
	df_comparativo.index.name = "Métrica"
	
	return df_comparativo


def analizar_comparacion_fuerza(df, datos_jugador, jugador, categoria):
	"""
	Análisis completo de comparación jugador vs grupo para fuerza
	"""

	
	# Selección de métricas (igual que en el individual)
	metricas_disponibles = ["CUAD 70°", "ISQ Wollin", "IMTP", "CMJ"]
	metricas_seleccionadas = st.multiselect(
		"Selección de Métricas - Selecciona las evaluaciones de fuerza para la comparación:",
		metricas_disponibles,
		default=["CUAD 70°", "ISQ Wollin", "IMTP"]
	)
	
	if metricas_seleccionadas:
		st.markdown(f"### {jugador} vs Grupal")
		
		with st.spinner("Generando gráfico comparativo..."):
			fig_comparacion = crear_grafico_comparacion_multifuerza(df, datos_jugador, categoria, jugador, metricas_seleccionadas)
			st.plotly_chart(fig_comparacion, use_container_width=True, config={'displayModeBar': False})
		
		# === RADAR CHART Z-SCORES ===
		st.markdown("<br>", unsafe_allow_html=True)
		
		# Header para el radar chart
		st.markdown(f"""
		<div style='background: linear-gradient(90deg, rgba(220, 38, 38, 0.8), rgba(17, 24, 39, 0.8));
					border-left: 4px solid rgba(220, 38, 38, 1);'>
			<h4 style='margin: 0; color: white; font-size: 18px;'>
				Comparación Z-Score: {jugador} vs {categoria}
			</h4>
		</div>
		""", unsafe_allow_html=True)
		
		# Generar radar chart comparativo con cache optimizado
		fig_radar_comparacion = crear_radar_comparacion_zscore(df, datos_jugador, categoria, jugador)
		
		radar_config = {
			'displayModeBar': False,
			'toImageButtonOptions': {
				'filename': f'radar_zscore_comparacion_{jugador}_{categoria}',
				'height': 600,
				'width': 1000
			}
		}
		
		st.plotly_chart(fig_radar_comparacion, use_container_width=True, config=radar_config)
		
		# === TABLA COMPARATIVA ===
		st.markdown(f"#### {jugador} vs Grupo")
		
		with st.spinner("Generando tabla comparativa..."):
			df_tabla_comparacion = crear_tabla_comparacion_jugador_grupo(df, datos_jugador, categoria, jugador, metricas_seleccionadas)
			
			# Mostrar tabla con el mismo estilo que fuerza_analysis
			st.dataframe(
				df_tabla_comparacion.style.format("{:.1f}").apply(
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
		
		# Sección de comparación completada
		
	else:
		st.warning("⚠️ Selecciona al menos una métrica para mostrar la comparación.")
