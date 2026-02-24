iimport sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from style import apply_style

import streamlit as st
import pandas as pd
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote
from collections import Counter
from io import BytesIO
from datetime import datetime
import xlsxwriter
import re

st.set_page_config(page_title="UTM Genie — Validador", page_icon="🧙", layout="centered")
apply_style()

st.markdown("""
<div style="margin-bottom:28px;padding-bottom:20px;border-bottom:1.5px solid #E4E4E7">
  <div style="font-family:'Sora',sans-serif;font-size:0.6rem;font-weight:500;
              letter-spacing:0.2em;text-transform:uppercase;color:#71717A;margin-bottom:8px">
    UTM Genie
  </div>
  <div style="font-family:'Sora',sans-serif;font-size:1.8rem;font-weight:600;
              letter-spacing:-0.04em;color:#1A1A1A;line-height:1.1;margin-bottom:10px">
    Validador y Corrector
  </div>
  <div style="font-family:'Sora',sans-serif;font-size:0.8rem;color:#71717A;letter-spacing:0.01em">
    Auditoría, detección y corrección automática de parámetros UTM
  </div>
</div>
""", unsafe_allow_html=True)

# ── Instrucciones ─────────────────────────────────────────────────
st.markdown("""
<div style="background:#EEF2F7;border:1.5px solid #C5D3E8;border-radius:6px;padding:18px 22px;margin-bottom:28px">
  <div style="font-family:'Sora',sans-serif;font-size:0.62rem;font-weight:500;letter-spacing:0.14em;
              text-transform:uppercase;color:#3D5A80;margin-bottom:12px">Cómo funciona</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
    <div>
      <div style="font-family:'Sora',sans-serif;font-size:0.78rem;font-weight:600;color:#1A1A1A;margin-bottom:6px">
        Validación individual
      </div>
      <div style="font-family:'Sora',sans-serif;font-size:0.76rem;color:#52525B;line-height:1.65">
        Pega una URL y obtén un diagnóstico inmediato con score de salud,
        desglose de parámetros y una versión corregida lista para copiar.
      </div>
    </div>
    <div>
      <div style="font-family:'Sora',sans-serif;font-size:0.78rem;font-weight:600;color:#1A1A1A;margin-bottom:6px">
        Auditoría por archivo
      </div>
      <div style="font-family:'Sora',sans-serif;font-size:0.76rem;color:#52525B;line-height:1.65">
        Sube un CSV o Excel con una columna <code style="background:#fff;padding:1px 5px;border-radius:3px;font-size:0.72rem">url</code>.
        Recibirás un reporte Excel con 3 hojas: resumen ejecutivo,
        auditoría completa con colores y URLs corregidas listas para usar.
      </div>
    </div>
  </div>
  <div style="margin-top:14px;padding-top:12px;border-top:1px solid #C5D3E8">
    <div style="font-family:'Sora',sans-serif;font-size:0.72rem;color:#3D5A80;line-height:1.7">
      <strong>Correcciones automáticas:</strong>
      elimina espacios · elimina parámetros duplicados (conserva el primero) ·
      mueve UTMs del fragmento # al query · normaliza valores a minúsculas ·
      marca como "No autocorregible" cuando faltan parámetros requeridos
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Lógica de validación y corrección
# ------------------------------------------------------------------

REQUIRED = ["utm_source", "utm_medium", "utm_campaign"]
OPTIONAL  = ["utm_content", "utm_term"]

def validate_url(url: str) -> dict:
    errors, warnings, params = [], [], {}
    raw = str(url).strip()

    if not raw or raw.lower() in ("nan", "none", ""):
        return {"errors": ["URL vacía o nula"], "warnings": [], "params": {}, "valid": False, "score": 0}

    parsed = urlparse(raw)
    query  = parse_qs(parsed.query, keep_blank_values=True)

    if not parsed.scheme.startswith("http"):
        errors.append("Sin esquema http(s)")
    if " " in raw:
        errors.append("Contiene espacios")

    for param in REQUIRED:
        if param not in query:
            errors.append(f"Falta {param}")
        elif not query[param][0].strip():
            errors.append(f"{param} vacío")
        else:
            params[param] = query[param][0]

    for param in OPTIONAL:
        if param in query:
            val = query[param][0].strip()
            if val:
                params[param] = val
            else:
                warnings.append(f"{param} presente pero vacío")

    raw_params = parsed.query.split("&")
    keys = [p.split("=")[0] for p in raw_params if "=" in p]
    dupes = [k for k, c in Counter(keys).items() if c > 1]
    if dupes:
        warnings.append(f"Parámetros duplicados: {', '.join(dupes)}")

    if parsed.fragment and "utm_" in parsed.fragment:
        warnings.append("UTMs en fragmento # — Analytics no los recoge")

    score = max(0, 100 - len(errors) * 25 - len(warnings) * 10)

    return {"errors": errors, "warnings": warnings, "params": params, "valid": len(errors) == 0, "score": score}


def fix_url(url: str) -> dict:
    """
    Intenta corregir automáticamente la URL.
    Devuelve: fixed_url, fixes_applied (lista), autocorregible (bool)
    """
    raw = str(url).strip()
    fixes = []

    if not raw or raw.lower() in ("nan", "none", ""):
        return {"fixed_url": raw, "fixes": [], "autocorregible": False}

    # 1. Limpiar espacios en la URL base
    if " " in raw:
        raw = raw.replace(" ", "%20")
        fixes.append("Espacios reemplazados por %20")

    parsed = urlparse(raw)

    # 2. Mover UTMs del fragmento # al query
    fragment_params = {}
    if parsed.fragment and "utm_" in parsed.fragment:
        frag_qs = parse_qs(parsed.fragment, keep_blank_values=True)
        for k, v in frag_qs.items():
            if k.startswith("utm_"):
                fragment_params[k] = v[0]
        if fragment_params:
            fixes.append(f"UTMs movidos del fragmento al query: {', '.join(fragment_params.keys())}")

    # 3. Parsear query actual y eliminar duplicados (conservar primero)
    raw_pairs = parsed.query.split("&") if parsed.query else []
    seen_keys = {}
    deduped   = []
    removed_dupes = []
    for pair in raw_pairs:
        if "=" not in pair:
            continue
        k, v = pair.split("=", 1)
        if k not in seen_keys:
            seen_keys[k] = v
            deduped.append((k, v))
        else:
            removed_dupes.append(k)
    if removed_dupes:
        fixes.append(f"Duplicados eliminados: {', '.join(set(removed_dupes))}")

    # 4. Normalizar valores UTM a minúsculas
    normalized = []
    norm_list  = []
    for k, v in deduped:
        if k.startswith("utm_") and v != v.lower():
            norm_list.append(k)
            normalized.append((k, v.lower()))
        else:
            normalized.append((k, v))
    if norm_list:
        fixes.append(f"Normalizados a minúsculas: {', '.join(norm_list)}")

    # 5. Añadir UTMs del fragmento si no existen ya
    final_params = dict(normalized)
    for k, v in fragment_params.items():
        if k not in final_params:
            final_params[k] = v.lower()

    # 6. Reconstruir query string conservando orden (requeridos primero)
    order = REQUIRED + OPTIONAL
    ordered = {k: v for k in order if k in final_params}
    rest    = {k: v for k, v in final_params.items() if k not in ordered}
    all_params = {**ordered, **rest}

    new_query = urlencode(all_params)
    fixed = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, ""))

    # 7. ¿Es autocorregible? Solo si los 3 requeridos están presentes tras la corrección
    result_check = validate_url(fixed)
    autocorregible = result_check["valid"]

    if not autocorregible:
        missing = [p for p in REQUIRED if p not in all_params]
        fixes.append(f"No autocorregible — faltan: {', '.join(missing)}")

    return {
        "fixed_url":      fixed,
        "fixes":          fixes,
        "autocorregible": autocorregible,
    }


def score_color(score):
    if score >= 90: return "#16a34a", "#F0FDF4", "#86EFAC"
    if score >= 60: return "#92400E", "#FFFBEB", "#FDE68A"
    return "#9F1239", "#FFF1F2", "#FECDD3"


def param_status_html(result):
    rows = []
    for p in REQUIRED + OPTIONAL:
        req = p in REQUIRED
        if p in result["params"]:
            icon, ic, bg = "✓", "#16a34a", "#F0FDF4"
            val = result["params"][p]
        elif req:
            icon, ic, bg = "✗", "#E11D48", "#FFF1F2"
            val = "falta"
        else:
            icon, ic, bg = "○", "#D4D4D8", "transparent"
            val = "no presente"
        label_extra = "" if req else ' <span style="font-size:0.6rem;color:#A1A1AA">(opcional)</span>'
        rows.append(f"""
        <div style="display:flex;align-items:center;gap:14px;padding:8px 12px;
                    background:{bg};border-radius:4px;margin:3px 0">
          <div style="font-size:0.9rem;color:{ic};font-weight:700;width:18px;text-align:center">{icon}</div>
          <div style="font-family:'DM Mono',monospace;font-size:0.72rem;color:#52525B;width:130px">{p}{label_extra}</div>
          <div style="font-family:'DM Mono',monospace;font-size:0.75rem;color:#3D5A80;font-weight:500">{val}</div>
        </div>""")
    return f'<div style="margin:14px 0">{"".join(rows)}</div>'


# ------------------------------------------------------------------
# Validación individual
# ------------------------------------------------------------------

st.markdown("## Validación individual")
single_url = st.text_input("", placeholder="https://tusitio.com?utm_source=google&utm_medium=cpc&utm_campaign=...", label_visibility="collapsed")

if single_url:
    r   = validate_url(single_url)
    fix = fix_url(single_url)
    tc, bg, bd = score_color(r["score"])

    # Score card
    st.markdown(f"""
    <div style="background:{bg};border:1.5px solid {bd};border-radius:8px;
                padding:16px 20px;display:flex;align-items:center;gap:20px;margin:12px 0">
      <div style="text-align:center;min-width:56px">
        <div style="font-family:'Sora',sans-serif;font-size:1.8rem;font-weight:700;color:{tc};line-height:1">{r["score"]}</div>
        <div style="font-size:0.6rem;letter-spacing:0.1em;text-transform:uppercase;color:{tc};opacity:0.7">score</div>
      </div>
      <div style="flex:1">
        <div style="font-family:'Sora',sans-serif;font-size:0.82rem;font-weight:500;color:{tc}">
          {"URL válida — todos los parámetros requeridos presentes" if r["valid"] else " · ".join(r["errors"])}
        </div>
        {"" if not r["warnings"] else f'<div style="font-size:0.75rem;color:#92400E;margin-top:4px">Avisos: {" · ".join(r["warnings"])}</div>'}
      </div>
    </div>
    <div style="background:#E4E4E7;border-radius:4px;height:4px;margin:0 0 16px 0">
      <div style="background:{tc};width:{r["score"]}%;height:4px;border-radius:4px"></div>
    </div>
    """, unsafe_allow_html=True)

    # Desglose parámetros
    st.markdown(param_status_html(r), unsafe_allow_html=True)

    # URL corregida
    st.markdown("### URL corregida")
    if fix["fixes"]:
        fixes_html = "".join([
            f'<div style="font-size:0.74rem;color:#52525B;padding:2px 0">· {f}</div>'
            for f in fix["fixes"]
        ])
        st.markdown(f"""
        <div style="background:#F8FAFC;border:1.5px solid #E4E4E7;border-radius:6px;padding:14px 16px;margin-bottom:10px">
          <div style="font-size:0.62rem;letter-spacing:0.1em;text-transform:uppercase;color:#71717A;margin-bottom:8px">Correcciones aplicadas</div>
          {fixes_html}
        </div>
        """, unsafe_allow_html=True)

    if fix["autocorregible"]:
        st.code(fix["fixed_url"])
        st.caption("URL corregida y lista para usar.")
    else:
        st.markdown(f"""
        <div style="background:#FFF1F2;border:1.5px solid #FECDD3;border-radius:6px;padding:12px 16px;
                    font-family:'Sora',sans-serif;font-size:0.8rem;color:#9F1239">
          No autocorregible — faltan parámetros requeridos que deben añadirse manualmente.
        </div>
        """, unsafe_allow_html=True)
        if fix["fixed_url"] != single_url:
            st.caption("Versión parcialmente corregida:")
            st.code(fix["fixed_url"])

st.markdown("---")

# ------------------------------------------------------------------
# Auditoría y corrección por archivo
# ------------------------------------------------------------------

st.markdown("## Auditoría por archivo")

col_info, col_dl = st.columns([3, 1])
with col_info:
    st.caption("Columna requerida: 'url'. Acepta CSV y Excel.")
with col_dl:
    csv_paths = ["app/data/utm_urls_ejemplo.csv", "data/utm_urls_ejemplo.csv"]
    csv_found = next((p for p in csv_paths if os.path.exists(p)), None)
    if csv_found:
        with open(csv_found, "rb") as f:
            st.download_button("Ver ejemplo", f, file_name="utm_urls_ejemplo.csv",
                               mime="text/csv", use_container_width=True)

uploaded_file = st.file_uploader("", type=["csv", "xlsx"], label_visibility="collapsed")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)

        if "url" not in df.columns:
            st.error("El archivo debe contener una columna llamada 'url'.")
        else:
            rows      = []
            all_errors = []

            for _, row in df.iterrows():
                r   = validate_url(str(row["url"]))
                fix = fix_url(str(row["url"]))

                if r["valid"]:
                    estado = "OK"
                elif r["warnings"] and not r["errors"]:
                    estado = "Aviso"
                else:
                    estado = "Error"

                rows.append({
                    "url_original":   str(row["url"]),
                    "url_corregida":  fix["fixed_url"],
                    "autocorregible": "Sí" if fix["autocorregible"] else "No",
                    "estado":         estado,
                    "score":          r["score"],
                    "correcciones":   "; ".join(fix["fixes"]) if fix["fixes"] else "—",
                    "errores":        "; ".join(r["errors"])   if r["errors"]   else "—",
                    "avisos":         "; ".join(r["warnings"]) if r["warnings"] else "—",
                    "utm_source":     r["params"].get("utm_source",   ""),
                    "utm_medium":     r["params"].get("utm_medium",   ""),
                    "utm_campaign":   r["params"].get("utm_campaign", ""),
                    "utm_content":    r["params"].get("utm_content",  ""),
                    "utm_term":       r["params"].get("utm_term",     ""),
                })
                all_errors.extend(r["errors"])

            result_df  = pd.DataFrame(rows)
            total      = len(result_df)
            ok         = (result_df["estado"] == "OK").sum()
            avisos     = (result_df["estado"] == "Aviso").sum()
            ko         = (result_df["estado"] == "Error").sum()
            avg_score  = int(result_df["score"].mean())
            n_fixed    = (result_df["autocorregible"] == "Sí").sum()

            # Scorecard resumen
            sc, bg, bd = score_color(avg_score)
            st.markdown(f"""
            <div style="background:{bg};border:1.5px solid {bd};border-radius:8px;padding:18px 24px;margin:16px 0">
              <div style="font-family:'Sora',sans-serif;font-size:0.6rem;font-weight:500;
                          letter-spacing:0.14em;text-transform:uppercase;color:{sc};margin-bottom:12px">
                Resumen de auditoría · {datetime.now().strftime("%d/%m/%Y")}
              </div>
              <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:12px">
                <div style="text-align:center">
                  <div style="font-size:1.5rem;font-weight:700;color:#1A1A1A">{total}</div>
                  <div style="font-size:0.6rem;letter-spacing:0.08em;text-transform:uppercase;color:#71717A">URLs</div>
                </div>
                <div style="text-align:center">
                  <div style="font-size:1.5rem;font-weight:700;color:#16a34a">{ok}</div>
                  <div style="font-size:0.6rem;letter-spacing:0.08em;text-transform:uppercase;color:#71717A">Correctas</div>
                </div>
                <div style="text-align:center">
                  <div style="font-size:1.5rem;font-weight:700;color:#E11D48">{ko}</div>
                  <div style="font-size:0.6rem;letter-spacing:0.08em;text-transform:uppercase;color:#71717A">Errores</div>
                </div>
                <div style="text-align:center">
                  <div style="font-size:1.5rem;font-weight:700;color:{sc}">{avg_score}</div>
                  <div style="font-size:0.6rem;letter-spacing:0.08em;text-transform:uppercase;color:#71717A">Score</div>
                </div>
                <div style="text-align:center">
                  <div style="font-size:1.5rem;font-weight:700;color:#3D5A80">{n_fixed}</div>
                  <div style="font-size:0.6rem;letter-spacing:0.08em;text-transform:uppercase;color:#71717A">Autocorregidas</div>
                </div>
              </div>
              <div style="background:#E4E4E7;border-radius:4px;height:5px;margin-top:14px">
                <div style="background:{sc};width:{avg_score}%;height:5px;border-radius:4px"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Tabla visual
            def render_table(data):
                header = """
                <div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;
                font-family:'Sora',sans-serif;font-size:0.73rem">
                <thead><tr style="border-bottom:2px solid #E4E4E7">
                  <th style="padding:8px 10px;font-size:0.6rem;letter-spacing:0.1em;text-transform:uppercase;color:#71717A;font-weight:500;text-align:left">Estado</th>
                  <th style="padding:8px 6px;font-size:0.6rem;letter-spacing:0.1em;text-transform:uppercase;color:#71717A;font-weight:500;text-align:center">Score</th>
                  <th style="padding:8px 10px;font-size:0.6rem;letter-spacing:0.1em;text-transform:uppercase;color:#71717A;font-weight:500;text-align:left">URL original</th>
                  <th style="padding:8px 10px;font-size:0.6rem;letter-spacing:0.1em;text-transform:uppercase;color:#71717A;font-weight:500;text-align:left">Correcciones</th>
                  <th style="padding:8px 8px;font-size:0.6rem;letter-spacing:0.1em;text-transform:uppercase;color:#71717A;font-weight:500;text-align:center">Auto</th>
                </tr></thead><tbody>"""

                body = ""
                for _, row in data.iterrows():
                    if row["estado"] == "OK":
                        badge  = '<span style="background:#DCFCE7;color:#16a34a;padding:2px 8px;border-radius:20px;font-size:0.65rem;font-weight:600">OK</span>'
                        row_bg = "#FAFFFE"
                        sc_col = "#16a34a"
                    elif row["estado"] == "Aviso":
                        badge  = '<span style="background:#FEF9C3;color:#92400E;padding:2px 8px;border-radius:20px;font-size:0.65rem;font-weight:600">Aviso</span>'
                        row_bg = "#FFFDF0"
                        sc_col = "#92400E"
                    else:
                        badge  = '<span style="background:#FFE4E6;color:#E11D48;padding:2px 8px;border-radius:20px;font-size:0.65rem;font-weight:600">Error</span>'
                        row_bg = "#FFF8F8"
                        sc_col = "#E11D48"

                    url_s = str(row["url_original"])[:52] + ("…" if len(str(row["url_original"])) > 52 else "")
                    corr  = str(row["correcciones"])[:55] + ("…" if len(str(row["correcciones"])) > 55 else "") if row["correcciones"] != "—" else '<span style="color:#A1A1AA">—</span>'
                    auto  = '<span style="color:#16a34a;font-weight:600">Sí</span>' if row["autocorregible"] == "Sí" else '<span style="color:#A1A1AA">No</span>'

                    body += f"""<tr style="background:{row_bg};border-bottom:1px solid #F4F4F5">
                      <td style="padding:9px 10px">{badge}</td>
                      <td style="padding:9px 6px;text-align:center;font-weight:700;color:{sc_col};font-family:'DM Mono',monospace">{row["score"]}</td>
                      <td style="padding:9px 10px;font-family:'DM Mono',monospace;font-size:0.68rem;color:#3D5A80" title="{row['url_original']}">{url_s}</td>
                      <td style="padding:9px 10px;font-size:0.71rem;color:#52525B">{corr}</td>
                      <td style="padding:9px 8px;text-align:center">{auto}</td>
                    </tr>"""

                return f"{header}{body}</tbody></table></div>"

            tab1, tab2, tab3, tab4 = st.tabs(["Todas", "Solo errores", "Autocorregidas", "Errores frecuentes"])

            with tab1:
                st.markdown(render_table(result_df), unsafe_allow_html=True)
            with tab2:
                err_df = result_df[result_df["estado"] == "Error"]
                if err_df.empty:
                    st.markdown('<p style="color:#16a34a;font-size:0.85rem;padding:12px 0">Sin errores.</p>', unsafe_allow_html=True)
                else:
                    st.markdown(render_table(err_df), unsafe_allow_html=True)
            with tab3:
                fixed_df = result_df[result_df["autocorregible"] == "Sí"]
                if fixed_df.empty:
                    st.markdown('<p style="color:#71717A;font-size:0.85rem;padding:12px 0">Ninguna URL fue autocorregida.</p>', unsafe_allow_html=True)
                else:
                    st.markdown(render_table(fixed_df), unsafe_allow_html=True)
            with tab4:
                if all_errors:
                    freq     = Counter(all_errors).most_common()
                    freq_html = "".join([
                        f'<div style="display:flex;justify-content:space-between;align-items:center;'
                        f'padding:9px 14px;background:{"#FFF8F8" if i%2==0 else "#FAFAFA"};border-radius:4px;margin:2px 0">'
                        f'<span style="font-size:0.78rem;color:#52525B">{err}</span>'
                        f'<span style="font-family:\'DM Mono\',monospace;font-size:0.78rem;font-weight:700;color:#E11D48">{cnt}</span>'
                        f'</div>'
                        for i, (err, cnt) in enumerate(freq)
                    ])
                    st.markdown(f"""
                    <div style="margin:8px 0">
                      <div style="display:flex;justify-content:space-between;padding:0 14px 6px;
                                  font-size:0.62rem;letter-spacing:0.1em;text-transform:uppercase;color:#71717A">
                        <span>Error</span><span>Frecuencia</span>
                      </div>{freq_html}
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown('<p style="color:#16a34a;font-size:0.85rem;padding:12px 0">Sin errores.</p>', unsafe_allow_html=True)

            # ── Excel de auditoría ─────────────────────────────────
            st.markdown("---")

            def build_audit_excel(result_df, avg_score, ok, ko, avisos, n_fixed, total, all_errors):
                buf = BytesIO()
                wb  = xlsxwriter.Workbook(buf)

                # Formatos base
                def fmt(wb, **kw):
                    base = {"font_name": "Arial", "font_size": 8, "valign": "vcenter"}
                    base.update(kw)
                    return wb.add_format(base)

                f_title  = fmt(wb, font_size=14, bold=True, font_color="#1A1A1A")
                f_meta   = fmt(wb, font_size=9, font_color="#71717A")
                f_hdr    = fmt(wb, bold=True, font_color="#FFFFFF", bg_color="#3D5A80",
                               border=1, border_color="#2e4460", align="center", text_wrap=True, font_size=8)
                f_ok     = fmt(wb, bold=True, font_color="#166534", bg_color="#DCFCE7", align="center", border=1, border_color="#BBF7D0")
                f_warn   = fmt(wb, bold=True, font_color="#92400E", bg_color="#FEF9C3", align="center", border=1, border_color="#FDE68A")
                f_err    = fmt(wb, bold=True, font_color="#9F1239", bg_color="#FFE4E6", align="center", border=1, border_color="#FECDD3")
                f_sc_ok  = fmt(wb, bold=True, font_color="#16a34a", align="center", border=1, border_color="#E4E4E7")
                f_sc_w   = fmt(wb, bold=True, font_color="#92400E", align="center", border=1, border_color="#E4E4E7")
                f_sc_e   = fmt(wb, bold=True, font_color="#E11D48", align="center", border=1, border_color="#E4E4E7")
                f_url    = fmt(wb, font_name="Courier New", font_color="#3D5A80", border=1, border_color="#E4E4E7")
                f_url_fix= fmt(wb, font_name="Courier New", font_color="#16a34a", border=1, border_color="#BBF7D0", bg_color="#F0FDF4")
                f_cell   = fmt(wb, border=1, border_color="#E4E4E7")
                f_mono   = fmt(wb, font_name="Courier New", font_color="#3D5A80", border=1, border_color="#E4E4E7")
                f_fix_lbl= fmt(wb, font_color="#166534", bg_color="#F0FDF4", border=1, border_color="#BBF7D0")

                # ── Hoja 1: Resumen ejecutivo ──────────────────────
                ws1 = wb.add_worksheet("Resumen")
                ws1.set_tab_color("#3D5A80")
                ws1.set_column("A:A", 30)
                ws1.set_column("B:B", 18)

                ws1.write("A1", "Reporte de Auditoría UTM", f_title)
                ws1.write("A2", f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", f_meta)

                ws1.write("A4", "RESUMEN GLOBAL", fmt(wb, font_size=8, bold=True, font_color="#3D5A80"))
                summary = [
                    ("URLs analizadas",     total),
                    ("URLs correctas",      ok),
                    ("URLs con avisos",     avisos),
                    ("URLs con errores",    ko),
                    ("URLs autocorregidas", n_fixed),
                    ("Score medio",         f"{avg_score}/100"),
                    ("Tasa de error",       f"{round(ko/total*100,1)}%" if total else "0%"),
                    ("Tasa autocorrección", f"{round(n_fixed/ko*100,1)}%" if ko else "N/A"),
                ]
                for i, (label, val) in enumerate(summary):
                    bg = "#FAFAFA" if i % 2 == 0 else "#FFFFFF"
                    ws1.write(5+i, 0, label, fmt(wb, border=1, border_color="#E4E4E7", bg_color=bg))
                    ws1.write(5+i, 1, val,   fmt(wb, bold=True, align="center", border=1, border_color="#E4E4E7", bg_color=bg))

                if all_errors:
                    ws1.write("A15", "ERRORES MÁS FRECUENTES", fmt(wb, font_size=8, bold=True, font_color="#3D5A80"))
                    ws1.write("A16", "Error",      f_hdr)
                    ws1.write("B16", "Frecuencia", f_hdr)
                    for i, (err, cnt) in enumerate(Counter(all_errors).most_common(10)):
                        bg = "#FFF8F8" if i % 2 == 0 else "#FFFFFF"
                        ws1.write(16+i, 0, err, fmt(wb, border=1, border_color="#E4E4E7", bg_color=bg))
                        ws1.write(16+i, 1, cnt, fmt(wb, bold=True, font_color="#E11D48", align="center", border=1, border_color="#E4E4E7", bg_color=bg))

                # ── Hoja 2: Auditoría completa ─────────────────────
                ws2 = wb.add_worksheet("Auditoría completa")
                ws2.set_tab_color("#3D5A80")
                ws2.freeze_panes(1, 0)
                ws2.set_row(0, 26)

                cols2   = ["Estado","Score","URL original","URL corregida","Autocorregible",
                           "Correcciones aplicadas","Errores","Avisos",
                           "utm_source","utm_medium","utm_campaign","utm_content","utm_term"]
                widths2 = [10,8,55,55,14,45,40,35,16,14,24,16,16]
                for c,(col,w) in enumerate(zip(cols2,widths2)):
                    ws2.write(0,c,col,f_hdr)
                    ws2.set_column(c,c,w)

                for i, row in result_df.iterrows():
                    r_num = i + 1
                    ws2.set_row(r_num, 15)
                    sfmt  = f_ok if row["estado"]=="OK" else (f_warn if row["estado"]=="Aviso" else f_err)
                    scfmt = f_sc_ok if row["score"]>=90 else (f_sc_w if row["score"]>=60 else f_sc_e)
                    ufmt  = f_url_fix if row["autocorregible"]=="Sí" else f_url

                    ws2.write(r_num, 0,  row["estado"],        sfmt)
                    ws2.write(r_num, 1,  row["score"],         scfmt)
                    ws2.write(r_num, 2,  row["url_original"],  f_url)
                    ws2.write(r_num, 3,  row["url_corregida"], ufmt)
                    ws2.write(r_num, 4,  row["autocorregible"],f_fix_lbl if row["autocorregible"]=="Sí" else f_cell)
                    ws2.write(r_num, 5,  row["correcciones"],  f_cell)
                    ws2.write(r_num, 6,  row["errores"],       f_cell)
                    ws2.write(r_num, 7,  row["avisos"],        f_cell)
                    ws2.write(r_num, 8,  row["utm_source"],    f_mono)
                    ws2.write(r_num, 9,  row["utm_medium"],    f_mono)
                    ws2.write(r_num, 10, row["utm_campaign"],  f_mono)
                    ws2.write(r_num, 11, row["utm_content"],   f_mono)
                    ws2.write(r_num, 12, row["utm_term"],      f_mono)

                # ── Hoja 3: Solo errores ───────────────────────────
                ws3 = wb.add_worksheet("Errores")
                ws3.set_tab_color("#E11D48")
                ws3.freeze_panes(1, 0)
                ws3.set_row(0, 26)
                for c,(col,w) in enumerate(zip(cols2,widths2)):
                    ws3.write(0,c,col,f_hdr)
                    ws3.set_column(c,c,w)

                err_rows = result_df[result_df["estado"]=="Error"]
                for i,(_, row) in enumerate(err_rows.iterrows()):
                    ws3.set_row(i+1,15)
                    scfmt = f_sc_ok if row["score"]>=90 else (f_sc_w if row["score"]>=60 else f_sc_e)
                    ufmt  = f_url_fix if row["autocorregible"]=="Sí" else f_url
                    ws3.write(i+1,0,  row["estado"],        f_err)
                    ws3.write(i+1,1,  row["score"],         scfmt)
                    ws3.write(i+1,2,  row["url_original"],  f_url)
                    ws3.write(i+1,3,  row["url_corregida"], ufmt)
                    ws3.write(i+1,4,  row["autocorregible"],f_fix_lbl if row["autocorregible"]=="Sí" else f_cell)
                    ws3.write(i+1,5,  row["correcciones"],  f_cell)
                    ws3.write(i+1,6,  row["errores"],       f_cell)
                    ws3.write(i+1,7,  row["avisos"],        f_cell)
                    ws3.write(i+1,8,  row["utm_source"],    f_mono)
                    ws3.write(i+1,9,  row["utm_medium"],    f_mono)
                    ws3.write(i+1,10, row["utm_campaign"],  f_mono)
                    ws3.write(i+1,11, row["utm_content"],   f_mono)
                    ws3.write(i+1,12, row["utm_term"],      f_mono)

                # ── Hoja 4: URLs corregidas listas para usar ───────
                ws4 = wb.add_worksheet("URLs corregidas")
                ws4.set_tab_color("#16a34a")
                ws4.freeze_panes(1, 0)
                ws4.set_row(0, 26)
                cols4   = ["url_corregida","autocorregible","estado_original","correcciones","utm_source","utm_medium","utm_campaign"]
                widths4 = [70,14,12,50,18,14,26]
                labels4 = ["URL corregida","Autocorregible","Estado original","Correcciones aplicadas","utm_source","utm_medium","utm_campaign"]
                for c,(col,w) in enumerate(zip(labels4,widths4)):
                    ws4.write(0,c,col,f_hdr)
                    ws4.set_column(c,c,w)

                for i,(_, row) in enumerate(result_df.iterrows()):
                    ws4.set_row(i+1,15)
                    ufmt = f_url_fix if row["autocorregible"]=="Sí" else f_url
                    sfmt = f_ok if row["estado"]=="OK" else (f_warn if row["estado"]=="Aviso" else f_err)
                    ws4.write(i+1,0, row["url_corregida"],  ufmt)
                    ws4.write(i+1,1, row["autocorregible"], f_fix_lbl if row["autocorregible"]=="Sí" else f_cell)
                    ws4.write(i+1,2, row["estado"],         sfmt)
                    ws4.write(i+1,3, row["correcciones"],   f_cell)
                    ws4.write(i+1,4, row["utm_source"],     f_mono)
                    ws4.write(i+1,5, row["utm_medium"],     f_mono)
                    ws4.write(i+1,6, row["utm_campaign"],   f_mono)

                wb.close()
                buf.seek(0)
                return buf

            excel_buf = build_audit_excel(result_df, avg_score, ok, ko, avisos, n_fixed, total, all_errors)
            fname     = f"auditoria_utm_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"

            c1, c2 = st.columns(2)
            with c1:
                st.download_button(
                    "Descargar auditoría Excel",
                    data=excel_buf,
                    file_name=fname,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    type="primary"
                )
            with c2:
                st.download_button(
                    "Descargar CSV",
                    data=result_df.to_csv(index=False).encode(),
                    file_name=f"auditoria_utm_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            st.caption("El Excel incluye 4 hojas: Resumen ejecutivo · Auditoría completa · Solo errores · URLs corregidas listas para usar.")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
