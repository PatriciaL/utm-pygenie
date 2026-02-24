import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from io import BytesIO

st.set_page_config(
    page_title="Naming Convention Creator",
    page_icon="🧙",
    layout="centered"
)
st.title("🧙 Configurador de Naming Convention")

st.markdown("""
**¿Cómo funciona?**  
Define los bloques de cada parámetro UTM, añade valores y ordénalos arrastrando.  
Cuando termines, ve al **Generador** — los valores se cargarán automáticamente. 🚀
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
    if f"blocks_{key}" not in st.session_state:
        st.session_state[f"blocks_{key}"] = defaults.copy()
    if f"vals_{key}" not in st.session_state:
        st.session_state[f"vals_{key}"] = {b: [] for b in defaults}
    if f"reset_count_{key}" not in st.session_state:
        st.session_state[f"reset_count_{key}"] = 0

# ------------------------------------------------------------------
# Callbacks
# ------------------------------------------------------------------

def reset_sec(key):
    defaults = SECTIONS[key]
    st.session_state[f"blocks_{key}"] = defaults.copy()
    st.session_state[f"vals_{key}"]   = {b: [] for b in defaults}
    st.session_state[f"reset_count_{key}"] += 1

def add_block_cb(key):
    name = st.session_state[f"newblk_{key}"].strip()
    if name and name not in st.session_state[f"blocks_{key}"]:
        st.session_state[f"blocks_{key}"].append(name)
        st.session_state[f"vals_{key}"][name] = []
    st.session_state[f"newblk_{key}"] = ""

def delete_block(key, blk):
    st.session_state[f"blocks_{key}"].remove(blk)
    st.session_state[f"vals_{key}"].pop(blk, None)
    st.rerun()

def add_val_cb(key, blk):
    txt = st.session_state[f"newval_{key}_{blk}"].strip()
    if txt:
        new_vals = [v.strip() for v in txt.split(",") if v.strip()]
        existing = st.session_state[f"vals_{key}"][blk]
        for v in new_vals:
            if v not in existing:
                existing.append(v)
    st.session_state[f"newval_{key}_{blk}"] = ""

def delete_val(key, blk, val):
    st.session_state[f"vals_{key}"][blk].remove(val)
    st.rerun()

def get_all_values(key):
    all_vals = []
    for blk in st.session_state[f"blocks_{key}"]:
        all_vals.extend(st.session_state[f"vals_{key}"].get(blk, []))
    return list(dict.fromkeys(all_vals))

# ------------------------------------------------------------------
# Renderizado de sección
# ------------------------------------------------------------------

def section(title: str, key: str):
    st.markdown(f"## {title}")

    # --- Drag & drop de bloques ---
    rc = st.session_state[f"reset_count_{key}"]
    result = sort_items(
        st.session_state[f"blocks_{key}"],
        direction="horizontal",
        key=f"sort_{key}_{rc}"
    )
    if result:
        # Sincronizar orden sin perder valores
        st.session_state[f"blocks_{key}"] = result

    st.caption("🔀 Arrastra los bloques para cambiar el orden")

    # --- Valores bajo cada bloque ---
    for blk in st.session_state[f"blocks_{key}"]:
        vals = st.session_state[f"vals_{key}"].get(blk, [])

        # Cabecera del bloque con botón borrar
        c1, c2 = st.columns([6, 1])
        with c1:
            st.markdown(f"**{blk}**")
        with c2:
            if st.button("🗑️", key=f"del_blk_{key}_{blk}", help=f"Borrar bloque '{blk}'"):
                delete_block(key, blk)

        # Pastillas de valores con botón borrar
        if vals:
            cols = st.columns(len(vals))
            for i, val in enumerate(vals):
                with cols[i]:
                    st.markdown(
                        f'<span style="background:#ff4b4b;color:white;padding:3px 10px;'
                        f'border-radius:20px;font-size:13px">{val}</span>',
                        unsafe_allow_html=True
                    )
                    if st.button("✕", key=f"del_val_{key}_{blk}_{val}", help=f"Borrar '{val}'"):
                        delete_val(key, blk, val)
        else:
            st.caption("_sin valores_")

        # Input para añadir valores a este bloque
        with st.expander(f"➕ Añadir valores a '{blk}'"):
            st.text_input(
                "Valores (separados por coma)",
                key=f"newval_{key}_{blk}",
                placeholder="valor1, valor2, valor3"
            )
            st.button(
                "Agregar",
                key=f"btn_addval_{key}_{blk}",
                on_click=add_val_cb,
                kwargs={"key": key, "blk": blk}
            )

        st.markdown("---")

    # --- Añadir nuevo bloque ---
    st.markdown("### ➕ Añadir nuevo bloque")
    col1, col2 = st.columns([4, 1])
    with col1:
        st.text_input("Nombre del bloque", key=f"newblk_{key}", placeholder="ej.: promocion", label_visibility="collapsed")
    with col2:
        st.button("Agregar", key=f"btn_addblk_{key}", on_click=add_block_cb, kwargs={"key": key})

    # --- Reset ---
    if st.button("↩️ Reset sección", key=f"reset_btn_{key}"):
        reset_sec(key)
        st.rerun()

    # --- Preview para el generador ---
    preview_vals = get_all_values(key)
    if preview_vals:
        st.caption(f"⚡ El generador usará: `{', '.join(preview_vals)}`")

    st.markdown("---")

# ------------------------------------------------------------------
# Renderizado de las 5 secciones
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
        for blk in st.session_state[f"blocks_{sec}"]:
            col += [blk] + st.session_state[f"vals_{sec}"].get(blk, []) + [""]
        cols[sec] = col
    max_len = max(len(v) for v in cols.values())
    for v in cols.values():
        v.extend([""] * (max_len - len(v)))
    return pd.DataFrame(cols)

if st.button("📥 Descargar Excel"):
    df_struct = pd.DataFrame([{
        f"utm_{sec}": "_".join(st.session_state[f"blocks_{sec}"])
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
# CTA: ir al generador
# ------------------------------------------------------------------
st.markdown("---")
st.success("✅ Cuando hayas configurado tus valores, ve al **Generador** y se cargarán automáticamente.")
st.page_link("pages/1_generator_UTM.py", label="⚡ Ir al Generador Masivo", icon="🔧")
