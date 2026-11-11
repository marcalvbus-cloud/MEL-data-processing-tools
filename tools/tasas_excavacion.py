import streamlit as st
import pandas as pd


def detectar_formato(archivo):
    excel = pd.ExcelFile(archivo)

    for hoja in excel.sheet_names:
        df = pd.read_excel(archivo, sheet_name=hoja)

        columnas = set(df.columns.astype(str))

        # Formato histórico MEL
        columnas_historicas = {
            "FECHA",
            "PALA",
            "TONE",
            "RENDNUEV",
            "TASAEXCA",
            "ERN",
            "ET"
        }

        if columnas_historicas.issubset(columnas):
            return "Histórico MEL", hoja, df

        # Formato nuevas palas
        columnas_nuevas = {
            "Fecha1",
            "Pala1",
            "Toneladas",
            "RendNuevo",
            "TasaExc",
            "ER"
        }

        if columnas_nuevas.issubset(columnas):
            return "Nuevas palas", hoja, df

    return "No reconocido", None, None


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

        st.subheader("Diagnóstico de archivos")

        for archivo in archivos:

            try:
                formato, hoja, df = detectar_formato(archivo)

                st.write(f"**Archivo:** {archivo.name}")

                if formato == "No reconocido":
                    st.warning(
                        "No se encontró una estructura de indicadores reconocida."
                    )

                else:
                    st.success(f"Formato detectado: {formato}")
                    st.write(f"Hoja detectada: {hoja}")
                    st.write(f"Registros encontrados: {len(df):,}")

                st.divider()

            except Exception as e:
                st.error(
                    f"No fue posible procesar {archivo.name}: {e}"
                )
