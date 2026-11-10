import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(
    page_title="MEL Data Processing Tools",
    page_icon="⚒️",
    layout="wide"
)

col_izq, col_centro, col_der = st.columns([1, 8, 1])

with col_centro:
    st.image("assets/banner.jpg", use_container_width=True)

st.markdown("### Seleccionar herramienta de procesamiento")

herramienta = st.selectbox(
    "Herramienta",
    [
        "Seleccione una herramienta...",
        "TONELAJE_PALAS"
    ]
)

st.divider()

st.write(
    "Carga el archivo base MD, selecciona un rango de fechas y obtén "
    "automáticamente el tonelaje diario de todas las palas."
)

st.divider()

# =========================================================
# CARGA DEL ARCHIVO
# =========================================================

archivo = st.file_uploader(
    "1. Cargar archivo Excel base",
    type=["xlsx", "xls"]
)

if archivo is not None:

    try:
        # Leer hoja Base
        df = pd.read_excel(
            archivo,
            sheet_name="Base",
            engine="openpyxl"
        )

        # Limpiar nombres de columnas
        df.columns = df.columns.astype(str).str.strip()

        # Columnas requeridas
        columnas_requeridas = [
            "Equipo",
            "Fecha",
            "Descargas (ton)"
        ]

        faltantes = [
            col for col in columnas_requeridas
            if col not in df.columns
        ]

        if faltantes:

            st.error(
                "El archivo no contiene las columnas necesarias: "
                + ", ".join(faltantes)
            )

        else:

            # =================================================
            # PREPARACIÓN DE LOS DATOS
            # =================================================

            datos = df[
                ["Equipo", "Fecha", "Descargas (ton)"]
            ].copy()

            # Convertir fecha
            datos["Fecha"] = pd.to_datetime(
                datos["Fecha"],
                errors="coerce"
            )

            # Convertir tonelaje a número
            datos["Descargas (ton)"] = pd.to_numeric(
                datos["Descargas (ton)"],
                errors="coerce"
            )

            # Eliminar registros inválidos
            datos = datos.dropna(
                subset=[
                    "Equipo",
                    "Fecha",
                    "Descargas (ton)"
                ]
            )

            # =================================================
            # FILTRAR SOLO PALAS
            # =================================================

            datos["Equipo"] = (
                datos["Equipo"]
                .astype(str)
                .str.strip()
            )

            palas = datos[
                datos["Equipo"]
                .str.contains(
                    "Pala",
                    case=False,
                    na=False
                )
            ].copy()

            if palas.empty:

                st.warning(
                    "No se encontraron equipos identificados como Pala."
                )

            else:

                fecha_min = palas["Fecha"].min().date()
                fecha_max = palas["Fecha"].max().date()

                st.success(
                    f"Archivo cargado correctamente. "
                    f"Período disponible: "
                    f"{fecha_min.strftime('%d-%m-%Y')} al "
                    f"{fecha_max.strftime('%d-%m-%Y')}."
                )

                # =================================================
                # SELECCIÓN DE FECHAS
                # =================================================

                st.subheader("2. Seleccionar período")

                col1, col2 = st.columns(2)

                with col1:

                    fecha_inicio = st.date_input(
                        "Fecha inicial",
                        value=fecha_min,
                        min_value=fecha_min,
                        max_value=fecha_max
                    )

                with col2:

                    fecha_fin = st.date_input(
                        "Fecha final",
                        value=fecha_max,
                        min_value=fecha_min,
                        max_value=fecha_max
                    )

                # =================================================
                # PROCESAMIENTO
                # =================================================

                if fecha_inicio > fecha_fin:

                    st.error(
                        "La fecha inicial no puede ser posterior "
                        "a la fecha final."
                    )

                else:

                    inicio = pd.Timestamp(fecha_inicio)
                    fin = pd.Timestamp(fecha_fin)

                    filtrado = palas[
                        (palas["Fecha"] >= inicio)
                        &
                        (palas["Fecha"] <= fin)
                    ].copy()

                    if filtrado.empty:

                        st.warning(
                            "No existen registros de palas "
                            "para el período seleccionado."
                        )

                    else:

                        # Agrupar tonelaje pala + fecha
                        agrupado = (
                            filtrado
                            .groupby(
                                ["Equipo", "Fecha"],
                                as_index=False
                            )["Descargas (ton)"]
                            .sum()
                        )

                        # Crear matriz pala x fecha
                        tabla = agrupado.pivot_table(
                            index="Equipo",
                            columns="Fecha",
                            values="Descargas (ton)",
                            aggfunc="sum",
                            fill_value=0
                        )

                        # Ordenar fechas
                        tabla = tabla.sort_index(axis=1)

                        # Total por pala
                        tabla["Total período"] = tabla.sum(axis=1)

                        # Total diario
                        fila_total = pd.DataFrame(
                            [tabla.sum(axis=0)],
                            index=["TOTAL"]
                        )

                        tabla = pd.concat(
                            [tabla, fila_total]
                        )

                        # =================================================
                        # INDICADORES
                        # =================================================

                        st.divider()

                        st.subheader("3. Resultado")

                        c1, c2, c3, c4 = st.columns(4)

                        tonelaje_total = filtrado[
                            "Descargas (ton)"
                        ].sum()

                        cantidad_palas = (
                            filtrado["Equipo"]
                            .nunique()
                        )

                        cantidad_dias = (
                            filtrado["Fecha"]
                            .dt.date
                            .nunique()
                        )

                        registros = len(filtrado)

                        c1.metric(
                            "Tonelaje total",
                            f"{tonelaje_total:,.0f} ton"
                        )

                        c2.metric(
                            "Palas",
                            cantidad_palas
                        )

                        c3.metric(
                            "Días",
                            cantidad_dias
                        )

                        c4.metric(
                            "Registros",
                            f"{registros:,}"
                        )

                        # =================================================
                        # FORMATO DE LA TABLA
                        # =================================================

                        tabla_visual = tabla.copy()

                        nombres_columnas = []

                        for columna in tabla_visual.columns:

                            if isinstance(
                                columna,
                                pd.Timestamp
                            ):

                                nombres_columnas.append(
                                    columna.strftime(
                                        "%d-%m-%Y"
                                    )
                                )

                            else:

                                nombres_columnas.append(
                                    columna
                                )

                        tabla_visual.columns = nombres_columnas

                        st.dataframe(
                            tabla_visual.style.format(
                                "{:,.0f}"
                            ),
                            use_container_width=True
                        )

                        # =================================================
                        # EXPORTAR A EXCEL
                        # =================================================

                        output = BytesIO()

                        with pd.ExcelWriter(
                            output,
                            engine="openpyxl"
                        ) as writer:

                            tabla_visual.to_excel(
                                writer,
                                sheet_name="Tonelajes"
                            )

                        output.seek(0)

                        nombre_archivo = (
                            "Tonelajes_Palas_"
                            + fecha_inicio.strftime("%Y%m%d")
                            + "_"
                            + fecha_fin.strftime("%Y%m%d")
                            + ".xlsx"
                        )

                        st.download_button(
                            label="⬇ Descargar resultado en Excel",
                            data=output,
                            file_name=nombre_archivo,
                            mime=(
                                "application/vnd.openxmlformats-"
                                "officedocument.spreadsheetml.sheet"
                            )
                        )

    except ValueError:

        st.error(
            "No se encontró la hoja 'Base' en el archivo Excel."
        )

    except Exception as error:

        st.error(
            f"Ocurrió un error al procesar el archivo: {error}"
        )

else:

    st.info(
        "Carga un archivo Excel para comenzar."
    )
