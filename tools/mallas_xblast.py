import io
import re
import pandas as pd
import streamlit as st


# =========================================================
# CONVERSIÓN DE PULGADAS A MILÍMETROS
# =========================================================

def convertir_pulgadas_a_mm(valor):
    if pd.isna(valor):
        return None

    texto = str(valor).strip()

    if not texto:
        return None

    texto = re.sub(r"\s+", " ", texto)

    try:
        pulgadas = float(texto.replace(",", "."))
        return round(pulgadas * 25.4)
    except ValueError:
        pass

    try:
        partes = texto.split()

        pulgadas = float(
            partes[0].replace(",", ".")
        )

        if len(partes) > 1:
            fraccion = partes[1]

            if "/" in fraccion:
                numerador, denominador = fraccion.split("/", 1)

                numerador = float(numerador)
                denominador = float(denominador)

                if denominador != 0:
                    pulgadas += numerador / denominador

        return round(pulgadas * 25.4)

    except (ValueError, IndexError):
        return None


# =========================================================
# LECTURA DEL CSV
# =========================================================

def leer_csv_xblast(archivo):
    contenido = archivo.getvalue()

    codificaciones = [
        "utf-8-sig",
        "utf-8",
        "cp1252",
        "latin-1"
    ]

    ultimo_error = None

    for codificacion in codificaciones:
        try:
            texto = contenido.decode(codificacion)

            df = pd.read_csv(
                io.StringIO(texto),
                sep=None,
                engine="python",
                dtype=str,
                skipinitialspace=True
            )

            return df

        except Exception as error:
            ultimo_error = error

    raise ValueError(
        f"No fue posible leer el CSV: {ultimo_error}"
    )


# =========================================================
# BUSCAR COLUMNAS
# =========================================================

def normalizar_nombre(texto):
    return (
        str(texto)
        .strip()
        .lower()
        .replace("º", "°")
    )


def buscar_columna(columnas, alternativas):
    mapa = {
        normalizar_nombre(columna): columna
        for columna in columnas
    }

    for alternativa in alternativas:
        clave = normalizar_nombre(alternativa)

        if clave in mapa:
            return mapa[clave]

    return None


# =========================================================
# PROCESAMIENTO X-BLAST
# =========================================================

def procesar_malla_xblast(df):
    df = df.copy()

    df.columns = [
        str(columna).strip()
        for columna in df.columns
    ]

    col_pozo = buscar_columna(
        df.columns,
        [
            "N°POZO",
            "NºPOZO",
            "NРPOZO",
            "NPOZO",
            "POZO"
        ]
    )

    col_este = buscar_columna(
        df.columns,
        ["COORDENADA ESTE"]
    )

    col_norte = buscar_columna(
        df.columns,
        ["COORDENADA NORTE"]
    )

    col_collar = buscar_columna(
        df.columns,
        ["Collar Z"]
    )

    col_length = buscar_columna(
        df.columns,
        ["Length"]
    )

    col_blast = buscar_columna(
        df.columns,
        ["Blast Name"]
    )

    col_subdrill = buscar_columna(
        df.columns,
        ["Subdrill Length"]
    )

    col_burden = buscar_columna(
        df.columns,
        ["Burden"]
    )

    col_spacing = buscar_columna(
        df.columns,
        ["Spacing"]
    )

    col_drill = buscar_columna(
        df.columns,
        ["Drill Rig"]
    )

    requeridas = {
        "N°POZO": col_pozo,
        "COORDENADA ESTE": col_este,
        "COORDENADA NORTE": col_norte,
        "Collar Z": col_collar,
        "Length": col_length,
        "Blast Name": col_blast,
        "Subdrill Length": col_subdrill,
        "Burden": col_burden,
        "Spacing": col_spacing,
        "Drill Rig": col_drill
    }

    faltantes = [
        nombre
        for nombre, columna in requeridas.items()
        if columna is None
    ]

    if faltantes:
        raise ValueError(
            "Faltan columnas requeridas: "
            + ", ".join(faltantes)
        )

    filas_originales = len(df)

    # -----------------------------------------------------
    # ELIMINAR ENCABEZADOS REPETIDOS Y FILAS VACÍAS
    # -----------------------------------------------------

    este_numerico = pd.to_numeric(
        df[col_este],
        errors="coerce"
    )

    df = df[
        este_numerico.notna()
    ].copy()

    filas_eliminadas = filas_originales - len(df)

    # -----------------------------------------------------
    # CREAR ID POZO
    # Blast Name + "_" + N°POZO
    # -----------------------------------------------------

    blast = (
        df[col_blast]
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )

    pozo = (
        df[col_pozo]
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )

    id_pozo = blast + "_" + pozo

    # -----------------------------------------------------
    # DRILL RIG PULGADAS -> MM
    # -----------------------------------------------------

    drill_mm = (
        df[col_drill]
        .apply(convertir_pulgadas_a_mm)
        .astype("Int64")
    )

    # -----------------------------------------------------
    # TABLA FINAL
    # -----------------------------------------------------

    resultado = pd.DataFrame({
        "ID POZO": id_pozo,
        "COORDENADA ESTE": pd.to_numeric(
            df[col_este],
            errors="coerce"
        ),
        "COORDENADA NORTE": pd.to_numeric(
            df[col_norte],
            errors="coerce"
        ),
        "Collar Z": pd.to_numeric(
            df[col_collar],
            errors="coerce"
        ),
        "Length": pd.to_numeric(
            df[col_length],
            errors="coerce"
        ),
        "Subdrill Length": pd.to_numeric(
            df[col_subdrill],
            errors="coerce"
        ),
        "Burden": pd.to_numeric(
            df[col_burden],
            errors="coerce"
        ),
        "Spacing": pd.to_numeric(
            df[col_spacing],
            errors="coerce"
        ),
        "Drill Rig (mm)": drill_mm,
        "Taco": "",
        "Grupo": ""
    })

    resultado = resultado.reset_index(
        drop=True
    )

    return resultado, filas_eliminadas


# =========================================================
# GENERAR EXCEL
# =========================================================

def generar_excel(resultado):
    salida = io.BytesIO()

    with pd.ExcelWriter(
        salida,
        engine="openpyxl"
    ) as writer:

        resultado.to_excel(
            writer,
            index=False,
            sheet_name="Malla Procesada"
        )

        hoja = writer.sheets[
            "Malla Procesada"
        ]

        for columna in hoja.columns:
            largo = max(
                len(str(celda.value))
                if celda.value is not None
                else 0
                for celda in columna
            )

            ancho = min(
                largo + 2,
                30
            )

            hoja.column_dimensions[
                columna[0].column_letter
            ].width = ancho

    salida.seek(0)

    return salida


# =========================================================
# INTERFAZ STREAMLIT
# =========================================================

def mostrar_mallas_xblast():
    st.subheader(
        "MALLAS X-BLAST | Procesamiento de mallas"
    )

    st.write(
        "Carga un archivo CSV exportado desde X-BLAST. "
        "La herramienta limpia los registros, crea el ID POZO, "
        "convierte el diámetro de perforación a milímetros "
        "y genera un archivo Excel procesado."
    )

    st.divider()

    archivo = st.file_uploader(
        "1. Cargar archivo CSV de X-BLAST",
        type=["csv"],
        key="mallas_xblast_uploader"
    )

    if archivo is None:
        st.info(
            "Carga un archivo CSV para comenzar."
        )
        return

    try:
        df = leer_csv_xblast(
            archivo
        )

        resultado, filas_eliminadas = (
            procesar_malla_xblast(df)
        )

        if resultado.empty:
            st.warning(
                "No se encontraron registros válidos."
            )
            return

        st.success(
            "Archivo procesado correctamente."
        )

        # -------------------------------------------------
        # INDICADORES
        # -------------------------------------------------

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Pozos procesados",
            f"{len(resultado):,}"
        )

        c2.metric(
            "Filas eliminadas",
            f"{filas_eliminadas:,}"
        )

        cantidad_mallas = (
            resultado["ID POZO"]
            .str.rsplit("_", n=1)
            .str[0]
            .nunique()
        )

        c3.metric(
            "Mallas detectadas",
            cantidad_mallas
        )

        c4.metric(
            "Columnas finales",
            len(resultado.columns)
        )

        # -------------------------------------------------
        # VISTA PREVIA
        # -------------------------------------------------

        st.subheader(
            "2. Vista previa"
        )

        st.dataframe(
            resultado,
            use_container_width=True,
            hide_index=True
        )

        # -------------------------------------------------
        # DESCARGA
        # -------------------------------------------------

        archivo_csv = resultado.to_csv(
            index=False,
            encoding="utf-8-sig"
        ).encode("utf-8-sig")

        nombre_original = archivo.name.rsplit(
            ".",
            1
        )[0]

        nombre_salida = (
            f"{nombre_original}_PROCESADO.csv"
        )

        st.download_button(
            "⬇ Descargar malla procesada CSV",
            data=archivo_csv,
            file_name=nombre_salida,
            mime="text/csv",
            type="primary"
        )

    except Exception as error:
        st.error(
            f"No fue posible procesar el archivo: {error}"
        )
