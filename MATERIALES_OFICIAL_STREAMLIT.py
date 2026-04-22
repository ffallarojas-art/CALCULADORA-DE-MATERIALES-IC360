import streamlit as st
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io

st.set_page_config(page_title="IC360 SAC", layout="wide")

# =========================
# ESTADO
# =========================
if "calc" not in st.session_state:
    st.session_state.calc = False
if "data" not in st.session_state:
    st.session_state.data = {}

# =========================
# DATA
# =========================
DATA_ICG = {
    "140 kg/cm2": {"cem": 7.01, "are": 0.51, "pie": 0.64, "agu": 0.184, "prop": "1:2.5:3.5"},
    "175 kg/cm2": {"cem": 8.43, "are": 0.54, "pie": 0.55, "agu": 0.185, "prop": "1:2.5:2.5"},
    "210 kg/cm2": {"cem": 9.73, "are": 0.52, "pie": 0.53, "agu": 0.186, "prop": "1:2:2"},
    "245 kg/cm2": {"cem": 11.50, "are": 0.50, "pie": 0.51, "agu": 0.187, "prop": "1:1.5:1.5"},
    "280 kg/cm2": {"cem": 13.34, "are": 0.45, "pie": 0.51, "agu": 0.189, "prop": "1:1:1.5"}
}

# =========================
# ESTILO
# =========================
st.markdown("""
<style>
.stApp { background-color: #0d1117; color: #f0f6fc; }
.card {
    background-color: #161b22;
    border: 2px solid #30363d;
    border-radius: 15px;
    padding: 20px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# =========================
# RESET
# =========================
def reset():
    st.session_state.calc = False
    st.session_state.data = {}

# =========================
# FORMULARIO
# =========================
if not st.session_state.calc:

    st.title("Calculadora de Materiales - IC360 SAC")

    col1, col2 = st.columns(2)

    with col1:
        fc = st.selectbox("f'c", list(DATA_ICG.keys()), index=2)
        vol = st.number_input("Volumen (m3)", min_value=0.0, step=0.1)

    with col2:
        desp = st.number_input("Desperdicio (%)", value=5)
        adi = st.selectbox("Aditivo", ["Ninguno", "Plastificante", "Superplastificante"])

    if st.button("CALCULAR"):
        if vol > 0:
            v_t = vol * (1 + desp / 100)
            d = DATA_ICG[fc]

            cem = v_t * d['cem']

            ml = 500 if "Super" in adi else (250 if adi == "Plastificante" else 0)
            adi_l = (cem * ml) / 1000

            st.session_state.data = {
                "fc": fc,
                "v": v_t,
                "cem": cem,
                "are_b": v_t * d['are'] * 37,
                "are_m": v_t * d['are'],
                "pie_b": v_t * d['pie'] * 37,
                "pie_m": v_t * d['pie'],
                "agu_l": v_t * d['agu'] * 1000,
                "agu_m": v_t * d['agu'],
                "adi": adi_l,
                "adi_t": adi
            }

            st.session_state.calc = True
            st.rerun()

        else:
            st.warning("Ingrese volumen válido")

# =========================
# RESULTADOS
# =========================
else:
    d = st.session_state.data

    st.title(f"Resultados f'c {d['fc']}")
    st.write(f"Volumen final: **{d['v']:.3f} m3**")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f'<div class="card"><h3>CEMENTO</h3><h1>{d["cem"]:.2f}</h1>BOLSAS</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card"><h3>PIEDRA</h3><h1>{d["pie_b"]:.1f}</h1>{d["pie_m"]:.2f} m3</div>', unsafe_allow_html=True)

    with c2:
        st.markdown(f'<div class="card"><h3>ARENA</h3><h1>{d["are_b"]:.1f}</h1>{d["are_m"]:.2f} m3</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card"><h3>AGUA</h3><h1>{d["agu_l"]:.1f}</h1>Litros</div>', unsafe_allow_html=True)

    st.markdown("---")

    # =========================
    # PDF EN MEMORIA (SOLUCIÓN CLAVE)
    # =========================
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph("REPORTE IC360 SAC", styles['Title']))
    content.append(Spacer(1, 10))

    tabla = [
        ["Material", "Cantidad"],
        ["Cemento", f"{d['cem']:.2f} bolsas"],
        ["Arena", f"{d['are_m']:.2f} m3"],
        ["Piedra", f"{d['pie_m']:.2f} m3"],
        ["Agua", f"{d['agu_l']:.1f} L"],
        ["Aditivo", f"{d['adi']:.2f} L"]
    ]

    t = Table(tabla)
    t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
    ]))

    content.append(t)
    doc.build(content)

    st.download_button(
        "EXPORTAR PDF",
        buffer.getvalue(),
        file_name="reporte_ic360.pdf",
        mime="application/pdf"
    )

    if st.button("NUEVO CÁLCULO"):
        reset()
        st.rerun()
