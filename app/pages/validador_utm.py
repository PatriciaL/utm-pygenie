import streamlit as st
import pandas as pd
from urllib.parse import urlparse, parse_qs

st.title("📂 Validador de URLs UTM (CSV)")

uploaded_file = st.file_uploader("Sube un archivo CSV con una columna de URLs", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    if "url" not in df.columns:
        st.error("⚠️ El archivo debe contener una columna llamada 'url'.")
    else:
        # Validación básica
        results = []
        for url in df["url"]:
            parsed = urlparse(url)
            query = parse_qs(parsed.query)
            missing = [p for p in ["utm_source", "utm_medium", "utm_campaign"] if p not in query]
            if missing:
                results.append({"url": url, "error": f"Faltan: {', '.join(missing)}"})
            else:
                results.append({"url": url, "error": ""})

        result_df = pd.DataFrame(results)
        st.dataframe(result_df)

        invalid = result_df[result_df["error"] != ""]
        if not invalid.empty:
            st.warning(f"🔍 {len(invalid)} URLs tienen errores.")
        else:
            st.success("✅ Todas las URLs tienen los parámetros obligatorios.")
