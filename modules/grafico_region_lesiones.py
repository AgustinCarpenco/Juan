import pandas as pd
import plotly.express as px
import streamlit as st

DATA_PATH = "data/lesiones_clean.csv"

def mostrar_grafico_region_lesiones():
    """
    Muestra un gráfico de barras verticales con la cantidad total de lesiones por región corporal.
    Mantiene el estilo visual corporativo del Club Atlético Colón.
    """
    # Leer dataset
    df = pd.read_csv(DATA_PATH)

    # Limpiar datos nulos en región si existen
    df = df.dropna(subset=["region"])

    # Agrupar por región y contar lesiones
    regiones = df.groupby("region").size().reset_index(name="cantidad_lesiones")

    # Ordenar de mayor a menor cantidad de lesiones
    regiones = regiones.sort_values(by="cantidad_lesiones", ascending=False)

    # Crear gráfico de barras verticales
    fig = px.bar(
        regiones,
        x="region",
        y="cantidad_lesiones",
        text="cantidad_lesiones",
        title="Distribución de lesiones por región corporal",
        color_discrete_sequence=["#dc2626"]  # Rojo Colón
    )

    # Personalización visual corporativa
    fig.update_traces(
        textposition="outside",
        textfont=dict(color="white", size=12),
        marker_line_color="white",
        marker_line_width=0.8
    )

    fig.update_layout(
        plot_bgcolor="#111827",      # Fondo oscuro
        paper_bgcolor="#111827",     # Fondo del papel oscuro
        font=dict(size=14, color="white"),        # tamaño de texto general
        title_font=dict(size=20, color="white"),  # tamaño del título principal
        xaxis=dict(
            showgrid=False, 
            title="Región corporal",
            title_font=dict(size=14, color="white"),  # título del eje X
            tickfont=dict(size=12, color="white"),    # valores del eje X
            tickangle=-45  # Rotar etiquetas para mejor legibilidad
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor="#333333",
            title="Cantidad de lesiones",
            title_font=dict(size=14, color="white"),  # título del eje Y
            tickfont=dict(size=12, color="white")     # valores del eje Y
        ),
        height=500,
        margin=dict(l=20, r=20, t=60, b=80),  # Margen inferior mayor para etiquetas rotadas
        showlegend=False  # Sin leyenda para diseño limpio
    )

    # Mostrar en Streamlit
    st.plotly_chart(fig, use_container_width=True)
