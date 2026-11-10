import streamlit as st

from tools.tonelaje_palas import mostrar_tonelaje_palas


# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

st.set_page_config(
    page_title="MEL Data Processing Tools",
    page_icon="⚒️",
    layout="wide"
)


# =========================================================
# PORTADA
# =========================================================

col_izq, col_centro, col_der = st.columns([1, 8, 1])

with col_centro:
    st.image(
        "assets/banner.jpg",
        use_container_width=True
    )


# =========================================================
# ESTADO DEL SELECTOR
# =========================================================

if "herramienta_seleccionada" not in st.session_state:
    st.session_state.herramienta_seleccionada = (
        "Seleccione una herramienta..."
    )


# =========================================================
# SELECTOR DE HERRAMIENTAS
# =========================================================

st.markdown("### Seleccionar herramienta de procesamiento")

herramienta = st.selectbox(
    "Herramienta",
    [
        "Seleccione una herramienta...",
        "TONELAJE_PALAS"
    ],
    key="herramienta_seleccionada"
)


# =========================================================
# EJECUCIÓN DE HERRAMIENTAS
# =========================================================

if herramienta != "Seleccione una herramienta...":

    st.divider()

    # Botón para regresar al menú
    if st.button(
        "← Back to menu",
        type="secondary"
    ):
        st.session_state.herramienta_seleccionada = (
            "Seleccione una herramienta..."
        )
        st.rerun()

    if herramienta == "TONELAJE_PALAS":
        mostrar_tonelaje_palas()
