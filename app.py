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

# ========= CONFIGURACIÓN DE MÉTRICAS ==========
metricas_por_seccion = {
    "Fuerza": {
        "CUAD 70° Der": "CUAD 70° Izq",
        "ISQ Wollin Der": "ISQ Wollin Izq",
        "IMTP F. Der (N)": "IMTP F. Izq (N)",
        "CMJ F. Der (N)": "CMJ F. Izq (N)",
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
        # Función para unificar estilo visual
        def estilo_barras(fig):
            fig.update_layout(
                plot_bgcolor="#1e1e1e",
                paper_bgcolor="#1e1e1e",
                font=dict(color="white"),
                height=420,
                margin=dict(t=120, b=40, l=40, r=40),  # más espacio arriba
                title=dict(
                    y=0.95,  # lo subimos más cerca del borde
                    yanchor='top',
                    font=dict(size=20)
                )
            )

            for trace in fig.data:
                if isinstance(trace, go.Bar):
                    trace.text = [f"{y} N" for y in trace.y]
                    trace.textposition = "outside"  
                    trace.textangle = 0
                    trace.textfont = dict(size=16, color="white")
                    trace.cliponaxis = False  
            return fig


        # 1. CUÁDRICEPS 70°
        cuad_der = datos_jugador.get("CUAD 70° Der", 0)
        cuad_izq = datos_jugador.get("CUAD 70° Izq", 0)
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=["Derecho", "Izquierdo"],
            y=[cuad_der, cuad_izq],
            marker_color=["#33A1FD", "#FD9E02"],
            text=[f"{cuad_der:.0f} N", f"{cuad_izq:.0f} N"],
            textposition="outside",
            textfont=dict(color="white", size=14)
        ))
        fig1.update_layout(title="Cuádriceps 70° – Comparación D/I", xaxis_title="Lado", yaxis_title="N (fuerza)")
        st.plotly_chart(estilo_barras(fig1), use_container_width=True)

        # 2. ISQ WOLLIN
        isq_der = datos_jugador.get("ISQ Wollin Der", 0)
        isq_izq = datos_jugador.get("ISQ Wollin Izq", 0)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=["Derecho", "Izquierdo"],
            y=[isq_der, isq_izq],
            marker_color=["#33A1FD", "#FD9E02"],
            text=[f"{isq_der:.0f} N", f"{isq_izq:.0f} N"],
            textposition="outside",
            textfont=dict(color="white", size=14)
        ))
        fig2.update_layout(title="ISQ Wollin – Comparación D/I", xaxis_title="Lado", yaxis_title="N (fuerza)")
        st.plotly_chart(estilo_barras(fig2), use_container_width=True)

        # 3. IMTP
        imtp_der = datos_jugador.get("IMTP F. Der (N)", 0)
        imtp_izq = datos_jugador.get("IMTP F. Izq (N)", 0)
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=["Derecho", "Izquierdo"],
            y=[imtp_der, imtp_izq],
            marker_color=["#33A1FD", "#FD9E02"],
            text=[f"{imtp_der:.0f} N", f"{imtp_izq:.0f} N"],
            textposition="outside",
            textfont=dict(color="white", size=14)
        ))
        fig3.update_layout(title="IMTP – Comparación D/I", xaxis_title="Lado", yaxis_title="N (fuerza)")
        st.plotly_chart(estilo_barras(fig3), use_container_width=True)

        # 4. CMJ Propulsivo / Frenado
        cmj_prop_der = datos_jugador.get("CMJ F. Der (N)", 0)
        cmj_prop_izq = datos_jugador.get("CMJ F. Izq (N)", 0)
        cmj_fren_der = datos_jugador.get("CMJ F. Der (N).1", 0)
        cmj_fren_izq = datos_jugador.get("CMJ F. Izq (N).1", 0)

        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            name="Propulsivo",
            x=["Derecho", "Izquierdo"],
            y=[cmj_prop_der, cmj_prop_izq],
            marker_color=["#00FF7F", "#00FF7F"],
            text=[f"{cmj_prop_der:.0f} N", f"{cmj_prop_izq:.0f} N"],
            textposition="outside",
            textfont=dict(color="white", size=14)
        ))
        fig4.add_trace(go.Bar(
            name="Frenado",
            x=["Derecho", "Izquierdo"],
            y=[cmj_fren_der, cmj_fren_izq],
            marker_color=["#FF6347", "#FF6347"],
            text=[f"{cmj_fren_der:.0f} N", f"{cmj_fren_izq:.0f} N"],
            textposition="outside",
            textfont=dict(color="white", size=14)
        ))
        fig4.update_layout(
            barmode="group",
            title="CMJ – Propulsivo vs Frenado",
            xaxis_title="Lado",
            yaxis_title="N (fuerza)"
        )
        st.plotly_chart(estilo_barras(fig4), use_container_width=True)

        # ========== RADAR DE FUERZA ==========
        st.markdown("#### 🔸 Perfil de Fuerza – Radar D/I")

        radar_metricas = {
            "CUAD 70° (N)": ("CUAD 70° Der", "CUAD 70° Izq"),
            "ISQ Wollin (N)": ("ISQ Wollin Der", "ISQ Wollin Izq"),
            "IMTP (N)": ("IMTP F. Der (N)", "IMTP F. Izq (N)"),
            "CMJ Prop (N)": ("CMJ F. Der (N)", "CMJ F. Izq (N)"),
            "CMJ Fren (N)": ("CMJ F. Der (N).1", "CMJ F. Izq (N).1")
        }


    etiquetas = list(radar_metricas.keys())
    valores_der, valores_izq = [], []

    for etiqueta, (m_der, m_izq) in radar_metricas.items():
        valores_der.append(datos_jugador.get(m_der, 0))
        valores_izq.append(datos_jugador.get(m_izq, 0))

    max_val = max(valores_der + valores_izq) * 1.1

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=valores_der,
        theta=etiquetas,
        fill='toself',
        name='Derecho',
        line=dict(color='#33A1FD', width=3),
        marker=dict(color='#33A1FD', size=8),
        mode='lines+markers+text',
        text=[f"{v:.0f} N" for v in valores_der],
        textposition='top center'
    ))

    fig_radar.add_trace(go.Scatterpolar(
        r=valores_izq,
        theta=etiquetas,
        fill='toself',
        name='Izquierdo',
        line=dict(color='#FD9E02', width=3),
        marker=dict(color='#FD9E02', size=8),
        mode='lines+markers+text',
        text=[f"{v:.0f} N" for v in valores_izq],
        textposition='top center'
    ))

    fig_radar.update_layout(
        title="🔸 Radar Comparativo de Fuerza D/I",
        title_font_size=20,
        polar=dict(
            bgcolor="#1e1e1e",
            radialaxis=dict(
                visible=True,
                showline=False,
                showticklabels=False,
                ticks='',
                gridcolor='gray',
                gridwidth=1
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color="white")
            )
        ),
        showlegend=True,
        paper_bgcolor="#1e1e1e",
        plot_bgcolor="#1e1e1e",
        font=dict(color="white"),
        height=550,
        legend=dict(orientation="h", y=-0.2)
    )

    st.plotly_chart(fig_radar, use_container_width=True)

else:
    st.warning("👉 Esta visualización detallada de 4 gráficos solo está disponible en la sección 'Fuerza'.")
