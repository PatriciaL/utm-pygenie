import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from io import BytesIO

st.set_page_config(
    page_title="Naming Convention Creator",
    page_icon="🧙",
    layout="centered"
)
st.title("🧙 Configurador de Naming Convention para UTM's")

st.markdown("""
**¿Cómo funciona?**

Arrastra los bloques de cada parámetro UTM, añade valores personalizados, y exporta la configuración como Excel.

- 🔀 **Arrastra los bloques y reordena**
- ➕ **Nuevo bloque** → escribe un nombre y pulsa **Agregar bloque**
- 📥 **Añadir valores** → selecciona el bloque y añade valores separados por comas
- 🗑️ **Borrar** bloques o valores individuales
- 📤 **Exportar** → descarga un archivo Excel con estructura y valores
""")

# ------------------------------------------------------------------
# Estado inicial
# ------------------------------------------------------------------

SECTIONS = {
    "campaign": ["producto", "pais", "fecha", "audiencia", "region"],
    "source":   ["google", "facebook", "instagram", "newsletter", "linkedin"],
    "medium":   ["cpc", "organic", "email", "referral", "social"],
    "content":  ["color", "version", "posicion"],
    "term":     ["keyword", "matchtype"],
}

for key, defaults in SECTIONS.items():
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
    if f"reset_count_{key}" not in st.session_state:
        st.session_state[f"reset_count_{key}"] = 0

# ------------------------------------------------------------------
# Callbacks
# ------------------------------------------------------------------

def reset_sec(key):
    defaults = SECTIONS[key]
    st.session_state[key] = defaults.copy()
    st.session_state[f"vals_{key}"] = {b: [] for b in defaults}
    st.session_state[f"sel_{key}"] = defaults[0]
    st.session_state[f"txt_{key}"] = ""
    st.session_state[f"newblk_{key}"] = ""
    st.session_state[f"reset_count_{key}"] += 1

def add_block_cb(key):
    name = st.session_state[f"newblk_input_{key}"].strip()
    if name and name not in st.session_state[key]:
        st.session_state[key].append(name)
        st.session_state[f"vals_{key}"][name] = []
        st.session_state[f"reset_count_{key}"] += 1  # fuerza re-render drag&drop
    st.session_state[f"newblk_input_{key}"] = ""

def delete_block(key, blk):
    if blk in st.session_state[key]:
        st.session_state[key].remove(blk)
    st.session_state[f"vals_{key}"].pop(blk, None)
    st.session_state[f"reset_count_{key}"] += 1

def add_values_cb(key):
    blk = st.session_state[f"sel_input_{key}"]
    txt = st.session_state[f"txt_input_{key}"].strip()
    if txt:
        vals = [v.strip() for v in txt.split(",") if v.strip()]
        existing = st.session_state[f"vals_{key}"].get(blk, [])
        for v in vals:
            if v not in existing:
                existing.append(v)
        st.session_state[f"vals_{key}"][blk] = existing
    st.session_state[f"txt_input_{key}"] = ""

def delete_val(key, blk, val):
    st.session_state[f"vals_{key}"][blk].remove(val)

def get_all_values(key):
    all_vals = []
    for blk in st.session_state[key]:
        all_vals.extend(st.session_state[f"vals_{key}"].get(blk, []))
    return list(dict.fromkeys(all_vals))

# ------------------------------------------------------------------
# Sección
# ------------------------------------------------------------------

def section(title: str, key: str):
    defaults = SECTIONS[key]
    st.markdown(f"## {title}")

    # Drag & drop — key dinámica para reflejar cambios
    rc = st.session_state[f"reset_count_{key}"]
    result = sort_items(
        st.session_state[key],
        direction="horizontal",
        key=f"sort_{key}_{rc}"
    )
    if result:
        st.session_state[key] = result

    st.caption("🔀 Arrastra los bloques para cambiar el orden")
    st.write("Orden actual:", st.session_state[key])

    # Bloques con sus valores y botones de borrado
    for blk in st.session_state[key]:
        vals = st.session_state[f"vals_{key}"].get(blk, [])
        c1, c2 = st.columns([8, 1])
        with c1:
            # Nombre del bloque + pastillas de valores inline
            pastillas = " ".join([
                f'<span style="background:#ff4b4b;color:white;padding:2px 8px;'
                f'border-radius:20px;font-size:12px;margin:1px">{v}</span>'
                for v in vals
            ])
            sin_vals = '<em style="color:#bbb;font-size:12px">sin valores</em>' if not vals else ""
            st.markdown(
                f'<div style="margin:6px 0"><strong>{blk}</strong> &nbsp; {pastillas}{sin_vals}</div>',
                unsafe_allow_html=True
            )
        with c2:
            if st.button("🗑️", key=f"del_blk_{key}_{blk}", help=f"Borrar bloque '{blk}'"):
                delete_block(key, blk)
                st.rerun()

        # Borrar valores individuales
        if vals:
            val_cols = st.columns(len(vals))
            for i, val in enumerate(vals):
                with val_cols[i]:
                    if st.button(f"✕ {val}", key=f"del_val_{key}_{blk}_{val}"):
                        delete_val(key, blk, val)
                        st.rerun()

    st.markdown("")

    # Reset
    if st.button("↩️ Reset sección", key=f"reset_btn_{key}"):
        reset_sec(key)
        st.rerun()

    # Añadir nuevo bloque
    st.markdown("### ➕ Añadir nuevo bloque")
    st.text_input("Nombre del bloque", key=f"newblk_input_{key}", placeholder="ej.: promocion")
    st.button("Agregar bloque", key=f"btn_addblk_{key}", on_click=add_block_cb, kwargs={"key": key})

    # Añadir valores a un bloque
    st.markdown("### 📥 Añadir valores al bloque")
    if st.session_state[key]:
        st.selectbox("Bloque destino", st.session_state[key], key=f"sel_input_{key}")
        st.text_input("Valores (coma separada)", key=f"txt_input_{key}", placeholder="valor1, valor2, valor3")
        st.button("Agregar valores", key=f"btn_addvals_{key}", on_click=add_values_cb, kwargs={"key": key})
    else:
        st.info("Añade al menos un bloque primero.")

    # Ver valores guardados
    with st.expander("🔍 Ver valores guardados"):
        st.json(st.session_state[f"vals_{key}"])

    # Preview para el generador
    preview = get_all_values(key)
    if preview:
        st.caption(f"⚡ El generador usará: `{', '.join(preview)}`")

    st.markdown("---")

# ------------------------------------------------------------------
# Renderizado de secciones
# ------------------------------------------------------------------

section("utm_campaign", "campaign")
section("utm_source",   "source")
section("utm_medium",   "medium")
section("utm_content",  "content")
section("utm_term",     "term")

# ------------------------------------------------------------------
# Exportar a Excel
# ------------------------------------------------------------------

st.header("📁 Exportar configuración a Excel")

def build_val_sheet():
    cols = {}
    for sec in SECTIONS:
        col = []
        for blk in st.session_state[sec]:
            col += [blk] + st.session_state[f"vals_{sec}"].get(blk, []) + [""]
        cols[sec] = col
    max_len = max(len(v) for v in cols.values())
    for v in cols.values():
        v.extend([""] * (max_len - len(v)))
    return pd.DataFrame(cols)

if st.button("📥 Descargar Excel"):
    df_struct = pd.DataFrame([{
        f"utm_{sec}": "_".join(st.session_state[sec])
        for sec in SECTIONS
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

# ------------------------------------------------------------------
# CTA al generador
# ------------------------------------------------------------------
st.markdown("---")
st.success("✅ Cuando hayas configurado tus valores, ve al **Generador** y se cargarán automáticamente.")
st.page_link("pages/1_generator_UTM.py", label="⚡ Ir al Generador Masivo", icon="🔧")
