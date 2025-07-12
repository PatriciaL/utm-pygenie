import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Naming Convention Builder", layout="wide")
st.title("🧱 Configurador de Naming Convention para UTM")

st.markdown("""
Organiza tus parámetros UTM mediante bloques *drag & drop*, agrega valores
personalizados y exporta la configuración como archivo Excel.

---

**Indicaciones rápidas**

1. Arrastra los bloques horizontales para definir el orden.
2. En cada bloque puedes añadir varios valores separados por comas.
3. Los valores quedan almacenados y puedes exportarlos en la hoja “valores”.
""")

# ---------- utilidades ----------
def init_section(key, default_list):
    """Inicializa estado para orden y listas de valores."""
    if key not in st.session_state:
        st.session_state[key] = default_list.copy()
    if f"list_{key}" not in st.session_state:
        st.session_state[f"list_{key}"] = {blk: [] for blk in default_list}

def reset_section(key, default_list):
    """Restablece orden y vacía listas de valores."""
    st.session_state[key] = default_list.copy()
    st.session_state[f"list_{key}"] = {blk: [] for blk in default_list}

def drag_section(title, key, default_list):
    """Sección con drag & drop y gestión de valores."""
    init_section(key, default_list)

    st.subheader(title)
    cols = st.columns([8, 1])
    with cols[0]:
        ordered = sort_items(
            items=st.session_state[key],
            direction="horizontal",
            key=f"sortable_{key}"
        )
        if isinstance(ordered, list):
            st.session_state[key] = ordered
    with cols[1]:
        if st.button("🔄 Reset", key=f"reset_{key}"):
            reset_section(key, default_list)

    # ---- valores por bloque ----
    for blk in st.session_state[key]:
        st.markdown(f"##### 🔹 Valores en **{blk}**")
        current_vals = st.session_state[f"list_{key}"][blk]
        st.write(current_vals or "*Sin valores*")

        new_val_key = f"{key}_{blk}_input"
        new_val = st.text_input(
            f"Nuevos valores (coma separada) → {blk}",
            key=new_val_key,
            placeholder="ej: rojo, azul, verde"
        )
        if st.button("➕ Agregar", key=f"{key}_{blk}_btn") and new_val.strip():
            añadidos = [v.strip() for v in new_val.split(",") if v.strip()]
            st.session_state[f"list_{key}"][blk].extend(añadidos)
            st.session_state[new_val_key] = ""  # limpia el campo
            st.success(f"Añadido: {', '.join(añadidos)}")

# ---------- secciones ----------
drag_section("✳️ utm_campaign", "campaign_order",
             ["tipoAudiencia", "pais", "plataforma", "producto",
              "funnel", "objetivo", "fecha", "audiencia", "region"])

# utm_source con GA4 sugeridos
st.subheader("📡 utm_source – Sugeridos GA4")
ga4_sources = ["google","facebook","instagram","newsletter","linkedin"]
sel_src   = st.multiselect("Elige sugeridos", ga4_sources, default=["google"])
extra_src = st.text_input("Otros (coma separada)", key="source_extra")
src_blocks = sel_src + [s.strip() for s in extra_src.split(",") if s.strip()]
if not src_blocks:
    src_blocks = ["google"]
drag_section("Ordenar utm_source", "source_order", src_blocks)

# utm_medium
st.subheader("🎯 utm_medium – Sugeridos GA4")
ga4_mediums = ["organic","cpc","email","referral","social"]
sel_med   = st.multiselect("Elige sugeridos", ga4_mediums, default=["cpc"])
extra_med = st.text_input("Otros (coma separada)", key="medium_extra")
med_blocks = sel_med + [m.strip() for m in extra_med.split(",") if m.strip()]
if not med_blocks:
    med_blocks = ["cpc"]
drag_section("Ordenar utm_medium", "medium_order", med_blocks)

# utm_content y utm_term fijos
drag_section("🧩 utm_content", "content_order", ["color", "version", "posicion"])
drag_section("🔍 utm_term", "term_order", ["keyword", "matchtype"])

# ---------- exportar ----------
st.markdown("---")
st.subheader("📁 Exportar configuración a Excel")

def concat_order(order_key):
    return "_".join(st.session_state.get(order_key, []))

def build_val_sheet():
    cols = {}
    for sec in ["campaign_order","source_order","medium_order","content_order","term_order"]:
        col = []
        for blk in st.session_state[sec]:
            vals = st.session_state[f"list_{sec}"][blk] or [""]
            col.extend([blk] + vals + [""])  # separador vacío
        cols[sec.replace("_order","")] = col
    # igualamos longitudes
    max_len = max(len(v) for v in cols.values())
    for k, v in cols.items():
        v.extend([""] * (max_len - len(v)))
    return pd.DataFrame(cols)

if st.button("📥 Generar Excel"):
    hoja1 = pd.DataFrame([{
        "utm_campaign": concat_order("campaign_order"),
        "utm_source"  : concat_order("source_order"),
        "utm_medium"  : concat_order("medium_order"),
        "utm_content" : concat_order("content_order"),
        "utm_term"    : concat_order("term_order"),
    }])
    hoja2 = build_val_sheet()

    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        hoja1.to_excel(writer, index=False, sheet_name="estructura")
        hoja2.to_excel(writer, index=False, sheet_name="valores")

    buf.seek(0)
    st.download_button(
        "⬇️ Descargar naming_config.xlsx",
        data=buf,
        file_name="naming_config.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
