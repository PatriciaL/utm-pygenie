import streamlit as st
import re
from urllib.parse import urlencode
import base64
from PIL import Image
import json
import os

# ---------- Configuración de la página ----------
st.set_page_config(
    page_title="UTM Genie - URL Builder",
    page_icon="🧙",
    layout="centered"
)

# ---------- Función para favicon ----------
def get_favicon_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

favicon_base64 = get_favicon_base64("components/utm_genie_favicon_64x64.png")
st.markdown(
    f"""
    <head>
        <link rel="icon" type="image/png" href="data:image/png;base64,{favicon_base64}">
    </head>
    """,
    unsafe_allow_html=True
)

# ---------- Logo y Sidebar ----------
logo = Image.open("components/utm_genie_logo_transparent_light.png")
st.sidebar.image(logo, width=100)
st.sidebar.title("🧭 Navegación")
page = st.sidebar.radio("Selecciona sección", [
    "🏗️ Generador UTM",
    "✅ Validador Individual",
    "📂 Validador por CSV",
    "🧪 Verificador Page View (GA)",
    "🤖 Chatbot Constructor",
    "⚙️ Naming personalizado (drag & drop)",
    "ℹ️ Acerca de"
])

# ---------- Funciones auxiliares ----------
def is_valid_utm(value):
    return bool(re.match(r"^[a-zA-Z0-9_-]+$", value))

def validated_input(label, key, helper_text=""):
    value = st.text_input(label, key=key)
    if helper_text:
        st.caption(f"Ej: {helper_text}")
    is_valid = is_valid_utm(value) if value else True
    color = "#d4edda" if is_valid else "#f8d7da"
    st.markdown(
        f"""
        <style>
        div[data-testid="stTextInput"] input#{key} {{
            background-color: {color};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    return value.strip()

# ---------- Cargar ejemplos ----------
EXAMPLES_PATH = "examples.json"
def load_examples():
    default = {
        "utm_source": "newsletter",
        "utm_medium": "email",
        "utm_campaign": "verano2025",
        "utm_term": "zapatos+rojos",
        "utm_content": "banner_lateral",
    }
    if os.path.exists(EXAMPLES_PATH):
        with open(EXAMPLES_PATH, "r") as f:
            return json.load(f)
    else:
        with open(EXAMPLES_PATH, "w") as f:
            json.dump(default, f, indent=2)
        return default

examples = load_examples()

# ---------- Página: Generador de UTM ----------
if page == "🏗️ Generador UTM":
    st.markdown("## 🔧 Generador de URLs con UTM")
    base_url = st.text_input("URL base", "https://tusitio.com")

    utm_source = validated_input("utm_source", "utm_source", examples["utm_source"])
    utm_medium = validated_input("utm_medium", "utm_medium", examples["utm_medium"])
    utm_campaign = validated_input("utm_campaign", "utm_campaign", examples["utm_campaign"])
    utm_term = validated_input("utm_term", "utm_term", examples["utm_term"])
    utm_content = validated_input("utm_content", "utm_content", examples["utm_content"])

    params = {
        "utm_source": utm_source,
        "utm_medium": utm_medium,
        "utm_campaign": utm_campaign,
        "utm_term": utm_term,
        "utm_content": utm_content,
    }
    params = {k: v for k, v in params.items() if v}

    if st.button("Generar URL"):
        if all(is_valid_utm(v) for v in params.values()):
            final_url = f"{base_url}?{urlencode(params)}"
            st.success("✅ URL generada:")
            st.code(final_url)
            st.balloons()
            st.link_button("🌐 Abrir URL generada", final_url)
            st.download_button("📋 Copiar URL", final_url, file_name="utm_url.txt", mime="text/plain")
            csv = f"url\n{final_url}"
            st.download_button("📅 Descargar CSV", csv, file_name="utm_url.csv", mime="text/csv")
        else:
            st.error("❌ Algunos campos contienen caracteres no válidos.")

# ---------- Página: Validador Individual ----------
elif page == "✅ Validador Individual":
    st.markdown("## ✅ Validador de URL única")
    st.info("En desarrollo...")

# ---------- Página: Validador CSV ----------
elif page == "📂 Validador por CSV":
    st.markdown("## 📂 Validador de URLs desde CSV")
    st.info("En desarrollo...")

# ---------- Página: Verificador Page View ----------
elif page == "🧪 Verificador Page View (GA)":
    st.markdown("## 🧪 Verificador de Page View en GA")
    st.info("En desarrollo...")

# ---------- Página: Chatbot ----------
elif page == "🤖 Chatbot Constructor":
    st.markdown("## 🤖 Chatbot Constructor de URLs")
    st.info("En desarrollo...")

# ---------- Página: Naming personalizado ----------
elif page == "⚙️ Naming personalizado (drag & drop)":
    st.markdown("## ⚙️ Constructor visual de naming conventions")
    st.info("Esta funcionalidad se habilitará en la siguiente fase. Drag & drop pronto disponible.")

# ---------- Página: Acerca de ----------
elif page == "ℹ️ Acerca de":
    st.markdown("## ℹ️ Acerca de UTM Genie")
    st.markdown("""
    Esta aplicación permite generar y validar URLs con parámetros UTM de forma rápida, validada y personalizable.

    **Autor:** Patricia  
    **Repositorio:** [GitHub](https://github.com/PatriciaL/utm-pygenie)
    """)
