import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from style import apply_style
import streamlit as st
import requests

st.set_page_config(page_title="UTM Genie — About", page_icon="🧙", layout="centered", initial_sidebar_state="expanded")
apply_style()

st.markdown("""
<div style="margin-bottom:28px;padding-bottom:20px;border-bottom:1.5px solid #E4E4E7">
  <div style="font-family:'Sora',sans-serif;font-size:0.6rem;font-weight:500;
              letter-spacing:0.2em;text-transform:uppercase;color:#71717A;margin-bottom:8px">
    UTM Genie
  </div>
  <div style="font-family:'Sora',sans-serif;font-size:1.8rem;font-weight:600;
              letter-spacing:-0.04em;color:#1A1A1A;line-height:1.1;margin-bottom:10px">
    Acerca de
  </div>
  <div style="font-family:'Sora',sans-serif;font-size:0.8rem;color:#71717A;letter-spacing:0.01em">
    Herramienta para campañas de marketing digital · Beta pública
  </div>
</div>
""", unsafe_allow_html=True)

# ── Beta banner ───────────────────────────────────────────
st.markdown("""
<div style="background:#FFFBEB;border:1.5px solid #FDE68A;border-radius:6px;padding:14px 18px;margin-bottom:28px">
  <div style="font-family:'Sora',sans-serif;font-size:0.62rem;font-weight:600;letter-spacing:0.14em;
              text-transform:uppercase;color:#92400E;margin-bottom:6px">Beta pública</div>
  <div style="font-family:'Sora',sans-serif;font-size:0.8rem;color:#78350F;line-height:1.65">
    UTM Genie está en fase beta. Puede tener bugs y las funcionalidades están en evolución constante.
    Si encuentras algo raro o tienes sugerencias, cuéntamelo por LinkedIn — cada opinión cuenta.
  </div>
</div>
""", unsafe_allow_html=True)

# ── Qué es ────────────────────────────────────────────────
st.markdown("""
<div style="font-family:'Sora',sans-serif;font-size:0.95rem;color:#3A3A3A;line-height:1.8;margin-bottom:32px">
  UTM Genie nació de un problema real: los parámetros UTM se escriben diferente en cada equipo,
  las hojas de cálculo se descontrolan y los errores no se detectan hasta que los datos ya están contaminados.
  Esta herramienta centraliza todo el flujo — desde definir las reglas hasta generar, validar y corregir URLs —
  en un solo sitio, sin fricción.
</div>
""", unsafe_allow_html=True)

# ── Cómo funciona ─────────────────────────────────────────
st.markdown("""
<div style="font-family:'Sora',sans-serif;font-size:0.62rem;font-weight:500;letter-spacing:0.14em;
            text-transform:uppercase;color:#71717A;margin-bottom:16px">Cómo funciona</div>
""", unsafe_allow_html=True)

steps = [
    (":material/tune:", "Naming Convention",
     "Define los bloques y valores permitidos para cada parámetro UTM. Es el punto de partida: establece las reglas una vez y el resto de la app las usa automáticamente."),
    (":material/link:", "Generador",
     "Crea URLs con parámetros UTM en modo individual (una URL concreta) o masivo (todas las combinaciones posibles a partir de los valores del Naming Convention). Descarga el resultado en CSV o Excel."),
    (":material/check_circle:", "Validador y Corrector",
     "Pega una URL o sube un archivo CSV/Excel. La app detecta errores — mayúsculas, espacios, duplicados, parámetros faltantes, UTMs en el fragmento # — y propone una versión corregida automáticamente. Genera un Excel de auditoría con 4 hojas listo para compartir con el equipo."),
    (":material/rate_review:", "Feedback",
     "Comparte tu opinión sobre la herramienta. Las respuestas se guardan en tiempo real y el dashboard NPS muestra el estado del producto."),
]

for title, desc in steps:
    st.markdown(f"""
    <div style="display:flex;gap:16px;align-items:flex-start;margin-bottom:20px;
                padding:16px 18px;background:#FAFAFA;border:1.5px solid #E4E4E7;border-radius:8px">
      <div style="font-size:1.3rem;flex-shrink:0;margin-top:2px">{icon}</div>
      <div>
        <div style="font-family:'Sora',sans-serif;font-size:0.82rem;font-weight:700;
                    color:#1A1A1A;margin-bottom:6px">{title}</div>
        <div style="font-family:'Sora',sans-serif;font-size:0.78rem;color:#52525B;line-height:1.65">{desc}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Próximamente ──────────────────────────────────────────
st.markdown("""
<div style="margin-top:8px;margin-bottom:32px">
  <div style="font-family:'Sora',sans-serif;font-size:0.62rem;font-weight:500;letter-spacing:0.14em;
              text-transform:uppercase;color:#71717A;margin-bottom:14px">Próximamente</div>
  <div style="display:flex;flex-direction:column;gap:10px">
    <div style="display:flex;align-items:center;gap:12px;padding:12px 16px;
                background:#F8FAFC;border:1.5px solid #E4E4E7;border-radius:6px">
      <div style="width:6px;height:6px;background:#3D5A80;border-radius:50%;flex-shrink:0"></div>
      <div style="font-family:'Sora',sans-serif;font-size:0.78rem;color:#3A3A3A;line-height:1.5">
        <strong>Soporte para <code>&amp;</code> como separador</strong> — algunos configuradores usan
        <code>&amp;</code> en lugar de <code>?</code> para los parámetros UTM. Próximamente compatible en el generador y el validador.
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:12px;padding:12px 16px;
                background:#F8FAFC;border:1.5px solid #E4E4E7;border-radius:6px">
      <div style="width:6px;height:6px;background:#3D5A80;border-radius:50%;flex-shrink:0"></div>
      <div style="font-family:'Sora',sans-serif;font-size:0.78rem;color:#3A3A3A;line-height:1.5">
        <strong>Sugerencias inteligentes</strong> — el validador sugerirá valores correctos basándose
        en tu Naming Convention cuando detecte un parámetro incorrecto o desconocido.
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:12px;padding:12px 16px;
                background:#F8FAFC;border:1.5px solid #E4E4E7;border-radius:6px">
      <div style="width:6px;height:6px;background:#3D5A80;border-radius:50%;flex-shrink:0"></div>
      <div style="font-family:'Sora',sans-serif;font-size:0.78rem;color:#3A3A3A;line-height:1.5">
        <strong>Historial de URLs generadas</strong> — para no repetir trabajo entre sesiones.
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Contacto ──────────────────────────────────────────────
st.markdown("""
<div style="font-family:'Sora',sans-serif;font-size:0.62rem;font-weight:500;letter-spacing:0.14em;
            text-transform:uppercase;color:#71717A;margin-bottom:12px">Contacto</div>
""", unsafe_allow_html=True)
st.link_button("LinkedIn — Patricia L.", "https://www.linkedin.com/in/patricialafuente/")

st.markdown("---")

# ── Proyectos en GitHub ───────────────────────────────────
st.markdown("""
<div style="font-family:'Sora',sans-serif;font-size:0.62rem;font-weight:500;letter-spacing:0.14em;
            text-transform:uppercase;color:#71717A;margin:20px 0 12px">Proyectos en GitHub</div>
""", unsafe_allow_html=True)

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
