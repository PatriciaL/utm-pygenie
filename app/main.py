# UTM Genie: Generador de URL's con UTM

#Importamos las librerias
import streamlit as st
import re
from urllib.parse import urlencode

import streamlit as st
import re
from urllib.parse import urlencode

st.set_page_config(page_title="Generador de URLs UTM", layout="centered")
st.title("🔧 Generador de URLs con UTM (con validación)")

# Función para validar UTM: solo letras, números, guiones y guiones bajos
def is_valid_utm(value):
    return bool(re.match(r"^[a-zA-Z0-9_-]+$", value))

# Input personalizado con color
def validated_input(label, key):
    value = st.text_input(label, key=key)
    is_valid = is_valid_utm(value) if value else True  # vacío se considera válido
    color = "#d4edda" if is_valid else "#f8d7da"  # verde o rojo
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

# Campos de entrada
base_url = st.text_input("URL base", "https://tusitio.com")

utm_source = validated_input("utm_source", "utm_source")
utm_medium = validated_input("utm_medium", "utm_medium")
utm_campaign = validated_input("utm_campaign", "utm_campaign")
utm_term = validated_input("utm_term", "utm_term")
utm_content = validated_input("utm_content", "utm_content")

# Construcción de parámetros
params = {
    "utm_source": utm_source,
    "utm_medium": utm_medium,
    "utm_campaign": utm_campaign,
    "utm_term": utm_term,
    "utm_content": utm_content,
}
params = {k: v for k, v in params.items() if v}

# Botón para generar URL
if st.button("Generar URL"):
    # Validar todos antes de generar
    if all(is_valid_utm(v) for v in params.values()):
        final_url = f"{base_url}?{urlencode(params)}"
        st.success("✅ URL generada:")
        st.code(final_url)
        st.markdown(
            f"""
            <a href="{final_url}" target="_blank">
                <button style="
                background-color:#4CAF50;
                color:white;
                padding:10px 20px;
                text-align:center;
                border:none;
                border-radius:6px;
                text-decoration:none;
                display:inline-block;
                font-size:16px;
                cursor:pointer;
                margin-top:10px;
        ">
            🌐 Ir al enlace generado
        </button>
    </a>
    """,
    unsafe_allow_html=True
)
    else:
        st.error("❌ Hay campos UTM con caracteres inválidos. Revísalos antes de continuar.")
