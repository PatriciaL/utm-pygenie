import streamlit as st
import pandas as pd
from streamlit_sortables import sort_items
from io import BytesIO

st.set_page_config(page_title="Naming Builder", layout="wide")
st.title("🧱 Configurador de Naming Convention para UTM")

st.markdown("""
Arrastra bloques, agrega valores a cada bloque y exporta todo a Excel.

Ahora puedes **crear tus propios bloques**:
1. Escribe el nombre del bloque.
2. Pulsa “Agregar bloque”.
3. Después podrás añadir valores a ese bloque nuevo.
""")

# ---------- helpers ----------
def init_sec(key, defaults):
    if key not in st.session_state:
        st.session_state[key] = defaults.copy()
    if f"vals_{key}" not in st.session_state:
        st.session_state[f"vals_{key}"] = {b: [] for b in defaults}
    # campos de ayuda
    if f"sel_{key}" not in st.session_state:
        st.session_state[f"sel_{key}"] = defaults[0]
    if f"txt_{key}" not in st.session_state:
        st.session_state[f"txt_{key}"] = ""
    if f"newblk_{key}" not in st.session_state:
        st.session_state[f"newblk_{key}"] = ""

def reset_sec(key, defaults):
    st.session_state[key] = defaults.copy()
    st.session_state[f"vals_{key}"] = {b: [] for b in defaults}
    st.session_state[f"sel_{key}"]  = defaults[0]
    st.session_state[f"txt_{key}"]  = ""
    st.session_state[f"newblk_{key}"] = ""

def add_block(sec_key, block_name):
    """Añade bloque si no existe."""
    if block_name and block_name not in st.session_state[sec_key]:
        st.session_state[sec_key].append(block_name)
        st.session_state[f"vals_{sec_key}"][block_name] = []

# ------ CALLBACKS -------
def add_block_callback(sec_key, input_key):
    name = st.session_state[input_key].strip()
    add_block(sec_key, name)
    st.session_state[input_key] = ""           # limpia input

def add_values_callback(sec_key):
    blk  = st.session_state[f"sel_{sec_key}"]
    txt  = st.session_state[f"txt_{sec_key}"]
    if txt.strip():
        vals = [v.strip() for v in txt.split(",") if v.strip()]
        st.session_state[f"vals_{sec_key}"][blk].extend(vals)
        st.session_state[f"vals_{sec_key}"][blk] = list(dict.fromkeys(
            st.session_state[f"vals_{sec_key}"][blk]))
    st.session_state[f"txt_{sec_key}"] = ""    # limpia input

# ---------- sección genérica ----------
def section(title, sec_key, defaults):
    init_sec(sec_key, defaults)

    st.markdown(f"## {title}")
    st.session_state[sec_key] = sort_items(
        st.session_state[sec_key],
        direction="horizontal",
        key=f"sort_{sec_key}"
    ) or st.session_state[sec_key]

    if st.button("Reset", key=f"reset_{sec_key}"):
        reset_sec(sec_key, defaults)

    st.write("Orden:", st.session_state[sec_key])

    # --- Añadir bloque personalizado ---
    st.caption("### ➕ Nuevo bloque")
    newblk_key = f"newblk_{sec_key}"
    st.text_input("Nombre del bloque", key=newblk_key, placeholder="ej.: promocion")
    st.button("Agregar bloque",
              key=f"btn_addblk_{sec_key}",
              on_click=add_block_callback,
              kwargs=dict(sec_key=sec_key, input_key=newblk_key))

    # --- Añadir valores ---
    st.caption("### ➕ Añadir valores al bloque seleccionado")
    st.selectbox("Bloque destino", st.session_state[sec_key], key=f"sel_{sec_key}")
    st.text_input("Valores (coma separada)", key=f"txt_{sec_key}",
                  placeholder="valor1, valor2, valor3")
    st.button("Agregar valores",
              key=f"btn_addvals_{sec_key}",
              on_click=add_values_callback,
              kwargs=dict(sec_key=sec_key))

    with st.expander("🔍 Ver valores guardados"):
        st.json(st.session_state[f"vals_{sec_key}"])

# ---------- secciones UTM ----------
section("utm_campaign", "campaign",
        ["producto","pais","fecha","audiencia","region"])
section("utm_source", "source",
        ["google","facebook","instagram","newsletter","linkedin"])
section("utm_medium", "medium",
        ["cpc","organic","email","referral","social"])
section("utm_content", "content",
        ["color","version","posicion"])
section("utm_term", "term",
        ["keyword","matchtype"])

# ---------- export ----------
st.markdown("---")
st.header("📁 Exportar a Excel")

def build_val_sheet():
    cols={}
    for sec in ["campaign","source","medium","content","term"]:
        col=[]
        for blk in st.session_state[sec]:
            col += [blk]+st.session_state[f"vals_{sec}"][blk]+[""]
        cols[sec]=col
    m=max(len(v) for v in cols.values())
    for v in cols.values(): v.extend([""]*(m-len(v)))
    return pd.DataFrame(cols)

if st.button("📥 Descargar Excel"):
    df_struct = pd.DataFrame([{
        "utm_campaign":"_".join(st.session_state["campaign"]),
        "utm_source"  :"_".join(st.session_state["source"]),
        "utm_medium"  :"_".join(st.session_state["medium"]),
        "utm_content" :"_".join(st.session_state["content"]),
        "utm_term"    :"_".join(st.session_state["term"]),
    }])
    df_vals = build_val_sheet()

    buf=BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as w:
        df_struct.to_excel(w, index=False, sheet_name="estructura")
        df_vals.to_excel(w,   index=False, sheet_name="valores")
    buf.seek(0)
    st.download_button("⬇️ naming_config.xlsx", buf,
                       file_name="naming_config.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
