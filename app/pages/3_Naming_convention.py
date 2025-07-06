# naming_builder.py

import streamlit as st
import pandas as pd
import base64
from streamlit_sortables import sort_items

st.set_page_config(page_title="🧩 Constructor Naming", layout="centered")
st.title("🧩 Constructor de Convenciones de Naming")

st.markdown("""
Organiza los campos que quieres usar para tus URLs con UTM.
Puedes reordenar, eliminar o añadir nuevos campos según tu estructura.
""")

# --- Campos iniciales basados en el Excel ejemplo ---
def get_default_fields():
    return [
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_term",
        "utm_content",
        "producto",
        "formato",
        "canal",
        "audiencia",
        "pais"
    ]

if "fields" not in st.session_state:
    st.session_state.fields = get_default_fields()

# --- Drag and drop ---
st.subheader("🔀 Reordenar campos")
reordered = sort_items(st.session_state.fields, direction="vertical", key="sortable")
if reordered:
    st.session_state.fields = reordered

# --- Editar campos ---
st.subheader("✏️ Editar campos")
edit_cols = st.columns([3, 1, 1])
with edit_cols[0]:
    new_field = st.text_input("Nuevo campo", key="new_field")
with edit_cols[1]:
    if st.button("➕ Añadir") and new_field:
        if new_field not in st.session_state.fields:
            st.session_state.fields.append(new_field)
            st.success(f"Campo '{new_field}' añadido.")
        else:
            st.warning("Ese campo ya existe.")
with edit_cols[2]:
    delete_field = st.selectbox("Eliminar campo", st.session_state.fields, key="del_field")
    if st.button("🗑️ Eliminar"):
        st.session_state.fields.remove(delete_field)
        st.success(f"Campo '{delete_field}' eliminado.")

# --- Vista previa ---
st.subheader("👁️ Vista previa de la estructura")
st.code(" - ".join(st.session_state.fields))

# --- Descargar como CSV ---
st.subheader("📥 Descargar estructura")
df_out = pd.DataFrame(st.session_state.fields, columns=["campo"])
csv = df_out.to_csv(index=False).encode("utf-8")
st.download_button("📄 Descargar CSV", csv, "naming_structure.csv", mime="text/csv")
