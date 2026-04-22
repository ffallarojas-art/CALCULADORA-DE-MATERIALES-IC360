import streamlit as st
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io

# ==========================================
# DATA TÉCNICA - FUENTE ICG
# ==========================================
DATA_ICG = {
    "140 kg/cm2": {"cem": 7.01, "are": 0.51, "pie": 0.64, "agu": 0.184, "prop": "1:2.5:3.5"},
    "175 kg/cm2": {"cem": 8.43, "are": 0.54, "pie": 0.55, "agu": 0.185, "prop": "1:2.5:2.5"},
    "210 kg/cm2": {"cem": 9.73, "are": 0.52, "pie": 0.53, "agu": 0.186, "prop": "1:2:2"},
    "245 kg/cm2": {"cem": 11.50, "are": 0.50, "pie": 0.51, "agu": 0.187, "prop": "1:1.5:1.5"},
    "280 kg/cm2": {"cem": 13.34, "are": 0.45, "pie": 0.51, "agu": 0.189, "prop": "1:1:1.5"}
}

def generar_pdf_buffer(data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    content = []
    styles = getSampleStyleSheet()
    content.append(Paragraph(f"REPORTE TÉCNICO - CORP. IC360 SAC", styles['Title']))
    content.append(Paragraph(f"<b>Responsable:</b> Ing. Frank Falla Rojas | <b>f'c:</b> {data['fc']}", styles['Normal']))
    content.append(Spacer(1, 20))
    
    tabla_data = [['MATERIAL', 'CANTIDAD COMERCIAL', 'VOLUMEN (m3)'],
                  ['Cemento Portland', f"{data['cem']:.2f} Bolsas", "-"],
                  ['Arena Gruesa', f"{data['are_b']:.1f} Baldes", f"{data['are_m3']:.3f}"],
                  ['Piedra Chancada', f"{data['pie_b']:.1f} Baldes", f"{data['pie_m3']:.3f}"],
                  ['Agua Potable', f"{data['agu_l']:.1f} Litros", f"{data['agu_m3']:.3f}"],
                  [f"Aditivo {data['adi_t']}", f"{data['adi']:.2f} Litros", "-"]]
    
    t = Table(tabla_data, colWidths=[160, 160, 160])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a1c2e")),
                           ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                           ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                           ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
    content.append(t)
    doc.build(content)
    buffer.seek(0)
    return buffer

def create_card_st(title, val, unit, color):
    # Emulación visual de las tarjetas de CustomTkinter mediante HTML/CSS
    st.markdown(f"""
        <div style="
            border: 2px solid {color};
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            background-color: #161b22;
            margin-bottom: 20px;
            height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <p style="color: {color}; font-family: 'Arial'; font-weight: bold; font-size: 15px; margin: 0;">{title}</p>
            <p style="color: white; font-family: 'Orbitron', sans-serif; font-size: 42px; font-weight: bold; margin: 10px 0;">{val}</p>
            <p style="color: #8b949e; font-family: 'Arial'; font-weight: bold; font-size: 16px; margin: 0;">{unit}</p>
        </div>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="CORP. IC360 SAC | CÁLCULO BÉTÓN", layout="wide")
    
    # Estilos globales para emular la fuente Orbitron y el tema oscuro
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
        .main { background-color: #0d1117; }
        h1, h2, h3 { font-family: 'Orbitron', sans-serif !important; color: #58a6ff; }
        </style>
    """, unsafe_allow_html=True)

    # Encabezado
    col_logo, col_resp = st.columns([2, 1])
    with col_logo:
        st.title("CORPORACIÓN IC360 SAC")
    with col_resp:
        st.markdown("<p style='text-align: right; color: #8b949e; padding-top: 25px;'>Ing. Frank Falla Rojas</p>", unsafe_allow_html=True)

    # Panel de Configuración (Home)
    with st.expander("PANEL DE CONFIGURACIÓN DE MEZCLA", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            fc_req = st.selectbox("Resistencia f'c requerida:", list(DATA_ICG.keys()), index=2)
            desp_perc = st.number_input("Factor de Desperdicio (%):", value=5)
        with c2:
            vol_neto = st.number_input("Volumen Neto a vaciar (m3):", value=0.0, step=0.1)
            tipo_adi = st.selectbox("Tipo de Aditivo:", ["Ninguno", "Plastificante", "Superplastificante"])

    if st.button("CALCULAR METRADOS", use_container_width=True):
        if vol_neto <= 0:
            st.error("Por favor, ingrese un volumen válido.")
        else:
            # Lógica de cálculo idéntica a la versión de escritorio
            v_t = vol_neto * (1 + (desp_perc / 100))
            d = DATA_ICG[fc_req]
            cem = v_t * d['cem']
            
            ml_p_bolsa = 500 if "Super" in tipo_adi else (250 if "Plastificante" == tipo_adi else 0)
            cant_aditivo = (cem * ml_p_bolsa) / 1000

            data = {
                "fc": fc_req, "cem": cem, "are_b": (v_t * d['are']) * 37, "are_m3": v_t * d['are'],
                "pie_b": (v_t * d['pie']) * 37, "pie_m3": v_t * d['pie'], "agu_l": v_t * d['agu'] * 1000, 
                "agu_m3": v_t * d['agu'], "adi": cant_aditivo, "adi_t": tipo_adi
            }

            st.divider()
            st.subheader(f"RESULTADOS TÉCNICOS: f'c {fc_req}")

            # Grid de Resultados (3 columnas)
            res1, res2, res3 = st.columns(3)
            with res1:
                create_card_st("CEMENTO PORTLAND", f"{data['cem']:.2f}", "BOLSAS", "#1f6aa5")
                create_card_st("AGUA TOTAL", f"{data['agu_l']:.1f} Litros", f"{data['agu_m3']:.3f} m3", "#2980b9")
            
            with res2:
                create_card_st("ARENA GRUESA", f"{data['are_b']:.1f} Baldes", f"{data['are_m3']:.2f} m3", "#c0392b")
                color_adi = "#8e44ad" if data['adi'] > 0 else "#7f8c8d"
                create_card_st(f"ADITIVO {data['adi_t'].upper()}", f"{data['adi']:.2f}", "LITROS", color_adi)
            
            with res3:
                create_card_st("PIEDRA CHANCADA", f"{data['pie_b']:.1f} Baldes", f"{data['pie_m3']:.2f} m3", "#d35400")

            # Función de Exportación PDF
            pdf_buf = generar_pdf_buffer(data)
            st.download_button(
                label="EXPORTAR REPORTE PDF",
                data=pdf_buf,
                file_name=f"Reporte_IC360_{fc_req.replace(' ','_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

if __name__ == "__main__":
    main()