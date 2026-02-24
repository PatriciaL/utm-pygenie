# UTM Genie - Generador de URLs con UTM (Individual + Masivo)

import streamlit as st
import re
import itertools
import os
import base64
from io import BytesIO
from urllib.parse import urlencode
from PIL import Image
import pandas as pd

# ---------- 1. Configuración de la página ----------
st.set_page_config(
    page_title="UTM Genie - Generador de URLs",
    page_icon="🧙",
    layout="centered"
)

# ---------- 2. Cargar favicon ----------
favicon_path = "components/utm_genie_favicon_64x64.png"
if os.path.exists(favicon_path):
    with open(favicon_path, "rb") as f:
        favicon_base64 = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <head>
            <link rel="icon" type="image/png" href="data:image/png;base64,{favicon_base64}">
        </head>
        """,
        unsafe_allow_html=True
    )

# ---------- 3. Cabecera con logo ----------
logo_path = "components/utm_genie_logo_genie_version.png"
col1, col2 = st.columns([1, 4])
with col1:
    if os.path.exists(logo_path):
        logo = Image.open(logo_path)
        st.image(logo, width=100)
    else:
        st.markdown("🧙")
with col2:
    st.markdown("## 🔧 Generador de URLs con UTM")

# ---------- 4. Toggle de modo ----------
modo = st.radio(
    "Modo",
    ["🔗 Individual", "⚡ Masivo"],
    horizontal=True,
    label_visibility="collapsed"
)
st.markdown("---")

# ============================================================
# FUNCIONES COMPARTIDAS
# ============================================================

def is_valid_utm(value):
    return bool(re.match(r"^[a-zA-Z0-9_\-]+$", value))

def parse_values(raw: str) -> list:
    if not raw or not raw.strip():
        return []
    return [v.strip() for v in raw.split(",") if v.strip()]


# ============================================================
# MODO INDIVIDUAL
# ============================================================

if modo == "🔗 Individual":

    def validated_input(label, key, help_text="", example_text=""):
        value = st.text_input(label, key=key, help=help_text)
        if value:
            if not is_valid_utm(value):
                st.warning("⚠️ Solo se permiten letras, números, guiones y guiones bajos.")
        if example_text:
            st.caption(f"💡 Ejemplo: `{example_text}`")
        return value.strip() if value else ""

    with st.expander("⚙️ Personalizar ejemplos"):
        examples = {
            "utm_source":   st.text_input("Ejemplo para utm_source",   "newsletter, facebook"),
            "utm_medium":   st.text_input("Ejemplo para utm_medium",   "email, cpc"),
            "utm_campaign": st.text_input("Ejemplo para utm_campaign", "lanzamiento2025"),
            "utm_term":     st.text_input("Ejemplo para utm_term",     "zapatos+rojos"),
            "utm_content":  st.text_input("Ejemplo para utm_content",  "banner_azul"),
        }

    base_url     = st.text_input("URL base", "https://tusitio.com")
    utm_source   = validated_input("utm_source *",   "utm_source",   help_text="Fuente del tráfico (obligatorio)",  example_text=examples["utm_source"])
    utm_medium   = validated_input("utm_medium *",   "utm_medium",   help_text="Canal o medio (obligatorio)",       example_text=examples["utm_medium"])
    utm_campaign = validated_input("utm_campaign *", "utm_campaign", help_text="Campaña específica (obligatorio)",  example_text=examples["utm_campaign"])
    utm_term     = validated_input("utm_term",       "utm_term",     help_text="Palabra clave (opcional)",          example_text=examples["utm_term"])
    utm_content  = validated_input("utm_content",    "utm_content",  help_text="Contenido del anuncio (opcional)",  example_text=examples["utm_content"])

    params = {k: v for k, v in {
        "utm_source":   utm_source,
        "utm_medium":   utm_medium,
        "utm_campaign": utm_campaign,
        "utm_term":     utm_term,
        "utm_content":  utm_content,
    }.items() if v}

    if st.button("Generar URL", type="primary"):
        missing = [k for k in ["utm_source", "utm_medium", "utm_campaign"] if not params.get(k)]
        invalid = [k for k, v in params.items() if not is_valid_utm(v)]

        if missing:
            st.error(f"❌ Faltan campos obligatorios: {', '.join(missing)}")
        elif invalid:
            st.error(f"❌ Caracteres no válidos en: {', '.join(invalid)}")
        else:
            final_url = f"{base_url}?{urlencode(params)}"
            st.session_state["final_url"] = final_url
            st.balloons()

    if "final_url" in st.session_state:
        final_url = st.session_state["final_url"]
        st.success("✅ URL generada:")
        st.code(final_url)
        st.link_button("🌐 Abrir URL", final_url)
        st.download_button(
            label="📥 Descargar como CSV",
            data=f"url\n{final_url}",
            file_name="utm_url.csv",
            mime="text/csv"
        )


# ============================================================
# MODO MASIVO
# ============================================================

else:
    st.markdown("Define valores múltiples para cada parámetro separados por comas. Se generarán **todas las combinaciones posibles**.")
    st.info("💡 Ejemplo: `google, facebook, instagram` en utm_source generará una URL por cada fuente.")

    base_url = st.text_input("🌐 URL base", "https://tusitio.com")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Obligatorios")
        sources_raw   = st.text_input("utm_source *",   placeholder="google, facebook, instagram")
        mediums_raw   = st.text_input("utm_medium *",   placeholder="cpc, email, social")
        campaigns_raw = st.text_input("utm_campaign *", placeholder="lanzamiento2025, black_friday")
    with col2:
        st.markdown("#### Opcionales")
        contents_raw = st.text_input("utm_content", placeholder="banner_azul, banner_rojo, texto")
        terms_raw    = st.text_input("utm_term",    placeholder="zapatos, zapatos+rojos")

    sources   = parse_values(sources_raw)
    mediums   = parse_values(mediums_raw)
    campaigns = parse_values(campaigns_raw)
    contents  = parse_values(contents_raw) or [""]
    terms     = parse_values(terms_raw)    or [""]

    # Preview en tiempo real
    if sources or mediums or campaigns:
        total = len(sources or [""]) * len(mediums or [""]) * len(campaigns or [""]) * len(contents) * len(terms)
        m1, m2, m3 = st.columns(3)
        m1.metric("Fuentes",  len(sources)   if sources   else 0)
        m2.metric("Medios",   len(mediums)   if mediums   else 0)
        m3.metric("Campañas", len(campaigns) if campaigns else 0)

        if sources and mediums and campaigns:
            st.success(f"✅ Se generarán **{total} URLs** con todas las combinaciones.")
        else:
            st.warning("⚠️ Completa utm_source, utm_medium y utm_campaign como mínimo.")

    st.markdown("---")

    if st.button("⚡ Generar todas las URLs", type="primary", use_container_width=True):
        if not sources or not mediums or not campaigns:
            st.error("❌ Debes rellenar utm_source, utm_medium y utm_campaign como mínimo.")
        else:
            rows = []
            for source, medium, campaign, content, term in itertools.product(sources, mediums, campaigns, contents, terms):
                params = {"utm_source": source, "utm_medium": medium, "utm_campaign": campaign}
                if content: params["utm_content"] = content
                if term:    params["utm_term"]    = term
                rows.append({
                    "utm_source":   source,
                    "utm_medium":   medium,
                    "utm_campaign": campaign,
                    "utm_content":  content or "",
                    "utm_term":     term    or "",
                    "url_final":    f"{base_url}?{urlencode(params)}",
                })
            st.session_state["bulk_urls"] = pd.DataFrame(rows)
            st.success(f"🎉 {len(rows)} URLs generadas correctamente.")

    if "bulk_urls" in st.session_state:
        df = st.session_state["bulk_urls"]
        st.markdown(f"### 📋 {len(df)} URLs generadas")

        filtered_df = df.copy()
        with st.expander("🔍 Filtrar resultados"):
            f_source = st.multiselect("Filtrar por utm_source", options=df["utm_source"].unique())
            f_medium = st.multiselect("Filtrar por utm_medium", options=df["utm_medium"].unique())
            if f_source: filtered_df = filtered_df[filtered_df["utm_source"].isin(f_source)]
            if f_medium: filtered_df = filtered_df[filtered_df["utm_medium"].isin(f_medium)]

        st.dataframe(
            filtered_df,
            use_container_width=True,
            column_config={"url_final": st.column_config.LinkColumn("URL Final")}
        )

        col_csv, col_xlsx = st.columns(2)
        with col_csv:
            st.download_button(
                "📥 Descargar CSV",
                data=filtered_df.to_csv(index=False).encode("utf-8"),
                file_name="utm_urls_masivas.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_xlsx:
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                filtered_df.to_excel(writer, index=False, sheet_name="URLs_UTM")
            buffer.seek(0)
            st.download_button(
                "📥 Descargar Excel",
                data=buffer,
                file_name="utm_urls_masivas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
