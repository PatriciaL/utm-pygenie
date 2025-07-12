import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd

st.set_page_config(page_title="Naming Convention Builder", layout="wide")
st.title("🧱 Configurador de Naming Convention para UTM")

st.markdown("""
Organiza tus parámetros UTM como bloques y define valores personalizados por cada componente.
Luego podrás exportar la configuración como CSV para reutilizarla.
""")

# ------------ Utilidades ------------
def init_section_state(key, default_list):
    if key not in st.session_state:
        st.session_state[key] = default_list.copy()
    if f"values_{key}" not in st.session_state:
        st.session_state[f"values_{key}"] = [""] * len(default_list)

def reset_section(key, default_list):
    st.session_state[key] = default_list.copy()
    st.session_state[f"values_{key}"] = [""] * len(default_list)

def drag_section(title, key, default_list):
    init_section_state(key, default_list)

    st.subheader(f"{title}")
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

    st.caption("Valores para cada bloque:")
    updated_values = []
    for idx, item in enumerate(st.session_state[key]):
        value_list = st.text_input(
            f"Valores para {item} (separados por comas)",
            value=st.session_state[f"values_{key}"][idx] if idx < len(st.session_state[f"values_{key}"]) else "",
            key=f"{key}_val_{idx}"
        )
        updated_values.append(value_list)
    st.session_state[f"values_{key}"] = updated_values

# ------------ Secciones ------------

# utm_campaign
drag_section("✳️ utm_campaign", "campaign_order", [
    "producto", "audiencia", "fecha", "region", "pais",
    "plataforma", "funnel", "objetivo", "tipoAudiencia"
])

# utm_source con ayuda
st.subheader("📡 utm_source")
ga4_sources = ["google","facebook","instagram","newsletter","linkedin"]
sel_src = st.multiselect("Valores GA4 recomendados", ga4_sources, default=["google"])
extra_src = st.text_input("Otros valores (coma separada)", key="source_extra")
source_blocks = sel_src + [s.strip() for s in extra_src.split(",") if s.strip()]
if not source_blocks:
    source_blocks = ["google"]
drag_section("Ordenar utm_source", "source_order", source_blocks)

# utm_medium con ayuda
st.subheader("🎯 utm_medium")
ga4_mediums = ["organic", "cpc", "email", "referral", "social"]
sel_med = st.multiselect("Valores GA4 recomendados", ga4_mediums, default=["cpc"])
extra_med = st.text_input("Otros valores (coma separada)", key="medium_extra")
medium_blocks = sel_med + [s.strip() for s in extra_med.split(",") if s.strip()]
if not medium_blocks:
    medium_blocks = ["cpc"]
drag_section("Ordenar utm_medium", "medium_order", medium_blocks)

# utm_content
drag_section("🧩 utm_content", "content_order", ["color", "version", "posicion"])

# utm_term
drag_section("🔍 utm_term", "term_order", ["keyword", "matchtype"])

# ----------- Exportar CSV -----------
st.markdown("---")
st.subheader("📁 Exportar configuración")

def export_column(key):
    values = st.session_state.get(f"values_{key}", [])
    return [f"{item} ({val})" if val else item for item, val in zip(st.session_state[key], values)]

if st.button("📤 Generar CSV"):
    config = {
        "utm_campaign": ", ".join(export_column("campaign_order")),
        "utm_source": ", ".join(export_column("source_order")),
        "utm_medium": ", ".join(export_column("medium_order")),
        "utm_content": ", ".join(export_column("content_order")),
        "utm_term": ", ".join(export_column("term_order")),
    }

    df = pd.DataFrame([config])
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar configuración CSV", data=csv, file_name="utm_naming_config.csv", mime="text/csv")
