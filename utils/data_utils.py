"""
Utilidades para manejo de datos
"""

import pandas as pd
import streamlit as st
import json
import hashlib
from config.settings import CACHE_TTL, DATA_PATH

@st.cache_data(ttl=CACHE_TTL['datos_principales'], show_spinner="Cargando datos de evaluaciones...")
def cargar_evaluaciones(path_excel):
	"""Carga y procesa datos de evaluaciones con cache optimizado"""
	df_4ta = pd.read_excel(path_excel, sheet_name="2005-06 (4ta)", header=1)
	df_reserva = pd.read_excel(path_excel, sheet_name="RESERVA", header=1)

	df_4ta["categoria"] = "4ta"
	df_reserva["categoria"] = "Reserva"

	df_total = pd.concat([df_4ta, df_reserva], ignore_index=True)
	return df_total

def cargar_datos_optimizado(path_excel=None):
	"""Carga datos con optimización de session state"""
	if path_excel is None:
		path_excel = DATA_PATH
		
	if 'df_cache' not in st.session_state or st.session_state.df_cache is None:
		st.session_state.df_cache = cargar_evaluaciones(path_excel)
	return st.session_state.df_cache

@st.cache_data(ttl=CACHE_TTL['jugadores_categoria'])
def obtener_jugadores_categoria(df, categoria_sel):
	"""Obtiene jugadores filtrados por categoría"""
	return df[df["categoria"] == categoria_sel]["Deportista"].dropna().unique()

@st.cache_data(ttl=CACHE_TTL['preparacion_datos'])
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

@st.cache_data(ttl=CACHE_TTL['estadisticas'])
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

@st.cache_data(ttl=CACHE_TTL['preparacion_datos'])
def preparar_datos_jugador(datos_jugador, columnas_tabla):
	"""Prepara datos del jugador para visualización con cache"""
	jugador_dict = {}
	for col_der, col_izq in columnas_tabla.items():
		jugador_dict[col_der] = round(datos_jugador.get(col_der, 0), 1)
		jugador_dict[col_izq] = round(datos_jugador.get(col_izq, 0), 1)
	return jugador_dict

@st.cache_data(ttl=CACHE_TTL['selecciones'])
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

def limpiar_cache_si_cambio(jugador, categoria):
	"""Limpia cache si hay cambio en la selección"""
	if (st.session_state.get('ultimo_jugador') != jugador or 
		st.session_state.get('ultima_categoria') != categoria):
		# Limpiar cache de métricas al cambiar selección
		st.session_state.metricas_cache = {}
		return True
	return False
