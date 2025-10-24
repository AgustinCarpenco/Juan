import streamlit as st
import pandas as pd
from datetime import datetime

DATA_PATH = "data/lesiones_clean.csv"

def mostrar_kpi_cantidad_lesiones(selected_player: str):
    """
    Muestra una card con la cantidad total de lesiones del jugador seleccionado.
    Respetar estilo visual del proyecto (tema oscuro, rojo Colón, fuentes y proporciones).
    """

    # Cargar dataset
    df = pd.read_csv(DATA_PATH)

    # Calcular cantidad de lesiones por jugador
    if selected_player:
        lesiones_jugador = df[df["jugador"] == selected_player]
        cantidad_lesiones = len(lesiones_jugador)
    else:
        cantidad_lesiones = 0

    # Renderizar card en Streamlit
    st.markdown(
        f"""
        <div style="
            background-color:#1f2937;
            padding:12px 20px;
            border-radius:10px;
            text-align:center;
            box-shadow: 0 0 8px rgba(0,0,0,0.3);
            margin-top:10px;
        ">
            <p style="color:#d1d5db; font-size:20px; font-weight:500; margin-bottom:8px;">
                Cantidad de lesiones
            </p>
            <p style="color:#dc2626; font-size:30px; font-weight:bold; margin:0;">
                {cantidad_lesiones}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def mostrar_kpi_dias_lesionado(selected_player: str):
    """
    Muestra una card con el total acumulado de días lesionado del jugador seleccionado.
    Suma todas las lesiones (dadas de alta o activas).
    Respeta estilo visual y colores corporativos del proyecto.
    """

    df = pd.read_csv(DATA_PATH, parse_dates=["fecha", "fecha_de_alta"])

    if selected_player:
        df_jugador = df[df["jugador"] == selected_player].copy()

        total_dias = 0
        hoy = datetime.today()

        for _, row in df_jugador.iterrows():
            fecha_inicio = row["fecha"]
            fecha_alta = row["fecha_de_alta"]

            if pd.notna(fecha_alta):
                dias = (fecha_alta - fecha_inicio).days
            else:
                dias = (hoy - fecha_inicio).days

            total_dias += max(dias, 0)  # evita valores negativos

    else:
        total_dias = 0

    st.markdown(
        f"""
        <div style="
            background-color:#1f2937;
            padding:12px 20px;
            border-radius:10px;
            text-align:center;
            box-shadow: 0 0 8px rgba(0,0,0,0.3);
            margin-top:10px;
        ">
            <p style="color:#d1d5db; font-size:20px; font-weight:500; margin-bottom:8px;">
                Días lesionado
            </p>
            <p style="color:#dc2626; font-size:30px; font-weight:bold; margin:0;">
                {total_dias}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def mostrar_kpi_dias_lesion_seleccionada(selected_player: str, selected_event: str):
    """
    Muestra días de la lesión seleccionada.
    selected_event viene del selectbox 'Evento de lesión' y tiene formato:
    'YYYY-MM-DD — <tipo_de_lesion> (<region>)'
    """
    df = pd.read_csv(DATA_PATH, parse_dates=["fecha", "fecha_de_alta"])

    dias_lesion = 0

    if selected_player and selected_event:
        # Filtrar por jugador
        df_j = df[df["jugador"] == selected_player].copy()

        # Construir la MISMA clave que usa el filtro de eventos
        df_j["evento_lesion"] = (
            df_j["fecha"].dt.strftime("%Y-%m-%d") + " — " +
            df_j["tipo_de_lesion"] + " (" + df_j["region"] + ")"
        )

        # Buscar el evento exacto (si hay duplicados, tomar el más reciente)
        match = (
            df_j[df_j["evento_lesion"] == selected_event]
            .sort_values("fecha", ascending=False)
            .head(1)
        )

        if not match.empty:
            row = match.iloc[0]
            fecha_inicio = row["fecha"]
            fecha_alta = row["fecha_de_alta"]

            if pd.notna(fecha_alta):
                dias_lesion = (fecha_alta - fecha_inicio).days
            else:
                from datetime import datetime
                hoy = pd.Timestamp(datetime.today().date())
                dias_lesion = (hoy - fecha_inicio).days

            dias_lesion = max(int(dias_lesion), 0)

    st.markdown(
        f"""
        <div style="
            background-color:#1f2937;
            padding:12px 20px;
            border-radius:10px;
            text-align:center;
            box-shadow: 0 0 8px rgba(0,0,0,0.3);
            margin-top:10px;
        ">
            <p style="color:#d1d5db; font-size:20px; font-weight:500; margin-bottom:8px;">
                Días de la lesión seleccionada
            </p>
            <p style="color:#dc2626; font-size:30px; font-weight:bold; margin:0;">
                {dias_lesion}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def mostrar_kpi_lesiones_activas(selected_player: str):
    """
    Muestra una card con la cantidad de lesiones activas (sin fecha de alta) del jugador seleccionado.
    Respeta el estilo visual y colores corporativos del proyecto.
    """

    df = pd.read_csv(DATA_PATH, parse_dates=["fecha", "fecha_de_alta"])

    if selected_player:
        df_jugador = df[df["jugador"] == selected_player]
        lesiones_activas = df_jugador["fecha_de_alta"].isna().sum()
    else:
        lesiones_activas = 0

    # Color dinámico
    color_valor = "#dc2626" if lesiones_activas > 0 else "#9ca3af"

    # Renderizar card
    st.markdown(
        f"""
        <div style="
            background-color:#1f2937;
            padding:12px 20px;
            border-radius:10px;
            text-align:center;
            box-shadow: 0 0 8px rgba(0,0,0,0.3);
            margin-top:10px;
        ">
            <p style="color:#d1d5db; font-size:20px; font-weight:500; margin-bottom:8px;">
                Lesiones activas
            </p>
            <p style="color:{color_valor}; font-size:30px; font-weight:bold; margin:0;">
                {lesiones_activas}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )