import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from style import apply_style

import streamlit as st
import pandas as pd
from urllib.parse import urlparse, parse_qs

st.set_page_config(page_title="UTM Genie — Validador", page_icon="🧙", layout="centered")
apply_style()

st.markdown("# Validador de URLs")
st.markdown('<p style="color:#71717A;font-size:0.8rem;margin-top:-8px">Verifica que tus URLs tienen los parámetros UTM correctos</p>', unsafe_allow_html=True)

def validate_url(url: str) -> list:
    errors = []
    url = str(url).strip()
    parsed = urlparse(url)
    query  = parse_qs(parsed.query)
    if not parsed.scheme.startswith("http"):
        errors.append("URL inválida o sin http(s)")
    for param in ["utm_source", "utm_medium", "utm_campaign"]:
        if param not in query:
            errors.append(f"Falta {param}")
        elif not query[param][0].strip():
            errors.append(f"{param} está vacío")
    if " " in url:
        errors.append("Contiene espacios")
    return errors

# ── Validación individual ─────────────────────────────────────────
st.markdown("## Validación individual")
single_url = st.text_input("Pega una URL aquí", placeholder="https://tusitio.com?utm_source=...")

if single_url:
    errors = validate_url(single_url)
    if errors:
        for e in errors:
            st.error(e)
    else:
        st.success("URL válida. Todos los parámetros UTM están presentes.")
        st.code(single_url)

st.markdown("---")

# ── Archivo de ejemplo ────────────────────────────────────────────
st.markdown("## Archivo de ejemplo")
csv_paths = ["app/data/utm_urls_ejemplo.csv", "data/utm_urls_ejemplo.csv"]
csv_found = next((p for p in csv_paths if os.path.exists(p)), None)
if csv_found:
    with open(csv_found, "rb") as f:
        st.download_button("Descargar CSV de ejemplo", f, file_name="utm_urls_ejemplo.csv", mime="text/csv")
else:
    st.warning("Archivo de ejemplo no encontrado.")

st.markdown("---")

# ── Validación por archivo ────────────────────────────────────────
st.markdown("## Validación por archivo")
st.caption("El archivo debe tener una columna llamada 'url'")

uploaded_file = st.file_uploader("Sube un CSV o Excel", type=["csv", "xlsx"], label_visibility="collapsed")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        if "url" not in df.columns:
            st.error("El archivo debe contener una columna llamada 'url'.")
        else:
            results = []
            for _, row in df.iterrows():
                url    = row["url"]
                errors = validate_url(str(url))
                results.append({
                    "url":      url,
                    "estado":   "Correcta" if not errors else "Error",
                    "detalles": "; ".join(errors) if errors else "OK"
                })

            result_df = pd.DataFrame(results)
            total = len(result_df)
            ok    = (result_df["estado"] == "Correcta").sum()
            ko    = total - ok

            c1, c2, c3 = st.columns(3)
            c1.metric("Total", total)
            c2.metric("Correctas", ok)
            c3.metric("Con errores", ko)

            st.dataframe(result_df, use_container_width=True)

            st.download_button("Descargar reporte",
                               data=result_df.to_csv(index=False).encode(),
                               file_name="reporte_validado.csv",
                               mime="text/csv")
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
