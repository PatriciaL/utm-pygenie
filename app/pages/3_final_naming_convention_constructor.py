import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from style import apply_style

import streamlit as st
from streamlit_sortables import sort_items
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="UTM Genie — Naming Convention", page_icon="🧙", layout="centered", initial_sidebar_state="expanded")
apply_style()

st.markdown("""
<div style="margin-bottom:28px;padding-bottom:20px;border-bottom:1.5px solid #E4E4E7">
  <div style="font-family:'Sora',sans-serif;font-size:0.6rem;font-weight:500;
              letter-spacing:0.2em;text-transform:uppercase;color:#71717A;margin-bottom:8px">
    UTM Genie
  </div>
  <div style="font-family:'Sora',sans-serif;font-size:1.8rem;font-weight:600;
              letter-spacing:-0.04em;color:#1A1A1A;line-height:1.1;margin-bottom:10px">
    Naming Convention
  </div>
  <div style="font-family:'Sora',sans-serif;font-size:0.8rem;color:#71717A;letter-spacing:0.01em">
    Define la estructura y valores de cada parámetro UTM
  </div>
</div>
""", unsafe_allow_html=True)

# Instrucciones + sticky CTA
st.markdown("""
<style>
/* Forzar el botón sticky de Streamlit a posición fija */
div[data-testid="stButton"].sticky-btn > button {
    position: fixed !important;
    bottom: 32px !important;
    right: 36px !important;
    z-index: 99999 !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    background: #3D5A80 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 14px 26px !important;
    box-shadow: 0 4px 20px rgba(61,90,128,0.45), 0 1px 4px rgba(0,0,0,0.15) !important;
    cursor: pointer !important;
    transition: background 0.15s, box-shadow 0.15s, transform 0.1s !important;
}
div[data-testid="stButton"].sticky-btn > button:hover {
    background: #2e4460 !important;
    box-shadow: 0 8px 28px rgba(61,90,128,0.55) !important;
    transform: translateY(-1px) !important;
}
</style>
<div style="background:#EEF2F7;border:1.5px solid #C5D3E8;border-radius:6px;padding:18px 22px;margin-bottom:4px">
  <div style="font-family:'Sora',sans-serif;font-size:0.62rem;font-weight:500;letter-spacing:0.14em;text-transform:uppercase;color:#3D5A80;margin-bottom:10px">Cómo funciona</div>
  <div style="font-family:'Sora',sans-serif;font-size:0.83rem;color:#1A1A1A;line-height:1.75;margin-bottom:14px">
    Define los <strong>bloques</strong> de cada parámetro UTM y añade <strong>valores</strong> a cada uno.
    Todo lo que configures aquí se cargará automáticamente en el <strong>Generador Masivo</strong>
    para que puedas generar todas las combinaciones sin escribir nada manualmente.
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px 24px">
    <div style="font-family:'Sora',sans-serif;font-size:0.74rem;color:#3D5A80"><strong>utm_campaign</strong> &rarr; combinaciones de bloques</div>
    <div style="font-family:'Sora',sans-serif;font-size:0.74rem;color:#3D5A80"><strong>utm_source</strong> &rarr; fuentes de tráfico</div>
    <div style="font-family:'Sora',sans-serif;font-size:0.74rem;color:#3D5A80"><strong>utm_medium</strong> &rarr; canales o medios</div>
    <div style="font-family:'Sora',sans-serif;font-size:0.74rem;color:#3D5A80"><strong>utm_content</strong> &rarr; variantes del anuncio</div>
    <div style="font-family:'Sora',sans-serif;font-size:0.74rem;color:#3D5A80"><strong>utm_term</strong> &rarr; palabras clave</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Botón sticky — usa st.switch_page para navegar sin perder session_state
st.markdown('<div class="sticky-btn">', unsafe_allow_html=True)
if st.button("Ir al Generador →", key="sticky_go_generator"):
    st.switch_page("pages/1_generator_UTM.py")
st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
# Estado inicial
# ------------------------------------------------------------------

SECTIONS = {
    "campaign": ["producto", "pais", "fecha", "audiencia", "region"],
    "source":   ["google", "facebook", "instagram", "newsletter", "linkedin"],
    "medium":   ["cpc", "organic", "email", "referral", "social"],
    "content":  ["color", "version", "posicion"],
    "term":     ["keyword", "matchtype"],
}

for key, defaults in SECTIONS.items():
    if key not in st.session_state:
        st.session_state[key] = defaults.copy()
    if f"vals_{key}" not in st.session_state:
        st.session_state[f"vals_{key}"] = {b: [] for b in defaults}
    if f"reset_count_{key}" not in st.session_state:
        st.session_state[f"reset_count_{key}"] = 0

# ------------------------------------------------------------------
# Callbacks — toda la mutación de estado aquí, nunca en el render
# ------------------------------------------------------------------

def reset_sec(key):
    defaults = SECTIONS[key]
    st.session_state[key] = defaults.copy()
    st.session_state[f"vals_{key}"] = {b: [] for b in defaults}
    st.session_state[f"reset_count_{key}"] += 1
    # Limpiar también los inputs del generador para forzar resync
    for k in ["bulk_source","bulk_medium","bulk_campaign","bulk_content","bulk_term"]:
        if k in st.session_state:
            del st.session_state[k]

def add_block_cb(key):
    name = st.session_state[f"newblk_input_{key}"].strip()
    if name and name not in st.session_state[key]:
        st.session_state[key].append(name)
        st.session_state[f"vals_{key}"][name] = []
        st.session_state[f"reset_count_{key}"] += 1
    st.session_state[f"newblk_input_{key}"] = ""

def delete_block_cb(key, blk):
    if blk in st.session_state[key]:
        st.session_state[key].remove(blk)
    st.session_state[f"vals_{key}"].pop(blk, None)
    st.session_state[f"reset_count_{key}"] += 1

def add_values_cb(key):
    blk = st.session_state[f"sel_input_{key}"]
    txt = st.session_state[f"txt_input_{key}"].strip()
    if txt:
        new_vals = [v.strip() for v in txt.split(",") if v.strip()]
        existing = st.session_state[f"vals_{key}"].get(blk, [])
        for v in new_vals:
            if v not in existing:
                existing.append(v)
        st.session_state[f"vals_{key}"][blk] = existing
        # Invalidar cache del generador para forzar resync
        for k in ["bulk_source","bulk_medium","bulk_campaign","bulk_content","bulk_term"]:
            if k in st.session_state:
                del st.session_state[k]
    st.session_state[f"txt_input_{key}"] = ""

def delete_val_cb(key, blk, val):
    if val in st.session_state[f"vals_{key}"].get(blk, []):
        st.session_state[f"vals_{key}"][blk].remove(val)
    for k in ["bulk_source","bulk_medium","bulk_campaign","bulk_content","bulk_term"]:
        if k in st.session_state:
            del st.session_state[k]

def get_all_values(key):
    all_vals = []
    for blk in st.session_state.get(key, []):
        all_vals.extend(st.session_state.get(f"vals_{key}", {}).get(blk, []))
    return list(dict.fromkeys(all_vals))

# ------------------------------------------------------------------
# Render de sección
# ------------------------------------------------------------------

def section(title: str, key: str):
    st.markdown(f"## {title}")

    # FIX: sort_items puede devolver None si no hay interacción — proteger siempre
    rc     = st.session_state[f"reset_count_{key}"]
    result = sort_items(st.session_state[key], direction="horizontal", key=f"sort_{key}_{rc}")
    if result and len(result) == len(st.session_state[key]):
        st.session_state[key] = result

    st.caption("Arrastra los bloques para cambiar el orden")

    # Bloques con sus valores como pastillas y botón de borrado
    for blk in list(st.session_state[key]):  # list() para evitar mutation durante iteración
        vals = st.session_state[f"vals_{key}"].get(blk, [])
        c1, c2 = st.columns([9, 1])
        with c1:
            pastillas = " ".join([
                f'<span style="background:#EEF2F7;color:#3D5A80;padding:2px 10px;'
                f'border-radius:20px;font-size:11px;border:1.5px solid #C5D3E8;'
                f'font-family:\'Sora\',sans-serif;letter-spacing:0.03em;margin:2px;display:inline-block">{v}</span>'
                for v in vals
            ])
            sin_vals = '<em style="color:#A1A1AA;font-size:11px">sin valores</em>' if not vals else ""
            st.markdown(
                f'<div style="margin:6px 0;font-size:0.82rem;line-height:2">'
                f'<strong style="font-family:\'Sora\',sans-serif">{blk}</strong>'
                f'&nbsp;&nbsp;{pastillas}{sin_vals}</div>',
                unsafe_allow_html=True
            )
        with c2:
            # FIX: usar on_click para que el callback se ejecute antes del re-render
            st.button("—", key=f"del_blk_{key}_{blk}",
                      help=f"Eliminar bloque '{blk}'",
                      on_click=delete_block_cb,
                      kwargs={"key": key, "blk": blk})

        # FIX: mostrar TODOS los valores, no solo los primeros 6
        if vals:
            for i in range(0, len(vals), 4):
                chunk = vals[i:i+4]
                val_cols = st.columns(len(chunk))
                for j, val in enumerate(chunk):
                    with val_cols[j]:
                        st.button(f"x {val}", key=f"del_val_{key}_{blk}_{val}",
                                  on_click=delete_val_cb,
                                  kwargs={"key": key, "blk": blk, "val": val})

    st.markdown("")

    # Añadir nuevo bloque
    st.markdown("### Nuevo bloque")
    nc1, nc2 = st.columns([4, 1])
    with nc1:
        st.text_input("", key=f"newblk_input_{key}", placeholder="ej. promocion", label_visibility="collapsed")
    with nc2:
        st.button("Agregar", key=f"btn_addblk_{key}", on_click=add_block_cb, kwargs={"key": key})

    # Reset
    st.button("Resetear sección", key=f"reset_btn_{key}", on_click=reset_sec, kwargs={"key": key})

    # Añadir valores
    st.markdown("### Añadir valores")
    if st.session_state[key]:
        st.selectbox("", st.session_state[key], key=f"sel_input_{key}", label_visibility="collapsed")
        st.text_input("", key=f"txt_input_{key}", placeholder="valor1, valor2, valor3", label_visibility="collapsed")
        st.button("Agregar valores", key=f"btn_addvals_{key}", on_click=add_values_cb, kwargs={"key": key})
    else:
        st.caption("Añade al menos un bloque primero.")

    # Debug / preview
    with st.expander("Ver valores guardados"):
        st.json(st.session_state[f"vals_{key}"])

    preview = get_all_values(key)
    if preview:
        st.caption(f"El generador usará: {', '.join(preview)}")

    st.markdown("---")

# ------------------------------------------------------------------
# Secciones
# ------------------------------------------------------------------

section("utm_campaign", "campaign")
section("utm_source",   "source")
section("utm_medium",   "medium")
section("utm_content",  "content")
section("utm_term",     "term")

# ------------------------------------------------------------------
# Exportar a Excel
# ------------------------------------------------------------------

st.markdown("## Exportar a Excel")

def build_val_sheet():
    cols = {}
    for sec in SECTIONS:
        col = []
        for blk in st.session_state[sec]:
            col += [blk] + st.session_state[f"vals_{sec}"].get(blk, []) + [""]
        cols[sec] = col
    max_len = max(len(v) for v in cols.values())
    for v in cols.values():
        v.extend([""] * (max_len - len(v)))
    return pd.DataFrame(cols)

if st.button("Descargar Excel"):
    import itertools as _it

    # ── Hoja 1: valores por parámetro ─────────────────────────────
    # utm_campaign → combinaciones de bloques (producto cartesiano)
    # resto        → lista plana de valores de todos sus bloques
    cols_export = {}

    # utm_campaign: producto cartesiano de valores de cada bloque
    cam_blocks = st.session_state.get("campaign", [])
    cam_vals   = st.session_state.get("vals_campaign", {})
    if cam_blocks:
        block_lists = [cam_vals.get(b, [b]) or [b] for b in cam_blocks]
        combos = ["_".join(c) for c in _it.product(*block_lists)]
        cols_export["utm_campaign"] = combos
    else:
        cols_export["utm_campaign"] = []

    # resto de parámetros: lista plana de valores (sin concatenar bloques)
    for sec in ["source", "medium", "content", "term"]:
        vals_flat = []
        for blk in st.session_state.get(sec, []):
            vals_flat.extend(st.session_state.get(f"vals_{sec}", {}).get(blk, []))
        cols_export[f"utm_{sec}"] = list(dict.fromkeys(vals_flat))  # deduplicar, mantener orden

    # Normalizar longitudes
    max_len = max((len(v) for v in cols_export.values()), default=0)
    for k in cols_export:
        cols_export[k] += [""] * (max_len - len(cols_export[k]))

    df_export = pd.DataFrame(cols_export)

    # ── Hoja 2: estructura de bloques (referencia) ─────────────────
    df_struct = pd.DataFrame([{
        f"utm_{sec}": " | ".join(st.session_state.get(sec, []))
        for sec in SECTIONS
    }])

    buffer = BytesIO()
    import xlsxwriter as _xlsxwriter
    wb = _xlsxwriter.Workbook(buffer)

    # ── Formatos ──────────────────────────────────────────
    def _fmt(wb, **kw):
        base = {"font_name": "Arial", "font_size": 9, "valign": "vcenter"}
        base.update(kw)
        return wb.add_format(base)

    hdr_fmt  = _fmt(wb, bold=True, bg_color="#3D5A80", font_color="#FFFFFF",
                    border=1, border_color="#2e4460", align="center", font_size=9)
    cell_fmt = _fmt(wb, font_name="Courier New", font_size=8, font_color="#3D5A80",
                    border=1, border_color="#E4E4E7")
    alt_fmt  = _fmt(wb, font_name="Courier New", font_size=8, font_color="#3D5A80",
                    bg_color="#F8FAFC", border=1, border_color="#E4E4E7")
    struct_fmt = _fmt(wb, font_size=8, font_color="#52525B",
                      border=1, border_color="#E4E4E7")

    # ── Hoja 1: valores_utm ────────────────────────────────
    ws1 = wb.add_worksheet("valores_utm")
    ws1.set_tab_color("#3D5A80")
    ws1.freeze_panes(1, 0)
    ws1.set_row(0, 22)

    col_widths = [45, 16, 14, 14, 20]
    for c, (col, w) in enumerate(zip(df_export.columns, col_widths)):
        ws1.write(0, c, col, hdr_fmt)
        ws1.set_column(c, c, w)

    for r, row in df_export.iterrows():
        fmt = alt_fmt if r % 2 == 0 else cell_fmt
        for c, val in enumerate(row):
            ws1.write(r + 1, c, str(val) if val else "", fmt)

    # ── Hoja 2: estructura_bloques ─────────────────────────
    ws2 = wb.add_worksheet("estructura_bloques")
    ws2.set_tab_color("#71717A")
    ws2.set_row(0, 22)
    for c, col in enumerate(df_struct.columns):
        ws2.write(0, c, col, hdr_fmt)
        ws2.set_column(c, c, 35)
    for c, val in enumerate(df_struct.iloc[0]):
        ws2.write(1, c, str(val), struct_fmt)

    wb.close()
    buffer.seek(0)
    st.download_button("naming_config.xlsx", data=buffer, file_name="naming_config.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.markdown("---")
st.caption("Los valores configurados se cargarán automáticamente en el Generador Masivo.")
