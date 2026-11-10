import io
import re

import pandas as pd
import streamlit as st


def convertir_pulgadas_a_mm(valor):
    """
    Convierte valores como:
    6 1/2  -> 165 mm
    10 5/8 -> 270 mm
    6.5    -> 165 mm
    """

    if pd.isna(valor):
        return None

    texto = str(valor).strip()

    if not texto:
        return None

    # Normalizar espacios
    texto = re.sub(r"\s+", " ", texto)

    try:
        # Valor decimal directo
        pulgadas = float(texto.replace(",", "."))
        return round(pulgadas * 25.4)

    except ValueError:
        pass

    pulgadas = 0.0
    partes = texto.split(" ")

    try:
        # Parte entera
        pulgadas = float(partes[0].replace(",", "."))

# Parte fraccionaria, por ejemplo 1/2 o 5/8
     if len(partes) > 1 and "/" in partes:
          numerador, denominador = partes[1].split("/", 1)
            numerador = float(numerador)
            denominador = float(denominador)

            if denominador != 0:
                pulgadas += numerador / denominador
        return round(pulgadas * 25.4)

    except (ValueError, IndexError):
        return None


def leer_csv_xblast(archivo):
    """
    Lee el CSV intentando distintas codificaciones y detectando
    automáticamente el separador.
    """

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

            return pd.read_csv(
                io.StringIO(texto),
                sep=None,
                engine="python",
                dtype=str,
                skipinitialspace=True
            )

        except Exception as error:
            ultimo_error = error

    raise ValueError(
        f"No fue posible leer el archivo CSV: {ultimo_error}"
    )


def buscar_columna(columnas, alternativas):
    """
    Busca una columna aunque el encabezado tenga pequeñas
    variaciones de codificación, mayúsculas o espacios.
    """

    columnas_limpias = {
        str(columna).strip().lower(): columna
        for columna in columnas
    }

    for alternativa in alternativas:

        alternativa_limpia = alternativa.strip().lower()

        if alternativa_limpia in columnas_limpias:
            return columnas_limpias[alternativa_limpia]

    return None


def procesar_malla_xblast(df):
    """
    Replica el procesamiento de la macro VBA usando nombres
    de columnas, en vez de posiciones fijas.
    """

    df = df.copy()

    # Limpiar nombres de columnas
    df.columns = [
        str(columna).strip()
        for columna in df.columns
    ]

    # Identificar columnas, incluyendo posibles problemas
    # de codificación en N°POZO
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
        [
            "COORDENADA ESTE",
            "Coordenada Este"
        ]
    )

    col_norte = buscar_columna(
        df.columns,
        [
            "COORDENADA NORTE",
            "Coordenada Norte"
        ]
    )

    col_collar = buscar_columna(
        df.columns,
        ["Collar Z"]
    )

    col_length = buscar_columna(
        df.columns,
        ["Length"]
    )

    col_layer = buscar_columna(
        df.columns,
        ["Layer Name"]
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

    col_drill_rig = buscar_columna(
        df.columns,
        ["Drill Rig"]
    )

    columnas_obligatorias = {
        "N°POZO": col_pozo,
        "COORDENADA ESTE": col_este,
        "COORDENADA NORTE": col_norte,
        "Collar Z": col_collar,
        "Length": col_length,
        "Blast Name": col_blast,
        "Subdrill Length": col_subdrill,
        "Burden": col_burden,
        "Spacing": col_spacing,
        "Drill Rig": col_drill_rig
    }

    faltantes = [
        nombre
        for nombre, columna in columnas_obligatorias.items()
        if columna is None
    ]

    if faltantes:

        raise ValueError(
            "Faltan las siguientes columnas requeridas: "
            + ", ".join(faltantes)
        )

    filas_originales = len(df)

    # Convertir Coordenada Este a número.
    # Esto permite eliminar:
    # - encabezados repetidos
    # - filas vacías
    # - filas que no contienen datos reales
    coordenada_este_numerica = pd.to_numeric(
        df[col_este],
        errors="coerce"
    )

    df = df[
        coordenada_este_numerica.notna()
    ].copy()

    filas_eliminadas = filas_originales - len(df)

    # Limpiar Blast Name y número de pozo
    blast_name = (
        df[col_blast]
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )

    numero_pozo = (
        df[col_pozo]
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )

    # Crear ID con guion bajo
    id_pozo = blast_name + "_" + numero_pozo

    # Conversión de pulgadas a milímetros
    drill_rig_mm = (
        df[col_drill_rig]
        .apply(convertir_pulgadas_a_mm)
        .astype("Int64")
    )

    # Construir resultado final en el orden requerido
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
        "Drill Rig (mm)": drill_rig_mm,
        "Taco": "",
        "Grupo": ""
    })

    # Eliminar registros sin identificador válido
    resultado = resultado[
        resultado["ID POZO"].notna()
        &
        ~resultado["ID POZO"].isin(
            ["nan_nan", "_", "None_None"]
        )
    ].copy()

    resultado.reset_index(
        drop=True,
        inplace=True
    )

    return resultado, filas_eliminadas


def generar_excel(resultado):
    """
    Genera el archivo Excel descargable.
    """

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

        hoja = writer.sheets["Malla Procesada"]

        # Ajustar anchos de columnas
        for columna in hoja.columns:

            largo_maximo = max(
                len(str(celda.value))
                if celda.value is not None
                else 0
                for celda in columna
            )

            ancho = min(
                largo_maximo + 2,
                30
            )

            hoja.column_dimensions[
                columna[0].column_letter
            ].width = ancho

    salida.seek(0)

    return salida


def mostrar_mallas_xblast():

    st.subheader(
        "MALLAS X-BLAST | Procesamiento de planos de perforación"
    )

    st.write(
        "Carga un archivo CSV exportado desde X-BLAST para limpiar "
        "encabezados repetidos, crear el ID único de cada pozo, "
        "convertir el diámetro de pulgadas a milímetros y generar "
        "una planilla Excel lista para trabajar."
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

        df_original = leer_csv_xblast(
            archivo
        )

        resultado, filas_eliminadas = procesar_malla_xblast(
            df_original
        )

        if resultado.empty:

            st.warning(
                "El archivo no contiene registros válidos "
                "después del procesamiento."
            )

            return

        st.success(
            "Archivo procesado correctamente."
        )

        # Indicadores
        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Pozos procesados",
            f"{len(resultado):,}"
        )

        c2.metric(
            "Encabezados/filas eliminadas",
            f"{filas_eliminadas:,}"
        )

        c3.metric(
            "Mallas detectadas",
            resultado["ID POZO"]
            .str.split("_")
            .str[0]
            .nunique()
        )

        c4.metric(
            "Columnas finales",
            len(resultado.columns)
        )

        st.subheader(
            "2. Vista previa del resultado"
        )

        st.dataframe(
            resultado,
            use_container_width=True,
            hide_index=True
        )

        # Crear Excel
        archivo_excel = generar_excel(
            resultado
        )

        nombre_original = archivo.name.rsplit(
            ".",
            1
        )[0]

        nombre_salida = (
            f"{nombre_original}_PROCESADO.xlsx"
        )

        st.download_button(
            label="⬇ Descargar malla procesada en Excel",
            data=archivo_excel,
            file_name=nombre_salida,
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            type="primary"
        )

    except Exception as error:

        st.error(
            f"No fue posible procesar el archivo: {error}"
        )
