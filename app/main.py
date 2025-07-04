# UTM Genie: Generador de URL's con UTM

#Importamos las librerias
import streamlit as st
import re
from urllib.parse import urlencode
import base64

import streamlit as st
import re
from urllib.parse import urlencode

st.set_page_config(page_title="Generador de URLs UTM", layout="centered")
st.title("🔧 Generador de URLs con UTM (con validación)")

# ----------------- Validacion ---------

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

#--------------- Inputs --------------
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

#-------------Generar url --------
# Botón para generar URL
if st.button("Generar URL"):
    # Validar todos antes de generar
    if all(is_valid_utm(v) for v in params.values()):
        final_url = f"{base_url}?{urlencode(params)}"
        st.success("✅ URL generada:")
        st.code(final_url)
        st.balloons()

        #------------ UX Bar ----------

               # ---------- UX Bar ----------
        st.markdown(f"""
            <script>
            function copyToClipboard(text) {{
                navigator.clipboard.writeText(text);
            }}
            </script>

            <div style="display: flex; gap: 10px; margin-top: 10px;">
                <button onclick="copyToClipboard('{final_url}')" style="
                    background-color: #2196F3;
                    color: white;
                    padding: 8px 16px;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 14px;">
                    📋 Copiar
                </button>

                <a href="{final_url}" target="_blank">
                    <button style="
                        background-color: #4CAF50;
                        color: white;
                        padding: 8px 16px;
                        border: none;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 14px;">
                        🌐 Abrir
                    </button>
                </a>
        """, unsafe_allow_html=True)

        # Descargar como CSV
        csv = f"url\n{final_url}"
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'data:file/csv;base64,{b64}'

        st.markdown(f"""
                <a download="utm_url.csv" href="{href}">
                    <button style="
                        background-color: #FF9800;
                        color: white;
                        padding: 8px 16px;
                        border: none;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 14px;">
                        📥 Descargar CSV
                    </button>
                </a>
            </div>
        """, unsafe_allow_html=True)
