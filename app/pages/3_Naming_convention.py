import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd

st.set_page_config(page_title="Naming Convention Builder", layout="wide")
st.title("Naming Convention Builder")

st.markdown("""
Este módulo te permite crear tu propio nombrado para que puedas personalizar tus parámetros UTM utilizando bloques *drag & drop* y luego exportarlo en csv para que lo utilices para su uso posterior.

👉Reordena los elementos en cada sección para definir la estructura que prefieras.  
👉 Puedes añadir elementos personalizados de acuerdo a tu negocio.  
👉 Al final puedes exportar la configuración como archivo `.csv`.

**ℹ️ Tipos de parámetros UTM:**
- `utm_campaign`: definimos el nombre de campaña. A más información demos mejor.
- `utm_source`: fuente del tráfico (GA4: google, facebook...)
- `utm_medium`: canal (GA4: cpc, email, organic...)
- `utm_content`: versión del contenido, test A/B, posición...
- `utm_term`: palabra clave o tipo de coincidencia, aunque puedes usarlo para cualquier otro propósito
""")

# --------- Utilidades ---------
def reset_section(key, default_list):
    st.session_state[key] = default_list.copy()

def drag_section(title, key, default_list):
    if key not in st.session_state:
        st.session_state[key] = default_list.copy()

    st.subheader(title)
    cols = st.columns([8, 1])
    with cols[0]:
        ordered = sort_items(
            items=st.session_state[key],
            direction="horizontal",
            key=f"sortable_{key}"
        )
        st.session_state[key] = ordered
    with cols[1]:
        if st.button("🔄 Reset", key=f"reset_{key}"):
            reset_section(key, default_list)

# --------- Secciones ---------

# utm_campaign
drag_section("✳️ utm_campaign", "campaign_order", ["producto", "audiencia", "fecha", "region"])

# utm_source
st.subheader("📡 utm_source")
st.caption("Selecciona valores sugeridos por GA4 en la configuracion de canales por defecto o añade los tuyos.")
ga4_sources = ["google", "facebook", "instagram", "newsletter", "linkedin"]
selected_sources = st.multiselect("Valores GA4", ga4_sources, default=["google"])
extra_sources = st.text_input("Otros valores personalizados (usa comas para por separar)", key="custom_source")
source_list = selected_sources + [s.strip() for s in extra_sources.split(",") if s.strip()]
if not source_list:
    source_list = ["google"]
drag_section("Ordenar utm_source", "source_order", source_list)

# utm_medium
st.subheader("🎯 utm_medium")
st.caption("Selecciona canales recomendados por GA4 o añade los tuyos.")
ga4_mediums = ["organic", "cpc", "email", "referral", "social"]
selected_mediums = st.multiselect("Valores GA4", ga4_mediums, default=["cpc"])
extra_mediums = st.text_input("Otros valores personalizados (coma separada)", key="custom_medium")
medium_list = selected_mediums + [s.strip() for s in extra_mediums.split(",") if s.strip()]
if not medium_list:
    medium_list = ["cpc"]
drag_section("Ordenar utm_medium", "medium_order", medium_list)

# utm_content
drag_section("🧩 utm_content", "content_order", ["color", "version", "posicion"])

# utm_term
drag_section("🔍 utm_term", "term_order", ["keyword", "matchtype"])

# --------- Exportar configuración ---------
st.markdown("---")
st.subheader("📁 Exportar configuración como CSV")

if st.button("📥 Generar CSV"):
    config = {
        "utm_campaign": " > ".join(st.session_state.get("campaign_order", [])),
        "utm_source": " > ".join(st.session_state.get("source_order", [])),
        "utm_medium": " > ".join(st.session_state.get("medium_order", [])),
        "utm_content": " > ".join(st.session_state.get("content_order", [])),
        "utm_term": " > ".join(st.session_state.get("term_order", [])),
    }
    df = pd.DataFrame([config])
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Descargar configuración CSV",
        data=csv,
        file_name="naming_config.csv",
        mime="text/csv"
    )
