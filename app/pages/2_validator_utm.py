import streamlit as st
import pandas as pd
import os
from urllib.parse import urlparse, parse_qs

# ---------- Configuración de la página ----------
st.set_page_config(page_title="Validador de URLs UTM", layout="centered")
st.title("📂 Validador de URLs con UTM")

st.markdown(
    "Este módulo permite verificar si tus URLs tienen los parámetros UTM requeridos y están bien formateadas. "
    "Puedes validar una URL manualmente o subir un archivo CSV/Excel con muchas URLs para analizarlas."
)

# ---------- Función de validación reutilizable ----------
def validate_url(url: str) -> list:
    """Devuelve una lista de errores. Lista vacía = URL válida."""
    errors = []
    url = str(url).strip()

    parsed = urlparse(url)
    query = parse_qs(parsed.query)

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

# ---------- 1. Validación individual ----------
st.subheader("✍️ Validar una URL individual")

single_url = st.text_input("Pega una URL aquí")

if single_url:
    errors = validate_url(single_url)
    if errors:
        for e in errors:
            st.error(f"❌ {e}")
    else:
        st.success("✅ URL válida. Todos los parámetros UTM están presentes.")
        st.code(single_url)

# ---------- 2. Archivo de ejemplo ----------
st.markdown("### 📄 ¿No tienes un archivo? Descarga uno de ejemplo para probar:")

# Busca el CSV tanto si se ejecuta desde /app como desde la raíz
csv_paths = [
    "app/data/utm_urls_ejemplo.csv",
    "data/utm_urls_ejemplo.csv",
]
csv_found = next((p for p in csv_paths if os.path.exists(p)), None)

if csv_found:
    with open(csv_found, "rb") as file:
        st.download_button("📥 Descargar CSV de ejemplo", file, file_name="utm_urls_ejemplo.csv", mime="text/csv")
else:
    st.warning("⚠️ Archivo de ejemplo no encontrado.")

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
            for _, row in df.iterrows():
                url = row["url"]
                errors = validate_url(str(url))
                results.append({
                    "url": url,
                    "estado": "✅ Correcta" if not errors else "❌ Error",
                    "detalles": "; ".join(errors) if errors else "OK"
                })

            result_df = pd.DataFrame(results)

            total = len(result_df)
            ok = (result_df["estado"] == "✅ Correcta").sum()
            ko = total - ok

            col1, col2, col3 = st.columns(3)
            col1.metric("Total URLs", total)
            col2.metric("✅ Correctas", ok)
            col3.metric("❌ Con errores", ko)

            st.markdown("### Resultado de la validación")
            st.dataframe(result_df, use_container_width=True)

            csv_out = result_df.to_csv(index=False).encode()
            st.download_button(
                label="📥 Descargar reporte",
                data=csv_out,
                file_name="reporte_validado.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {str(e)}")
