import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Naming Convention Builder", layout="wide")
st.title("🧱 Configurador de Naming Convention para UTM")

# ------------ utilidades ------------
def init_section(key, default_list):
    if key not in st.session_state:
        st.session_state[key] = default_list.copy()
    if f"list_{key}" not in st.session_state:
        st.session_state[f"list_{key}"] = {blk: [] for blk in default_list}

def reset_section(key, default_list):
    st.session_state[key] = default_list.copy()
    st.session_state[f"list_{key}"] = {blk: [] for blk in default_list}

def add_values_callback(sec_key, blk, input_key):
    txt = st.session_state[input_key]
    if txt.strip():
        nuevos = [v.strip() for v in txt.split(",") if v.strip()]
        st.session_state[f"list_{sec_key}"][blk].extend(nuevos)
        st.session_state[input_key] = ""      # ✅ limpiamos aquí (callback)

def drag_section(title, sec_key, default_list):
    init_section(sec_key, default_list)

    st.subheader(title)
    cols = st.columns([8, 1])
    with cols[0]:
        ordered = sort_items(
            st.session_state[sec_key],
            direction="horizontal",
            key=f"sortable_{sec_key}"
        )
        if isinstance(ordered, list):
            st.session_state[sec_key] = ordered
    with cols[1]:
        if st.button("🔄 Reset", key=f"reset_{sec_key}"):
            reset_section(sec_key, default_list)

    # ---- valores por bloque ----
    for blk in st.session_state[sec_key]:
        st.markdown(f"**{blk}**")
        st.write(st.session_state[f"list_{sec_key}"][blk] or "*Sin valores*")

        input_key = f"{sec_key}_{blk}_txt"
        st.text_input(
            "Añadir valores (coma separada)",
            key=input_key,
            placeholder="rojo, azul, verde"
        )
        st.button(
            "➕ Agregar",
            key=f"btn_{sec_key}_{blk}",
            on_click=add_values_callback,
            kwargs=dict(sec_key=sec_key, blk=blk, input_key=input_key)
        )

# ------------ secciones ------------
drag_section("✳️ utm_campaign", "campaign_order",
             ["tipoAudiencia","pais","plataforma","producto",
              "funnel","objetivo","fecha","audiencia","region"])

drag_section("📡 utm_source",  "source_order",
             ["google","facebook","instagram","newsletter","linkedin"])

drag_section("🎯 utm_medium",  "medium_order",
             ["organic","cpc","email","referral","social"])

drag_section("🧩 utm_content", "content_order", ["color","version","posicion"])
drag_section("🔍 utm_term",    "term_order",    ["keyword","matchtype"])

# ------------ exportar ------------
def concat(sec):
    return "_".join(st.session_state.get(sec, []))

def build_val_sheet():
    cols = {}
    for sec in ["campaign_order","source_order","medium_order","content_order","term_order"]:
        col = []
        for blk in st.session_state[sec]:
            vals = st.session_state[f"list_{sec}"][blk] or [""]
            col.extend([blk] + vals + [""])
        cols[sec.replace("_order","")] = col
    m = max(len(v) for v in cols.values())
    for k,v in cols.items():
        v.extend([""]*(m-len(v)))
    return pd.DataFrame(cols)

st.markdown("---")
if st.button("📥 Generar Excel"):
    hoja1 = pd.DataFrame([{
        "utm_campaign": concat("campaign_order"),
        "utm_source": concat("source_order"),
        "utm_medium": concat("medium_order"),
        "utm_content": concat("content_order"),
        "utm_term": concat("term_order"),
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
