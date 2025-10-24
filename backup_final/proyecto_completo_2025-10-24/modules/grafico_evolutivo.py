import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Ruta al dataset
DATA_PATH = "data/lesiones_clean.csv"

def mostrar_grafico_evolutivo():
    """
    Gráfico evolutivo mensual de lesiones (total general).
    - No depende de filtros.
    - Muestra la cantidad total de lesiones por mes en orden cronológico.
    - Estilo consistente con el dashboard.
    """

    # Leer dataset
    df = pd.read_csv(DATA_PATH, parse_dates=["fecha"])

    if df.empty:
        st.warning("⚠️ No hay datos disponibles para generar el gráfico.")
        return

    # Agrupar por mes (total lesiones por mes)
    df["mes"] = df["fecha"].dt.to_period("M").dt.to_timestamp()
    resumen = (
        df.groupby("mes")
        .size()
        .reset_index(name="cantidad_lesiones")
        .sort_values("mes")
    )

    # Etiquetas formateadas: "Ene 2024"
    resumen["mes_formato"] = resumen["mes"].dt.strftime("%b %Y")

    # Eje Y con números enteros
    max_lesiones = int(resumen["cantidad_lesiones"].max())
    y_range = [0, max_lesiones + 1]

    # Crear figura
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=resumen["mes_formato"],
        y=resumen["cantidad_lesiones"],
        mode="lines+markers+text",
        line=dict(color="#dc2626", width=3),
        marker=dict(size=8, color="#dc2626"),
        text=resumen["cantidad_lesiones"],
        textposition="top center",
        fill="tozeroy",
        fillcolor="rgba(220,38,38,0.15)",
        name="Lesiones"
    ))

    # Personalización visual
    fig.update_layout(
        title="Evolución mensual de lesiones (total general)",
        xaxis_title="Mes",
        yaxis_title="Cantidad de lesiones",
        plot_bgcolor="#111827",
        paper_bgcolor="#111827",
        font=dict(size=14, color="white"),        # tamaño de texto general
        title_font=dict(size=20, color="white"),  # tamaño del título principal
        xaxis=dict(
            showgrid=False,
            tickangle=-35,
            tickmode="array",
            tickvals=resumen["mes_formato"].tolist(),
            ticktext=resumen["mes_formato"].tolist(),
            range=[-0.5, len(resumen["mes_formato"]) - 0.5],  # deja espacio en los extremos
            fixedrange=True,
            title_font=dict(size=14, color="white"),  # título del eje X
            tickfont=dict(size=12, color="white"),    # valores del eje X
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#333333",
            zeroline=False,
            tickmode="linear",
            dtick=1,
            range=y_range,
            title_font=dict(size=14, color="white"),  # título del eje Y
            tickfont=dict(size=12, color="white"),    # valores del eje Y
        ),
        height=450,
        margin=dict(l=40, r=40, t=60, b=80),  # más aire en los bordes
        showlegend=False,
    )

    # Mostrar en Streamlit
    st.plotly_chart(fig, use_container_width=True)