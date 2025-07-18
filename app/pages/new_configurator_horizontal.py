import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from io import BytesIO

# ------------------------------------------------------------------
# Configuración de página
# ------------------------------------------------------------------

st.set_page_config(
    page_title="Naming Convention Creator",
    page_icon="🧙",
    layout="wide"
)
st.title("Configurador de Naming Convention para UTM's")

st.markdown("""
**¿Cómo funciona?**

Arrastra los bloques de cada parámetro UTM, añade valores personalizados, y exporta la configuración como Excel.

### Funcionalidades:
- 🔀 **Arrastra los bloques y reordena**  
- ➕ **Nuevo bloque**  
- 📥 **Añadir valores al bloque**  
- 📤 **Exportar Excel con configuración**
""")

# ------------------------------------------------------------------
# Funciones utilitarias
# ------------------------------------------------------------------

def init_sec(key: str, defaults: list):
    if key not in st.session_state:
        st.session_state[key] = defaults.copy()
    if f"vals_{key}" not in st.session_state:
        st.session_state[f"vals_{key}"] = {b: [] for b in defaults}
    if f"sel_{key}" not in st.session_state:
        st.session_state[f"sel_{key}"] = defaults[0]
    if f"txt_{key}" not in st.session_state:
        st.session_state[f"txt_{key}"] = ""
    if f"newblk_{key}" not in st.session_state:
        st.session_state[f"newblk_{key}"] = ""

def reset_sec(key: str, defaults: list):
    st.session_state[key] = defaults.copy()
    st.session_state[f"vals_{key}"] = {b: [] for b in defaults}
    st.session_state[f"sel_{key}"] = defaults[0]
    st.session_state[f"txt_{key}"] = ""
    st.session_state[f"newblk_{key}"] = ""

def add_block(sec_key: str, block_name: str):
    if block_name and block_name not in st.session_state[sec_key]:
        st.session_state[sec_key].append(block_name)
        st.session_state[f"vals_{sec_key}"][block_name] = []

def add_block_callback(sec_key: str, input_key: str):
    name = st.session_state[input_key].strip()
    if name:
        add_block(sec_key, name)
    st.session_state[input_key] = ""
    st.rerun()

def add_values_callback(sec_key: str):
    blk = st.session_state[f"sel_{sec_key}"]
    txt = st.session_state[f"txt_{sec_key}"]
    if txt.strip():
        vals = [v.strip() for v in txt.split(",") if v.strip()]
        st.session_state[f"vals_{sec_key}"][blk].extend(vals)
        st.session_state[f"vals_{sec_key}"][blk] = list(dict.fromkeys(st.session_state[f"vals_{sec_key}"][blk]))
    st.session_state[f"txt_{sec_key}"] = ""

# ------------------------------------------------------------------
# Render de sección individual
# ------------------------------------------------------------------

def section(title: str, sec_key: str, defaults: list):
    init_sec(sec_key, defaults)

    st.markdown(f"### {title}")
    st.session_state[sec_key] = sort_items(
        st.session_state[sec_key],
        direction="horizontal",
        key=f"sort_{sec_key}"
    ) or st.session_state[sec_key]

    st.caption("🔀 Arrastra los bloques para cambiar el orden")
    st.write("Orden actual:", st.session_state[sec_key])

    if st.button("↩️ Reset sección", key=f"reset_{sec_key}"):
        reset_sec(sec_key, defaults)

    st.text_input("➕ Nombre del nuevo bloque", key=f"newblk_{sec_key}", placeholder="ej.: promocion")
    st.button("Agregar bloque",
              key=f"btn_addblk_{sec_key}",
              on_click=add_block_callback,
              kwargs=dict(sec_key=sec_key, input_key=f"newblk_{sec_key}"))

    st.selectbox("Bloque destino", st.session_state[sec_key], key=f"sel_{sec_key}")
    st.text_input("Valores (coma separada)", key=f"txt_{sec_key}", placeholder="valor1, valor2, valor3")
    st.button("Agregar valores",
              key=f"btn_addvals_{sec_key}",
              on_click=add_values_callback,
              kwargs=dict(sec_key=sec_key))

    with st.expander("🔍 Ver valores guardados"):
        st.json(st.session_state[f"vals_{sec_key}"])

# ------------------------------------------------------------------
# LAYOUT HORIZONTAL CON COLUMNAS
# ------------------------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    section("utm_source", "source", ["google", "facebook", "instagram", "newsletter", "linkedin"])
    section("utm_medium", "medium", ["cpc", "organic", "email", "referral", "social"])

with col2:
    section("utm_campaign", "campaign", ["producto", "pais", "fecha", "audiencia", "region"])

with col3:
    section("utm_content", "content", ["color", "version", "posicion"])
    section("utm_term", "term", ["keyword", "matchtype"])

# ------------------------------------------------------------------
# Exportar configuración a Excel
# ------------------------------------------------------------------

st.markdown("---")
st.header("📁 Exportar configuración a Excel")

def build_val_sheet():
    cols = {}
    for sec in ["campaign", "source", "medium", "content", "term"]:
        col = []
        for blk in st.session_state[sec]:
            col += [blk] + st.session_state[f"vals_{sec}"][blk] + [""]
        cols[sec] = col
    max_len = max(len(v) for v in cols.values())
    for v in cols.values():
        v.extend([""] * (max_len - len(v)))
    return pd.DataFrame(cols)

if st.button("📥 Descargar Excel"):
    df_struct = pd.DataFrame([{
        "utm_campaign": "_".join(st.session_state["campaign"]),
        "utm_source"  : "_".join(st.session_state["source"]),
        "utm_medium"  : "_".join(st.session_state["medium"]),
        "utm_content" : "_".join(st.session_state["content"]),
        "utm_term"    : "_".join(st.session_state["term"]),
    }])
    df_vals = build_val_sheet()

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_struct.to_excel(writer, index=False, sheet_name="estructura")
        df_vals.to_excel(writer, index=False, sheet_name="valores")
    buffer.seek(0)

    st.download_button(
        label="⬇️ naming_config.xlsx",
        data=buffer,
        file_name="naming_config.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
