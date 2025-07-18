import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from io import BytesIO

# ------------------------------------------------------------------
# Configuración de página
# ------------------------------------------------------------------
st.set_page_config(page_title="Naming Builder UTM", layout="wide")
st.title("🧱 Configurador de Naming Convention para UTM")

st.markdown("""
Arrastra los bloques de cada parámetro UTM, añade valores personalizados, y exporta la configuración como Excel.

- ✏️ **Nuevo bloque** → escribe un nombre y pulsa **Agregar bloque**  
- ➕ **Añadir valores** → selecciona el bloque y añade valores separados por comas  
- 📤 **Exportar** → descarga un archivo Excel con estructura y valores
""")

# ------------------------------------------------------------------
# Funciones utilitarias
# ------------------------------------------------------------------

def init_sec(key: str, defaults: list):
    """
    Inicializa el estado de una sección (bloques ordenables y valores asociados).
    """
    if key not in st.session_state:
        st.session_state[key] = defaults.copy()
    if f"vals_{key}" not in st.session_state:
        st.session_state[f"vals_{key}"] = {b: [] for b in defaults}
    if f"sel_{key}" not in st.session_state:
        st.session_state[f"sel_{key}"] = defaults[0]
    if f"txt_{key}" not in st.session_state:
        st.session_state[f"txt_{key}"] = ""
    if f"newblk_{key}" not in st.session_state:
        st.session_state[f"newblk_{key}"] = ""

def reset_sec(key: str, defaults: list):
    """
    Restaura el estado inicial de una sección (bloques y valores).
    """
    st.session_state[key] = defaults.copy()
    st.session_state[f"vals_{key}"] = {b: [] for b in defaults}
    st.session_state[f"sel_{key}"] = defaults[0]
    st.session_state[f"txt_{key}"] = ""
    st.session_state[f"newblk_{key}"] = ""

def add_block(sec_key: str, block_name: str):
    """
    Agrega un nuevo bloque a la sección si no existe.
    """
    if block_name and block_name not in st.session_state[sec_key]:
        st.session_state[sec_key].append(block_name)
        st.session_state[f"vals_{sec_key}"][block_name] = []

def add_block_callback(sec_key: str, input_key: str):
    """
    Callback: agrega un bloque, limpia el campo y recarga interfaz.
    """
    name = st.session_state[input_key].strip()
    if name:
        add_block(sec_key, name)
    st.session_state[input_key] = ""
    st.rerun()

def add_values_callback(sec_key: str):
    """
    Callback: agrega valores al bloque seleccionado y limpia el input.
    """
    blk = st.session_state[f"sel_{sec_key}"]
    txt = st.session_state[f"txt_{sec_key}"]
    if txt.strip():
        # Separar valores por coma y limpiar
        vals = [v.strip() for v in txt.split(",") if v.strip()]
        st.session_state[f"vals_{sec_key}"][blk].extend(vals)
        # Eliminar duplicados preservando el orden
        st.session_state[f"vals_{sec_key}"][blk] = list(dict.fromkeys(st.session_state[f"vals_{sec_key}"][blk]))
    st.session_state[f"txt_{sec_key}"] = ""

# ------------------------------------------------------------------
# Sección interactiva por parámetro UTM
# ------------------------------------------------------------------

def section(title: str, sec_key: str, defaults: list):
    """
    Renderiza una sección con drag & drop, input de valores, reset y exportación.
    """
    init_sec(sec_key, defaults)

    st.markdown(f"## {title}")
    
    # Drag & Drop horizontal de bloques
    st.session_state[sec_key] = sort_items(
        st.session_state[sec_key],
        direction="horizontal",
        key=f"sort_{sec_key}"
    ) or st.session_state[sec_key]

    st.caption("🔀 Arrastra los bloques para cambiar el orden")
    st.write("Orden actual:", st.session_state[sec_key])

    if st.button("↩️ Reset sección", key=f"reset_{sec_key}"):
        reset_sec(sec_key, defaults)

    # ---------- NUEVO BLOQUE ----------
    st.markdown("### ➕ Añadir nuevo bloque")
    newblk_key = f"newblk_{sec_key}"
    st.text_input("Nombre del bloque", key=newblk_key, placeholder="ej.: promocion")
    st.button("Agregar bloque",
              key=f"btn_addblk_{sec_key}",
              on_click=add_block_callback,
              kwargs=dict(sec_key=sec_key, input_key=newblk_key))

    # ---------- AÑADIR VALORES ----------
    st.markdown("### ➕ Añadir valores al bloque")
    st.selectbox("Bloque destino", st.session_state[sec_key], key=f"sel_{sec_key}")
    st.text_input("Valores (coma separada)", key=f"txt_{sec_key}", placeholder="valor1, valor2, valor3")
    st.button("Agregar valores",
              key=f"btn_addvals_{sec_key}",
              on_click=add_values_callback,
              kwargs=dict(sec_key=sec_key))

    # Vista expandible de los valores
    with st.expander("🔍 Ver valores guardados"):
        st.json(st.session_state[f"vals_{sec_key}"])

# ------------------------------------------------------------------
# Renderizado de las 5 secciones UTM
# ------------------------------------------------------------------

section("utm_campaign", "campaign", ["producto", "pais", "fecha", "audiencia", "region"])
section("utm_source", "source", ["google", "facebook", "instagram", "newsletter", "linkedin"])
section("utm_medium", "medium", ["cpc", "organic", "email", "referral", "social"])
section("utm_content", "content", ["color", "version", "posicion"])
section("utm_term", "term", ["keyword", "matchtype"])

# ------------------------------------------------------------------
# Exportar configuración a Excel
# ------------------------------------------------------------------
st.markdown("---")
st.header("📁 Exportar configuración a Excel")

def build_val_sheet():
    """
    Crea una hoja de valores: cada columna es un parámetro UTM,
    y cada celda contiene bloques y sus valores verticalmente.
    """
    cols = {}
    for sec in ["campaign", "source", "medium", "content", "term"]:
        col = []
        for blk in st.session_state[sec]:
            col += [blk] + st.session_state[f"vals_{sec}"][blk] + [""]
        cols[sec] = col
    # Igualar longitud de columnas
    max_len = max(len(v) for v in cols.values())
    for v in cols.values():
        v.extend([""] * (max_len - len(v)))
    return pd.DataFrame(cols)

if st.button("📥 Descargar Excel"):
    # Hoja 1: estructura de los nombres
    df_struct = pd.DataFrame([{
        "utm_campaign": "_".join(st.session_state["campaign"]),
        "utm_source"  : "_".join(st.session_state["source"]),
        "utm_medium"  : "_".join(st.session_state["medium"]),
        "utm_content" : "_".join(st.session_state["content"]),
        "utm_term"    : "_".join(st.session_state["term"]),
    }])

    # Hoja 2: valores por sección
    df_vals = build_val_sheet()

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_struct.to_excel(writer, index=False, sheet_name="estructura")
        df_vals.to_excel(writer, index=False, sheet_name="valores")
    buffer.seek(0)

    st.download_button(
        label="⬇️ naming_config.xlsx",
        data=buffer,
        file_name="naming_config.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
