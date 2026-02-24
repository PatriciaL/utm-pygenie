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
Arrastra los bloques de cada parámetro UTM, añade valores personalizados y exporta la configuración.
Cuando termines, ve al **Generador** — los valores se cargarán automáticamente. 🚀

- 🔀 **Arrastra los bloques** para cambiar el orden
- ➕ **Nuevo bloque** para añadir campos personalizados
- 📥 **Añadir valores** para rellenar los desplegables
- 📤 **Exportar** para descargar la configuración en Excel
""")

# ------------------------------------------------------------------
# Inicialización de estado global
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
    if f"reset_count_{key}" not in st.session_state:
        st.session_state[f"reset_count_{key}"] = 0

# ------------------------------------------------------------------
# Funciones utilitarias
# ------------------------------------------------------------------

def reset_sec(key: str):
    defaults = SECTIONS[key]
    st.session_state[key] = defaults.copy()
    st.session_state[f"vals_{key}"] = {b: [] for b in defaults}
    st.session_state[f"reset_count_{key}"] += 1

def add_block_callback(sec_key: str):
    name = st.session_state[f"newblk_input_{sec_key}"].strip()
    if name and name not in st.session_state[sec_key]:
        st.session_state[sec_key].append(name)
        st.session_state[f"vals_{sec_key}"][name] = []
    st.session_state[f"newblk_input_{sec_key}"] = ""

def add_values_callback(sec_key: str):
    blk = st.session_state[f"sel_input_{sec_key}"]
    txt = st.session_state[f"txt_input_{sec_key}"]
    if txt.strip():
        vals = [v.strip() for v in txt.split(",") if v.strip()]
        st.session_state[f"vals_{sec_key}"][blk].extend(vals)
        st.session_state[f"vals_{sec_key}"][blk] = list(dict.fromkeys(
            st.session_state[f"vals_{sec_key}"][blk]
        ))
    st.session_state[f"txt_input_{sec_key}"] = ""

def get_all_values(sec_key: str) -> list:
    all_vals = []
    for blk in st.session_state.get(sec_key, []):
        all_vals.extend(st.session_state.get(f"vals_{sec_key}", {}).get(blk, []))
    return list(dict.fromkeys(all_vals))

# ------------------------------------------------------------------
# Renderizado de sección
# ------------------------------------------------------------------

def section(title: str, sec_key: str):
    st.markdown(f"## {title}")

    # Drag & drop con key dinámica para que el reset funcione
    reset_count = st.session_state[f"reset_count_{sec_key}"]
    result = sort_items(
        st.session_state[sec_key],
        direction="horizontal",
        key=f"sort_{sec_key}_{reset_count}"
    )
    if result:
        st.session_state[sec_key] = result

    st.caption("🔀 Arrastra los bloques para cambiar el orden")
    st.write("Orden actual:", st.session_state[sec_key])

    if st.button("↩️ Reset sección", key=f"reset_btn_{sec_key}"):
        reset_sec(sec_key)
        st.rerun()

    # --- Añadir nuevo bloque ---
    st.markdown("### ➕ Añadir nuevo bloque")
    st.text_input(
        "Nombre del bloque",
        key=f"newblk_input_{sec_key}",
        placeholder="ej.: promocion"
    )
    st.button(
        "Agregar bloque",
        key=f"btn_addblk_{sec_key}",
        on_click=add_block_callback,
        kwargs={"sec_key": sec_key}
    )

    # --- Añadir valores al bloque ---
    st.markdown("### 📥 Añadir valores al bloque")
    bloques_actuales = st.session_state[sec_key]
    if bloques_actuales:
        st.selectbox(
            "Bloque destino",
            bloques_actuales,
            key=f"sel_input_{sec_key}"
        )
        st.text_input(
            "Valores (separados por coma)",
            key=f"txt_input_{sec_key}",
            placeholder="valor1, valor2, valor3"
        )
        st.button(
            "Agregar valores",
            key=f"btn_addvals_{sec_key}",
            on_click=add_values_callback,
            kwargs={"sec_key": sec_key}
        )
    else:
        st.info("Añade al menos un bloque antes de agregar valores.")

    # --- Ver valores guardados ---
    with st.expander("🔍 Ver valores guardados"):
        st.json(st.session_state[f"vals_{sec_key}"])

    # --- Preview para el generador ---
    preview_vals = get_all_values(sec_key)
    if preview_vals:
        st.caption(f"⚡ El generador masivo usará: `{', '.join(preview_vals)}`")

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
# Exportar configuración a Excel
# ------------------------------------------------------------------

st.header("📁 Exportar configuración a Excel")

def build_val_sheet():
    cols = {}
    for sec in SECTIONS:
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
# CTA: ir al generador
# ------------------------------------------------------------------
st.markdown("---")
st.success("✅ Cuando hayas configurado tus valores, ve al **Generador** y se cargarán automáticamente.")
st.page_link("pages/1_generator_UTM.py", label="⚡ Ir al Generador Masivo", icon="🔧")
