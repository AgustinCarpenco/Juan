import json
import base64
import streamlit as st
import pandas as pd
from PIL import Image
import plotly.graph_objects as go
from functools import lru_cache
import hashlib

# ========= CONFIGURACIÓN DE ANIMACIONES ==========
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

# ========= CONFIGURACIÓN DE SESSION STATE ==========

# Inicializar session state para optimización
if 'df_cache' not in st.session_state:
	st.session_state.df_cache = None
if 'ultimo_jugador' not in st.session_state:
	st.session_state.ultimo_jugador = None
if 'ultima_categoria' not in st.session_state:
	st.session_state.ultima_categoria = None
if 'metricas_cache' not in st.session_state:
	st.session_state.metricas_cache = {}

# ========= FUNCIONES ==========

@st.cache_data(ttl=3600, show_spinner="Cargando datos de evaluaciones...")
def cargar_evaluaciones(path_excel):
	"""Carga y procesa datos de evaluaciones con cache optimizado"""
	df_4ta = pd.read_excel(path_excel, sheet_name="2005-06 (4ta)", header=1)
	df_reserva = pd.read_excel(path_excel, sheet_name="RESERVA", header=1)

	df_4ta["categoria"] = "4ta"
	df_reserva["categoria"] = "Reserva"

	df_total = pd.concat([df_4ta, df_reserva], ignore_index=True)
	return df_total

@lru_cache(maxsize=32)
def get_base64_image(image_path):
	"""Convierte imagen a base64 con cache LRU"""
	with open(image_path, "rb") as img_file:
		encoded = base64.b64encode(img_file.read()).decode()
	return encoded

@st.cache_data(ttl=600)
def crear_hash_jugador(datos_jugador):
	"""Crea hash único para datos del jugador para optimizar cache"""
	# Convertir Series a dict para hashear
	if hasattr(datos_jugador, 'to_dict'):
		datos_dict = datos_jugador.to_dict()
	else:
		datos_dict = dict(datos_jugador)
	
	# Crear hash único basado en los datos
	datos_str = json.dumps(datos_dict, sort_keys=True, default=str)
	hash_obj = hashlib.md5(datos_str.encode())
	return hash_obj.hexdigest()

@st.cache_data(ttl=1200)
def procesar_datos_categoria(df, categoria):
	"""Procesa y filtra datos por categoría con cache"""
	df_categoria = df[df["categoria"] == categoria].copy()
	
	# FILTRAR filas de resumen estadístico
	valores_a_excluir = ['MEDIA', 'SD', 'TOTAL EN RIESGO ALTO', 'RIESGO RELATIVO', 
						'TOTAL EN RIESGO MODERADO', 'TOTAL EN BAJO RIESGO', 
						'Apellido y Nombre', 'ALTO RIESGO', 'MODERADO RIESGO', 'BAJO RIESGO']
	
	df_categoria = df_categoria[
		(~df_categoria['Deportista'].isin(valores_a_excluir)) & 
		(df_categoria['Deportista'].notna()) &
		(~df_categoria['Deportista'].str.contains('RIESGO|MEDIA|TOTAL|SD', case=False, na=False))
	].copy()
	
	return df_categoria

@st.cache_data(ttl=900)
def calcular_estadisticas_categoria(df_categoria, columnas_tabla):
	"""Calcula medias y desviaciones estándar con cache"""
	# Forzar a número para evitar errores silenciosos
	for col in list(columnas_tabla.keys()) + list(columnas_tabla.values()):
		df_categoria[col] = pd.to_numeric(df_categoria[col], errors="coerce")

	# Calcular medias del grupo
	media_dict = {}
	for col_der, col_izq in columnas_tabla.items():
		media_dict[col_der] = round(df_categoria[col_der].mean(skipna=True), 1)
		media_dict[col_izq] = round(df_categoria[col_izq].mean(skipna=True), 1)

	# Calcular desviaciones estándar del grupo
	std_dict = {}
	for col_der, col_izq in columnas_tabla.items():
		std_dict[col_der] = round(df_categoria[col_der].std(skipna=True), 1)
		std_dict[col_izq] = round(df_categoria[col_izq].std(skipna=True), 1)
	
	return media_dict, std_dict

@st.cache_data(ttl=600)
def preparar_datos_jugador(datos_jugador, columnas_tabla):
	"""Prepara datos del jugador para visualización con cache"""
	jugador_dict = {}
	for col_der, col_izq in columnas_tabla.items():
		jugador_dict[col_der] = round(datos_jugador.get(col_der, 0), 1)
		jugador_dict[col_izq] = round(datos_jugador.get(col_izq, 0), 1)
	return jugador_dict

def cargar_datos_optimizado(path_excel):
	"""Carga datos con optimización de session state"""
	if 'df_cache' not in st.session_state or st.session_state.df_cache is None:
		st.session_state.df_cache = cargar_evaluaciones(path_excel)
	return st.session_state.df_cache

def limpiar_cache_si_cambio(jugador, categoria):
	"""Limpia cache si hay cambio en la selección"""
	if (st.session_state.get('ultimo_jugador') != jugador or 
		st.session_state.get('ultima_categoria') != categoria):
		# Limpiar cache de métricas al cambiar selección
		st.session_state.metricas_cache = {}
		return True
	return False

@st.cache_data(ttl=1800, show_spinner="Generando gráfico de fuerza...")
def crear_grafico_multifuerza(datos_jugador_hash, metricas_seleccionadas, metricas_columnas):
	"""Crea gráfico de multifuerza con cache optimizado"""
	# Reconstruir datos del jugador desde hash
	datos_jugador = datos_jugador_hash
	barras_der, barras_izq, nombres = [], [], []
	lsi_labels = {}

	for metrica in metricas_seleccionadas:
		if metrica == "CMJ":
			# Propulsiva
			val_der_prop = datos_jugador.get("CMJ F. Der (N)", 0)
			val_izq_prop = datos_jugador.get("CMJ F. Izq (N)", 0)
			lsi_fp = datos_jugador.get("CMJ FP LSI (%) I/D", None)

			barras_der.append(val_der_prop)
			barras_izq.append(val_izq_prop)
			nombres.append("CMJ Prop")
			lsi_labels["CMJ Prop"] = lsi_fp

			# Frenado
			val_der_fren = datos_jugador.get("CMJ F. Der (N).1", 0)
			val_izq_fren = datos_jugador.get("CMJ F. Izq (N).1", 0)
			lsi_ff = datos_jugador.get("CMJ FF LSI (%) I/D", None)

			barras_der.append(val_der_fren)
			barras_izq.append(val_izq_fren)
			nombres.append("CMJ Fren")
			lsi_labels["CMJ Fren"] = lsi_ff
		else:
			col_der, col_izq = metricas_columnas[metrica]
			val_der = datos_jugador.get(col_der, 0)
			val_izq = datos_jugador.get(col_izq, 0)
			barras_der.append(val_der)
			barras_izq.append(val_izq)
			nombres.append(metrica)

	fig = go.Figure()

	fig.add_trace(go.Bar(
		x=nombres,
		y=barras_der,
		name="🔴 Derecho",
		marker=dict(
			color="rgba(220, 38, 38, 0.85)",  # Rojo Colón
			line=dict(width=2.5, color="rgba(220, 38, 38, 1)"),
			pattern=dict(
				shape="",
				bgcolor="rgba(220, 38, 38, 0.3)",
				fgcolor="rgba(220, 38, 38, 1)"
			),
			# Simulación de bordes redondeados con gradiente
			opacity=0.9
		),
		text=[f"{v:.0f} N" for v in barras_der],
		textposition="outside",
		textfont=dict(size=13, color="white", family="Roboto", weight="bold"),
		hovertemplate='<b>🔴 Derecho</b><br>%{x}: %{y:.0f} N<br><i>Lado dominante</i><extra></extra>',
		# Efecto de sombra simulado
		offsetgroup=1,
		# Animaciones y hover effects
		hoverlabel=dict(
			bgcolor="rgba(220, 38, 38, 0.9)",
			bordercolor="rgba(220, 38, 38, 1)",
			font=dict(color="white", family="Roboto")
		)
	))

	fig.add_trace(go.Bar(
		x=nombres,
		y=barras_izq,
		name="⚫ Izquierdo",
		marker=dict(
			color="rgba(31, 41, 55, 0.85)",  # Negro Colón
			line=dict(width=2.5, color="rgba(31, 41, 55, 1)"),
			pattern=dict(
				shape="",
				bgcolor="rgba(31, 41, 55, 0.3)",
				fgcolor="rgba(31, 41, 55, 1)"
			),
			# Simulación de bordes redondeados con gradiente
			opacity=0.9
		),
		text=[f"{v:.0f} N" for v in barras_izq],
		textposition="outside",
		textfont=dict(size=13, color="white", family="Roboto", weight="bold"),
		hovertemplate='<b>⚫ Izquierdo</b><br>%{x}: %{y:.0f} N<br><i>Lado no dominante</i><extra></extra>',
		# Efecto de sombra simulado
		offsetgroup=2,
		# Animaciones y hover effects
		hoverlabel=dict(
			bgcolor="rgba(31, 41, 55, 0.9)",
			bordercolor="rgba(31, 41, 55, 1)",
			font=dict(color="white", family="Roboto")
		)
	))

	# LSI annotations
	for name in nombres:
		if name == "CUAD 70°":
			lsi_val = datos_jugador.get("CUAD LSI (%)", None)
		elif name == "ISQ Wollin":
			lsi_val = datos_jugador.get("ISQUIO LSI (%)", None)
		elif name == "IMTP":
			lsi_val = datos_jugador.get("IMTP LSI (%)", None)
		else:
			lsi_val = lsi_labels.get(name)

		if lsi_val and lsi_val > 0:
			idx = nombres.index(name)
			
			# Determinar color según rango LSI
			if 90 <= lsi_val <= 110:  # Zona óptima
				lsi_color = "rgba(50, 205, 50, 0.9)"  # Verde
				border_color = "rgba(50, 205, 50, 1)"
			elif 80 <= lsi_val < 90 or 110 < lsi_val <= 120:  # Zona de alerta
				lsi_color = "rgba(255, 165, 0, 0.9)"  # Naranja
				border_color = "rgba(255, 165, 0, 1)"
			else:  # Zona de riesgo
				lsi_color = "rgba(255, 69, 0, 0.9)"  # Rojo
				border_color = "rgba(255, 69, 0, 1)"
			
			fig.add_annotation(
				text=f"<b>LSI: {lsi_val:.1f}%</b>",
				x=name,
				y=max(barras_der[idx], barras_izq[idx]) * 1.35,  # Mayor separación
				showarrow=False,
				font=dict(size=11, color="white", family="Roboto", weight="bold"),
				xanchor="center",
				align="center",
				bgcolor=lsi_color,
				bordercolor=border_color,
				borderwidth=2,
				borderpad=8,  # Más padding
				# Simulación de bordes redondeados
				opacity=0.95
			)
	
	# Agregar logo del club como marca de agua
	try:
		escudo_base64 = get_base64_image("/Users/agustin/Documents/Agustin_2025/Juan Colon/data/escudo.png")
		fig.add_layout_image(
			dict(
				source=f"data:image/png;base64,{escudo_base64}",
				xref="paper", yref="paper",
				x=0.95, y=0.05,  # Esquina inferior derecha
				sizex=0.15, sizey=0.15,
				xanchor="right", yanchor="bottom",
				opacity=0.1,  # Muy sutil
				layer="below"
			)
		)
	except:
		pass  # Si no encuentra el logo, continúa sin él

	fig.update_layout(
		barmode="group",
		bargap=0.3,  # Espaciado entre grupos de barras
		bargroupgap=0.1,  # Espaciado dentro de cada grupo
		title=dict(
			text="⚽ Evaluación Física Integral – Atlético Colón ⚽<br><span style='font-size:16px; color:rgba(255,255,255,0.8);'>Comparación Derecha/Izquierda – Métricas de Fuerza</span>",
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
			bgcolor="rgba(220, 38, 38, 0.2)",  # Fondo rojo sutil
			bordercolor="rgba(220, 38, 38, 0.5)",
			borderwidth=2
		),
		plot_bgcolor="rgba(17, 24, 39, 1)",  # Fondo deportivo oscuro
		paper_bgcolor="rgba(17, 24, 39, 1)",
		font=dict(color="white", family="Roboto"),
		height=620,  # Aumentado para acomodar LSI
		margin=dict(t=110, b=60, l=60, r=60),  # Más margen superior
		showlegend=True,
		# Configuración de animaciones
		transition=dict(
			duration=800,  # Duración de transiciones en ms
			easing="cubic-in-out"  # Tipo de animación suave
		),
		# Hover interactions mejoradas
		hovermode="x unified",  # Hover unificado por categoría
		hoverdistance=100,  # Distancia de detección del hover
		spikedistance=1000,  # Distancia para líneas de referencia
		# Animaciones de carga
		updatemenus=[
			dict(
				type="buttons",
				direction="left",
				buttons=list([
					dict(
						args=[{"visible": [True, True]},
							  {"title": "Comparación D/I – Métricas seleccionadas",
							   "annotations": []}],
						label="Actualizar",
						method="restyle"
					)
				]),
				pad={"r": 10, "t": 10},
				showactive=False,
				x=0.01,
				xanchor="left",
				y=1.02,
				yanchor="top",
				visible=False  # Oculto por defecto
			),
		]
	)

	return fig

@st.cache_data(ttl=1800, show_spinner="Generando radar Z-Score...")
def crear_radar_zscore(datos_jugador_hash, jugador_nombre):
	"""
	Crea un radar chart con los Z-Scores del jugador seleccionado - Optimizado con cache
	"""
	# Reconstruir datos del jugador desde hash
	datos_jugador = datos_jugador_hash
	# Definir las métricas Z-Score y sus etiquetas
	z_score_metricas = {
		'Z SCORE CUAD Der': 'CUAD Der',
		'Z SCORE CUAD Izq': 'CUAD Izq', 
		'Z SCORE ISQ Der': 'ISQ Der',
		'Z SCORE ISQ Izq': 'ISQ Izq',
		'Z SCORE F PICO': 'F. Pico',
		'Z SCORE F PROP': 'F. Propulsiva',
		'Z SCORE F FREN': 'F. Frenado'
	}
	
	# Extraer valores Z-Score del jugador
	valores = []
	etiquetas = []
	
	for columna, etiqueta in z_score_metricas.items():
		if columna in datos_jugador:
			valor = datos_jugador[columna]
			if pd.notna(valor) and valor is not None:
				valores.append(float(valor))
				etiquetas.append(etiqueta)
			else:
				valores.append(0)
				etiquetas.append(etiqueta)
	
	# Crear el radar chart
	fig = go.Figure()
	
	# Agregar la traza del jugador
	fig.add_trace(go.Scatterpolar(
		r=valores,
		theta=etiquetas,
		fill='toself',
		name=jugador_nombre,
		line=dict(color='rgba(220, 38, 38, 0.8)', width=3),
		fillcolor='rgba(220, 38, 38, 0.2)',
		marker=dict(
			color='rgba(220, 38, 38, 1)',
			size=8,
			line=dict(color='white', width=2)
		),
		hovertemplate='<b>%{theta}</b><br>Z-Score: %{r:.2f}<extra></extra>'
	))
	
	# Agregar líneas de referencia
	# Línea en Z=0 (promedio)
	fig.add_trace(go.Scatterpolar(
		r=[0] * len(etiquetas),
		theta=etiquetas,
		mode='lines',
		name='Promedio (Z=0)',
		line=dict(color='rgba(128, 128, 128, 0.8)', width=2, dash='dash'),
		showlegend=True,
		hovertemplate='<b>Promedio</b><br>Z-Score: 0.00<extra></extra>'
	))
	
	# Configuración del layout
	fig.update_layout(
		title=dict(
			text=f"<b>Radar Z-Scores - {jugador_nombre}</b>",
			x=0.5,
			font=dict(size=20, color='white')
		),
		polar=dict(
			radialaxis=dict(
				visible=True,
				range=[-3, 3],  # Rango típico para Z-scores
				tickmode='linear',
				tick0=-3,
				dtick=1,
				gridcolor='rgba(128, 128, 128, 0.3)',
				linecolor='rgba(128, 128, 128, 0.5)',
				tickfont=dict(color='white', size=12)
			),
			angularaxis=dict(
				tickfont=dict(color='white', size=13, family='Arial Black'),
				gridcolor='rgba(128, 128, 128, 0.3)',
				linecolor='rgba(128, 128, 128, 0.5)'
			)
		),
		plot_bgcolor='rgba(0,0,0,0)',
		paper_bgcolor='rgba(0,0,0,0)',
		font=dict(color='white'),
		legend=dict(
			x=0.02,
			y=0.98,
			bgcolor='rgba(17, 24, 39, 0.8)',
			bordercolor='rgba(220, 38, 38, 0.5)',
			borderwidth=1,
			font=dict(color='white', size=12)
		),
		height=500,
		margin=dict(l=80, r=80, t=80, b=80)
	)
	
	return fig

# ========= CONFIGURACIÓN DE MÉTRICAS ==========
metricas_por_seccion = {
    "Fuerza": {
        "CUAD 70° Der": "CUAD 70° Izq",
        "ISQ Wollin Der": "ISQ Wollin Izq",
        "IMTP F. Der (N)": "IMTP F. Izq (N)",
        "CMJ F. Der (N)": "CMJ F. Izq (N)"
    },
    "Movilidad": {
        "AKE Der": "AKE Izq",
        "M-TT CAD Der": "M-TT CAD Izq",
        "Lunge Der": "Lunge Izq"
    },
    "Funcionalidad": {
        "T. S. Der": "T. S. Izq"
    }
}

# ========= CARGA DE DATOS OPTIMIZADA ==========
df = cargar_datos_optimizado("/Users/agustin/Documents/Agustin_2025/Juan Colon/data/1ra evaluación.xlsx")
categorias = df["categoria"].dropna().unique()

# ========= CONFIGURACIÓN DE ESCUDO ==========
escudo_path = "/Users/agustin/Documents/Agustin_2025/Juan Colon/data/escudo.png"
escudo_base64 = get_base64_image(escudo_path)

# ========= SIDEBAR DEPORTIVO ==========
with st.sidebar:
    # Solo escudo centrado
    st.markdown(f"""
    <div style='text-align: center; padding: 20px; margin-bottom: 30px;'>
        <img src='data:image/png;base64,{escudo_base64}' width='80' 
             style='filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));'/>
    </div>
    """, unsafe_allow_html=True)

    # Selectores optimizados con callbacks
    categoria = st.selectbox(
        "Categoría", 
        categorias,
        key="categoria_selector",
        help="Selecciona la categoría para filtrar jugadores"
    )
    
    # Cache de jugadores por categoría
    @st.cache_data(ttl=1800)
    def obtener_jugadores_categoria(df, categoria_sel):
        return df[df["categoria"] == categoria_sel]["Deportista"].dropna().unique()
    
    jugadores_filtrados = obtener_jugadores_categoria(df, categoria)
    
    jugador = st.selectbox(
        "Deportista", 
        jugadores_filtrados,
        key="jugador_selector",
        help="Selecciona el deportista para análisis individual"
    )
    
    # Limpiar cache si hay cambio en la selección
    limpiar_cache_si_cambio(jugador, categoria)
    
    # Actualizar session state
    st.session_state.ultimo_jugador = jugador
    st.session_state.ultima_categoria = categoria

    vista = st.radio("Tipo de Análisis", ["Perfil del Jugador", "Perfil del Grupo", "Comparación Jugador vs Grupo"])
    seccion = st.radio("Evaluación", ["Fuerza", "Movilidad", "Funcionalidad"])

    st.markdown("---")
    
    # Información del staff
    st.markdown("""
    <div style='background: rgba(220, 38, 38, 0.1); padding: 10px; border-radius: 8px; border-left: 4px solid rgba(220, 38, 38, 1);'>
        <p style='margin: 0; font-size: 12px; color: rgba(255,255,255,0.7);'>
            <strong>Staff Técnico</strong><br>
            Evaluación: 1ra Fase<br>
            Análisis
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    exportar = st.button("Exportar Reporte", help="Descargar análisis en PDF")

# ========= HEADER DEPORTIVO PROFESIONAL ==========
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

# ========= PERFIL DEL JUGADOR ==========
if vista == "Perfil del Jugador":
    # Header de sección deportivo
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

    datos_jugador = df[(df["categoria"] == categoria) & (df["Deportista"] == jugador)].iloc[0]

    if seccion == "Fuerza":
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
            
            st.plotly_chart(fig_multifuerza, use_container_width=True, config={
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f'grafico_{jugador}_{categoria}',
                    'height': 620,
                    'width': 1000,
                    'scale': 2
                }
            })
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # === RADAR CHART Z-SCORES ===
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Header para el radar chart
            st.markdown(f"""
            <div style='background: linear-gradient(90deg, rgba(59, 130, 246, 0.8), rgba(17, 24, 39, 0.8)); 
                        padding: 12px; border-radius: 8px; margin: 15px 0;
                        border-left: 4px solid rgba(59, 130, 246, 1);'>
                <h4 style='margin: 0; color: white; font-size: 18px;'>
                    Análisis Z-Score - Perfil Normalizado
                </h4>
                <p style='margin: 5px 0 0 0; color: rgba(255,255,255,0.8); font-size: 13px;'>
                    Comparación con la media poblacional (Z=0 = promedio)
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Generar radar chart con cache optimizado
            fig_radar = crear_radar_zscore(datos_jugador_dict, jugador)
            
            st.plotly_chart(fig_radar, use_container_width=True, config={
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f'radar_zscore_{jugador}_{categoria}',
                    'height': 500,
                    'width': 800,
                    'scale': 2
                }
            })
            
            # Información interpretativa del Z-Score
            st.markdown("""
            <div style='background: rgba(59, 130, 246, 0.1); padding: 12px; border-radius: 8px; margin: 10px 0;
                        border-left: 3px solid rgba(59, 130, 246, 1);'>
                <p style='margin: 0; font-size: 13px; color: rgba(255,255,255,0.9);'>
                    <strong>Interpretación Z-Score:</strong><br>
                    • <strong>Z > +1:</strong> Rendimiento superior al promedio<br>
                    • <strong>Z = 0:</strong> Rendimiento promedio del grupo<br>
                    • <strong>Z < -1:</strong> Rendimiento inferior al promedio
                </p>
            </div>
            """, unsafe_allow_html=True)

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

            # Crear DataFrame comparativo (sin fila de diferencia)
            df_comparativo = pd.DataFrame([
                jugador_dict,
                media_dict,
                std_dict
            ])[column_order]
            df_comparativo.index = [f"{jugador}", f"Media {categoria}", f"Desv. Est. {categoria}"]
            
            # Mostrar tabla con estilo
            st.dataframe(
                df_comparativo.style.format("{:.1f}").apply(
                    lambda x: ['background-color: rgba(220, 38, 38, 0.1)' if i == 0 
                              else 'background-color: rgba(255, 255, 255, 0.05)' if i == 1
                              else 'background-color: rgba(59, 130, 246, 0.1)' for i in range(len(x))], 
                    axis=0
                ),
                use_container_width=True
            )
            
        else:
            st.info("Selecciona al menos una métrica para visualizar el gráfico.")

    elif seccion == "Movilidad":
        st.markdown("Aquí irán los análisis de movilidad.")
    elif seccion == "Funcionalidad":
        st.markdown("Aquí irán los análisis de funcionalidad.")

else:
    st.warning("Esta visualización detallada está disponible solo en el modo 'Perfil del Jugador'.")

# ========= FOOTER DEPORTIVO ==========
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
