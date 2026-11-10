import streamlit as st

from tools.tonelaje_palas import mostrar_tonelaje_palas
from tools.mallas_xblast import mostrar_mallas_xblast


# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

st.set_page_config(
    page_title="MEL Data Processing Tools",
    page_icon="⚒️",
    layout="wide"
)


# =========================================================
# FUNCIÓN VOLVER AL MENÚ
# =========================================================

def volver_menu():
    st.session_state.herramienta_seleccionada = (
        "Seleccione una herramienta..."
    )


# =========================================================
# BOTÓN VOLVER AL MENÚ
# =========================================================

if (
    "herramienta_seleccionada" in st.session_state
    and
    st.session_state.herramienta_seleccionada
    != "Seleccione una herramienta..."
):
    st.button(
        "← Back to menu",
        type="secondary",
        on_click=volver_menu
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
# SELECTOR DE ÁREA
# =========================================================

def cambiar_area():
    st.session_state.herramienta_seleccionada = (
        "Seleccione una herramienta..."
    )

area = st.selectbox(
    "Área",
    [
        "Seleccione un área...",
        "QAQC",
        "Secuencia",
        "Diseño",
        "X-Energy"
    ],
    key="area_seleccionada",
    on_change=cambiar_area
)


# =========================================================
# HERRAMIENTAS DISPONIBLES POR ÁREA
# =========================================================

herramientas_por_area = {
    "Seleccione un área...": [],
    "QAQC": [
        "TONELAJE_PALAS",
        "MALLAS X-BLAST"
    ],
    "Secuencia": [],
    "Diseño": [],
    "X-Energy": []
}


# =========================================================
# SELECTOR DE HERRAMIENTAS
# =========================================================

st.markdown("### Seleccionar herramienta de procesamiento")

opciones_herramientas = [
    "Seleccione una herramienta..."
] + herramientas_por_area.get(area, [])

herramienta = st.selectbox(
    "Herramienta",
    opciones_herramientas,
    key="herramienta_seleccionada"
)


# =========================================================
# EJECUCIÓN DE HERRAMIENTAS
# =========================================================

if herramienta == "TONELAJE_PALAS":
    mostrar_tonelaje_palas()

elif herramienta == "MALLAS X-BLAST":
    mostrar_mallas_xblast()
