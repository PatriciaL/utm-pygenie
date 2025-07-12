import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Naming Convention Builder", layout="wide")
st.title("🧱 Configurador de Naming Convention para UTM")

st.markdown("""
Arrastra los bloques para ordenar cada parámetro UTM, añade valores (separados por comas) y
exporta la configuración a Excel.

Cada bloque usa un **formulario** propio: al pulsar *Agregar* se añade el/los valores y el
form se limpia, evitando errores de frontend.
""")

# ---------- helpers ----------
def init_section(sec_key, default_list):
    if sec_key not in st.session_state:
        st.session_state[sec_key] = default_list.copy()
    if f"vals_{sec_key}" not in st.session_state:
        st.session_state[f"vals_{sec_key}"] = {blk: [] for blk in default_list}

def reset_section(sec_key, default_list):
    st.session_state[sec_key] = default_list.copy()
    st.session_state[f"vals_{sec_key}"] = {blk: [] for blk in default_list}

def drag_section(title, sec_key, default_list):
    init_section(sec_key, default_list)

    st.subheader(title)
    st.session_state[sec_key] = sort_items(
        st.session_state[sec_key],
        direction="horizontal",
        key=f"sortable_{sec_key}"
    ) or st.session_state[sec_key]

    if st.button("🔄 Reset", key=f"reset_{sec_key}"):
        reset_section(sec_key, default_list)

    # -- formulario de valores por bloque --
    for blk in st.session_state[sec_key]:
        with st.form(f"form_{sec_key}_{blk}", clear_on_submit=True):
            st.markdown(f"**{blk}** — {st.session_state[f'vals_{sec_key}'][blk] or 'sin valores'}")
            txt = st.text_input("Añadir valores (coma separada)")
            submitted = st.form_submit_button("➕ Agregar")
            if submitted and txt.strip():
                nuevos = [v.strip() for v in txt.split(",") if v.strip()]
                st.session_state[f"vals_{sec_key}"][blk].extend(nuevos)
                st.success(f"Añadido: {', '.join(nuevos)}")

# ---------- secciones ----------
drag_section("✳️ utm_campaign", "campaign_order",
             ["tipoAudiencia","pais","plataforma","producto",
              "funnel","objetivo","fecha","audiencia","region"])

drag_section("📡 utm_source", "source_order",
             ["google","facebook","instagram","newsletter","linkedin"])

drag_section("🎯 utm_medium", "medium_order",
             ["organic","cpc","email","referral","social"])

drag_section("🧩 utm_content", "content_order",
             ["color","version","posicion"])

drag_section("🔍 utm_term", "term_order",
             ["keyword","matchtype"])

# ---------- export ----------
st.markdown("---")
st.subheader("📁 Exportar a Excel")

def _join(sec): return "_".join(st.session_state[sec])

def build_val_sheet():
    cols = {}
    for sec in ["campaign_order","source_order","medium_order","content_order","term_order"]:
        col = []
        for blk in st.session_state[sec]:
            vals = st.session_state[f"vals_{sec}"][blk] or [""]
            col.extend([blk] + vals + [""])
        cols[sec.replace("_order","")] = col
    max_len = max(len(v) for v in cols.values())
    for k,v in cols.items():
        v.extend([""]*(max_len-len(v)))
    return pd.DataFrame(cols)

if st.button("📥 Generar Excel"):
    hoja1 = pd.DataFrame([{
        "utm_campaign": _join("campaign_order"),
        "utm_source": _join("source_order"),
        "utm_medium": _join("medium_order"),
        "utm_content": _join("content_order"),
        "utm_term": _join("term_order"),
    }])
    hoja2 = build_val_sheet()

    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as w:
        hoja1.to_excel(w, sheet_name="estructura", index=False)
        hoja2.to_excel(w, sheet_name="valores", index=False)
    buf.seek(0)

    st.download_button("⬇️ Descargar naming_config.xlsx",
                       data=buf,
                       file_name="naming_config.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
