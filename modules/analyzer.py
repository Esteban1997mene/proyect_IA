
# ============================================================
# INTI PROJECTS ENTERPRISE
# INTILED SAS BIC
#
# Archivo: modules/analyzer.py
# Analizador documental por convocatoria
# ============================================================

import hashlib
import io
import re
from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

from services.opportunity_workspace import (
    iniciar_workspace,
    listar_oportunidades,
    oportunidad_activa,
    activar_oportunidad,
    sincronizar_legacy,
    guardar_datos_modulo,
    obtener_datos_modulo,
    registrar_evento,
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

MODULO = "analizador_documental"

ZONA = ZoneInfo("America/Bogota")

MAX_ARCHIVO_MB = 15
MAX_PAGINAS_PDF = 80
MAX_CARACTERES = 100000

TIPOS_DOCUMENTO = [
    "Pliego de condiciones",
    "Términos de referencia",
    "Anexo técnico",
    "Ficha técnica",
    "Adenda",
    "Documento jurídico",
    "Documento financiero",
    "Otro documento",
]

ESTADOS_REVISION = [
    "Pendiente de verificar",
    "Cumple - verificado",
    "No cumple - verificado",
    "No aplica",
]

CATEGORIAS_REVISION = {
    "Experiencia": [
        r"\bexperiencia\b",
        r"\bcontratos ejecutados\b",
        r"\bcontratos similares\b",
    ],
    "Requisitos jurídicos": [
        r"\brepresentante legal\b",
        r"\bexistencia y representacion\b",
        r"\bregistro unico\b",
        r"\bcapacidad juridica\b",
    ],
    "Capacidad financiera": [
        r"\bliquidez\b",
        r"\bendeudamiento\b",
        r"\bcapital de trabajo\b",
        r"\bindicadores financieros\b",
    ],
    "Especificaciones técnicas": [
        r"\bespecificaciones tecnicas\b",
        r"\bluminarias\b",
        r"\bfotovoltaico\b",
        r"\bpotencia\b",
        r"\bautonomia\b",
    ],
    "Garantías": [
        r"\bgarantia\b",
        r"\bpoliza\b",
        r"\bseriedad de la oferta\b",
    ],
    "Plazos": [
        r"\bplazo de ejecucion\b",
        r"\bfecha de cierre\b",
        r"\bcronograma\b",
        r"\bplazo contractual\b",
    ],
    "Alianzas": [
        r"\bconsorcio\b",
        r"\bunion temporal\b",
        r"\bproponente plural\b",
    ],
}

CHECKLIST = [
    "Experiencia contractual",
    "Capacidad jurídica",
    "Capacidad financiera",
    "Especificaciones técnicas",
    "Garantías y pólizas",
    "Cronograma y plazo",
    "Documentación habilitante",
    "Modalidad de participación",
]


# ============================================================
# UTILIDADES
# ============================================================

def fecha_actual():
    return datetime.now(ZONA).isoformat(
        timespec="seconds"
    )


def clave_segura(texto):
    return hashlib.sha256(
        str(texto).encode("utf-8")
    ).hexdigest()[:16]


def limpiar_texto(texto):
    texto = str(texto or "")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def normalizar_busqueda(texto):
    import unicodedata

    texto = unicodedata.normalize(
        "NFKD", str(texto or "").lower()
    )

    return "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )


def datos_iniciales():
    return {
        "version": 1,
        "documentos": {},
        "verificaciones": {},
        "observaciones_generales": "",
        "actualizado": fecha_actual(),
    }


def cargar_datos():
    datos = obtener_datos_modulo(
        MODULO,
        defecto=None,
    )

    if not isinstance(datos, dict):
        return datos_iniciales()

    resultado = deepcopy(datos)
    resultado.setdefault("documentos", {})
    resultado.setdefault("verificaciones", {})
    resultado.setdefault(
        "observaciones_generales", ""
    )
    resultado.setdefault(
        "actualizado", fecha_actual()
    )
    return resultado


def guardar_datos(datos, accion):
    expediente = oportunidad_activa()

    if expediente is None:
        return False

    copia = deepcopy(datos)
    copia["actualizado"] = fecha_actual()

    correcto = guardar_datos_modulo(
        MODULO, copia
    )

    if correcto:
        registrar_evento(
            expediente["id"], accion
        )

    return correcto


# ============================================================
# ESTILO CORPORATIVO
# ============================================================

def estilos():
    st.markdown(
        """
        <style>
        .inti-doc-hero {
            background: linear-gradient(
                115deg, #202630, #303A48
            );
            padding: 32px 35px;
            border-radius: 18px;
            margin-bottom: 24px;
        }

        .inti-doc-eyebrow {
            color: #FFAD72;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 1.5px;
            margin-bottom: 12px;
        }

        .inti-doc-title {
            color: #FFFFFF;
            font-size: 36px;
            font-weight: 800;
            margin-bottom: 12px;
        }

        .inti-doc-description {
            color: #D2D9E3;
            font-size: 15px;
            line-height: 1.7;
        }

        .inti-doc-section {
            color: #242C39;
            font-size: 21px;
            font-weight: 750;
            margin: 25px 0 14px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def encabezado():
    st.markdown(
        """
        <div class="inti-doc-hero">
            <div class="inti-doc-eyebrow">
                INTILED SAS BIC · GESTIÓN DOCUMENTAL
            </div>
            <div class="inti-doc-title">
                Analizador de documentos
            </div>
            <div class="inti-doc-description">
                Organiza los pliegos, anexos y documentos
                técnicos de cada convocatoria. Identifica
                apartados relevantes y registra las
                verificaciones del expediente activo.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def titulo_seccion(texto):
    import html

    st.markdown(
        '<div class="inti-doc-section">'
        + html.escape(texto)
        + '</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# SELECCIÓN DEL EXPEDIENTE
# ============================================================

def seleccionar_expediente():
    expedientes = listar_oportunidades()

    if not expedientes:
        st.info(
            "Aún no tienes convocatorias guardadas. "
            "Guarda una oportunidad en el Radar "
            "para comenzar."
        )
        return None

    activo = oportunidad_activa()

    opciones = [
        expediente["id"]
        for expediente in expedientes
    ]

    etiquetas = {
        expediente["id"]: (
            str(
                expediente["oportunidad"].get(
                    "codigo", "Sin código"
                )
            )
            + " · "
            + str(
                expediente["oportunidad"].get(
                    "titulo", "Sin título"
                )
            )[:85]
        )
        for expediente in expedientes
    }

    posicion = (
        opciones.index(activo["id"])
        if activo and activo["id"] in opciones
        else 0
    )

    titulo_seccion(
        "01. Seleccionar convocatoria"
    )

    col1, col2 = st.columns([3, 1])

    with col1:
        elegido = st.selectbox(
            "Expediente",
            opciones,
            index=posicion,
            format_func=lambda valor: etiquetas.get(
                valor, valor
            ),
            key=(
                "inti_docs_selector_"
                + clave_segura(
                    activo["id"] if activo else "none"
                )
            ),
        )

    with col2:
        st.write("")
        st.write("")

        if st.button(
            "Activar",
            type="primary",
            use_container_width=True,
            key="inti_docs_activar",
        ):
            activar_oportunidad(elegido)
            st.rerun()

    if activo is None:
        st.warning(
            "Selecciona una convocatoria "
            "y presiona Activar."
        )
        return None

    oportunidad = activo["oportunidad"]

    with st.container(border=True):
        st.markdown(
            "**Convocatoria activa:** "
            + str(
                oportunidad.get("titulo")
                or "Sin título"
            )
        )

        st.caption(
            "Entidad: "
            + str(
                oportunidad.get("entidad")
                or "No informada"
            )
            + " · Código: "
            + str(
                oportunidad.get("codigo")
                or "No informado"
            )
        )

    return activo


# ============================================================
# EXTRAER TEXTO DE DOCUMENTOS
# ============================================================

def extraer_pdf(contenido):
    try:
        from pypdf import PdfReader
    except ImportError:
        raise RuntimeError(
            "Falta instalar pypdf en requirements.txt."
        )

    lector = PdfReader(
        io.BytesIO(contenido)
    )

    textos = []
    paginas = min(
        len(lector.pages),
        MAX_PAGINAS_PDF,
    )

    for numero in range(paginas):
        try:
            texto = (
                lector.pages[numero].extract_text()
                or ""
            )
        except Exception:
            texto = ""

        textos.append(
            f"\n[Página {numero + 1}]\n{texto}"
        )

    return "\n".join(textos), {
        "paginas_totales": len(lector.pages),
        "paginas_procesadas": paginas,
        "procesamiento_parcial": (
            paginas < len(lector.pages)
        ),
    }


def extraer_word(contenido):
    try:
        from docx import Document
    except ImportError:
        raise RuntimeError(
            "Falta instalar python-docx "
            "en requirements.txt."
        )

    documento = Document(
        io.BytesIO(contenido)
    )

    textos = [
        parrafo.text
        for parrafo in documento.paragraphs
        if parrafo.text.strip()
    ]

    for tabla in documento.tables:
        for fila in tabla.rows:
            contenido_fila = " | ".join(
                celda.text
                for celda in fila.cells
            )
            textos.append(contenido_fila)

    return "\n".join(textos), {
        "procesamiento_parcial": False
    }


def extraer_txt(contenido):
    try:
        return contenido.decode(
            "utf-8-sig"
        ), {
            "procesamiento_parcial": False
        }
    except UnicodeDecodeError:
        return contenido.decode(
            "latin-1"
        ), {
            "procesamiento_parcial": False
        }


def procesar_archivo(archivo, tipo):
    contenido = archivo.getvalue()

    if len(contenido) > MAX_ARCHIVO_MB * 1024 * 1024:
        raise ValueError(
            f"El documento supera {MAX_ARCHIVO_MB} MB."
        )

    extension = archivo.name.lower().rsplit(
        ".", 1
    )[-1]

    if extension == "pdf":
        texto, metadata = extraer_pdf(contenido)
    elif extension == "docx":
        texto, metadata = extraer_word(contenido)
    elif extension == "txt":
        texto, metadata = extraer_txt(contenido)
    else:
        raise ValueError(
            "Formato no admitido."
        )

    texto = limpiar_texto(texto)

    truncado = len(texto) > MAX_CARACTERES

    if truncado:
        texto = texto[:MAX_CARACTERES]

    metadata["texto_truncado"] = truncado

    huella = hashlib.sha256(
        contenido
    ).hexdigest()

    return {
        "id": huella[:24],
        "nombre": archivo.name,
        "tipo": tipo,
        "extension": extension,
        "tamano_bytes": len(contenido),
        "fecha_carga": fecha_actual(),
        "texto": texto,
        "metadata": metadata,
        "hallazgos": detectar_apartados(texto),
        "observaciones": "",
    }


# ============================================================
# DETECCIÓN PRELIMINAR DE APARTADOS
# ============================================================

def detectar_apartados(texto):
    texto_normalizado = normalizar_busqueda(
        texto
    )

    hallazgos = {}

    for categoria, patrones in (
        CATEGORIAS_REVISION.items()
    ):
        coincidencias = []

        for patron in patrones:
            for match in re.finditer(
                patron,
                texto_normalizado,
                flags=re.IGNORECASE,
            ):
                inicio = max(
                    0, match.start() - 130
                )
                final = min(
                    len(texto),
                    match.end() + 230,
                )

                fragmento = texto[
                    inicio:final
                ].strip()

                if fragmento:
                    coincidencias.append(fragmento)

                if len(coincidencias) >= 5:
                    break

            if len(coincidencias) >= 5:
                break

        if coincidencias:
            hallazgos[categoria] = coincidencias

    return hallazgos


# ============================================================
# SUBIR DOCUMENTOS
# ============================================================

def seccion_cargar(expediente):
    titulo_seccion(
        "02. Incorporar documentos"
    )

    identificador = clave_segura(
        expediente["id"]
    )

    tipo = st.selectbox(
        "Tipo de documento",
        TIPOS_DOCUMENTO,
        key=f"inti_docs_tipo_{identificador}",
    )

    archivos = st.file_uploader(
        "Seleccionar archivos",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        key=f"inti_docs_archivos_{identificador}",
    )

    st.caption(
        "Se extrae texto para revisión. "
        "Los PDF escaneados sin capa de texto "
        "no se interpretan automáticamente."
    )

    if st.button(
        "Incorporar al expediente",
        type="primary",
        use_container_width=True,
        key=f"inti_docs_subir_{identificador}",
    ):
        if not archivos:
            st.warning(
                "Selecciona al menos un archivo."
            )
            return

        if (
            oportunidad_activa() is None
            or oportunidad_activa()["id"]
            != expediente["id"]
        ):
            st.error(
                "Cambió el expediente activo. "
                "Vuelve a seleccionarlo."
            )
            return

        datos = cargar_datos()

        agregados = 0
        duplicados = 0
        errores = []

        for archivo in archivos:
            try:
                documento = procesar_archivo(
                    archivo, tipo
                )

                if documento["id"] in datos[
                    "documentos"
                ]:
                    duplicados += 1
                    continue

                datos["documentos"][
                    documento["id"]
                ] = documento

                agregados += 1

            except Exception as error:
                errores.append(
                    f"{archivo.name}: {error}"
                )

        if agregados:
            guardar_datos(
                datos,
                f"Se incorporaron {agregados} "
                "documentos al expediente",
            )

            st.success(
                f"{agregados} documento(s) "
                "incorporado(s) correctamente."
            )

        if duplicados:
            st.info(
                f"{duplicados} documento(s) "
                "ya estaban guardados."
            )

        for error in errores:
            st.error(error)

        if agregados:
            st.rerun()


# ============================================================
# CONSULTAR DOCUMENTOS
# ============================================================

def seccion_documentos(expediente):
    titulo_seccion(
        "03. Documentos del expediente"
    )

    datos = cargar_datos()
    documentos = datos["documentos"]

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Documentos",
        len(documentos),
    )

    c2.metric(
        "Con texto extraído",
        sum(
            bool(doc.get("texto"))
            for doc in documentos.values()
        ),
    )

    c3.metric(
        "Apartados identificados",
        sum(
            len(doc.get("hallazgos", {}))
            for doc in documentos.values()
        ),
    )

    if not documentos:
        st.info(
            "Aún no se han incorporado "
            "documentos a esta convocatoria."
        )
        return

    for documento_id, documento in (
        documentos.items()
    ):
        with st.expander(
            documento["nombre"],
            expanded=False,
        ):
            st.write(
                "**Tipo:** "
                + documento["tipo"]
            )

            st.write(
                "**Fecha de incorporación:** "
                + documento["fecha_carga"]
            )

            st.write(
                "**Caracteres extraídos:** "
                + str(
                    len(documento.get("texto", ""))
                )
            )

            metadata = documento.get(
                "metadata", {}
            )

            if metadata.get(
                "procesamiento_parcial"
            ):
                st.warning(
                    "Solo se procesó parte del PDF."
                )

            if metadata.get(
                "texto_truncado"
            ):
                st.warning(
                    "El texto se limitó a "
                    f"{MAX_CARACTERES} caracteres."
                )

            if not documento.get("texto"):
                st.warning(
                    "No se extrajo texto legible. "
                    "Puede ser un PDF escaneado."
                )

            st.markdown(
                "#### Apartados identificados"
            )

            hallazgos = documento.get(
                "hallazgos", {}
            )

            if not hallazgos:
                st.info(
                    "No se identificaron expresiones "
                    "de las categorías configuradas. "
                    "Esto no significa que el documento "
                    "carezca de requisitos."
                )

            for categoria, fragmentos in (
                hallazgos.items()
            ):
                st.markdown(
                    f"**{categoria}**"
                )

                for fragmento in fragmentos:
                    st.caption(fragmento)

            texto = documento.get(
                "texto", ""
            )

            if texto:
                st.text_area(
                    "Texto extraído",
                    value=texto[:12000],
                    height=220,
                    disabled=True,
                    key=(
                        "inti_docs_texto_"
                        + documento_id
                    ),
                )

            confirmar = st.checkbox(
                "Confirmo que deseo retirar "
                "este documento del expediente",
                key=(
                    "inti_docs_confirmar_"
                    + documento_id
                ),
            )

            if st.button(
                "Retirar documento",
                disabled=not confirmar,
                key=(
                    "inti_docs_retirar_"
                    + documento_id
                ),
            ):
                datos_actuales = cargar_datos()

                datos_actuales[
                    "documentos"
                ].pop(documento_id, None)

                guardar_datos(
                    datos_actuales,
                    "Documento retirado: "
                    + documento["nombre"],
                )

                st.rerun()


# ============================================================
# LISTA DE VERIFICACIÓN
# ============================================================

def seccion_verificaciones(expediente):
    titulo_seccion(
        "04. Verificación de requisitos"
    )

    st.caption(
        "Estas verificaciones deben basarse en "
        "los documentos del proceso y los "
        "soportes acreditados de INTILED."
    )

    datos = cargar_datos()
    identificador = clave_segura(
        expediente["id"]
    )

    verificaciones = datos[
        "verificaciones"
    ]

    with st.form(
        key=f"inti_docs_form_{identificador}"
    ):
        nuevos = {}

        for categoria in CHECKLIST:
            guardado = verificaciones.get(
                categoria, {}
            )

            if not isinstance(guardado, dict):
                guardado = {}

            st.markdown(
                f"**{categoria}**"
            )

            col1, col2 = st.columns(
                [1, 2]
            )

            estado_actual = guardado.get(
                "estado",
                "Pendiente de verificar",
            )

            with col1:
                estado = st.selectbox(
                    "Estado",
                    ESTADOS_REVISION,
                    index=(
                        ESTADOS_REVISION.index(
                            estado_actual
                        )
                        if estado_actual
                        in ESTADOS_REVISION
                        else 0
                    ),
                    key=(
                        "inti_docs_estado_"
                        + identificador
                        + clave_segura(categoria)
                    ),
                )

            with col2:
                observacion = st.text_input(
                    "Soporte u observación",
                    value=guardado.get(
                        "observacion", ""
                    ),
                    key=(
                        "inti_docs_observacion_"
                        + identificador
                        + clave_segura(categoria)
                    ),
                )

            nuevos[categoria] = {
                "estado": estado,
                "observacion": observacion,
                "fecha": fecha_actual(),
            }

        guardar = st.form_submit_button(
            "Guardar verificaciones",
            type="primary",
            use_container_width=True,
        )

    if guardar:
        if (
            oportunidad_activa() is None
            or oportunidad_activa()["id"]
            != expediente["id"]
        ):
            st.error(
                "La convocatoria cambió. "
                "No se guardaron las verificaciones."
            )
            return

        datos_actuales = cargar_datos()
        datos_actuales[
            "verificaciones"
        ] = nuevos

        if guardar_datos(
            datos_actuales,
            "Verificaciones documentales actualizadas",
        ):
            st.success(
                "Verificaciones guardadas "
                "en esta convocatoria."
            )

    st.divider()

    st.markdown(
        "**Resumen documental**"
    )

    vigentes = cargar_datos()[
        "verificaciones"
    ]

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Cumple verificado",
        sum(
            item.get("estado")
            == "Cumple - verificado"
            for item in vigentes.values()
        ),
    )

    c2.metric(
        "No cumple verificado",
        sum(
            item.get("estado")
            == "No cumple - verificado"
            for item in vigentes.values()
        ),
    )

    c3.metric(
        "Pendientes",
        len(CHECKLIST) - sum(
            item.get("estado") in (
                "Cumple - verificado",
                "No cumple - verificado",
                "No aplica",
            )
            for item in vigentes.values()
        ),
    )


# ============================================================
# HISTORIAL Y OBSERVACIONES
# ============================================================

def seccion_seguimiento(expediente):
    titulo_seccion(
        "05. Observaciones y seguimiento"
    )

    datos = cargar_datos()
    identificador = clave_segura(
        expediente["id"]
    )

    notas = st.text_area(
        "Observaciones generales",
        value=datos.get(
            "observaciones_generales", ""
        ),
        height=150,
        key=f"inti_docs_notas_{identificador}",
        placeholder=(
            "Registra aclaraciones, anexos "
            "pendientes y conclusiones..."
        ),
    )

    if st.button(
        "Guardar observaciones",
        type="primary",
        use_container_width=True,
        key=f"inti_docs_guardar_notas_{identificador}",
    ):
        actuales = cargar_datos()

        actuales[
            "observaciones_generales"
        ] = notas

        if guardar_datos(
            actuales,
            "Observaciones documentales actualizadas",
        ):
            st.success(
                "Observaciones guardadas."
            )

    with st.expander(
        "Consultar historial de la convocatoria"
    ):
        eventos = expediente.get(
            "historial", []
        )

        if not eventos:
            st.info(
                "Todavía no hay eventos registrados."
            )

        for evento in reversed(
            eventos[-30:]
        ):
            st.caption(
                str(evento.get("fecha", ""))
                + " · "
                + str(evento.get("accion", ""))
            )


# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

def mostrar_analizador():
    iniciar_workspace()
    sincronizar_legacy()

    estilos()
    encabezado()

    expediente = seleccionar_expediente()

    if expediente is None:
        return

    tab_documentos, tab_revision, tab_historial = (
        st.tabs([
            "Documentos",
            "Verificación",
            "Seguimiento",
        ])
    )

    with tab_documentos:
        seccion_cargar(expediente)
        seccion_documentos(expediente)

    with tab_revision:
        seccion_verificaciones(expediente)

    with tab_historial:
        seccion_seguimiento(expediente)

    st.divider()

    st.caption(
        "INTI Projects Enterprise · INTILED SAS BIC. "
        "La extracción y detección de apartados "
        "no equivalen a una evaluación automática "
        "del cumplimiento contractual."
    )


# ============================================================
# ALIAS DE COMPATIBILIDAD
# ============================================================

def mostrar_analizador_documentos():
    return mostrar_analizador()


def mostrar_analizador_documental():
    return mostrar_analizador()


def mostrar_analyzer():
    return mostrar_analizador()
