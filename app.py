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
# SELECTOR DE HERRAMIENTAS
# =========================================================

st.markdown("### Seleccionar herramienta de procesamiento")

herramienta = st.selectbox(
    "Herramienta",
    [
        "Seleccione una herramienta...",
        "TONELAJE_PALAS"
    ]
)


# =========================================================
# EJECUCIÓN DE HERRAMIENTAS
# =========================================================

if herramienta == "TONELAJE_PALAS":

    st.divider()

    mostrar_tonelaje_palas()
