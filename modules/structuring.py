import streamlit as st
from datetime import datetime

from services.structuring_engine import (
    generar_prestructuracion,
    lista_a_texto,
    metodologia_a_texto
)


# ============================================================
# INTI PROJECTS AI
# CENTRO DE ESTRUCTURACIÓN DE PROYECTOS
# ============================================================
#
# FLUJO IDEAL:
#
# Radar
#   ↓
# Oportunidad
#   ↓
# Análisis INTILED
#   ↓
# Analizador documental
#   ↓
# Estructuración
#
# La estructuración puede trabajar en dos estados:
#
# 1. PREESTRUCTURACIÓN
#    Basada en metadata + ADN INTILED.
#
# 2. ESTRUCTURACIÓN VALIDADA
#    Basada en TDR/pliegos/documentos analizados.
#
# ============================================================


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def obtener_valor(
    oportunidad,
    campo,
    default="No informado"
):
    valor = oportunidad.get(campo)

    if valor is None or valor == "":
        return default

    return valor


def obtener_id_oportunidad(oportunidad):

    return str(
        oportunidad.get("referencia")
        or oportunidad.get("id_proceso")
        or oportunidad.get("id")
        or oportunidad.get("titulo")
        or "proyecto_intiled"
    )


def obtener_clave_documental(oportunidad):

    return str(
        oportunidad.get("referencia")
        or oportunidad.get("id_proceso")
        or oportunidad.get("titulo")
        or ""
    )


def inicializar_widget(
    clave,
    valor=""
):
    """
    Inicializa un widget únicamente cuando todavía
    no existe en st.session_state.
    """

    if clave not in st.session_state:
        st.session_state[clave] = valor or ""


# ============================================================
# INICIALIZAR PROYECTO
# ============================================================

def inicializar_proyecto(oportunidad):

    id_proyecto = obtener_id_oportunidad(
        oportunidad
    )

    if "proyectos_estructuracion" not in st.session_state:
        st.session_state[
            "proyectos_estructuracion"
        ] = {}

    proyectos = st.session_state[
        "proyectos_estructuracion"
    ]

    if id_proyecto not in proyectos:

        proyectos[id_proyecto] = {

            "id":
                id_proyecto,

            "fecha_creacion":
                datetime.now().isoformat(),

            "ultima_actualizacion":
                datetime.now().isoformat(),

            "estado":
                "PREESTRUCTURACIÓN",

            "oportunidad":
                oportunidad,

            "tipo_estructuracion":
                "Oferta / contratación pública",

            # =================================================
            # FICHA
            # =================================================

            "ficha": {

                "nombre":
                    oportunidad.get(
                        "titulo",
                        ""
                    ),

                "entidad":
                    oportunidad.get(
                        "entidad",
                        ""
                    ),

                "pais":
                    oportunidad.get(
                        "pais",
                        ""
                    ),

                "departamento":
                    oportunidad.get(
                        "departamento",
                        ""
                    ),

                "municipio":
                    oportunidad.get(
                        "ciudad",
                        ""
                    ),

                "sector":
                    oportunidad.get(
                        "sector",
                        ""
                    ),

                "presupuesto":
                    oportunidad.get(
                        "valor",
                        ""
                    ),

                "modalidad":
                    oportunidad.get(
                        "modalidad",
                        ""
                    ),

                "fecha_cierre":
                    oportunidad.get(
                        "fecha_cierre",
                        ""
                    ),

                "fuente":
                    oportunidad.get(
                        "fuente",
                        ""
                    ),

                "referencia":
                    oportunidad.get(
                        "referencia",
                        ""
                    )
            },

            # =================================================
            # DIAGNÓSTICO
            # =================================================

            "diagnostico": {

                "problema":
                    "",

                "necesidad":
                    "",

                "justificacion":
                    ""
            },

            # =================================================
            # OBJETIVOS
            # =================================================

            "objetivos": {

                "general":
                    "",

                "especificos":
                    ""
            },

            # =================================================
            # ESTRUCTURACIÓN TÉCNICA
            # =================================================

            "alcance":
                "",

            "solucion_tecnica":
                "",

            "metodologia":
                "",

            # =================================================
            # PLANIFICACIÓN
            # =================================================

            "edt":
                [],

            "cronograma":
                [],

            "equipo":
                [],

            "presupuesto":
                [],

            "riesgos":
                [],

            "indicadores":
                [],

            "sostenibilidad":
                "",

            # =================================================
            # ESTRATEGIA
            # =================================================

            "estrategia_intiled":
                "",

            # =================================================
            # DOCUMENTOS
            # =================================================

            "documentos":
                [],

            # =================================================
            # CONTROL
            # =================================================

            "preestructuracion_generada":
                False,

            "documentacion_validada":
                False,

            # =================================================
            # TRAZABILIDAD
            # =================================================

            "origen_contenido": {

                "ficha":
                    "CONVOCATORIA",

                "diagnostico":
                    "PENDIENTE",

                "objetivos":
                    "PENDIENTE",

                "alcance":
                    "PENDIENTE",

                "solucion_tecnica":
                    "PENDIENTE",

                "metodologia":
                    "PENDIENTE",

                "edt":
                    "PENDIENTE",

                "cronograma":
                    "PENDIENTE",

                "equipo":
                    "PENDIENTE",

                "presupuesto":
                    "PENDIENTE",

                "riesgos":
                    "PENDIENTE",

                "indicadores":
                    "PENDIENTE"
            }
        }

    # Actualizamos metadata de la oportunidad
    proyectos[id_proyecto][
        "oportunidad"
    ] = oportunidad

    return proyectos[
        id_proyecto
    ]


# ============================================================
# BUSCAR ANÁLISIS DOCUMENTAL
# ============================================================

def obtener_analisis_documental(
    oportunidad
):

    clave = obtener_clave_documental(
        oportunidad
    )

    analisis_documentales = (
        st.session_state.get(
            "analisis_documentales",
            {}
        )
    )

    if not isinstance(
        analisis_documentales,
        dict
    ):
        return None

    return analisis_documentales.get(
        clave
    )


# ============================================================
# CALCULAR PROGRESO
# ============================================================

def calcular_progreso(proyecto):

    secciones = {

        "Ficha":
            bool(
                proyecto.get(
                    "ficha",
                    {}
                ).get(
                    "nombre"
                )
            ),

        "Diagnóstico":
            bool(
                proyecto.get(
                    "diagnostico",
                    {}
                ).get(
                    "problema"
                )
            ),

        "Objetivos":
            bool(
                proyecto.get(
                    "objetivos",
                    {}
                ).get(
                    "general"
                )
            ),

        "Alcance":
            bool(
                proyecto.get(
                    "alcance"
                )
            ),

        "Solución técnica":
            bool(
                proyecto.get(
                    "solucion_tecnica"
                )
            ),

        "Metodología":
            bool(
                proyecto.get(
                    "metodologia"
                )
            ),

        "EDT":
            bool(
                proyecto.get(
                    "edt"
                )
            ),

        "Cronograma":
            bool(
                proyecto.get(
                    "cronograma"
                )
            ),

        "Equipo":
            bool(
                proyecto.get(
                    "equipo"
                )
            ),

        "Presupuesto":
            bool(
                proyecto.get(
                    "presupuesto"
                )
            ),

        "Riesgos":
            bool(
                proyecto.get(
                    "riesgos"
                )
            ),

        "Indicadores":
            bool(
                proyecto.get(
                    "indicadores"
                )
            ),

        "Sostenibilidad":
            bool(
                proyecto.get(
                    "sostenibilidad"
                )
            )
    }

    completadas = sum(
        1
        for valor in secciones.values()
        if valor
    )

    total = len(
        secciones
    )

    if total == 0:
        return 0, secciones

    porcentaje = round(
        completadas
        / total
        * 100
    )

    return porcentaje, secciones


# ============================================================
# CABECERA
# ============================================================

def mostrar_cabecera(proyecto):

    oportunidad = proyecto[
        "oportunidad"
    ]

    st.title(
        "🏗️ Centro de Estructuración"
    )

    st.caption(
        "Construcción técnica, metodológica, "
        "económica y estratégica de proyectos INTILED."
    )

    st.divider()

    titulo = obtener_valor(
        oportunidad,
        "titulo",
        "Proyecto sin nombre"
    )

    st.markdown(
        f"## {titulo}"
    )

    referencia = obtener_valor(
        oportunidad,
        "referencia",
        ""
    )

    if referencia:
        st.caption(
            f"Proceso: {referencia}"
        )

    col1, col2, col3, col4 = st.columns(
        4
    )

    with col1:

        score = oportunidad.get(
            "radar_score",
            0
        )

        st.metric(
            "Radar Score",
            f"{score}/100"
        )

    with col2:

        st.metric(
            "Entidad",
            obtener_valor(
                oportunidad,
                "entidad"
            )
        )

    with col3:

        st.metric(
            "Presupuesto",
            obtener_valor(
                oportunidad,
                "valor"
            )
        )

    with col4:

        st.metric(
            "Estado",
            proyecto.get(
                "estado",
                "PREESTRUCTURACIÓN"
            )
        )


# ============================================================
# PROGRESO
# ============================================================

def mostrar_progreso(proyecto):

    porcentaje, secciones = (
        calcular_progreso(
            proyecto
        )
    )

    st.subheader(
        "📊 Progreso de estructuración"
    )

    st.progress(
        porcentaje / 100
    )

    st.write(
        f"**{porcentaje}% completado**"
    )

    columnas = st.columns(
        4
    )

    for indice, (
        nombre,
        completado
    ) in enumerate(
        secciones.items()
    ):

        with columnas[
            indice % 4
        ]:

            if completado:

                st.write(
                    f"✅ {nombre}"
                )

            else:

                st.write(
                    f"⚪ {nombre}"
                )


# ============================================================
# ESTADO DOCUMENTAL
# ============================================================

def mostrar_estado_documental(
    proyecto
):

    oportunidad = proyecto[
        "oportunidad"
    ]

    analisis = obtener_analisis_documental(
        oportunidad
    )

    st.subheader(
        "📑 Documentación contractual"
    )

    # ========================================================
    # SIN DOCUMENTACIÓN
    # ========================================================

    if not analisis:

        proyecto[
            "documentacion_validada"
        ] = False

        st.warning(
            "⚠️ INTI todavía no dispone de los TDR, "
            "pliegos o anexos analizados para esta "
            "convocatoria."
        )

        st.write(
            "Puedes realizar una preestructuración "
            "preliminar, pero para construir una propuesta "
            "contractualmente sólida primero deben "
            "analizarse los documentos oficiales."
        )

        col1, col2 = st.columns(
            [2, 1]
        )

        with col1:

            if st.button(
                "📑 Cargar y analizar pliegos / TDR",
                type="primary",
                use_container_width=True,
                key=f"tdr_{proyecto['id']}"
            ):

                st.session_state[
                    "oportunidad_seleccionada"
                ] = oportunidad

                st.session_state[
                    "analizar_documentos"
                ] = True

                st.session_state[
                    "navegar_a"
                ] = "📑 Analizador de documentos"

                st.rerun()

        with col2:

            st.caption(
                "Recomendado antes de continuar "
                "con la propuesta definitiva."
            )

        return False

    # ========================================================
    # DOCUMENTACIÓN DISPONIBLE
    # ========================================================

    proyecto[
        "documentacion_validada"
    ] = True

    st.success(
        "✅ INTI encontró información documental "
        "asociada a esta convocatoria."
    )

    documentos = analisis.get(
        "documentos",
        []
    )

    porcentaje = analisis.get(
        "porcentaje_analisis"
    )

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        st.metric(
            "Documentos",
            len(documentos)
        )

    with col2:

        if porcentaje is None:

            st.metric(
                "Análisis documental",
                "Disponible"
            )

        else:

            st.metric(
                "Análisis documental",
                f"{porcentaje}%"
            )

    with col3:

        bid_score = analisis.get(
            "bid_score"
        )

        if bid_score is None:

            st.metric(
                "Bid Score",
                "Pendiente"
            )

        else:

            st.metric(
                "Bid Score",
                f"{bid_score}/100"
            )

    if st.button(
        "📑 Revisar documentos analizados",
        use_container_width=True,
        key=f"revisar_tdr_{proyecto['id']}"
    ):

        st.session_state[
            "oportunidad_seleccionada"
        ] = oportunidad

        st.session_state[
            "navegar_a"
        ] = "📑 Analizador de documentos"

        st.rerun()

    return True


# ============================================================
# TIPO DE ESTRUCTURACIÓN
# ============================================================

def mostrar_tipo_estructuracion(
    proyecto
):

    st.subheader(
        "🧭 Tipo de estructuración"
    )

    opciones = [
        "Oferta / contratación pública",
        "Suministro e instalación",
        "Consultoría",
        "Interventoría",
        "Proyecto privado",
        "Proyecto de inversión pública",
        "Proyecto de cooperación",
        "Proyecto interno INTILED"
    ]

    actual = proyecto.get(
        "tipo_estructuracion",
        opciones[0]
    )

    if actual not in opciones:
        actual = opciones[0]

    clave = (
        f"tipo_estructuracion_"
        f"{proyecto['id']}"
    )

    inicializar_widget(
        clave,
        actual
    )

    tipo = st.selectbox(
        "Seleccione el tipo de proyecto",
        opciones,
        key=clave
    )

    proyecto[
        "tipo_estructuracion"
    ] = tipo

    if (
        tipo
        == "Proyecto de inversión pública"
    ):

        st.info(
            "🇨🇴 Este proyecto podrá conectarse "
            "posteriormente con el módulo MGA."
        )


# ============================================================
# GENERADOR INTI
# ============================================================

def mostrar_generador_inti(
    proyecto
):

    st.subheader(
        "🤖 Preestructuración asistida por INTI"
    )

    documentacion = proyecto.get(
        "documentacion_validada",
        False
    )

    if documentacion:

        st.success(
            "📑 Existen documentos asociados al proyecto. "
            "En la siguiente evolución del motor, INTI "
            "utilizará directamente la información "
            "extraída de esos documentos."
        )

    else:

        st.warning(
            "Esta generación utilizará únicamente la "
            "información disponible de la oportunidad "
            "y el ADN INTILED. El resultado será "
            "un **borrador preliminar**."
        )

    texto_boton = (
        "🤖 Regenerar preestructuración con INTI"
        if proyecto.get(
            "preestructuracion_generada"
        )
        else
        "🤖 Generar preestructuración con INTI"
    )

    if st.button(
        texto_boton,
        type="primary",
        use_container_width=True,
        key=f"generar_inti_{proyecto['id']}"
    ):

        oportunidad = proyecto[
            "oportunidad"
        ]

        with st.spinner(
            "INTI está estructurando "
            "el proyecto..."
        ):

            resultado = (
                generar_prestructuracion(
                    oportunidad
                )
            )

        # ====================================================
        # DIAGNÓSTICO
        # ====================================================

        diagnostico = resultado.get(
            "diagnostico",
            {}
        )

        problema = diagnostico.get(
            "problema",
            ""
        )

        necesidad = diagnostico.get(
            "necesidad",
            ""
        )

        justificacion = diagnostico.get(
            "justificacion",
            ""
        )

        proyecto[
            "diagnostico"
        ][
            "problema"
        ] = problema

        proyecto[
            "diagnostico"
        ][
            "necesidad"
        ] = necesidad

        proyecto[
            "diagnostico"
        ][
            "justificacion"
        ] = justificacion

        # ====================================================
        # OBJETIVOS
        # ====================================================

        objetivos = resultado.get(
            "objetivos",
            {}
        )

        objetivo_general = objetivos.get(
            "general",
            ""
        )

        objetivos_especificos = (
            lista_a_texto(
                objetivos.get(
                    "especificos",
                    []
                )
            )
        )

        proyecto[
            "objetivos"
        ][
            "general"
        ] = objetivo_general

        proyecto[
            "objetivos"
        ][
            "especificos"
        ] = objetivos_especificos

        # ====================================================
        # ALCANCE
        # ====================================================

        alcance = resultado.get(
            "alcance",
            {}
        )

        alcance_texto = lista_a_texto(
            alcance.get(
                "componentes",
                []
            )
        )

        proyecto[
            "alcance"
        ] = alcance_texto

        # ====================================================
        # SOLUCIÓN TÉCNICA
        # ====================================================

        solucion = resultado.get(
            "solucion_tecnica",
            {}
        )

        solucion_texto = solucion.get(
            "texto",
            ""
        )

        proyecto[
            "solucion_tecnica"
        ] = solucion_texto

        # ====================================================
        # METODOLOGÍA
        # ====================================================

        metodologia = resultado.get(
            "metodologia",
            {}
        )

        metodologia_texto = (
            metodologia_a_texto(
                metodologia.get(
                    "fases",
                    []
                )
            )
        )

        proyecto[
            "metodologia"
        ] = metodologia_texto

        # ====================================================
        # SINCRONIZAR WIDGETS
        # ====================================================

        st.session_state[
            f"problema_{proyecto['id']}"
        ] = problema

        st.session_state[
            f"necesidad_{proyecto['id']}"
        ] = necesidad

        st.session_state[
            f"justificacion_{proyecto['id']}"
        ] = justificacion

        st.session_state[
            f"objetivo_general_{proyecto['id']}"
        ] = objetivo_general

        st.session_state[
            f"objetivos_especificos_{proyecto['id']}"
        ] = objetivos_especificos

        st.session_state[
            f"alcance_{proyecto['id']}"
        ] = alcance_texto

        st.session_state[
            f"solucion_{proyecto['id']}"
        ] = solucion_texto

        st.session_state[
            f"metodologia_{proyecto['id']}"
        ] = metodologia_texto

        # ====================================================
        # TRAZABILIDAD
        # ====================================================

        origen = (
            "PROPUESTA_INTI"
            if not documentacion
            else
            "PROPUESTA_INTI_PENDIENTE_VALIDACION_DOCUMENTAL"
        )

        for seccion in [
            "diagnostico",
            "objetivos",
            "alcance",
            "solucion_tecnica",
            "metodologia"
        ]:

            proyecto[
                "origen_contenido"
            ][
                seccion
            ] = origen

        proyecto[
            "preestructuracion_generada"
        ] = True

        proyecto[
            "estado"
        ] = "BORRADOR INTI"

        proyecto[
            "ultima_actualizacion"
        ] = datetime.now().isoformat()

        st.rerun()


# ============================================================
# FICHA
# ============================================================

def mostrar_ficha(
    proyecto
):

    st.subheader(
        "📋 Ficha general"
    )

    st.caption(
        "📥 Información precargada desde "
        "la convocatoria seleccionada."
    )

    ficha = proyecto[
        "ficha"
    ]

    campos = {
        "nombre":
            "Nombre del proyecto",

        "entidad":
            "Entidad / cliente",

        "pais":
            "País",

        "departamento":
            "Departamento / región",

        "municipio":
            "Municipio / ciudad",

        "sector":
            "Sector",

        "presupuesto":
            "Presupuesto de referencia",

        "modalidad":
            "Modalidad",

        "fecha_cierre":
            "Fecha de cierre",

        "referencia":
            "Referencia del proceso"
    }

    # --------------------------------------------------------
    # NOMBRE
    # --------------------------------------------------------

    clave_nombre = (
        f"ficha_nombre_{proyecto['id']}"
    )

    inicializar_widget(
        clave_nombre,
        ficha.get(
            "nombre",
            ""
        )
    )

    ficha[
        "nombre"
    ] = st.text_area(
        "Nombre del proyecto",
        key=clave_nombre,
        height=100
    )

    # --------------------------------------------------------
    # COLUMNAS
    # --------------------------------------------------------

    col1, col2 = st.columns(
        2
    )

    campos_col1 = [
        "entidad",
        "pais",
        "departamento",
        "presupuesto"
    ]

    campos_col2 = [
        "municipio",
        "sector",
        "modalidad",
        "fecha_cierre"
    ]

    with col1:

        for campo in campos_col1:

            clave = (
                f"ficha_{campo}_"
                f"{proyecto['id']}"
            )

            inicializar_widget(
                clave,
                str(
                    ficha.get(
                        campo,
                        ""
                    )
                )
            )

            ficha[
                campo
            ] = st.text_input(
                campos[campo],
                key=clave
            )

    with col2:

        for campo in campos_col2:

            clave = (
                f"ficha_{campo}_"
                f"{proyecto['id']}"
            )

            inicializar_widget(
                clave,
                str(
                    ficha.get(
                        campo,
                        ""
                    )
                )
            )

            ficha[
                campo
            ] = st.text_input(
                campos[campo],
                key=clave
            )


# ============================================================
# DIAGNÓSTICO
# ============================================================

def mostrar_diagnostico(
    proyecto
):

    st.subheader(
        "🔍 Diagnóstico y necesidad"
    )

    origen = proyecto.get(
        "origen_contenido",
        {}
    ).get(
        "diagnostico",
        "PENDIENTE"
    )

    if origen.startswith(
        "PROPUESTA_INTI"
    ):

        st.warning(
            "🤖 Contenido propuesto por INTI. "
            "Debe contrastarse con los documentos "
            "oficiales de la convocatoria."
        )

    diagnostico = proyecto[
        "diagnostico"
    ]

    # --------------------------------------------------------
    # PROBLEMA
    # --------------------------------------------------------

    clave = (
        f"problema_{proyecto['id']}"
    )

    inicializar_widget(
        clave,
        diagnostico.get(
            "problema",
            ""
        )
    )

    diagnostico[
        "problema"
    ] = st.text_area(
        "Problema central",
        key=clave,
        height=180,
        placeholder=(
            "Describe el problema que origina "
            "la necesidad del proyecto..."
        )
    )

    # --------------------------------------------------------
    # NECESIDAD
    # --------------------------------------------------------

    clave = (
        f"necesidad_{proyecto['id']}"
    )

    inicializar_widget(
        clave,
        diagnostico.get(
            "necesidad",
            ""
        )
    )

    diagnostico[
        "necesidad"
    ] = st.text_area(
        "Necesidad identificada",
        key=clave,
        height=170
    )

    # --------------------------------------------------------
    # JUSTIFICACIÓN
    # --------------------------------------------------------

    clave = (
        f"justificacion_{proyecto['id']}"
    )

    inicializar_widget(
        clave,
        diagnostico.get(
            "justificacion",
            ""
        )
    )

    diagnostico[
        "justificacion"
    ] = st.text_area(
        "Justificación",
        key=clave,
        height=220
    )


# ============================================================
# OBJETIVOS
# ============================================================

def mostrar_objetivos(
    proyecto
):

    st.subheader(
        "🎯 Objetivos"
    )

    origen = proyecto.get(
        "origen_contenido",
        {}
    ).get(
        "objetivos",
        "PENDIENTE"
    )

    if origen.startswith(
        "PROPUESTA_INTI"
    ):

        st.warning(
            "🤖 Objetivos propuestos por INTI. "
            "Deben validarse antes de incorporarlos "
            "a la propuesta definitiva."
        )

    objetivos = proyecto[
        "objetivos"
    ]

    # --------------------------------------------------------
    # GENERAL
    # --------------------------------------------------------

    clave = (
        f"objetivo_general_{proyecto['id']}"
    )

    inicializar_widget(
        clave,
        objetivos.get(
            "general",
            ""
        )
    )

    objetivos[
        "general"
    ] = st.text_area(
        "Objetivo general",
        key=clave,
        height=160
    )

    # --------------------------------------------------------
    # ESPECÍFICOS
    # --------------------------------------------------------

    clave = (
        f"objetivos_especificos_{proyecto['id']}"
    )

    inicializar_widget(
        clave,
        objetivos.get(
            "especificos",
            ""
        )
    )

    objetivos[
        "especificos"
    ] = st.text_area(
        "Objetivos específicos",
        key=clave,
        height=280,
        placeholder=(
            "1. ...\n"
            "2. ...\n"
            "3. ..."
        )
    )


# ============================================================
# ALCANCE
# ============================================================

def mostrar_alcance(
    proyecto
):

    st.subheader(
        "📐 Alcance"
    )

    origen = proyecto.get(
        "origen_contenido",
        {}
    ).get(
        "alcance",
        "PENDIENTE"
    )

    if origen.startswith(
        "PROPUESTA_INTI"
    ):

        st.warning(
            "🤖 Alcance preliminar generado por INTI. "
            "Debe compararse con el alcance contractual."
        )

    clave = (
        f"alcance_{proyecto['id']}"
    )

    inicializar_widget(
        clave,
        proyecto.get(
            "alcance",
            ""
        )
    )

    proyecto[
        "alcance"
    ] = st.text_area(
        "Alcance técnico del proyecto",
        key=clave,
        height=380,
        placeholder=(
            "Define qué incluye, entregables, "
            "límites y exclusiones del proyecto..."
        )
    )


# ============================================================
# SOLUCIÓN TÉCNICA
# ============================================================

def mostrar_solucion_tecnica(
    proyecto
):

    st.subheader(
        "⚡ Solución técnica"
    )

    origen = proyecto.get(
        "origen_contenido",
        {}
    ).get(
        "solucion_tecnica",
        "PENDIENTE"
    )

    if origen.startswith(
        "PROPUESTA_INTI"
    ):

        st.warning(
            "🤖 Solución preliminar propuesta por INTI. "
            "Las cantidades, potencias, equipos y "
            "especificaciones deben validarse."
        )

    clave = (
        f"solucion_{proyecto['id']}"
    )

    inicializar_widget(
        clave,
        proyecto.get(
            "solucion_tecnica",
            ""
        )
    )

    proyecto[
        "solucion_tecnica"
    ] = st.text_area(
        "Descripción de la solución",
        key=clave,
        height=420
    )


# ============================================================
# METODOLOGÍA
# ============================================================

def mostrar_metodologia(
    proyecto
):

    st.subheader(
        "🧠 Metodología de ejecución"
    )

    origen = proyecto.get(
        "origen_contenido",
        {}
    ).get(
        "metodologia",
        "PENDIENTE"
    )

    if origen.startswith(
        "PROPUESTA_INTI"
    ):

        st.warning(
            "🤖 Metodología preliminar propuesta "
            "por INTI. Debe ajustarse a los TDR, "
            "plazos y entregables reales."
        )

    clave = (
        f"metodologia_{proyecto['id']}"
    )

    inicializar_widget(
        clave,
        proyecto.get(
            "metodologia",
            ""
        )
    )

    proyecto[
        "metodologia"
    ] = st.text_area(
        "Metodología propuesta",
        key=clave,
        height=500
    )


# ============================================================
# PLANIFICACIÓN
# ============================================================

def mostrar_planificacion(
    proyecto
):

    st.subheader(
        "🧩 Planificación del proyecto"
    )

    if not proyecto.get(
        "documentacion_validada"
    ):

        st.warning(
            "Para generar una EDT, cronograma, "
            "presupuesto y equipo confiables se "
            "recomienda analizar primero los TDR."
        )

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        st.info(
            "### 🧱 EDT\n\n"
            "Paquetes de trabajo, actividades, "
            "subactividades y entregables."
        )

        st.info(
            "### 💰 Presupuesto\n\n"
            "Personal, equipos, materiales, "
            "logística, impuestos, AIU "
            "e imprevistos."
        )

    with col2:

        st.info(
            "### 📅 Cronograma\n\n"
            "Fases, duración, dependencias, "
            "hitos y entregables."
        )

        st.info(
            "### ⚠️ Riesgos\n\n"
            "Riesgos técnicos, financieros, "
            "jurídicos, operacionales "
            "y contractuales."
        )

    with col3:

        st.info(
            "### 👷 Equipo\n\n"
            "Perfiles, dedicaciones, experiencia "
            "y responsabilidades."
        )

        st.info(
            "### 📈 Indicadores\n\n"
            "Indicadores de producto, resultado, "
            "gestión e impacto."
        )

    # ========================================================
    # SOSTENIBILIDAD
    # ========================================================

    st.divider()

    st.subheader(
        "🌱 Sostenibilidad"
    )

    clave = (
        f"sostenibilidad_{proyecto['id']}"
    )

    inicializar_widget(
        clave,
        proyecto.get(
            "sostenibilidad",
            ""
        )
    )

    proyecto[
        "sostenibilidad"
    ] = st.text_area(
        "Estrategia de sostenibilidad",
        key=clave,
        height=200,
        placeholder=(
            "Operación, mantenimiento, "
            "sostenibilidad técnica, económica, "
            "ambiental y social..."
        )
    )


# ============================================================
# TRAZABILIDAD
# ============================================================

def mostrar_trazabilidad(
    proyecto
):

    st.subheader(
        "🔎 Trazabilidad"
    )

    st.write(
        "INTI diferencia permanentemente "
        "el origen de cada dato."
    )

    col1, col2, col3, col4 = st.columns(
        4
    )

    with col1:

        st.info(
            "📥 **CONVOCATORIA**\n\n"
            "SECOP, TDR, pliegos, anexos "
            "y documentos oficiales."
        )

    with col2:

        st.success(
            "🏢 **INTILED**\n\n"
            "Experiencia, personal, productos "
            "y documentación corporativa."
        )

    with col3:

        st.warning(
            "🤖 **PROPUESTA INTI**\n\n"
            "Borradores, análisis, cálculos "
            "y recomendaciones."
        )

    with col4:

        st.error(
            "⚠️ **PENDIENTE**\n\n"
            "Dato que todavía necesita "
            "verificación."
        )

    st.divider()

    origenes = proyecto.get(
        "origen_contenido",
        {}
    )

    for seccion, origen in origenes.items():

        if origen == "CONVOCATORIA":
            icono = "📥"

        elif origen == "INTILED":
            icono = "🏢"

        elif origen.startswith(
            "PROPUESTA_INTI"
        ):
            icono = "🤖"

        else:
            icono = "⚠️"

        nombre = (
            seccion
            .replace(
                "_",
                " "
            )
            .title()
        )

        st.write(
            f"{icono} **{nombre}:** {origen}"
        )


# ============================================================
# GUARDAR
# ============================================================

def mostrar_guardado(
    proyecto
):

    st.divider()

    col1, col2 = st.columns(
        [3, 1]
    )

    with col1:

        ultima = proyecto.get(
            "ultima_actualizacion"
        )

        st.caption(
            "Actualmente el proyecto se conserva "
            "en la sesión de Streamlit. "
            "Posteriormente será persistido "
            "en la base de datos."
        )

        if ultima:

            st.caption(
                f"Última actualización: {ultima}"
            )

    with col2:

        if st.button(
            "💾 Guardar avance",
            type="primary",
            use_container_width=True,
            key=f"guardar_{proyecto['id']}"
        ):

            proyecto[
                "ultima_actualizacion"
            ] = datetime.now().isoformat()

            st.success(
                "Avance guardado correctamente."
            )


# ============================================================
# MÓDULO PRINCIPAL
# ============================================================

def mostrar_estructuracion():

    # ========================================================
    # VERIFICAR OPORTUNIDAD
    # ========================================================

    if (
        "oportunidad_seleccionada"
        not in st.session_state
    ):

        st.title(
            "🏗️ Centro de Estructuración"
        )

        st.caption(
            "Construcción técnica, metodológica, "
            "económica y estratégica."
        )

        st.divider()

        st.info(
            "No existe una oportunidad seleccionada."
        )

        st.write(
            "Ve al **🔎 Radar de oportunidades**, "
            "selecciona un proceso y después "
            "regresa a este módulo."
        )

        return

    # ========================================================
    # OPORTUNIDAD
    # ========================================================

    oportunidad = st.session_state[
        "oportunidad_seleccionada"
    ]

    # ========================================================
    # PROYECTO
    # ========================================================

    proyecto = inicializar_proyecto(
        oportunidad
    )

    # ========================================================
    # CABECERA
    # ========================================================

    mostrar_cabecera(
        proyecto
    )

    st.divider()

    # ========================================================
    # PROGRESO
    # ========================================================

    mostrar_progreso(
        proyecto
    )

    st.divider()

    # ========================================================
    # DOCUMENTACIÓN
    # ========================================================

    mostrar_estado_documental(
        proyecto
    )

    st.divider()

    # ========================================================
    # TIPO
    # ========================================================

    mostrar_tipo_estructuracion(
        proyecto
    )

    st.divider()

    # ========================================================
    # GENERACIÓN INTI
    # ========================================================

    mostrar_generador_inti(
        proyecto
    )

    st.divider()

    # ========================================================
    # PESTAÑAS
    # ========================================================

    tabs = st.tabs(
        [
            "📋 Ficha",
            "🔍 Diagnóstico",
            "🎯 Objetivos",
            "📐 Alcance",
            "⚡ Solución técnica",
            "🧠 Metodología",
            "🧩 Planificación",
            "🔎 Trazabilidad"
        ]
    )

    with tabs[0]:

        mostrar_ficha(
            proyecto
        )

    with tabs[1]:

        mostrar_diagnostico(
            proyecto
        )

    with tabs[2]:

        mostrar_objetivos(
            proyecto
        )

    with tabs[3]:

        mostrar_alcance(
            proyecto
        )

    with tabs[4]:

        mostrar_solucion_tecnica(
            proyecto
        )

    with tabs[5]:

        mostrar_metodologia(
            proyecto
        )

    with tabs[6]:

        mostrar_planificacion(
            proyecto
        )

    with tabs[7]:

        mostrar_trazabilidad(
            proyecto
        )

    # ========================================================
    # GUARDADO
    # ========================================================

    mostrar_guardado(
        proyecto
    )
