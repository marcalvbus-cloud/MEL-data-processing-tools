import streamlit as st
import pandas as pd
import io


def mostrar():
    st.header("Procesamiento de Tasas de Excavación")

    st.write(
        "Herramienta para procesar y analizar los archivos de indicadores "
        "de palas utilizados en el modelo X-Energy."
    )

    archivos = st.file_uploader(
        "Cargar archivos de indicadores de palas",
        type=["xlsx", "xlsm"],
        accept_multiple_files=True
    )

    if archivos:
        st.success(f"Archivos cargados: {len(archivos)}")
