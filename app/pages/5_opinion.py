import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from style import apply_style

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="UTM Genie — Feedback", page_icon="🧙", layout="centered")
apply_style()

st.markdown("""
<div style="margin-bottom:28px;padding-bottom:20px;border-bottom:1.5px solid #E4E4E7">
  <div style="font-family:'Sora',sans-serif;font-size:0.6rem;font-weight:500;
              letter-spacing:0.2em;text-transform:uppercase;color:#71717A;margin-bottom:8px">
    UTM Genie
  </div>
  <div style="font-family:'Sora',sans-serif;font-size:1.8rem;font-weight:600;
              letter-spacing:-0.04em;color:#1A1A1A;line-height:1.1;margin-bottom:10px">
    Feedback
  </div>
  <div style="font-family:'Sora',sans-serif;font-size:0.8rem;color:#71717A;letter-spacing:0.01em">
    Tu opinión nos ayuda a mejorar la herramienta
  </div>
</div>

""", unsafe_allow_html=True)
st.markdown("No pedimos datos personales. Puedes usar un pseudónimo si quieres.")

st.markdown("## Identificación opcional")
nombre = st.text_input("Nombre o pseudónimo")

st.markdown("## ¿Con qué probabilidad nos recomendarías?")
caritas = {
    "0": 0, "1": 1, "2": 2, "3": 3, "4": 4,
    "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10
}
nps_opcion = st.radio("Selecciona una puntuación:", list(caritas.keys()), horizontal=True)
nps_score  = caritas[nps_opcion]

comentario = st.text_area("Comentario (opcional)", placeholder="¿Por qué diste esa puntuación?")

if st.button("Enviar", type="primary"):
    respuesta = {
        "timestamp":    datetime.now().isoformat(),
        "nombre":       nombre or "Anónimo",
        "nps_score":    nps_score,
        "comentario":   comentario
    }
    st.success("Gracias por tu opinión.")
    df  = pd.DataFrame([respuesta])
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Descargar respuesta", csv, file_name="respuesta_nps.csv", mime="text/csv")
