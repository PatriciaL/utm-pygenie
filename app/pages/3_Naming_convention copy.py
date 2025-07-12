import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Naming Convention Builder", layout="wide")
st.title("🧱 Configurador de Naming Convention para UTM")

# ------------ helpers ------------
def init_section(key, default_list):
    if key not in st.session_state:
        st.session_state[key] = default_list.copy()
    if f"list_{key}" not in st.session_state:
        st.session_state[f"list_{key}"] = {item: [] for item in default_list}
    if f"sel_{key}" not in st.session_state:
        st.session_state[f"sel_{key}"] = {item: "" for item in default_list}

def reset_section(key, default_list):
    st.session_state[key] = default_list.copy()
    st.session_state[f"list_{key}"] = {item: [] for item in default_list}
    st.session_state[f"sel_{key}"]  = {item: "" for item in default_list}

def drag_section(title, key, default_list):
    init_section(key, default_list)

    st.subheader(title)
    cols = st.columns([8,1])
    with cols[0]:
        new_order = sort_items(
            st.session_state[key],
            direction="horizontal",
            key=f"sortable_{key}"
        )
        if isinstance(new_order, list):
            st.session_state[key] = new_order
    with cols[1]:
        if st.button("🔄 Reset", key=f"reset_{key}"):
            reset_section(key, default_list)

    # ---- values per block ----
    st.expander("➕ Añadir / Elegir valores", expanded=False)
    with st.expander(f"Valores en {title}", expanded=False):
        for item in st.session_state[key]:
            st.markdown(f"**{item}**")
            # añadir valor
            new_val = st.text_input(f"Nuevo valor para {item}", key=f"{key}_add_{item}")
            if st.button("➕ Agregar", key=f"{key}_btn_{item}") and new_val.strip():
                st.session_state[f"list_{key}"][item].append(new_val.strip())
                st.success(f"Añadido “{new_val}” a {item}")
            # select valor
            current_vals = st.session_state[f"list_{key}"][item]
            sel = st.selectbox(
                "Elegir valor activo",
                [""] + current_vals,
                index=([""] + current_vals).index(st.session_state[f"sel_{key}"].get(item, "")),
                key=f"select_{key}_{item}"
            )
            st.session_state[f"sel_{key}"][item] = sel

# ------------ secciones ------------
drag_section("✳️ utm_campaign","campaign_order",
    ["producto","audiencia","fecha","region","pais","plataforma","funnel","objetivo","tipoAudiencia"])

drag_section("📡 utm_source","source_order",
    ["google","facebook","instagram","newsletter","linkedin"])

drag_section("🎯 utm_medium","medium_order",
    ["organic","cpc","email","referral","social"])

drag_section("🧩 utm_content","content_order",
    ["color","version","posicion"])

drag_section("🔍 utm_term","term_order",
    ["keyword","matchtype"])

# ------------ export ------------
st.markdown("---")
st.subheader("📁 Exportar a Excel")

def build_concat(section):
    order = st.session_state.get(section, [])
    sel   = st.session_state.get(f"sel_{section}", {})
    parts = [f"{blk}:{sel.get(blk,'')}" if sel.get(blk) else blk for blk in order]
    return "_".join(parts)

if st.button("📥 Generar Excel"):
    # Hoja 1: plantilla
    plantilla = {
        "utm_campaign": build_concat("campaign_order"),
        "utm_source"  : build_concat("source_order"),
        "utm_medium"  : build_concat("medium_order"),
        "utm_content" : build_concat("content_order"),
        "utm_term"    : build_concat("term_order"),
    }
    df_plantilla = pd.DataFrame([plantilla])

    # Hoja 2: listas verticales
    lista_cols = {}
    for sec in ["campaign_order","source_order","medium_order","content_order","term_order"]:
        col_vals = []
        for blk in st.session_state[sec]:
            valores = st.session_state[f"list_{sec}"][blk]
            if not valores:
                valores = [""]
            # añadimos nombre del bloque arriba
            col_vals.extend([blk] + valores + [""])  # espacio vacío separador
        lista_cols[sec.replace("_order","")] = col_vals
    df_listas = pd.DataFrame(dict(lista_cols))

    # Guardar a Excel en memoria
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_plantilla.to_excel(writer, index=False, sheet_name="plantilla")
        df_listas.to_excel(writer, index=False, sheet_name="listas")
    buffer.seek(0)

    st.download_button(
        "⬇️ Descargar naming_config.xlsx",
        data=buffer,
        file_name="naming_config.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
