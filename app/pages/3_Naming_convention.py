import streamlit as st
from streamlit_sortables import sort_items

def drag_section(label, key, default_items):
    st.subheader(label)

    # Asegurar tipo correcto en session_state
    if key not in st.session_state or not isinstance(st.session_state[key], list):
        st.session_state[key] = default_items.copy()

    # Mostrar los campos ordenables
    new_order = sort_items(
        st.session_state[key],
        direction="horizontal",
        key=key
    )

    # Guardar nuevo orden en session_state
    st.session_state[key] = new_order

    # Mostrar longitud de cada campo
    st.write("### Longitud de cada campo:")
    for item in new_order:
        st.write(f"`{item}` → {len(item)} caracteres")

    # Botón para crear nombre final
    if st.button("Crear", key=f"crear_{key}"):
        result = "_".join(new_order)
        st.success(f"Nombre generado: `{result}` ({len(result)} caracteres)")

# USO DEL COMPONENTE
drag_section("✳️ utm_campaign", "campaign_order", ["producto", "audiencia", "fecha", "region"])
