improt streamlit as st
import pandas as pd 
import re
from io import StringIO


st.set_page_config(page_title="UTM Validator", page_icon="🔍", layour="centered")
st.title("Validador de URLs con Parametrizadas")
st.markdown ("Valida tu URL o arrastra un archivo CSV para analizar muchas a la vez")

#----------------------
#Funciones de validacion
#----------------------

def is_Valid_utm(param):
     return bool(re.match(r"^[a-zA-Z0-9_-]+$", str(param).strip()))

def validate_url_structure(url):
    required = ["utm_source","utm_medium","utm_campaign"]
    missing = []
    if not url.startswith("http"):
        return False, "La UEL no empieza por http o https"
    if "?" not in url:
        return False, "La URL no contiene parámetros UTM"
    query = url.split("?")[-1]
    parts = query.split("&")
    keys = [kv.splot("=")[0] for kv in parts if "=" in kv]
    for req in required:
        if req not in keys:
            missong.append(req)
    if missing:
        return False, f"Faltan los parámetros obligatorios:{','.join(missing)}"
    return True, ""

# ------------------------
# Validación individual
# ------------------------
st.subheader("🔍 Validar una URL individual")
url = st.text_input("Introduce la URL")
if st.button("Validar URL"):
    valid, msg = validate_url_structure(url)
    if valid:
        st.success("URL válida ✅")
    else:
        st.error(f"Error: {msg}")

# ------------------------
# Validación desde CSV
# ------------------------
st.subheader("📂 Validar desde archivo CSV")
file = st.file_uploader("Sube un archivo CSV con una columna llamada 'url'", type=["csv"])
if file:
    try:
        df = pd.read_csv(file)
        if "url" not in df.columns:
            st.error("El archivo debe tener una columna llamada 'url'")
        else:
            results = []
            for idx, row in df.iterrows():
                url = str(row["url"])
                valid, msg = validate_url_structure(url)
                results.append({
                    "url": url,
                    "valida": "✅" if valid else "❌",
                    "error": "" if valid else msg
                })
            results_df = pd.DataFrame(results)
            st.write("### Resultado de la validación")
            st.dataframe(results_df)

            # Descargar CSV corregido
            csv = results_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📅 Descargar resultado como CSV",
                data=csv,
                file_name="urls_validadas.csv",
                mime="text/csv"
            )
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")

