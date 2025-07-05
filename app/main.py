import streamlit as st
from PIL import Image

st.set_page_config(page_title="Inicio | UTM Genie", page_icon="🧙")

logo = Image.open("components/utm_genie_logo_transparent_light.png")
st.image(logo, width=120)

st.markdown("# 🧙 Bienvenido a UTM Genie")
st.markdown("""
Esta aplicación te ayuda a construir, validar y verificar URLs con parámetros UTM.

### Módulos disponibles:
- 🏗️ Generador de URLs UTM
- ✅ Validador individual o por CSV
- 🧪 Verificador de Page View
- 🤖 Chatbot de generación UTM
- ⚙️ Constructor drag & drop (próximamente)

Usa el menú de la izquierda para empezar.
""")
