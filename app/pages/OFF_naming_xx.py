import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd

st.set_page_config(page_title="🧱 Naming Convention Builder", layout="wide")

st.title("🧱 Configurador de Naming Convention para UTM")
st.markdown("""
Organiza tus parámetros UTM mediante bloques drag & drop, agrega valores personalizados y exporta la configuración como archivo Excel.

### 🧭 Instrucciones rápidas
- Arrastra los bloques horizontalmente para definir el orden.
- En cada bloque puedes añadir varios valores separados por comas.
- Los valores quedan almacenados y puedes exportarlos en la hoja “valores”.
""")

# ---------- Inicializar sesión ----------
params = {
    "utm_campaign": ["producto", "pais", "fecha", "audiencia"],
    "utm_source": ["google", "newsletter"],
    "utm_medium": ["cpc", "email"],
    "utm_content": ["color", "version", "posicion"],
    "utm_term": ["keyword", "matchtype"]
}

for key, blocks in params.items():
    short_key = key.split("_")[1]
    if short_key not in st.session_state:
        st.session_state[short_key] = blocks.copy()
    if f"vals_{short_key}" not in st.session_state:
        st.session_state[f"vals_{short_key}"] = {blk: [] for blk in blocks}
    if f"newblk_{short_key}" not in st.session_state:
        st.session_state[f"newblk_{short_key}"] = ""

# ---------- Función para construir valores como hoja ----------
def build_val_df():
    cols = {}
    for k in ["campaign", "source", "medium", "content", "term"]:
        col = []
        for blk in st.session_state[k]:
            col.append(blk)
            values = st.session_state[f"vals_{k}"].get(blk, [])
            if not isinstance(values, list):
                values = [str(values)]
            else:
                values = [str(v) for v in values]
            col.extend(values)
            col.append("")  # separación visual
        cols[k] = col

    max_len = max(len(c) for c in cols.values())
    for c in cols.values():
        c.extend([""] * (max_len - len(c)))
    return pd.DataFrame(cols)

# ---------- Función para crear cada sección ----------
def section(title, key, default_blocks):
    st.markdown(f"## ✳️ {title}")
    col1, col2 = st.columns([8, 2])

    # Agregar nuevo bloque manualmente
    with col2:
        new_blk = st.text_input("➕ Añadir nuevo bloque", key=f"newblk_{key}")
        if st.button("Agregar", key=f"add_{key}"):
            new_blks = [b.strip() for b in new_blk.split(",") if b.strip()]
            for b in new_blks:
                if b not in st.session_state[key]:
                    st.session_state[key].append(b)
                    st.session_state[f"vals_{key}"][b] = []
            st.session_state[f"newblk_{key}"] = ""

    # Drag and drop de bloques
    with col1:
        result = sort_items(st.session_state[key], direction="horizontal", key=f"sort_{key}")
        if isinstance(result, list):
            st.session_state[key] = result

    # Mostrar y añadir valores asociados por bloque
    for blk in st.session_state[key]:
        st.markdown(f"#### 🔹 Valores en {blk}")
        existing = st.session_state[f"vals_{key}"].get(blk, [])
        if existing:
            st.write(", ".join(existing))
        new_val = st.text_input(f"Nuevos valores (coma separada) → {blk}", key=f"txt_{key}_{blk}")
        if st.button("Añadir", key=f"btn_{key}_{blk}"):
            vals = [v.strip() for v in new_val.split(",") if v.strip()]
            st.session_state[f"vals_{key}"].setdefault(blk, []).extend(vals)
            st.session_state[f"txt_{key}_{blk}"] = ""

# ---------- Crear secciones ----------
section("utm_campaign", "campaign", ["producto", "pais", "fecha", "audiencia"])
section("utm_source", "source", ["google", "newsletter"])
section("utm_medium", "medium", ["cpc", "email"])
section("utm_content", "content", ["color", "version", "posicion"])
section("utm_term", "term", ["keyword", "matchtype"])

# ---------- Exportar configuración ----------
st.markdown("---")
st.subheader("📁 Exportar a Excel")

if st.button("⬇️ Descargar configuración"):
    df1 = pd.DataFrame([{
        "utm_campaign": "_".join(st.session_state["campaign"]),
        "utm_source": "_".join(st.session_state["source"]),
        "utm_medium": "_".join(st.session_state["medium"]),
        "utm_content": "_".join(st.session_state["content"]),
        "utm_term": "_".join(st.session_state["term"])
    }])

    df2 = build_val_df()

    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df1.to_excel(writer, index=False, sheet_name="configuracion")
        df2.to_excel(writer, index=False, sheet_name="valores")
    st.download_button(
        label="📤 Descargar archivo Excel",
        data=output.getvalue(),
        file_name="naming_utm_config.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
