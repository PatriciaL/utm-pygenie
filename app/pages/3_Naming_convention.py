import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd

st.set_page_config(page_title="Naming Convention Builder", layout="wide")
st.title("Configurador de Naming Convention para UTM")

st.markdown("""
Este módulo te permite crear una convención personalizada para tus parámetros UTM utilizando bloques drag & drop.
Puedes ordenar los componentes, elegir valores sugeridos por GA4 y generar un archivo CSV con tu estructura.
""")

# ---------- Utilidades ----------
def reset_section(key, default_list):
    st.session_state[key] = default_list.copy()

def drag_section(title, key, default_list):
    if key not in st.session_state:
        st.session_state[key] = default_list

    st.subheader(title)
    cols = st.columns([8, 1])
    with cols[0]:
        new_order = sort_items(
            st.session_state[key],
            direction="horizontal",
            key=key
        )
        st.session_state[key] = new_order
    with cols[1]:
        if st.button("🔄 Reset", key=f"reset_{key}"):
            reset_section(key, default_list)

# ---------- Secciones ----------

drag_section("✳️ utm_campaign", "campaign_order", ["producto", "audiencia", "fecha", "region"])

# utm_source con ayuda GA4
st.subheader("📡 utm_source")
ga4_sources = ["google", "facebook", "instagram", "newsletter", "linkedin"]
selected_sources = st.multiselect("Valores comunes (GA4)", ga4_sources, default=["google"])
extra_sources = st.text_input("Otros valores personalizados (separados por coma)")
custom_source_blocks = selected_sources + [s.strip() for s in extra_sources.split(",") if s.strip()]
drag_section("Ordenar bloques de utm_source", "source_order", custom_source_blocks)

# utm_medium con ayuda GA4
st.subheader("🎯 utm_medium")
ga4_mediums = ["organic", "cpc", "email", "referral", "social"]
selected_mediums = st.multiselect("Valores comunes (GA4)", ga4_mediums, default=["cpc"])
extra_mediums = st.text_input("Otros valores personalizados (separados por coma)", key="medium_input")
custom_medium_blocks = selected_mediums + [s.strip() for s in extra_mediums.split(",") if s.strip()]
if "medium_order" not in st.session_state or st.session_state["medium_order"] != custom_medium_blocks:
    st.session_state["medium_order"] = custom_medium_blocks
drag_section("Ordenar bloques de utm_medium", "medium_order", st.session_state["medium_order"])

drag_section("🧩 utm_content", "content_order", ["color", "version", "posicion"])
drag_section("🔍 utm_term", "term_order", ["keyword", "matchtype"])

# ---------- Generar CSV ----------
st.markdown("---")
st.subheader("📁 Generar archivo con configuración personalizada")

if st.button("📥 Generar CSV"):
    data = {
        "utm_campaign": " > ".join(st.session_state["campaign_order"]),
        "utm_source": " > ".join(st.session_state["source_order"]),
        "utm_medium": " > ".join(st.session_state["medium_order"]),
        "utm_content": " > ".join(st.session_state["content_order"]),
        "utm_term": " > ".join(st.session_state["term_order"]),
    }
    df = pd.DataFrame([data])
    st.dataframe(df)
    csv = df.to_csv(index=False).encode()
    st.download_button("⬇️ Descargar configuración CSV", data=csv, file_name="naming_config.csv", mime="text/csv")
