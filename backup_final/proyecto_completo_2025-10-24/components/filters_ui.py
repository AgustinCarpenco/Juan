# components/filters_ui.py

import streamlit as st
import pandas as pd

# 🔹 Ruta al dataset limpio
DATA_PATH = "data/lesiones_clean.csv"

def mostrar_filtros_principales():
    """
    Muestra los filtros principales: Jugador, evento de lesión y tipo informativo.
    Retorna el jugador, evento seleccionados, tipo extraído y fechas de la lesión.
    """
    
    # Leer el dataset con fechas parseadas
    df = pd.read_csv(DATA_PATH, parse_dates=["fecha", "fecha_de_alta"])
    
    # Obtener lista de jugadores únicos
    jugadores = sorted(df["jugador"].dropna().unique())
    
    # Crear una fila de columnas para los filtros
    col1, col2, col3, col4, col5 = st.columns([1.2, 2.0, 1.1, 0.85, 0.85])
    
    with col1:
        selected_player = st.selectbox(
            "Jugador",
            jugadores,
            key="filtro_jugador",
            help="Selecciona un jugador para visualizar sus lesiones."
        )
    
    # 🔹 Filtrar por jugador seleccionado
    df_eventos = df[df["jugador"] == selected_player].copy()

    # 🔹 Crear columna combinada para mostrar los eventos de forma descriptiva
    df_eventos["evento_lesion"] = (
        df_eventos["fecha"].dt.strftime("%Y-%m-%d") + " — " +
        df_eventos["tipo_de_lesion"].astype(str) + " (" + df_eventos["region"].astype(str) + ")"
    )

    # 🔹 Ordenar los eventos de más reciente a más antiguo
    df_eventos = df_eventos.sort_values("fecha", ascending=False)

    # 🔹 Eliminar duplicados manteniendo el orden actual
    df_eventos = df_eventos.drop_duplicates(subset="evento_lesion", keep="first")

    # 🔹 Obtener la lista de eventos en orden descendente real
    eventos = df_eventos["evento_lesion"].tolist()

    with col2:
        # 🔹 Filtro: Evento de lesión
        selected_event = st.selectbox(
            "Evento de lesión",
            eventos,
            key="filtro_evento_lesion",
            help="Selecciona un evento de lesión para ver sus detalles."
        )
    
    # Buscar la fila del evento seleccionado
    evento_row = df_eventos[df_eventos["evento_lesion"] == selected_event].iloc[0]
    tipo_lesion = evento_row["tipo_de_lesion"]
    fecha_inicio = evento_row["fecha"]
    fecha_fin = evento_row["fecha_de_alta"]
    
    # Mostrar tipo de lesión como campo informativo
    with col3:
        st.text_input(
            "Tipo de lesión",
            value=tipo_lesion if pd.notna(tipo_lesion) else "N/A",
            disabled=True,
            key="info_tipo_lesion",
            help="Tipo de lesión del evento seleccionado (informativo)."
        )
    
    # Mostrar fechas como campos informativos
    with col4:
        st.text_input(
            "Desde",
            value=fecha_inicio.strftime("%Y-%m-%d") if pd.notna(fecha_inicio) else "N/A",
            disabled=True,
            key="info_fecha_inicio",
            help="Fecha de inicio de la lesión (informativo)."
        )
    
    with col5:
        fecha_fin_str = fecha_fin.strftime("%Y-%m-%d") if pd.notna(fecha_fin) else "Activa"
        st.text_input(
            "Hasta",
            value=fecha_fin_str,
            disabled=True,
            key="info_fecha_fin",
            help="Fecha de alta de la lesión (informativo)."
        )
    
    return selected_player, selected_event, tipo_lesion, fecha_inicio, fecha_fin
