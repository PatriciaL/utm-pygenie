# UTM Genie - Generador de URLs con UTM

import streamlit as st
import re
from urllib.parse import urlencode
import base64
from PIL import Image

# ---------- 1. Configuración de la página ----------
st.set_page_config(
    page_title="UTM Genie - URL Builder",
    page_icon="🧙",
    layout="centered"
)

# ---------- 2. Cargar favicon ----------
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

# ---------- 3. Cargar logo y mostrar cabecera ----------
logo = Image.open("components/utm_genie_logo_transparent_light.png")
col1, col2 = st.columns([1, 4])
with col1:
    st.image(logo, width=100)
with col2:
    st.markdown("## 🔧 Generador de URLs con UTM")

# ---------- 4. Menú lateral ----------
st.sidebar.image(logo, width=80)
st.sidebar.title("🧭 Navegación")
page = st.sidebar.radio("Ir a:", [
    "🏗️ Generador UTM",
    "✅ Validador Individual",
    "📂 Validador por CSV",
    "🧪 Verificador Page View (GA)",
    "🤖 Chatbot Constructor",
    "⚙️ Naming personalizado",
    "ℹ️ Acerca de"
])

# ---------- 5. Validación ----------
def is_valid_utm(value):
    return bool(re.match(r"^[a-zA-Z0-9_-]+$", value))

def validated_input(label, key, help_text="", example_text=""):
    value = st.text_input(label, key=key, help=help_text)
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
    if example_text:
        st.caption(f"💡 Ejemplo: `{example_text}`")
    return value.strip()

# ---------- 6. Página principal ----------
if page == "🏗️ Generador UTM":
    with st.expander("⚙️ Personalizar ejemplos"):
        examples = {
            "utm_source": st.text_input("Ejemplo para utm_source", "newsletter, facebook"),
            "utm_medium": st.text_input("Ejemplo para utm_medium", "email, cpc"),
            "utm_campaign": st.text_input("Ejemplo para utm_campaign", "lanzamiento2025"),
            "utm_term": st.text_input("Ejemplo para utm_term", "zapatos+rojos"),
            "utm_content": st.text_input("Ejemplo para utm_content", "banner_azul")
        }

    base_url = st.text_input("URL base", "https://tusitio.com")
    utm_source = validated_input("utm_source", "utm_source", help_text="Fuente del tráfico", example_text=examples["utm_source"])
    utm_medium = validated_input("utm_medium", "utm_medium", help_text="Canal o medio", example_text=examples["utm_medium"])
    utm_campaign = validated_input("utm_campaign", "utm_campaign", help_text="Campaña específica", example_text=examples["utm_campaign"])
    utm_term = validated_input("utm_term", "utm_term", help_text="Palabra clave", example_text=examples["utm_term"])
    utm_content = validated_input("utm_content", "utm_content", help_text="Contenido del anuncio", example_text=examples["utm_content"])

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
            st.session_state["final_url"] = final_url
            st.balloons()

    if "final_url" in st.session_state:
        final_url = st.session_state["final_url"]
        st.success("✅ URL generada:")
        st.code(final_url)
        #st.button("📋 Copiar URL", on_click=lambda: st.toast("URL copiada (simulado)"))
        st.link_button("🌐 Abrir URL", final_url)

        csv = f"url\n{final_url}"
        st.download_button(
            label="📥 Descargar como CSV",
            data=csv,
            file_name="utm_url.csv",
            mime="text/csv"
        )

# ---------- 7. Otras secciones ----------
elif page == "Validador Individual":
    st.info("Validación individual: próximamente")

elif page == "📂 Validador por CSV":
    st.info("¿No sabes si tus url están correctas?: próximamente")

elif page == "Verificador Page View (GA)":
    st.info("Comprobar que la url genera una sesión en GA4")

elif page == "Chatbot Constructor":
    st.info("Chatbot en desarrollo")

elif page == "Naming personalizado":
    st.info("🧩 Constructor drag & drop: próximamente")

elif page == " Acerca de":
    st.markdown("""
    ## ℹ️ Acerca de UTM Genie
    Esta app te permite construir y validar URLs UTM de forma rápida y precisa.

    **Creado por:** Patricia  
    **Repositorio:** [utm-pygenie](https://github.com/PatriciaL/utm-pygenie)
    """)

