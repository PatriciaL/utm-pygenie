import streamlit as st
import pandas as pd
from streamlit_sortables import sort_items
from io import BytesIO

st.set_page_config(page_title="Naming Builder", layout="wide")
st.title("🧱 Configurador de Naming Convention para UTM")

st.markdown("""
Arrastra bloques, agrega valores a cada bloque y exporta la configuración.

**Novedad:** ahora puedes **crear tus propios bloques**.  
""")

# ---------- helpers ----------
def init_sec(key, defaults):
    """Inicia orden de bloques y lista de valores."""
    if key not in st.session_state:
        st.session_state[key] = defaults.copy()
    if f"vals_{key}" not in st.session_state:
        st.session_state[f"vals_{key}"] = {b: [] for b in defaults}

def reset_sec(key, defaults):
    st.session_state[key] = defaults.copy()
    st.session_state[f"vals_{key}"] = {b: [] for b in defaults}

def add_block(sec_key, new_block):
    """Añade un bloque personalizado en la lista de orden y crea clave de valores."""
    if new_block and new_block not in st.session_state[sec_key]:
        st.session_state[sec_key].append(new_block)
        st.session_state[f"vals_{sec_key}"][new_block] = []

def add_values_callback(sec_key):
    """Callback botón Agregar valores."""
    blk  = st.session_state[f"sel_{sec_key}"]
    txt  = st.session_state[f"txt_{sec_key}"]
    if txt.strip():
        vals = [v.strip() for v in txt.split(",") if v.strip()]
        st.session_state[f"vals_{sec_key}"][blk].extend(vals)
        st.session_state[f"vals_{sec_key}"][blk] = list(dict.fromkeys(
            st.session_state[f"vals_{sec_key}"][blk]))  # sin duplicados
    st.session_state[f"txt_{sec_key}"] = ""  # limpia

def section(title, sec_key, defaults):
    init_sec(sec_key, defaults)

    st.markdown(f"### {title}")
    st.session_state[sec_key] = sort_items(
        st.session_state[sec_key],
        direction="horizontal",
        key=f"sort_{sec_key}"
    ) or st.session_state[sec_key]

    # --- añadir bloque personalizado ---
    with st.expander("➕ Añadir nuevo bloque"):
        new_block = st.text_input("Nombre del nuevo bloque", key=f"newblk_{sec_key}")
        if st.button("Agregar bloque", key=f"btnblk_{sec_key}") and new_block.strip():
            add_block(sec_key, new_block.strip())
            st.success(f"Bloque “{new_block}” añadido")
            st.session_state[f"newblk_{sec_key}"] = ""  # limpia

    # --- formulario estable para valores ---
    st.selectbox("Bloque destino", st.session_state[sec_key], key=f"sel_{sec_key}")
    st.text_input("Valores (coma separada)", key=f"txt_{sec_key}")
    st.button("➕ Agregar valores", key=f"addvals_{sec_key}",
              on_click=add_values_callback, kwargs=dict(sec_key=sec_key))

    # vista
    with st.expander("🔍 Ver valores guardados"):
        st.json(st.session_state[f"vals_{sec_key}"])

# ---------- secciones ----------
section("✳️ utm_campaign", "campaign",
        ["producto","pais","fecha","audiencia","region"])

section("📡 utm_source", "source",
        ["google","facebook","instagram","newsletter","linkedin"])

section("🎯 utm_medium", "medium",
        ["cpc","organic","email","referral","social"])

section("🧩 utm_content", "content",
        ["color","version","posicion"])

section("🔍 utm_term", "term",
        ["keyword","matchtype"])

# ---------- export ----------
st.markdown("---")
st.header("📁 Exportar a Excel")

def _col(sec):
    col=[]
    for blk in st.session_state[sec]:
        col+=[blk]+st.session_state[f"vals_{sec}"][blk]+[""]
    return col

if st.button("📥 Descargar Excel"):
    df1 = pd.DataFrame([{
        "utm_campaign": "_".join(st.session_state["campaign"]),
        "utm_source"  : "_".join(st.session_state["source"]),
        "utm_medium"  : "_".join(st.session_state["medium"]),
        "utm_content" : "_".join(st.session_state["content"]),
        "utm_term"    : "_".join(st.session_state["term"]),
    }])
    cols={k:_col(k) for k in ["campaign","source","medium","content","term"]}
    m=max(len(v) for v in cols.values())
    for v in cols.values(): v.extend([""]*(m-len(v)))
    df2=pd.DataFrame(cols)

    buf=BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as w:
        df1.to_excel(w, sheet_name="estructura", index=False)
        df2.to_excel(w, sheet_name="valores",     index=False)
    buf.seek(0)
    st.download_button("⬇️ naming_config.xlsx", buf,
        "naming_config.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
