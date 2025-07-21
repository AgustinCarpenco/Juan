import json
import base64
import streamlit as st
import pandas as pd
from PIL import Image
import plotly.graph_objects as go

# ========= FUNCIONES ==========

def cargar_evaluaciones(path_excel):
    df_4ta = pd.read_excel(path_excel, sheet_name="2005-06 (4ta)", header=1)
    df_reserva = pd.read_excel(path_excel, sheet_name="RESERVA", header=1)

    df_4ta["categoria"] = "4ta"
    df_reserva["categoria"] = "Reserva"

    df_total = pd.concat([df_4ta, df_reserva], ignore_index=True)
    return df_total

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return encoded

def crear_grafico_multifuerza(datos_jugador, metricas_seleccionadas, metricas_columnas):
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
        name="Derecho",
        marker=dict(color="#33A1FD", line=dict(width=1.5, color="#1e1e1e")),
        text=[f"{v:.0f} N" for v in barras_der],
        textposition="outside",
        textfont=dict(size=14),
        hovertemplate='Derecho<br>%{x}: %{y:.0f} N<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=nombres,
        y=barras_izq,
        name="Izquierdo",
        marker=dict(color="#FD9E02", line=dict(width=1.5, color="#1e1e1e")),
        text=[f"{v:.0f} N" for v in barras_izq],
        textposition="outside",
        textfont=dict(size=14),
        hovertemplate='Izquierdo<br>%{x}: %{y:.0f} N<extra></extra>'
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
            fig.add_annotation(
                text=f"<b>LSI: {lsi_val:.1f}%</b>",
                x=name,
                y=max(barras_der[idx], barras_izq[idx]) * 1.25,
                showarrow=False,
                font=dict(size=14, color="white"),
                xanchor="center",
                align="center",
                bgcolor="rgba(255,255,255,0.15)",
                bordercolor="white",
                borderwidth=1,
                borderpad=4
            )

    fig.update_layout(
        barmode="group",
        title=dict(
            text="Comparación D/I – Métricas seleccionadas",
            font=dict(size=22),
            y=0.92
        ),
        xaxis=dict(
            title=dict(text="Métrica", font=dict(size=15)),
            tickfont=dict(size=13)
        ),
        yaxis=dict(
            title=dict(text="N (fuerza)", font=dict(size=15)),
            tickfont=dict(size=13)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="right",
            x=1,
            font=dict(size=13)
        ),
        plot_bgcolor="#1e1e1e",
        paper_bgcolor="#1e1e1e",
        font=dict(color="white"),
        height=560,
        margin=dict(t=80, b=40, l=40, r=40)
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

# ========= CARGA DE DATOS ==========
df = cargar_evaluaciones("/Users/agustin/Documents/Agustin_2025/Juan Colon/data/1ra evaluación.xlsx")
categorias = df["categoria"].dropna().unique()

# ========= SIDEBAR ==========
with st.sidebar:
    st.title("⚙️ Panel de control")

    categoria = st.selectbox("📂 Seleccionar categoría", categorias)
    jugadores_filtrados = df[df["categoria"] == categoria]["Deportista"].dropna().unique()
    jugador = st.selectbox("👤 Seleccionar jugador", jugadores_filtrados)

    vista = st.radio("📊 Tipo de vista", ["Perfil del Jugador", "Perfil del Grupo", "Comparación Jugador vs Grupo"])
    seccion = st.radio("🧩 Sección", ["Fuerza", "Movilidad", "Funcionalidad"])

    st.markdown("---")
    exportar = st.button("📄 Exportar perfil a PDF")

# ========= ENCABEZADO + ESCUDO ==========
escudo_path = "/Users/agustin/Documents/Agustin_2025/Juan Colon/data/escudo.png"
escudo_base64 = get_base64_image(escudo_path)

st.markdown(
    f"""
    <div style='text-align: center;'>
        <img src='data:image/png;base64,{escudo_base64}' width='100'/>
        <h1 style='margin-bottom: 0;'>Evaluación Física Integral</h1>
        <h3 style='margin-top: 0;'>Club Atlético Colón</h3>
    </div>
    """,
    unsafe_allow_html=True
)

# ========= PERFIL DEL JUGADOR ==========
if vista == "Perfil del Jugador":
    st.markdown(f"### 📊 Perfil del Jugador – {seccion}")

    datos_jugador = df[(df["categoria"] == categoria) & (df["Deportista"] == jugador)].iloc[0]

    if seccion == "Fuerza":
        # === Selección de métricas de fuerza ===
        metricas_disponibles = ["CUAD 70°", "ISQ Wollin", "IMTP", "CMJ"]
        metricas_columnas = {
            "CUAD 70°": ("CUAD 70° Der", "CUAD 70° Izq"),
            "ISQ Wollin": ("ISQ Wollin Der", "ISQ Wollin Izq"),
            "IMTP": ("IMTP F. Der (N)", "IMTP F. Izq (N)"),
            "CMJ": ("CMJ F. Der (N)", "CMJ F. Izq (N)")
        }

        metricas_seleccionadas = st.multiselect(
            "Selecciona las métricas a comparar",
            metricas_disponibles,
            default=["CUAD 70°", "ISQ Wollin", "IMTP"]
        )

        if metricas_seleccionadas:
            fig_multifuerza = crear_grafico_multifuerza(datos_jugador, metricas_seleccionadas, metricas_columnas)
            st.plotly_chart(fig_multifuerza, use_container_width=True)
        else:
            st.info("Selecciona al menos una métrica para visualizar el gráfico.")

    elif seccion == "Movilidad":
        st.markdown("🧘‍♂️ Aquí irán los análisis de movilidad.")
    elif seccion == "Funcionalidad":
        st.markdown("🏃‍♂️ Aquí irán los análisis de funcionalidad.")

else:
    st.warning("👉 Esta visualización detallada está disponible solo en el modo 'Perfil del Jugador'.")
