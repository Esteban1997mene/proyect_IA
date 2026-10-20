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
# Este módulo convierte una oportunidad seleccionada
# en un proyecto estructurable dentro de INTI.
#
# FUENTES DE INFORMACIÓN:
#
# 📥 CONVOCATORIA
# Información proveniente de SECOP / TDR / Pliegos.
#
# 🏢 INTILED
# Información corporativa validada.
#
# 🤖 INTI
# Propuestas, cálculos y recomendaciones del sistema.
#
# ⚠️ PENDIENTE
# Información que todavía debe ser validada.
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
        oportunidad.get("id_proceso")
        or oportunidad.get("referencia")
        or oportunidad.get("titulo")
        or "proyecto_intiled"
    )


# ============================================================
# INICIALIZAR PROYECTO
# ============================================================

def inicializar_proyecto(oportunidad):

    id_proyecto = obtener_id_oportunidad(
        oportunidad
    )

    # --------------------------------------------------------
    # CREAR CONTENEDOR GENERAL
    # --------------------------------------------------------

    if "proyectos_estructuracion" not in st.session_state:

        st.session_state[
            "proyectos_estructuracion"
        ] = {}

    proyectos = st.session_state[
        "proyectos_estructuracion"
    ]

    # --------------------------------------------------------
    # CREAR PROYECTO SI NO EXISTE
    # --------------------------------------------------------

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
            # ESTRUCTURACIÓN
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
                    "PENDIENTE"
            }
        }

    return proyectos[
        id_proyecto
    ]


# ============================================================
# CALCULAR PROGRESO
# ============================================================

def calcular_progreso(proyecto):

    secciones = {

        "Ficha general":
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

    porcentaje = round(
        (
            completadas
            / total
        )
        * 100
    )

    return (
        porcentaje,
        secciones
    )


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
        "económica y estratégica del proyecto."
    )

    st.divider()

    titulo = obtener_valor(
        oportunidad,
        "titulo",
        "Proyecto sin nombre"
    )

    st.markdown(
        f"### {titulo}"
    )

    st.write("")

    col1, col2, col3, col4 = st.columns(
        4
    )

    # --------------------------------------------------------
    # RADAR SCORE
    # --------------------------------------------------------

    with col1:

        score = oportunidad.get(
            "radar_score",
            0
        )

        st.metric(
            "Radar Score",
            f"{score}/100"
        )

    # --------------------------------------------------------
    # ENTIDAD
    # --------------------------------------------------------

    with col2:

        st.metric(
            "Entidad",
            obtener_valor(
                oportunidad,
                "entidad"
            )
        )

    # --------------------------------------------------------
    # PRESUPUESTO
    # --------------------------------------------------------

    with col3:

        st.metric(
            "Presupuesto",
            obtener_valor(
                oportunidad,
                "valor"
            )
        )

    # --------------------------------------------------------
    # ESTADO
    # --------------------------------------------------------

    with col4:

        st.metric(
            "Estado",
            proyecto.get(
                "estado",
                "PREESTRUCTURACIÓN"
            )
        )

    # --------------------------------------------------------
    # REFERENCIA
    # --------------------------------------------------------

    referencia = oportunidad.get(
        "referencia"
    )

    if referencia:

        st.caption(
            f"Referencia del proceso: {referencia}"
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

    tipo = st.selectbox(
        "Seleccione el tipo de proyecto",
        opciones,
        index=opciones.index(
            actual
        )
    )

    proyecto[
        "tipo_estructuracion"
    ] = tipo

    if (
        tipo
        == "Proyecto de inversión pública"
    ):

        st.info(
            "Este proyecto podrá posteriormente "
            "sincronizarse con el módulo "
            "🇨🇴 Proyectos públicos / MGA."
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

    st.write(
        "INTI puede preparar un borrador inicial "
        "utilizando la información disponible de "
        "la oportunidad y el ADN empresarial "
        "de INTILED."
    )

    st.warning(
        "El contenido generado es una "
        "**propuesta de trabajo**. "
        "No reemplaza los pliegos, TDR, "
        "estudios previos ni documentos "
        "oficiales del proceso."
    )

    # --------------------------------------------------------
    # BOTÓN
    # --------------------------------------------------------

    if st.button(
        "🤖 Generar preestructuración con INTI",
        type="primary",
        use_container_width=True
    ):

        oportunidad = proyecto[
            "oportunidad"
        ]

        with st.spinner(
            "INTI está construyendo la "
            "preestructuración del proyecto..."
        ):

            resultado = (
                generar_prestructuracion(
                    oportunidad
                )
            )

        # ====================================================
        # DIAGNÓSTICO
        # ====================================================

        diagnostico = resultado[
            "diagnostico"
        ]

        proyecto[
            "diagnostico"
        ][
            "problema"
        ] = diagnostico.get(
            "problema",
            ""
        )

        proyecto[
            "diagnostico"
        ][
            "necesidad"
        ] = diagnostico.get(
            "necesidad",
            ""
        )

        proyecto[
            "diagnostico"
        ][
            "justificacion"
        ] = diagnostico.get(
            "justificacion",
            ""
        )

        # ====================================================
        # OBJETIVOS
        # ====================================================

        objetivos = resultado[
            "objetivos"
        ]

        proyecto[
            "objetivos"
        ][
            "general"
        ] = objetivos.get(
            "general",
            ""
        )

        proyecto[
            "objetivos"
        ][
            "especificos"
        ] = lista_a_texto(
            objetivos.get(
                "especificos",
                []
            )
        )

        # ====================================================
        # ALCANCE
        # ====================================================

        alcance = resultado[
            "alcance"
        ]

        proyecto[
            "alcance"
        ] = lista_a_texto(
            alcance.get(
                "componentes",
                []
            )
        )

        # ====================================================
        # SOLUCIÓN TÉCNICA
        # ====================================================

        solucion = resultado[
            "solucion_tecnica"
        ]

        proyecto[
            "solucion_tecnica"
        ] = solucion.get(
            "texto",
            ""
        )

        # ====================================================
        # METODOLOGÍA
        # ====================================================

        metodologia = resultado[
            "metodologia"
        ]

        proyecto[
            "metodologia"
        ] = metodologia_a_texto(
            metodologia.get(
                "fases",
                []
            )
        )

        # ====================================================
        # TRAZABILIDAD
        # ====================================================

        proyecto[
            "origen_contenido"
        ][
            "diagnostico"
        ] = "PROPUESTA_INTI"

        proyecto[
            "origen_contenido"
        ][
            "objetivos"
        ] = "PROPUESTA_INTI"

        proyecto[
            "origen_contenido"
        ][
            "alcance"
        ] = "PROPUESTA_INTI"

        proyecto[
            "origen_contenido"
        ][
            "solucion_tecnica"
        ] = "PROPUESTA_INTI"

        proyecto[
            "origen_contenido"
        ][
            "metodologia"
        ] = "PROPUESTA_INTI"

        # ====================================================
        # ESTADO
        # ====================================================

        proyecto[
            "estado"
        ] = "BORRADOR INTI"

        proyecto[
            "ultima_actualizacion"
        ] = datetime.now().isoformat()

        # ====================================================
        # RESULTADO
        # ====================================================

        st.success(
            "Preestructuración generada correctamente."
        )

        st.info(
            "Revisa las pestañas Diagnóstico, "
            "Objetivos, Alcance, Solución técnica "
            "y Metodología."
        )

        st.rerun()


# ============================================================
# FICHA GENERAL
# ============================================================

def mostrar_ficha(
    proyecto
):

    st.subheader(
        "📋 Ficha general"
    )

    ficha = proyecto[
        "ficha"
    ]

    st.caption(
        "📥 Los datos precargados provienen "
        "de la oportunidad detectada."
    )

    # --------------------------------------------------------
    # NOMBRE
    # --------------------------------------------------------

    nombre = st.text_area(
        "Nombre del proyecto",
        value=ficha.get(
            "nombre",
            ""
        ),
        height=100,
        key=f"ficha_nombre_{proyecto['id']}"
    )

    # --------------------------------------------------------
    # COLUMNAS
    # --------------------------------------------------------

    col1, col2 = st.columns(
        2
    )

    with col1:

        entidad = st.text_input(
            "Entidad / cliente",
            value=ficha.get(
                "entidad",
                ""
            ),
            key=f"ficha_entidad_{proyecto['id']}"
        )

        pais = st.text_input(
            "País",
            value=ficha.get(
                "pais",
                ""
            ),
            key=f"ficha_pais_{proyecto['id']}"
        )

        departamento = st.text_input(
            "Departamento / región",
            value=ficha.get(
                "departamento",
                ""
            ),
            key=f"ficha_departamento_{proyecto['id']}"
        )

        presupuesto = st.text_input(
            "Presupuesto de referencia",
            value=str(
                ficha.get(
                    "presupuesto",
                    ""
                )
            ),
            key=f"ficha_presupuesto_{proyecto['id']}"
        )

    with col2:

        municipio = st.text_input(
            "Municipio / ciudad",
            value=ficha.get(
                "municipio",
                ""
            ),
            key=f"ficha_municipio_{proyecto['id']}"
        )

        sector = st.text_input(
            "Sector",
            value=ficha.get(
                "sector",
                ""
            ),
            key=f"ficha_sector_{proyecto['id']}"
        )

        modalidad = st.text_input(
            "Modalidad",
            value=ficha.get(
                "modalidad",
                ""
            ),
            key=f"ficha_modalidad_{proyecto['id']}"
        )

        fecha_cierre = st.text_input(
            "Fecha de cierre",
            value=str(
                ficha.get(
                    "fecha_cierre",
                    ""
                )
            ),
            key=f"ficha_fecha_{proyecto['id']}"
        )

    # --------------------------------------------------------
    # GUARDAR
    # --------------------------------------------------------

    ficha[
        "nombre"
    ] = nombre

    ficha[
        "entidad"
    ] = entidad

    ficha[
        "pais"
    ] = pais

    ficha[
        "departamento"
    ] = departamento

    ficha[
        "municipio"
    ] = municipio

    ficha[
        "sector"
    ] = sector

    ficha[
        "modalidad"
    ] = modalidad

    ficha[
        "presupuesto"
    ] = presupuesto

    ficha[
        "fecha_cierre"
    ] = fecha_cierre


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

    if origen == "PROPUESTA_INTI":

        st.warning(
            "🤖 **Origen:** Propuesta INTI. "
            "Debe validarse con los documentos "
            "oficiales del proceso."
        )

    else:

        st.caption(
            "⚠️ Información pendiente de estructuración."
        )

    diagnostico = proyecto[
        "diagnostico"
    ]

    # --------------------------------------------------------
    # PROBLEMA
    # --------------------------------------------------------

    diagnostico[
        "problema"
    ] = st.text_area(
        "Problema central",
        value=diagnostico.get(
            "problema",
            ""
        ),
        height=180,
        placeholder=(
            "Describe el problema que origina "
            "la necesidad del proyecto..."
        ),
        key=f"problema_{proyecto['id']}"
    )

    # --------------------------------------------------------
    # NECESIDAD
    # --------------------------------------------------------

    diagnostico[
        "necesidad"
    ] = st.text_area(
        "Necesidad identificada",
        value=diagnostico.get(
            "necesidad",
            ""
        ),
        height=160,
        key=f"necesidad_{proyecto['id']}"
    )

    # --------------------------------------------------------
    # JUSTIFICACIÓN
    # --------------------------------------------------------

    diagnostico[
        "justificacion"
    ] = st.text_area(
        "Justificación",
        value=diagnostico.get(
            "justificacion",
            ""
        ),
        height=200,
        key=f"justificacion_{proyecto['id']}"
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

    if origen == "PROPUESTA_INTI":

        st.warning(
            "🤖 Objetivos propuestos por INTI. "
            "Requieren revisión antes de incorporarse "
            "a una propuesta oficial."
        )

    objetivos = proyecto[
        "objetivos"
    ]

    # --------------------------------------------------------
    # GENERAL
    # --------------------------------------------------------

    objetivos[
        "general"
    ] = st.text_area(
        "Objetivo general",
        value=objetivos.get(
            "general",
            ""
        ),
        height=150,
        key=f"objetivo_general_{proyecto['id']}"
    )

    # --------------------------------------------------------
    # ESPECÍFICOS
    # --------------------------------------------------------

    objetivos[
        "especificos"
    ] = st.text_area(
        "Objetivos específicos",
        value=objetivos.get(
            "especificos",
            ""
        ),
        height=260,
        placeholder=(
            "1. ...\n"
            "2. ...\n"
            "3. ..."
        ),
        key=f"objetivos_especificos_{proyecto['id']}"
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

    if origen == "PROPUESTA_INTI":

        st.warning(
            "🤖 Alcance preliminar generado por INTI. "
            "Debe compararse con el alcance contractual."
        )

    proyecto[
        "alcance"
    ] = st.text_area(
        "Alcance técnico del proyecto",
        value=proyecto.get(
            "alcance",
            ""
        ),
        height=350,
        placeholder=(
            "Define qué incluye y qué no incluye "
            "la intervención..."
        ),
        key=f"alcance_{proyecto['id']}"
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

    if origen == "PROPUESTA_INTI":

        st.warning(
            "🤖 Solución técnica preliminar propuesta "
            "por INTI. No representa todavía una "
            "especificación contractual."
        )

    st.caption(
        "🏢 Posteriormente este componente se cruzará "
        "con productos, tecnologías y capacidades "
        "validadas de INTILED."
    )

    proyecto[
        "solucion_tecnica"
    ] = st.text_area(
        "Descripción de la solución",
        value=proyecto.get(
            "solucion_tecnica",
            ""
        ),
        height=400,
        key=f"solucion_{proyecto['id']}"
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

    if origen == "PROPUESTA_INTI":

        st.warning(
            "🤖 Metodología preliminar propuesta "
            "por INTI. Las fases deberán ajustarse "
            "al cronograma y requisitos oficiales."
        )

    proyecto[
        "metodologia"
    ] = st.text_area(
        "Metodología propuesta",
        value=proyecto.get(
            "metodologia",
            ""
        ),
        height=500,
        placeholder=(
            "Describe fases, actividades, "
            "controles, entregables y metodología..."
        ),
        key=f"metodologia_{proyecto['id']}"
    )


# ============================================================
# PLANIFICACIÓN
# ============================================================

def mostrar_modulos_avanzados(
    proyecto
):

    st.subheader(
        "🧩 Planificación del proyecto"
    )

    st.write(
        "En esta etapa INTI incorporará los motores "
        "especializados para convertir la propuesta "
        "conceptual en un proyecto ejecutable."
    )

    # --------------------------------------------------------
    # PRIMERA FILA
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        st.info(
            "### 🧱 EDT\n\n"
            "Paquetes de trabajo, actividades, "
            "subactividades y entregables."
        )

    with col2:

        st.info(
            "### 📅 Cronograma\n\n"
            "Fases, duración, dependencias, "
            "hitos y ruta de ejecución."
        )

    with col3:

        st.info(
            "### 👷 Equipo\n\n"
            "Perfiles profesionales, dedicaciones, "
            "responsabilidades y experiencia."
        )

    # --------------------------------------------------------
    # SEGUNDA FILA
    # --------------------------------------------------------

    col4, col5, col6 = st.columns(
        3
    )

    with col4:

        st.info(
            "### 💰 Presupuesto\n\n"
            "Personal, materiales, equipos, "
            "logística, AIU, impuestos "
            "e imprevistos."
        )

    with col5:

        st.info(
            "### ⚠️ Riesgos\n\n"
            "Riesgos técnicos, financieros, "
            "jurídicos, ambientales "
            "y operacionales."
        )

    with col6:

        st.info(
            "### 📈 Indicadores\n\n"
            "Indicadores de producto, resultado, "
            "gestión e impacto."
        )

    # --------------------------------------------------------
    # SOSTENIBILIDAD
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "🌱 Sostenibilidad"
    )

    proyecto[
        "sostenibilidad"
    ] = st.text_area(
        "Estrategia de sostenibilidad",
        value=proyecto.get(
            "sostenibilidad",
            ""
        ),
        height=180,
        placeholder=(
            "Operación, mantenimiento, sostenibilidad "
            "técnica, financiera, ambiental y social..."
        ),
        key=f"sostenibilidad_{proyecto['id']}"
    )


# ============================================================
# TRAZABILIDAD
# ============================================================

def mostrar_trazabilidad(
    proyecto
):

    st.subheader(
        "🔎 Trazabilidad de información"
    )

    st.write(
        "INTI diferencia el origen de la información "
        "para evitar mezclar datos oficiales con "
        "supuestos o propuestas generadas."
    )

    col1, col2, col3, col4 = st.columns(
        4
    )

    with col1:

        st.info(
            "📥 **CONVOCATORIA**\n\n"
            "SECOP, pliegos, TDR, anexos "
            "y documentos oficiales."
        )

    with col2:

        st.success(
            "🏢 **INTILED**\n\n"
            "Experiencia, personal, productos "
            "y documentos corporativos validados."
        )

    with col3:

        st.warning(
            "🤖 **PROPUESTA INTI**\n\n"
            "Análisis, cálculos, borradores "
            "y recomendaciones generadas."
        )

    with col4:

        st.error(
            "⚠️ **PENDIENTE**\n\n"
            "Información que requiere "
            "verificación o soporte."
        )

    # --------------------------------------------------------
    # ESTADO DE SECCIONES
    # --------------------------------------------------------

    st.divider()

    st.write(
        "### Estado actual de la información"
    )

    origenes = proyecto.get(
        "origen_contenido",
        {}
    )

    for seccion, origen in origenes.items():

        if origen == "CONVOCATORIA":

            icono = "📥"

        elif origen == "INTILED":

            icono = "🏢"

        elif origen == "PROPUESTA_INTI":

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
# GUARDADO
# ============================================================

def mostrar_guardado(
    proyecto
):

    st.divider()

    col1, col2 = st.columns(
        [3, 1]
    )

    with col1:

        st.caption(
            "En esta versión el proyecto se conserva "
            "durante la sesión activa de Streamlit. "
            "Posteriormente conectaremos este módulo "
            "con la base de datos de INTI."
        )

        ultima = proyecto.get(
            "ultima_actualizacion"
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
                "Avance guardado correctamente "
                "durante la sesión."
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
            "económica y estratégica del proyecto."
        )

        st.divider()

        st.info(
            "No existe una oportunidad seleccionada."
        )

        st.write(
            "Ve al **🔎 Radar de oportunidades**, "
            "selecciona un proceso y después regresa "
            "a **🏗️ Estructuración**."
        )

        return

    # ========================================================
    # OPORTUNIDAD
    # ========================================================

    oportunidad = st.session_state[
        "oportunidad_seleccionada"
    ]

    # ========================================================
    # CREAR / RECUPERAR PROYECTO
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
    # TIPO DE ESTRUCTURACIÓN
    # ========================================================

    mostrar_tipo_estructuracion(
        proyecto
    )

    st.divider()

    # ========================================================
    # GENERADOR INTI
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

    # --------------------------------------------------------
    # FICHA
    # --------------------------------------------------------

    with tabs[0]:

        mostrar_ficha(
            proyecto
        )

    # --------------------------------------------------------
    # DIAGNÓSTICO
    # --------------------------------------------------------

    with tabs[1]:

        mostrar_diagnostico(
            proyecto
        )

    # --------------------------------------------------------
    # OBJETIVOS
    # --------------------------------------------------------

    with tabs[2]:

        mostrar_objetivos(
            proyecto
        )

    # --------------------------------------------------------
    # ALCANCE
    # --------------------------------------------------------

    with tabs[3]:

        mostrar_alcance(
            proyecto
        )

    # --------------------------------------------------------
    # SOLUCIÓN TÉCNICA
    # --------------------------------------------------------

    with tabs[4]:

        mostrar_solucion_tecnica(
            proyecto
        )

    # --------------------------------------------------------
    # METODOLOGÍA
    # --------------------------------------------------------

    with tabs[5]:

        mostrar_metodologia(
            proyecto
        )

    # --------------------------------------------------------
    # PLANIFICACIÓN
    # --------------------------------------------------------

    with tabs[6]:

        mostrar_modulos_avanzados(
            proyecto
        )

    # --------------------------------------------------------
    # TRAZABILIDAD
    # --------------------------------------------------------

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
