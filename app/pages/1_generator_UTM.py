import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from style import apply_style

import streamlit as st
import re, itertools
from io import BytesIO
from urllib.parse import urlencode
import pandas as pd

st.set_page_config(page_title="UTM Genie — Generador", page_icon="🧙", layout="centered", initial_sidebar_state="expanded")
apply_style()

st.markdown("""
<div style="margin-bottom:28px;padding-bottom:20px;border-bottom:1.5px solid #E4E4E7">
  <div style="font-family:'Sora',sans-serif;font-size:0.6rem;font-weight:500;
              letter-spacing:0.2em;text-transform:uppercase;color:#71717A;margin-bottom:8px">
    UTM Genie
  </div>
  <div style="font-family:'Sora',sans-serif;font-size:1.8rem;font-weight:600;
              letter-spacing:-0.04em;color:#1A1A1A;line-height:1.1;margin-bottom:10px">
    Generador de URLs
  </div>
  <div style="font-family:'Sora',sans-serif;font-size:0.8rem;color:#71717A;letter-spacing:0.01em">
    Crea URLs con parámetros UTM correctamente formateados
  </div>
</div>
""", unsafe_allow_html=True)

modo = st.radio("", ["Individual", "Masivo"], horizontal=True, label_visibility="collapsed")
st.markdown("---")

def is_valid_utm(v):
    return bool(re.match(r"^[a-zA-Z0-9_\-]+$", v))

def parse_values(raw):
    if not raw or not raw.strip(): return []
    return [v.strip() for v in raw.split(",") if v.strip()]

def get_naming_values(sec_key):
    blocks = st.session_state.get(sec_key, [])
    vals   = st.session_state.get(f"vals_{sec_key}", {})
    all_vals = []
    for blk in blocks:
        all_vals.extend(vals.get(blk, []))
    return ", ".join(list(dict.fromkeys(all_vals)))

def sync_naming_to_inputs():
    mapping = {
        "bulk_source":   get_naming_values("source"),
        "bulk_medium":   get_naming_values("medium"),
        "bulk_campaign": get_naming_values("campaign"),
        "bulk_content":  get_naming_values("content"),
        "bulk_term":     get_naming_values("term"),
    }
    for k, v in mapping.items():
        if v and k not in st.session_state:
            st.session_state[k] = v

# ═══════════════════════════════════════════════════════════════════
# MODO INDIVIDUAL
# ═══════════════════════════════════════════════════════════════════
if modo == "Individual":

    def field(label, key, required=False, hint="", example=""):
        tag = " *" if required else ""
        val = st.text_input(f"{label}{tag}", key=key, help=hint)
        if val and not is_valid_utm(val):
            st.markdown('<p style="color:#E11D48;font-size:0.75rem;margin-top:-8px">Solo letras, números, guiones y guiones bajos.</p>', unsafe_allow_html=True)
        if example:
            st.caption(f"ej. {example}")
        return val.strip() if val else ""

    with st.expander("Personalizar ejemplos"):
        examples = {
            "utm_source":   st.text_input("utm_source",   "newsletter, facebook", key="ex_source"),
            "utm_medium":   st.text_input("utm_medium",   "email, cpc",           key="ex_medium"),
            "utm_campaign": st.text_input("utm_campaign", "lanzamiento2025",       key="ex_campaign"),
            "utm_term":     st.text_input("utm_term",     "zapatos+rojos",         key="ex_term"),
            "utm_content":  st.text_input("utm_content",  "banner_azul",           key="ex_content"),
        }

    base_url     = st.text_input("URL base", "https://tusitio.com")
    utm_source   = field("utm_source",   "utm_source",   required=True,  hint="Fuente del tráfico",       example=examples["utm_source"])
    utm_medium   = field("utm_medium",   "utm_medium",   required=True,  hint="Canal o medio",            example=examples["utm_medium"])
    utm_campaign = field("utm_campaign", "utm_campaign", required=True,  hint="Nombre de la campaña",     example=examples["utm_campaign"])
    utm_term     = field("utm_term",     "utm_term",     required=False, hint="Palabra clave (opcional)", example=examples["utm_term"])
    utm_content  = field("utm_content",  "utm_content",  required=False, hint="Variante del anuncio",     example=examples["utm_content"])

    params = {k: v for k, v in {
        "utm_source": utm_source, "utm_medium": utm_medium, "utm_campaign": utm_campaign,
        "utm_term": utm_term, "utm_content": utm_content,
    }.items() if v}

    if st.button("Generar URL", type="primary"):
        missing = [k for k in ["utm_source","utm_medium","utm_campaign"] if not params.get(k)]
        invalid = [k for k,v in params.items() if not is_valid_utm(v)]
        if missing:
            st.error(f"Faltan campos obligatorios: {', '.join(missing)}")
        elif invalid:
            st.error(f"Caracteres no válidos en: {', '.join(invalid)}")
        else:
            st.session_state["final_url"] = f"{base_url}?{urlencode(params)}"
            st.balloons()

    if "final_url" in st.session_state:
        url = st.session_state["final_url"]
        st.success("URL generada")
        st.code(url)
        c1, c2 = st.columns(2)
        with c1:
            st.link_button("Abrir URL", url)
        with c2:
            st.download_button("Descargar CSV", data=f"url\n{url}", file_name="utm_url.csv", mime="text/csv")

# ═══════════════════════════════════════════════════════════════════
# MODO MASIVO
# ═══════════════════════════════════════════════════════════════════
else:
    sync_naming_to_inputs()

    has_naming = any([
        get_naming_values("source"),
        get_naming_values("medium"),
        get_naming_values("campaign"),
    ])

    if has_naming:
        st.info("Valores cargados desde tu Naming Convention. Puedes editarlos antes de generar.")
    else:
        st.markdown('<p style="color:#71717A;font-size:0.85rem">Separa los valores con comas — se generarán todas las combinaciones posibles.</p>', unsafe_allow_html=True)
        st.page_link("pages/3_final_naming_convention_constructor.py", label="Configura tu Naming Convention primero")

    base_url = st.text_input("URL base", "https://tusitio.com", key="bulk_base_url")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("## Obligatorios")
        sources_raw   = st.text_input("utm_source *",   key="bulk_source",   placeholder="google, facebook, instagram")
        mediums_raw   = st.text_input("utm_medium *",   key="bulk_medium",   placeholder="cpc, email, social")
        campaign_mode = st.radio("utm_campaign *", ["Valor fijo", "Bloques del Naming Convention"], horizontal=True)
        if campaign_mode == "Valor fijo":
            campaigns_raw = st.text_input("Valores de utm_campaign", key="bulk_campaign", placeholder="lanzamiento2025, black_friday")
        else:
            if "campaign" in st.session_state and st.session_state["campaign"]:
                blocks       = st.session_state["campaign"]
                block_values = {blk: st.session_state.get("vals_campaign", {}).get(blk, [blk]) for blk in blocks}
                combos       = ["_".join(c) for c in itertools.product(*[v if v else [b] for b, v in block_values.items()])]
                campaigns_raw = ", ".join(combos)
                st.caption(f"Combinaciones: {campaigns_raw}")
            else:
                campaigns_raw = ""
                st.warning("Aún no has configurado bloques en el Naming Convention.")
    with col2:
        st.markdown("## Opcionales")
        contents_raw = st.text_input("utm_content", key="bulk_content", placeholder="banner_azul, banner_rojo")
        terms_raw    = st.text_input("utm_term",    key="bulk_term",    placeholder="zapatos, zapatos+rojos")

    sources   = parse_values(sources_raw)
    mediums   = parse_values(mediums_raw)
    campaigns = parse_values(campaigns_raw)
    contents  = parse_values(contents_raw) or [""]
    terms     = parse_values(terms_raw)    or [""]

    if sources or mediums or campaigns:
        total = len(sources or [""]) * len(mediums or [""]) * len(campaigns or [""]) * len(contents) * len(terms)
        m1, m2, m3 = st.columns(3)
        m1.metric("Fuentes",  len(sources)   if sources   else 0)
        m2.metric("Medios",   len(mediums)   if mediums   else 0)
        m3.metric("Campañas", len(campaigns) if campaigns else 0)
        if sources and mediums and campaigns:
            st.success(f"{total} URLs listas para generar.")
        else:
            st.warning("Completa utm_source, utm_medium y utm_campaign.")

    st.markdown("---")

    if st.button("Generar todas las URLs", type="primary", use_container_width=True):
        if not sources or not mediums or not campaigns:
            st.error("Completa utm_source, utm_medium y utm_campaign.")
        else:
            rows = []
            for src, med, cam, con, trm in itertools.product(sources, mediums, campaigns, contents, terms):
                p = {"utm_source": src, "utm_medium": med, "utm_campaign": cam}
                if con: p["utm_content"] = con
                if trm: p["utm_term"]    = trm
                rows.append({"utm_source": src, "utm_medium": med, "utm_campaign": cam,
                              "utm_content": con or "", "utm_term": trm or "",
                              "url_final": f"{base_url}?{urlencode(p)}"})
            st.session_state["bulk_urls"] = pd.DataFrame(rows)
            st.success(f"{len(rows)} URLs generadas.")

    if "bulk_urls" in st.session_state:
        df = st.session_state["bulk_urls"]
        st.markdown(f"### {len(df)} URLs generadas")

        filtered_df = df.copy()
        with st.expander("Filtrar resultados"):
            f_source = st.multiselect("utm_source", options=df["utm_source"].unique())
            f_medium = st.multiselect("utm_medium", options=df["utm_medium"].unique())
            if f_source: filtered_df = filtered_df[filtered_df["utm_source"].isin(f_source)]
            if f_medium: filtered_df = filtered_df[filtered_df["utm_medium"].isin(f_medium)]

        st.dataframe(filtered_df, use_container_width=True,
                     column_config={"url_final": st.column_config.LinkColumn("URL Final")})

        c1, c2 = st.columns(2)
        with c1:
            st.download_button("Descargar CSV", data=filtered_df.to_csv(index=False).encode(),
                               file_name="utm_urls_masivas.csv", mime="text/csv", use_container_width=True)
        with c2:
            buf = BytesIO()
            with pd.ExcelWriter(buf, engine="xlsxwriter") as w:
                filtered_df.to_excel(w, index=False, sheet_name="URLs_UTM")
            buf.seek(0)
            st.download_button("Descargar Excel", data=buf, file_name="utm_urls_masivas.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               use_container_width=True)
