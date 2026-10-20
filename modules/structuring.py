import streamlit as st
from datetime import datetime


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

    if "proyectos_estructuracion" not in st.session_state:

        st.session_state[
            "proyectos_estructuracion"
        ] = {}

    proyectos = st.session_state[
        "proyectos_estructuracion"
    ]

    # --------------------------------------------------------
    # CREAR PROYECTO
    # --------------------------------------------------------

    if id_proyecto not in proyectos:

        proyectos[id_proyecto] = {

            "id":
                id_proyecto,

            "fecha_creacion":
                datetime.now().isoformat(),

            "estado":
                "PREESTRUCTURACIÓN",

            "oportunidad":
                oportunidad,

            "tipo_estructuracion":
                "Oferta / contratación pública",

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
                    )
            },

            "diagnostico": {

                "problema":
                    "",

                "necesidad":
                    "",

                "justificacion":
                    ""
            },

            "objetivos": {

                "general":
                    "",

                "especificos":
                    ""
            },

            "alcance":
                "",

            "solucion_tecnica":
                "",

            "metodologia":
                "",

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

            "estrategia_intiled":
                "",

            "documentos":
                []
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
                ).get("nombre")
            ),

        "Diagnóstico":
            bool(
                proyecto.get(
                    "diagnostico",
                    {}
                ).get("problema")
            ),

        "Objetivos":
            bool(
                proyecto.get(
                    "objetivos",
                    {}
                ).get("general")
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
# CABECERA DEL PROYECTO
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

    st.markdown(
        "### "
        + obtener_valor(
            oportunidad,
            "titulo",
            "Proyecto sin nombre"
        )
    )

    col1, col2, col3, col4 = st.columns(
        4
    )

    with col1:

        st.metric(
            "Radar Score",
            str(
                oportunidad.get(
                    "radar_score",
                    0
                )
            )
            + "/100"
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

    if tipo == "Proyecto de inversión pública":

        st.info(
            "Este proyecto podrá posteriormente "
            "sincronizarse con el módulo "
            "🇨🇴 Proyectos públicos / MGA."
        )


# ============================================================
# FICHA GENERAL
# ============================================================

def mostrar_ficha(proyecto):

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

    nombre = st.text_area(
        "Nombre del proyecto",
        value=ficha.get(
            "nombre",
            ""
        ),
        height=100
    )

    col1, col2 = st.columns(
        2
    )

    with col1:

        entidad = st.text_input(
            "Entidad / cliente",
            value=ficha.get(
                "entidad",
                ""
            )
        )

        pais = st.text_input(
            "País",
            value=ficha.get(
                "pais",
                ""
            )
        )

        departamento = st.text_input(
            "Departamento / región",
            value=ficha.get(
                "departamento",
                ""
            )
        )

    with col2:

        municipio = st.text_input(
            "Municipio / ciudad",
            value=ficha.get(
                "municipio",
                ""
            )
        )

        sector = st.text_input(
            "Sector",
            value=ficha.get(
                "sector",
                ""
            )
        )

        modalidad = st.text_input(
            "Modalidad",
            value=ficha.get(
                "modalidad",
                ""
            )
        )

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


# ============================================================
# DIAGNÓSTICO
# ============================================================

def mostrar_diagnostico(proyecto):

    st.subheader(
        "🔍 Diagnóstico y necesidad"
    )

    st.caption(
        "🤖 En una etapa posterior INTI podrá "
        "proponer esta información utilizando "
        "los TDR, estudios y fuentes oficiales."
    )

    diagnostico = proyecto[
        "diagnostico"
    ]

    diagnostico[
        "problema"
    ] = st.text_area(
        "Problema central",
        value=diagnostico.get(
            "problema",
            ""
        ),
        height=120,
        placeholder=(
            "Describe el problema que origina "
            "la necesidad del proyecto..."
        )
    )

    diagnostico[
        "necesidad"
    ] = st.text_area(
        "Necesidad identificada",
        value=diagnostico.get(
            "necesidad",
            ""
        ),
        height=120
    )

    diagnostico[
        "justificacion"
    ] = st.text_area(
        "Justificación",
        value=diagnostico.get(
            "justificacion",
            ""
        ),
        height=150
    )


# ============================================================
# OBJETIVOS
# ============================================================

def mostrar_objetivos(proyecto):

    st.subheader(
        "🎯 Objetivos"
    )

    objetivos = proyecto[
        "objetivos"
    ]

    objetivos[
        "general"
    ] = st.text_area(
        "Objetivo general",
        value=objetivos.get(
            "general",
            ""
        ),
        height=120
    )

    objetivos[
        "especificos"
    ] = st.text_area(
        "Objetivos específicos",
        value=objetivos.get(
            "especificos",
            ""
        ),
        height=180,
        placeholder=(
            "1. ...\n"
            "2. ...\n"
            "3. ..."
        )
    )


# ============================================================
# ALCANCE
# ============================================================

def mostrar_alcance(proyecto):

    st.subheader(
        "📐 Alcance"
    )

    proyecto[
        "alcance"
    ] = st.text_area(
        "Alcance técnico del proyecto",
        value=proyecto.get(
            "alcance",
            ""
        ),
        height=250,
        placeholder=(
            "Define qué incluye y qué no incluye "
            "la intervención..."
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

    st.caption(
        "🏢 Aquí se incorporarán posteriormente "
        "las tecnologías, productos y capacidades "
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
        height=300
    )


# ============================================================
# METODOLOGÍA
# ============================================================

def mostrar_metodologia(proyecto):

    st.subheader(
        "🧠 Metodología de ejecución"
    )

    proyecto[
        "metodologia"
    ] = st.text_area(
        "Metodología propuesta",
        value=proyecto.get(
            "metodologia",
            ""
        ),
        height=350,
        placeholder=(
            "Describe fases, actividades, "
            "controles, entregables y metodología..."
        )
    )


# ============================================================
# MÓDULOS AVANZADOS
# ============================================================

def mostrar_modulos_avanzados(
    proyecto
):

    st.subheader(
        "🧩 Módulos de estructuración"
    )

    st.write(
        "Estos componentes serán desarrollados "
        "como motores especializados de INTI."
    )

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        st.info(
            "### 🧱 EDT\n"
            "Actividades, paquetes de trabajo "
            "y entregables."
        )

        st.info(
            "### 👷 Equipo\n"
            "Personal, perfiles, dedicaciones "
            "y experiencia."
        )

    with col2:

        st.info(
            "### 📅 Cronograma\n"
            "Fases, actividades, duración "
            "y dependencias."
        )

        st.info(
            "### 💰 Presupuesto\n"
            "APU, personal, equipos, AIU, "
            "impuestos e imprevistos."
        )

    with col3:

        st.info(
            "### ⚠️ Riesgos\n"
            "Riesgos técnicos, financieros, "
            "jurídicos y operacionales."
        )

        st.info(
            "### 📈 Indicadores\n"
            "Producto, resultado, impacto "
            "y seguimiento."
        )


# ============================================================
# TRAZABILIDAD
# ============================================================

def mostrar_trazabilidad():

    st.subheader(
        "🔎 Trazabilidad de información"
    )

    st.write(
        "INTI diferenciará permanentemente "
        "el origen de cada dato:"
    )

    col1, col2, col3, col4 = st.columns(
        4
    )

    with col1:

        st.info(
            "📥 **Convocatoria**\n\n"
            "SECOP, pliegos, TDR y anexos."
        )

    with col2:

        st.success(
            "🏢 **INTILED**\n\n"
            "Experiencia y documentos "
            "corporativos validados."
        )

    with col3:

        st.warning(
            "🤖 **INTI**\n\n"
            "Propuestas, análisis "
            "y recomendaciones."
        )

    with col4:

        st.error(
            "⚠️ **Pendiente**\n\n"
            "Información que todavía "
            "requiere validación."
        )


# ============================================================
# GUARDAR
# ============================================================

def mostrar_guardado(proyecto):

    st.divider()

    col1, col2 = st.columns(
        [3, 1]
    )

    with col1:

        st.caption(
            "En esta versión la estructuración "
            "se conserva durante la sesión activa. "
            "Posteriormente será almacenada "
            "en la base de datos."
        )

    with col2:

        if st.button(
            "💾 Guardar avance",
            type="primary",
            use_container_width=True
        ):

            proyecto[
                "ultima_actualizacion"
            ] = datetime.now().isoformat()

            st.success(
                "Avance guardado en la sesión."
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

        st.info(
            "No existe una oportunidad seleccionada."
        )

        st.write(
            "Ve al **🔎 Radar de oportunidades**, "
            "selecciona un proceso y después regresa "
            "a este módulo."
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
    # TIPO
    # ========================================================

    mostrar_tipo_estructuracion(
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
    # SOLUCIÓN
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

        mostrar_trazabilidad()

    # ========================================================
    # GUARDAR
    # ========================================================

    mostrar_guardado(
        proyecto
    )
