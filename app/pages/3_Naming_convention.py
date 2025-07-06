import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd

st.set_page_config(page_title="Naming Convention Builder", layout="wide")
st.title("🧱 Configurador de Naming Convention para UTM")

st.markdown("""
Este módulo te permite construir tus convenciones de naming personalizadas para cada uno de los parámetros UTM.

1. 🔀 Ordena los bloques con **drag & drop** por parámetro.
2. 🔄 Usa los botones de **reset** para volver a la configuración inicial.
3. 📥 Exporta tu configuración como CSV para compartirla o documentarla.
4. 📚 Se incluyen sugerencias comunes (GA4) para `utm_source` y `utm_medium`.

---""")

# ---------- Utilidades ----------
def reset_section(key, default_list):
    st.session_state[key] = default_list.copy()

def drag_section(title, key, default_list):
    if key not in st.session_state:
        st.session_state[key] = default_list.copy()

    st.subheader(title)
    cols = st.columns([8, 1])
    with cols[0]:
        result = sort_items(
            st.session_state[key],
            direction="horizontal",
            key=key
        )
        if result and isinstance(result, list) and "items" in result[0]:
            st.session_state[key] = result[0]["items"]
    with cols[1]:
        if st.button("🔄 Reset", key=f"reset_{key}"):
            reset_section(key, default_list)

# ---------- Secciones ----------

# utm_campaign
drag_section("✳️ utm_campaign", "campaign_order", ["producto", "audiencia", "fecha", "region"])

# utm_source
st.subheader("📡 utm_source")
st.caption("Fuente que origina el tráfico. Ejemplo: google, newsletter, facebook.")
ga4_sources = ["google", "facebook", "instagram", "newsletter", "linkedin"]
selected_sources = st.multiselect("Valores comunes (GA4)", ga4_sources, default=["google"])
extra_sources = st.text_input("Otros valores personalizados (separados por coma)")
custom_source_blocks = selected_sources + [s.strip() for s in extra_sources.split(",") if s.strip()]
drag_section("🔀 Ordenar bloques de utm_source", "source_order", custom_source_blocks)

# utm_medium
st.subheader("🎯 utm_medium")
st.caption("Tipo de canal. Ejemplo: cpc, email, social, referral.")
ga4_mediums = ["organic", "cpc", "email", "referral", "social"]
selected_mediums = st.multiselect("Valores comunes (GA4)", ga4_mediums, default=["cpc"])
extra_mediums = st.text_input("Otros valores personalizados (separados por coma)", key="medium_input")
custom_medium_blocks = selected_mediums + [s.strip() for s in extra_mediums.split(",") if s.strip()]
drag_section("🔀 Ordenar bloques de utm_medium", "medium_order", custom_medium_blocks)

# utm_content
drag_section("🧩 utm_content", "content_order", ["color", "version", "posicion"])

# utm_term
drag_section("🔍 utm_term", "term_order", ["keyword", "matchtype"])

# ---------- Exportar CSV ----------
st.markdown("---")
st.subheader("📁 Generar archivo con configuración personalizada")

if st.button("📥 Generar CSV"):
    data = {
        "utm_campaign": " > ".join(st.session_state.get("campaign_order", [])),
        "utm_source": " > ".join(st.session_state.get("source_order", [])),
        "utm_medium": " > ".join(st.session_state.get("medium_order", [])),
        "utm_content": " > ".join(st.session_state.get("content_order", [])),
        "utm_term": " > ".join(st.session_state.get("term_order", [])),
    }
    df = pd.DataFrame([data])
    st.dataframe(df)
    csv = df.to_csv(index=False).encode()
    st.download_button("⬇️ Descargar configuración CSV", data=csv, file_name="naming_config.csv", mime="text/csv")
