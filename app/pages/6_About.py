import streamlit as st
import requests
import os

# ---------------- Configuración de la página ----------------
st.set_page_config(page_title="Sobre la herramienta", layout="centered")
st.title("🧙 Sobre esta herramienta")

# ---------------- Imagen de cabecera (con fallback) ----------------
logo_path = "components/utm_genie_logo_transparent_light.png"
if os.path.exists(logo_path):
    st.image(logo_path, use_container_width=True)

# ---------------- Descripción ----------------
st.markdown("""
Esta herramienta fue creada para facilitar la construcción y exportación de convenciones de naming para parámetros UTM,
especialmente útil para campañas de marketing digital.
""")

# ---------------- Botón de LinkedIn ----------------
st.markdown("### 🔗 Conecta conmigo")
linkedin_url = "https://www.linkedin.com/in/patricialafuente/"
st.link_button("💼 Ir a mi perfil de LinkedIn", linkedin_url)

# ---------------- Proyectos desde GitHub ----------------
st.markdown("---")
st.markdown("### 📂 Proyectos en GitHub")

github_user = "PatriciaL"
gh_api_url = f"https://api.github.com/users/{github_user}/repos"

try:
    response = requests.get(gh_api_url, timeout=5)
    response.raise_for_status()
    repos = response.json()

    for repo in repos:
        st.markdown(f"""
        **[{repo['name']}]({repo['html_url']})**  
        {repo['description'] or '_Sin descripción_'}  
        ⭐ {repo['stargazers_count']} | 🔄 {repo['forks_count']}
        ---
        """)
except Exception:
    st.warning("No se pudieron cargar los proyectos desde GitHub.")

# ---------------- Créditos ----------------
with st.expander("📬 Créditos"):
    st.markdown("""
    - Código desarrollado en Python con Streamlit
    - Proyecto personal publicado en GitHub
    """)
