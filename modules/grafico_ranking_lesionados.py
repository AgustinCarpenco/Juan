import pandas as pd
import plotly.express as px
import streamlit as st

DATA_PATH = "data/lesiones_clean.csv"

def mostrar_grafico_ranking_lesionados():
    """
    Muestra un gráfico de barras horizontales con el ranking de jugadores según
    la cantidad total de lesiones registradas (de mayor a menor).
    Mantiene el estilo visual corporativo del Club Atlético Colón.
    """
    # Leer dataset
    df = pd.read_csv(DATA_PATH)

    # Agrupar por jugador y contar lesiones
    ranking = df.groupby("jugador").size().reset_index(name="cantidad_lesiones")

    # Ordenar de mayor a menor y tomar top 10
    ranking = ranking.sort_values(by="cantidad_lesiones", ascending=False).head(10)

    # Crear gráfico de barras horizontales
    fig = px.bar(
        ranking,
        x="cantidad_lesiones",
        y="jugador",
        orientation="h",
        text="cantidad_lesiones",
        title="Ranking de jugadores más lesionados",
        color_discrete_sequence=["#dc2626"]  # Rojo Colón
    )

    # Personalización visual corporativa
    fig.update_traces(
        textposition="outside",
        textfont=dict(color="white", size=12),
        marker_line_color="white",   # borde blanco
        marker_line_width=0.8        # grosor sutil
    )

    fig.update_layout(
        plot_bgcolor="#111827",      # Fondo oscuro
        paper_bgcolor="#111827",     # Fondo del papel oscuro
        font=dict(size=14, color="white"),        # tamaño de texto general
        title_font=dict(size=20, color="white"),  # tamaño del título principal
        xaxis=dict(
            showgrid=False, 
            title="Cantidad de lesiones",
            title_font=dict(size=14, color="white"),  # título del eje X
            tickfont=dict(size=12, color="white")     # valores del eje X
        ),
        yaxis=dict(
            showgrid=False, 
            title="Jugador",
            title_font=dict(size=14, color="white"),  # título del eje Y
            tickfont=dict(size=12, color="white"),    # valores del eje Y
            categoryorder="total ascending"  # Orden ascendente para barras horizontales
        ),
        height=500,
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=False  # Sin leyenda para diseño limpio
    )

    # Mostrar en Streamlit
    st.plotly_chart(fig, use_container_width=True)
