import streamlit as st
import pandas as pd
from datetime import datetime

# ------------------------ CONFIGURACIÓN DE PÁGINA ------------------------
st.set_page_config(
    page_title="Naming Convention Creator",
    page_icon="🧙",
    layout="centered"
)
st.title("📝 Encuesta de Satisfacción")

st.markdown("""
Gracias por tomarte un momento para darnos feedback. Tu opinión es muy importante  
No pedimos datos personales. Si deseas, puedes usar un **pseudónimo**.
""")

# ------------------------ FORMULARIO DE CONTACTO ------------------------
st.header("Identifícate (opcional)")
nombre = st.text_input("Nombre o pseudónimo")

# ------------------------ SECCIÓN NPS CON CARITAS ------------------------
st.header("😊 ¿Qué tan probable es que nos recomiendes?")

caritas = {
    "😡 0": 0, "😕 1": 1, "😕 2": 2, "😐 3": 3, "😐 4": 4,
    "🙂 5": 5, "🙂 6": 6, "😊 7": 7, "😁 8": 8, "🤩 9": 9, "😍 10": 10
}
nps_opcion = st.radio("Selecciona una opción:", list(caritas.keys()), horizontal=True)
nps_score = caritas[nps_opcion]

# ------------------------ COMENTARIO OPCIONAL ------------------------
comentario = st.text_area("¿Por qué diste esa puntuación?", placeholder="Escribe tu comentario aquí, si quieres añadir algo más...")

# ------------------------ ENVÍO ------------------------
if st.button("📨 Enviar"):
    # Guardar respuestas en DataFrame
    respuesta = {
        "timestamp": datetime.now().isoformat(),
        "nombre": nombre or "Anónimo",
        "nps_score": nps_score,
        "nps_emoticon": nps_opcion,
        "comentario": comentario
    }

    st.success("¡Gracias por tu opinión! 🎉")

    # (Opcional) Exportar CSV de una sola respuesta
    df = pd.DataFrame([respuesta])
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar respuesta en CSV", csv, file_name="respuesta_nps.csv", mime="text/csv")
