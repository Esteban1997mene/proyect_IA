
import streamlit as st
from datetime import datetime

# ============================================================
# INTI PROJECTS ENTERPRISE
# DASHBOARD EJECUTIVO
# INTILED SAS BIC
# ============================================================


# ============================================================
# NAVEGACIÓN
# ============================================================

def ir_a(destino):
    st.session_state["navegar_a"] = destino
    st.rerun()


# ============================================================
# DATOS DISPONIBLES
# ============================================================

def obtener_lista_sesion(claves):

    for clave in claves:
        valor = st.session_state.get(clave)

        if isinstance(valor, list):
            return valor

    return []


def obtener_datos_dashboard():

    proyectos = obtener_lista_sesion([
        "portfolio_projects"
    ])

    oportunidades = obtener_lista_sesion([
        "oportunidades",
        "radar_oportunidades",
        "oportunidades_encontradas",
        "resultados_radar"
    ])

    bloqueados = sum(
        1 for p in proyectos
        if isinstance(p, dict)
        and "Bloqueado" in str(
            p.get("estado", "")
        )
    )

    prioritarios = sum(
        1 for p in proyectos
        if isinstance(p, dict)
        and str(
            p.get("prioridad", "")
        ).startswith("P1")
    )

    acciones = sum(
        1 for p in proyectos
        if isinstance(p, dict)
        and str(
            p.get("proxima_accion", "")
        ).strip()
    )

    return {
        "proyectos": proyectos,
        "oportunidades": oportunidades,
        "total_proyectos": len(proyectos),
        "total_oportunidades": len(oportunidades),
        "bloqueados": bloqueados,
        "prioritarios": prioritarios,
        "acciones": acciones
    }


# ============================================================
# ENCABEZADO
# ============================================================

def mostrar_hero():

    fecha = datetime.now().strftime(
        "%d/%m/%Y"
    )

    st.markdown(
        f"""
        <div class="inti-page-header">
            <div class="inti-eyebrow">
                CENTRO DE CONTROL
            </div>
            <h1 class="inti-page-title">
                Panel ejecutivo
            </h1>
            <div class="inti-page-description">
                Inteligencia de oportunidades, formulación
                y gestión de proyectos de INTILED SAS BIC.
                <span style="margin-left:12px;">
                    {fecha}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="inti-hero">
            <div class="inti-hero-tag">
                INTI PROJECTS ENTERPRISE
            </div>
            <div class="inti-hero-title">
                De la oportunidad al proyecto.
            </div>
            <div class="inti-hero-text">
                Identifica convocatorias, analiza su viabilidad,
                estructura soluciones y prepara propuestas
                competitivas desde un mismo entorno de trabajo.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(
        [1.3, 1.3, 1]
    )

    with col1:
        if st.button(
            "Explorar convocatorias",
            type="primary",
            use_container_width=True,
            key="dash_ir_radar"
        ):
            ir_a("🔎 Radar de oportunidades")

    with col2:
        if st.button(
            "Abrir portafolio",
            use_container_width=True,
            key="dash_ir_portafolio"
        ):
            ir_a("📊 Portafolio INTILED")

    with col3:
        if st.button(
            "Analizar documentos",
            use_container_width=True,
            key="dash_ir_documentos"
        ):
            ir_a("📑 Analizador de documentos")


# ============================================================
# INDICADORES
# ============================================================

def mostrar_indicadores(datos):

    st.markdown(
        '<div class="inti-section-title">'
        'Resumen de gestión'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Oportunidades cargadas",
            datos["total_oportunidades"]
        )

    with col2:
        st.metric(
            "Proyectos registrados",
            datos["total_proyectos"]
        )

    with col3:
        st.metric(
            "Proyectos prioritarios",
            datos["prioritarios"]
        )

    with col4:
        st.metric(
            "Acciones registradas",
            datos["acciones"]
        )

    if (
        datos["total_proyectos"] == 0
        and datos["total_oportunidades"] == 0
    ):
        st.caption(
            "Los indicadores muestran únicamente los datos "
            "disponibles en la sesión actual. "
            "Todavía no representan una base de datos centralizada."
        )


# ============================================================
# FLUJO DE TRABAJO
# ============================================================

def mostrar_flujo():

    st.markdown(
        '<div class="inti-section-title">'
        'Flujo de trabajo'
        '</div>',
        unsafe_allow_html=True
    )

    pasos = [
        {
            "numero": "01",
            "titulo": "Descubrir",
            "descripcion": (
                "Localizar convocatorias y "
                "oportunidades comerciales."
            ),
            "destino": "🔎 Radar de oportunidades"
        },
        {
            "numero": "02",
            "titulo": "Evaluar",
            "descripcion": (
                "Determinar pertinencia y "
                "viabilidad para INTILED."
            ),
            "destino": "🧠 Análisis INTILED"
        },
        {
            "numero": "03",
            "titulo": "Analizar",
            "descripcion": (
                "Revisar TDR, requisitos "
                "y documentación."
            ),
            "destino": "📑 Analizador de documentos"
        },
        {
            "numero": "04",
            "titulo": "Estructurar",
            "descripcion": (
                "Desarrollar la solución "
                "técnica y económica."
            ),
            "destino": "🏗️ Estructuración"
        },
        {
            "numero": "05",
            "titulo": "Proponer",
            "descripcion": (
                "Preparar los documentos "
                "de la propuesta."
            ),
            "destino": "📄 Generador de propuestas"
        }
    ]

    columnas = st.columns(5)

    for indice, paso in enumerate(pasos):

        with columnas[indice]:

            with st.container(border=True):

                st.markdown(
                    f"""
                    <div style="
                        color:#F47721;
                        font-size:13px;
                        font-weight:800;
                        margin-bottom:8px;
                    ">
                        PASO {paso['numero']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"**{paso['titulo']}**"
                )

                st.caption(
                    paso["descripcion"]
                )

                if st.button(
                    "Abrir",
                    key=f"dash_paso_{indice}",
                    use_container_width=True
                ):
                    ir_a(
                        paso["destino"]
                    )


# ============================================================
# PROYECTOS PRIORITARIOS
# ============================================================

def mostrar_proyectos(datos):

    st.markdown(
        '<div class="inti-section-title">'
        'Proyectos que requieren atención'
        '</div>',
        unsafe_allow_html=True
    )

    proyectos = datos["proyectos"]

    if not proyectos:

        with st.container(border=True):
            st.markdown(
                "#### Aún no hay proyectos disponibles"
            )
            st.write(
                "Carga tu portafolio o registra un proyecto "
                "para visualizar aquí las prioridades."
            )

            if st.button(
                "Ir al portafolio",
                key="dash_cargar_portafolio"
            ):
                ir_a("📊 Portafolio INTILED")

        return

    destacados = [
        p for p in proyectos
        if isinstance(p, dict)
        and (
            str(
                p.get("prioridad", "")
            ).startswith("P1")
            or "Bloqueado" in str(
                p.get("estado", "")
            )
        )
    ]

    if not destacados:
        st.info(
            "No hay proyectos P1 o bloqueados "
            "en los datos disponibles."
        )
        return

    for proyecto in destacados[:5]:

        with st.container(border=True):

            col1, col2, col3 = st.columns(
                [3, 2, 1]
            )

            with col1:
                st.markdown(
                    "**"
                    + str(
                        proyecto.get(
                            "nombre",
                            "Sin nombre"
                        )
                    )
                    + "**"
                )

                st.caption(
                    str(
                        proyecto.get(
                            "entidad",
                            "Sin entidad"
                        )
                    )
                )

            with col2:
                st.write(
                    proyecto.get(
                        "estado",
                        "Sin estado"
                    )
                )
                st.caption(
                    proyecto.get(
                        "prioridad",
                        "Sin prioridad"
                    )
                )

            with col3:
                if st.button(
                    "Gestionar",
                    key="dash_gestion_"
                    + str(
                        proyecto.get(
                            "id",
                            id(proyecto)
                        )
                    ),
                    use_container_width=True
                ):
                    ir_a("📊 Portafolio INTILED")


# ============================================================
# ACCESOS ADICIONALES
# ============================================================

def mostrar_accesos():

    st.markdown(
        '<div class="inti-section-title">'
        'Herramientas de gestión'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown(
                "### Proyectos públicos"
            )
            st.write(
                "Estructuración y formulación "
                "de iniciativas de inversión."
            )
            if st.button(
                "Abrir MGA",
                key="dash_mga",
                use_container_width=True
            ):
                ir_a("🇨🇴 Proyectos públicos / MGA")

    with col2:
        with st.container(border=True):
            st.markdown(
                "### Investigación"
            )
            st.write(
                "Consulta de información y "
                "referencias técnicas."
            )
            if st.button(
                "Abrir investigación",
                key="dash_research",
                use_container_width=True
            ):
                ir_a("📚 Investigación")

    with col3:
        with st.container(border=True):
            st.markdown(
                "### Seguimiento"
            )
            st.write(
                "Control de avances, actividades "
                "y oportunidades."
            )
            if st.button(
                "Abrir seguimiento",
                key="dash_tracking",
                use_container_width=True
            ):
                ir_a("📊 Seguimiento")


# ============================================================
# DASHBOARD PRINCIPAL
# ============================================================

def mostrar_dashboard():

    datos = obtener_datos_dashboard()

    mostrar_hero()

    st.write("")

    mostrar_indicadores(datos)

    st.write("")

    mostrar_flujo()

    st.write("")

    mostrar_proyectos(datos)

    st.write("")

    mostrar_accesos()

    st.write("")

    st.caption(
        "INTI Projects Enterprise · INTILED SAS BIC"
    )

