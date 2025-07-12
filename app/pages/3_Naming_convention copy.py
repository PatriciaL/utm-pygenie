import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Naming Convention Builder", layout="wide")
st.title("🧱 Configurador de Naming Convention para UTM")

st.markdown("""
Este módulo te permite construir una convención de nombres para tus parámetros UTM usando bloques drag & drop.

- 🔀 Reordena los elementos por parámetro UTM
- ➕ Agrega valores por bloque
- ⬇️ Exporta la configuración como archivo Excel
""")

# ---------- Utilidades ----------

def reset_section(key, default_list):
    st.session_state[key] = default_list.copy()
    for blk in default_list:
        st.session_state[f"list_{key}"][blk] = []

def drag_section(title, key, default_list):
    if key not in st.session_state:
        st.session_state[key] = default_list.copy()
    if f"list_{key}" not in st.session_state:
        st.session_state[f"list_{key}"] = {k: [] for k in default_list}

    st.subheader(title)
    cols = st.columns([8, 1])
    with cols[0]:
        ordered = sort_items(
            items=st.session_state[key],
            direction="horizontal",
            key=f"sortable_{key}"
        )
        if ordered and isinstance(ordered, list):
            st.session_state[key] = ordered
    with cols[1]:
        if st.button("🔄 Reset", key=f"reset_{key}"):
            reset_section(key, default_list)

    # Entrada de valores para cada bloque
    for item in st.session_state[key]:
        st.markdown(f"##### 🔹 Valores en `{item}`")
        current_vals = st.session_state[f"list_{key}"].get(item, [])
        st.write(current_vals or "*Sin valores aún*")
        new_val = st.text_input(f"Nuevo valor para {item}", key=f"{key}_{item}")
        if st.button(f"Añadir a {item}", key=f"btn_{key}_{item}"):
            nuevos = [v.strip() for v in new_val.split(",") if v.strip()]
            st.session_state[f"list_{key}"][item].extend(nuevos)
            st.experimental_rerun()

# ---------- Secciones drag & drop ----------

drag_section("✳️ utm_campaign", "campaign_order",
             ["tipoAudiencia", "pais", "plataforma", "producto", "funnel", "objetivo", "fecha", "audiencia", "region"])

# utm_source con ayuda GA4
st.subheader("📡 utm_source")
ga4_sources = ["google","Google Ads","facebook","pinterest","youtube","vimeo","whatsapp","instagram-stories",
               "x", "instagram", "newsletter","email", "linkedin","tiktok","podimo","google-pmax","google-red",
               "google-int-shop","seedtag","twitch","indigitall","snapchat","bing","yahoo","bing-ads"]
selected_sources = st.multiselect("Valores GA4", ga4_sources, default=["google"])
extra_sources = st.text_input("Otros valores personalizados (usa comas para separar)", key="custom_source")
source_list = selected_sources + [s.strip() for s in extra_sources.split(",") if s.strip()]
if not source_list:
    source_list = ["google"]
drag_section("Ordenar utm_source", "source_order", source_list)

# utm_medium con ayuda GA4
st.subheader("🎯 utm_medium")
ga4_mediums = ["organic", "cpc", "email", "referral", "social","audio","display","banner","interstitial","cpm",
               "expandible","push","qr","video-organic","paid","retargeting","sms","influencer"]
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

# ---------- Exportar configuración ----------
st.markdown("---")
st.subheader("📁 Exportar a Excel")

if st.button("📥 Generar Excel"):
    # Hoja 1: estructura
    estructura = {
        "utm_campaign": "_".join(st.session_state.get("campaign_order", [])),
        "utm_source": "_".join(st.session_state.get("source_order", [])),
        "utm_medium": "_".join(st.session_state.get("medium_order", [])),
        "utm_content": "_".join(st.session_state.get("content_order", [])),
        "utm_term": "_".join(st.session_state.get("term_order", [])),
    }
    df_estructura = pd.DataFrame([estructura])

    # Hoja 2: listas de valores
    lista_cols = {}
    for sec in ["campaign_order", "source_order", "medium_order", "content_order", "term_order"]:
        col_vals = []
        for blk in st.session_state[sec]:
            valores = st.session_state[f"list_{sec}"].get(blk, []) or [""]
            col_vals.extend([blk] + valores + [""])  # nombre + valores + espacio
        lista_cols[sec.replace("_order", "")] = col_vals

    # Igualar longitudes
    max_len = max(len(v) for v in lista_cols.values())
    for k in lista_cols:
        lista_cols[k] += [""] * (max_len - len(lista_cols[k]))

    df_listas = pd.DataFrame(lista_cols)

    # Guardar en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_estructura.to_excel(writer, index=False, sheet_name="estructura")
        df_listas.to_excel(writer, index=False, sheet_name="valores")

    st.download_button(
        label="⬇️ Descargar Excel",
        data=output.getvalue(),
        file_name="naming_config.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
