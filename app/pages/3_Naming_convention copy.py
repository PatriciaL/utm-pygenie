import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd

st.set_page_config(page_title="Naming Convention Builder", layout="wide")
st.title("🧱 Configurador de Naming Convention para UTM")

st.markdown("""
Ordena los bloques arrastrando, añade valores personalizados en los desplegables
y exporta tu configuración como CSV.
""")

# ------------ helpers ------------
def init_state(key, default_list):
    if key not in st.session_state or not isinstance(st.session_state[key], list):
        st.session_state[key] = default_list.copy()

def reset_section(key, default_list):
    st.session_state[key] = default_list.copy()
    st.session_state[f"values_{key}"] = [""] * len(default_list)

def drag_section(title, key, default_list):
    init_state(key, default_list)

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

    # ------ valores para cada bloque ------
    st.caption("Valores para cada bloque:")
    values = st.session_state.get(f"values_{key}", [""] * len(st.session_state[key]))
    updated_values = []
    for idx, label in enumerate(st.session_state[key]):
        val = st.text_input(f"{label}", value=values[idx] if idx < len(values) else "", key=f"{key}_{idx}")
        updated_values.append(val)
    st.session_state[f"values_{key}"] = updated_values


# ------------- Secciones -------------
drag_section("utm_campaign", "campaign_order",
             ["producto", "audiencia", "fecha", "region", "pais",
              "plataforma", "funnel", "objetivo", "tipoAudiencia"])

# utm_source
st.subheader("📡 utm_source")
ga4_sources = ["google","facebook","instagram","newsletter","linkedin"]
sel_src = st.multiselect("Valores GA4", ga4_sources, default=["google"])
extra_src = st.text_input("Otros (coma separada)", key="src_extra")
source_blocks = sel_src + [s.strip() for s in extra_src.split(",") if s.strip()]
if not source_blocks:
    source_blocks = ["google"]
drag_section("Ordenar utm_source", "source_order", source_blocks)

# utm_medium
st.subheader("🎯 utm_medium")
ga4_meds = ["organic","cpc","email","referral","social"]
sel_med = st.multiselect("Valores GA4", ga4_meds, default=["cpc"])
extra_med = st.text_input("Otros (coma separada)", key="med_extra")
medium_blocks = sel_med + [s.strip() for s in extra_med.split(",") if s.strip()]
if not medium_blocks:
    medium_blocks = ["cpc"]
drag_section("Ordenar utm_medium", "medium_order", medium_blocks)

drag_section("utm_content", "content_order", ["color", "version", "posicion"])
drag_section("utm_term", "term_order", ["keyword", "matchtype"])

# ------------- Export CSV -------------
st.markdown("---")
st.subheader("📁 Exportar configuración")

def concat(order_key):
    order   = st.session_state.get(order_key, [])
    values  = st.session_state.get(f"values_{order_key}", [])
    pairs   = [f"{o}:{v or ''}" for o, v in zip(order, values)]
    return "|".join(pairs)

if st.button("📥 Generar CSV"):
    config = {
        "utm_campaign": concat("campaign_order"),
        "utm_source" : concat("source_order"),
        "utm_medium" : concat("medium_order"),
        "utm_content": concat("content_order"),
        "utm_term"   : concat("term_order"),
    }
    df = pd.DataFrame([config])
    st.dataframe(df)

    st.download_button(
        "⬇️ Descargar CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="naming_config.csv",
        mime="text/csv"
    )
