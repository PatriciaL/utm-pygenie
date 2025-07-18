import streamlit as st
import pandas as pd
from urllib.parse import urlparse, parse_qs

# ---------- Configuración de la página ----------
st.set_page_config(page_title="Validador de URLs UTM", layout="centered")
st.title("📂 Validador de URLs con UTM")

st.markdown("Este módulo permite verificar si tus URLs tienen los parámetros UTM requeridos y están bien formateadas. "
            "Puedes validar una URL manualmente o subir un archivo CSV/Excel con muchas URLs para analizarlas.")

# ---------- 1. Validación individual ----------
st.subheader("✍️ Validar una URL individual")

single_url = st.text_input("Pega una URL aquí")

if single_url:
    parsed = urlparse(single_url)
    query = parse_qs(parsed.query)
    missing = [p for p in ["utm_source", "utm_medium", "utm_campaign"] if p not in query]

    if missing:
        st.error(f"❌ Faltan parámetros obligatorios: {', '.join(missing)}")
    elif " " in single_url:
        st.warning("⚠️ La URL contiene espacios. Intenta codificarlos o usar guiones bajos.")
    else:
        st.success("✅ URL válida. Todos los parámetros UTM están presentes.")
        st.code(single_url)

# ---------- 2. Archivo de ejemplo ----------
st.markdown("### 📄 ¿No tienes un archivo? Descarga uno de ejemplo para probar:")

try:
    with open("app/data/utm_urls_ejemplo.csv", "rb") as file:
        st.download_button("📥 Descargar CSV de ejemplo", file, file_name="utm_urls_ejemplo.csv", mime="text/csv")
except FileNotFoundError:
    st.warning("⚠️ Archivo de ejemplo no encontrado en 'app/data/'. Asegúrate de que el archivo existe.")

# ---------- 3. Validación por archivo ----------
st.subheader("📤 Validar URLs desde archivo (CSV o Excel)")

uploaded_file = st.file_uploader("Sube un archivo con una columna llamada 'url'", type=["csv", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        if "url" not in df.columns:
            st.error("❌ El archivo debe contener una columna llamada 'url'.")
        else:
            results = []
            for i, row in df.iterrows():
                url = row["url"]
                parsed = urlparse(str(url))
                query = parse_qs(parsed.query)
                errors = []

                # Validaciones
                if not parsed.scheme.startswith("http"):
                    errors.append("URL inválida o sin http(s)")

                for param in ["utm_source", "utm_medium", "utm_campaign"]:
                    if param not in query:
                        errors.append(f"Falta {param}")

                if " " in str(url):
                    errors.append("Contiene espacios")

                results.append({
                    "url": url,
                    "estado": "✅ Correcta" if not errors else "❌ Error",
                    "detalles": "; ".join(errors) if errors else "OK"
                })

            result_df = pd.DataFrame(results)
            st.markdown("### ✅ Resultado de la validación")
            st.dataframe(result_df, use_container_width=True)

            # Botón para descargar archivo corregido
            csv_out = result_df.to_csv(index=False).encode()
            st.download_button(
                label="📥 Descargar reporte corregido",
                data=csv_out,
                file_name="reporte_validado.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {str(e)}")
