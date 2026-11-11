import streamlit as st
import pandas as pd


def detectar_hojas(archivo):
    excel = pd.ExcelFile(archivo)
    hojas_detectadas = []

    columnas_historicas = {
        "FECHA",
        "PALA",
        "TONE",
        "RENDNUEV",
        "TASAEXCA",
        "ERN",
        "ET"
    }

    columnas_nuevas = {
        "Fecha1",
        "Pala1",
        "Toneladas",
        "RendNuevo",
        "TasaExc",
        "ER"
    }

    for hoja in excel.sheet_names:

        try:
            df = pd.read_excel(archivo, sheet_name=hoja)
            columnas = set(df.columns.astype(str))

            if columnas_historicas.issubset(columnas):

                fechas = pd.to_datetime(
                    df["FECHA"],
                    errors="coerce"
                )

                hojas_detectadas.append({
                    "Hoja": hoja,
                    "Formato": "Histórico MEL",
                    "Fecha inicial": fechas.min(),
                    "Fecha final": fechas.max(),
                    "Registros": len(df)
                })

            elif columnas_nuevas.issubset(columnas):

                fechas = pd.to_datetime(
                    df["Fecha1"],
                    errors="coerce"
                )

                hojas_detectadas.append({
                    "Hoja": hoja,
                    "Formato": "Nuevas palas",
                    "Fecha inicial": fechas.min(),
                    "Fecha final": fechas.max(),
                    "Registros": len(df)
                })

        except Exception:
            continue

    return hojas_detectadas


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
                hojas = detectar_hojas(archivo)

                st.write(f"**Archivo:** {archivo.name}")

                if not hojas:
                    st.warning(
                        "No se encontraron hojas con una estructura "
                        "de indicadores reconocida."
                    )

                else:
                    st.success(
                        f"Hojas de indicadores detectadas: {len(hojas)}"
                    )

                    resumen = pd.DataFrame(hojas)

                    resumen["Fecha inicial"] = (
                        resumen["Fecha inicial"]
                        .dt.strftime("%d-%m-%Y")
                    )

                    resumen["Fecha final"] = (
                        resumen["Fecha final"]
                        .dt.strftime("%d-%m-%Y")
                    )

                    st.dataframe(
                        resumen,
                        use_container_width=True,
                        hide_index=True
                    )

                st.divider()

            except Exception as e:
                st.error(
                    f"No fue posible procesar {archivo.name}: {e}"
                )
