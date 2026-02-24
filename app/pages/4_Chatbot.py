import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from style import apply_style

import streamlit as st

st.set_page_config(page_title="UTM Genie — Chatbot", page_icon="🧙", layout="centered")
apply_style()

st.markdown("""
<div style="margin-bottom:28px;padding-bottom:20px;border-bottom:1.5px solid #E4E4E7">
  <div style="font-family:'Sora',sans-serif;font-size:0.6rem;font-weight:500;
              letter-spacing:0.2em;text-transform:uppercase;color:#71717A;margin-bottom:8px">
    UTM Genie
  </div>
  <div style="font-family:'Sora',sans-serif;font-size:1.8rem;font-weight:600;
              letter-spacing:-0.04em;color:#1A1A1A;line-height:1.1;margin-bottom:10px">
    Asistente UTM
  </div>
  <div style="font-family:'Sora',sans-serif;font-size:0.8rem;color:#71717A;letter-spacing:0.01em">
    Próximamente disponible
  </div>
</div>

""", unsafe_allow_html=True)
st.info("Esta funcionalidad está en desarrollo.")
