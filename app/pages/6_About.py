import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from style import apply_style

import streamlit as st
import requests

st.set_page_config(page_title="UTM Genie — About", page_icon="🧙", layout="centered")
apply_style()

st.markdown("""
<div style="margin-bottom:28px;padding-bottom:20px;border-bottom:1.5px solid #E4E4E7">
  <div style="font-family:'Sora',sans-serif;font-size:0.6rem;font-weight:500;
              letter-spacing:0.2em;text-transform:uppercase;color:#71717A;margin-bottom:8px">
    UTM Genie
  </div>
  <div style="font-family:'Sora',sans-serif;font-size:1.8rem;font-weight:600;
              letter-spacing:-0.04em;color:#1A1A1A;line-height:1.1;margin-bottom:10px">
    Sobre UTM Genie
  </div>
  <div style="font-family:'Sora',sans-serif;font-size:0.8rem;color:#71717A;letter-spacing:0.01em">
    Herramienta para campañas de marketing digital
  </div>
</div>

""", unsafe_allow_html=True)
st.markdown("""
Herramienta creada para simplificar la construcción, validación y estandarización  
de parámetros UTM en campañas de marketing digital.
""")

st.markdown("## Contacto")
st.link_button("LinkedIn", "https://www.linkedin.com/in/patricialafuente/")

st.markdown("---")
st.markdown("## Proyectos en GitHub")

try:
    response = requests.get("https://api.github.com/users/PatriciaL/repos", timeout=5)
    response.raise_for_status()
    for repo in response.json():
        st.markdown(f"""
**[{repo['name']}]({repo['html_url']})**  
{repo['description'] or '—'}  
{repo['stargazers_count']} stars · {repo['forks_count']} forks

---
""")
except Exception:
    st.warning("No se pudieron cargar los proyectos desde GitHub.")

with st.expander("Créditos"):
    st.markdown("Desarrollado en Python con Streamlit · Proyecto personal publicado en GitHub")
