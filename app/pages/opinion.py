import streamlit as st
import pandas as pd
from datetime import datetime

# Configurar página
st.set_page_config(page_title="Formulario de Contacto + NPS", layout="centered")
st.title("📬 Formulario de Contacto y Encuesta de Satisfacción")

st.markdown("Por favor completa este breve formulario. ¡Tu opinión es muy valiosa! 🙌")

# --------- FORMULARIO DE CONTACTO ---------
st.header("👤 Tus datos")

nombre = st.text_input("Nombre completo")
email = st.text_input("Correo electrónico")
mensaje = st.text_area("Mensaje o comentario")

# --------- SECCIÓN NPS ---------
st.header("🌟 ¿Qué tan probable es que nos recomiendes?")
nps_score = st.slider("Selecciona una puntuación de 0 (nada probable) a 10 (muy probable)", 0, 10, 5)
nps_comentario = st.text_area("¿Qué te motivó a dar esa puntuación?", placeholder="Opcional")

# --------- ENVÍO ---------
if st.button("📨 Enviar formulario"):
    if not nombre or not email:
        st.error("Por favor completa tu nombre y correo.")
    else:
        # Guardar o mostrar datos
        submitted = {
            "timestamp": datetime.now().isoformat(),
            "nombre": nombre,
            "email": email,
            "mensaje": mensaje,
            "nps_score": nps_score,
            "nps_comentario": nps_comentario
        }

        # Muestra mensaje de éxito
        st.success("¡Gracias por tu respuesta! 🎉")

        # Vista previa de datos
        st.write("📝 Tus datos registrados:")
        st.json(submitted)

        # (Opcional) Guardar en CSV o base de datos
        # Aquí simulado con descarga directa
        df = pd.DataFrame([submitted])
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Descargar respuesta", csv, file_name="respuesta_contacto.csv", mime="text/csv")
