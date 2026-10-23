import streamlit as st
from datetime import date

from services.portfolio_auth import (
    esta_autenticado,
    mostrar_login
)

from services.meetings_engine import (
    TIPOS_AVANCE,
    crear_reunion,
    crear_avance,
    resumen_reunion,
    obtener_compromisos,
    generar_resumen_texto
)


# ============================================================
# INTI PROJECTS AI
# REUNIONES Y AVANCES
# ============================================================


def inicializar_reuniones():

    if "portfolio_meetings" not in st.session_state:
        st.session_state["portfolio_meetings"] = []

    return st.session_state["portfolio_meetings"]


def obtener_proyectos():

    return st.session_state.get(
        "portfolio_projects",
        []
    )


# ============================================================
# ENCABEZADO
# ============================================================

def mostrar_encabezado():

    st.title("📅 Reuniones y Avances")

    st.caption(
        "Seguimiento ejecutivo del portafolio "
        "de proyectos de INTILED SAS BIC."
    )

    st.info(
        "Registra únicamente lo que cambió desde "
        "la reunión anterior. INTI conservará el "
        "histórico del proyecto."
    )


# ============================================================
# CREAR REUNIÓN
# ============================================================

def mostrar_crear_reunion(reuniones):

    st.subheader("➕ Nueva reunión")

    with st.form("form_nueva_reunion"):

        col1, col2 = st.columns(2)

        with col1:

            fecha = st.date_input(
                "Fecha de reunión",
                value=date.today()
            )

            titulo = st.text_input(
                "Nombre de la reunión",
                placeholder=(
                    "Ej. Seguimiento de proyectos "
                    "23 de octubre"
                )
            )

        with col2:

            responsable = st.text_input(
                "Responsable / líder"
            )

            observaciones = st.text_area(
                "Observaciones generales",
                height=100
            )

        guardar = st.form_submit_button(
            "💾 Crear reunión",
            type="primary",
            use_container_width=True
        )

        if guardar:

            if not titulo.strip():

                st.error(
                    "Debes indicar el nombre "
                    "de la reunión."
                )

            else:

                reunion = crear_reunion(
                    fecha,
                    titulo.strip(),
                    responsable.strip(),
                    observaciones.strip()
                )

                reuniones.append(reunion)

                st.session_state[
                    "reunion_activa"
                ] = reunion["id"]

                st.success(
                    "Reunión creada correctamente."
                )

                st.rerun()


# ============================================================
# SELECCIONAR REUNIÓN
# ============================================================

def seleccionar_reunion(reuniones):

    if not reuniones:
        return None

    reuniones_ordenadas = sorted(
        reuniones,
        key=lambda x: x.get("fecha", ""),
        reverse=True
    )

    opciones = {
        (
            f"{r.get('fecha', '')} | "
            f"{r.get('titulo', '')}"
        ): r["id"]
        for r in reuniones_ordenadas
    }

    etiquetas = list(opciones.keys())

    reunion_activa = st.session_state.get(
        "reunion_activa"
    )

    indice = 0

    if reunion_activa:

        for i, etiqueta in enumerate(etiquetas):

            if opciones[etiqueta] == reunion_activa:
                indice = i
                break

    seleccion = st.selectbox(
        "Seleccionar reunión",
        etiquetas,
        index=indice
    )

    id_reunion = opciones[seleccion]

    st.session_state[
        "reunion_activa"
    ] = id_reunion

    for reunion in reuniones:

        if reunion["id"] == id_reunion:
            return reunion

    return None


# ============================================================
# RESUMEN REUNIÓN
# ============================================================

def mostrar_resumen_reunion(reunion):

    resumen = resumen_reunion(reunion)

    st.subheader(
        "📊 Resumen de la reunión"
    )

    col1, col2, col3, col4, col5 = (
        st.columns(5)
    )

    with col1:
        st.metric(
            "Movimientos",
            resumen["total"]
        )

    with col2:
        st.metric(
            "Avances",
            resumen["avances"]
        )

    with col3:
        st.metric(
            "Nuevos",
            resumen["nuevos"]
        )

    with col4:
        st.metric(
            "Bloqueados",
            resumen["bloqueos"]
        )

    with col5:
        st.metric(
            "Aplazados",
            resumen["aplazados"]
        )


# ============================================================
# REGISTRAR AVANCE
# ============================================================

def mostrar_registro_avance(
    reunion,
    proyectos
):

    st.subheader(
        "⚡ Registrar movimiento"
    )

    nombres_proyectos = [
        p.get("nombre", "")
        for p in proyectos
        if p.get("nombre")
    ]

    opciones = [
        "➕ Nueva iniciativa / proyecto"
    ] + nombres_proyectos

    with st.form(
        f"avance_{reunion['id']}"
    ):

        proyecto_seleccionado = st.selectbox(
            "Proyecto",
            opciones
        )

        if (
            proyecto_seleccionado
            == "➕ Nueva iniciativa / proyecto"
        ):

            proyecto = st.text_input(
                "Nombre de la nueva iniciativa"
            )

        else:

            proyecto = proyecto_seleccionado

        tipo = st.selectbox(
            "¿Qué ocurrió?",
            TIPOS_AVANCE
        )

        descripcion = st.text_area(
            "¿Qué cambió desde la última reunión?",
            placeholder=(
                "Ej. Se cambió la fuente de "
                "financiación y debe replantearse "
                "la simulación financiera."
            ),
            height=130
        )

        col1, col2 = st.columns(2)

        with col1:

            responsable = st.text_input(
                "Responsable"
            )

        with col2:

            fecha_compromiso = st.date_input(
                "Fecha del próximo compromiso",
                value=date.today()
            )

        proxima_accion = st.text_area(
            "Próxima acción",
            placeholder=(
                "Ej. Hablar con la entidad y "
                "presentar nueva simulación financiera."
            )
        )

        guardar = st.form_submit_button(
            "💾 Registrar avance",
            type="primary",
            use_container_width=True
        )

        if guardar:

            if not str(proyecto).strip():

                st.error(
                    "Debes seleccionar o indicar "
                    "un proyecto."
                )

            elif not descripcion.strip():

                st.error(
                    "Describe el cambio o avance."
                )

            else:

                avance = crear_avance(
                    proyecto=str(proyecto).strip(),
                    tipo=tipo,
                    descripcion=descripcion.strip(),
                    responsable=responsable.strip(),
                    proxima_accion=(
                        proxima_accion.strip()
                    ),
                    fecha_compromiso=(
                        fecha_compromiso
                    )
                )

                reunion[
                    "avances"
                ].append(avance)

                st.success(
                    "Movimiento registrado."
                )

                st.rerun()


# ============================================================
# MOVIMIENTOS DE LA REUNIÓN
# ============================================================

def mostrar_movimientos(reunion):

    st.subheader(
        "📝 Movimientos registrados"
    )

    avances = reunion.get(
        "avances",
        []
    )

    if not avances:

        st.info(
            "Todavía no se han registrado "
            "movimientos en esta reunión."
        )

        return

    for avance in avances:

        with st.container(
            border=True
        ):

            st.markdown(
                f"### {avance.get('proyecto', '')}"
            )

            st.write(
                f"**{avance.get('tipo', '')}**"
            )

            st.write(
                avance.get(
                    "descripcion",
                    ""
                )
            )

            col1, col2 = st.columns(2)

            with col1:

                st.caption(
                    "Responsable: "
                    f"{avance.get('responsable') or 'Sin asignar'}"
                )

            with col2:

                st.caption(
                    "Compromiso: "
                    f"{avance.get('fecha_compromiso') or 'Sin fecha'}"
                )

            if avance.get(
                "proxima_accion"
            ):

                st.write(
                    "**➡️ Próxima acción:**"
                )

                st.write(
                    avance[
                        "proxima_accion"
                    ]
                )


# ============================================================
# COMPROMISOS
# ============================================================

def mostrar_compromisos(reuniones):

    st.subheader(
        "🎯 Compromisos abiertos"
    )

    compromisos = obtener_compromisos(
        reuniones
    )

    if not compromisos:

        st.info(
            "No existen compromisos registrados."
        )

        return

    datos = []

    for compromiso in compromisos:

        datos.append({
            "Proyecto":
                compromiso["proyecto"],

            "Acción":
                compromiso["accion"],

            "Responsable":
                compromiso["responsable"],

            "Fecha":
                compromiso["fecha_compromiso"],

            "Reunión":
                compromiso["fecha_reunion"]
        })

    st.dataframe(
        datos,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# INFORME EJECUTIVO
# ============================================================

def mostrar_informe(reunion):

    st.subheader(
        "🤖 Resumen ejecutivo"
    )

    resumen = generar_resumen_texto(
        reunion
    )

    st.text_area(
        "Informe de la reunión",
        value=resumen,
        height=400,
        disabled=True
    )


# ============================================================
# MÓDULO PRINCIPAL
# ============================================================

def mostrar_reuniones():

    # Seguridad compartida con Portafolio INTILED
    if not esta_autenticado():

        mostrar_login()
        return

    reuniones = inicializar_reuniones()

    proyectos = obtener_proyectos()

    mostrar_encabezado()

    st.divider()

    tab1, tab2, tab3 = st.tabs(
        [
            "📅 Reunión",
            "🎯 Compromisos",
            "➕ Nueva reunión"
        ]
    )

    # ========================================================
    # REUNIÓN ACTIVA
    # ========================================================

    with tab1:

        if not reuniones:

            st.info(
                "Todavía no existen reuniones. "
                "Crea la primera desde la pestaña "
                "'Nueva reunión'."
            )

        else:

            reunion = seleccionar_reunion(
                reuniones
            )

            if reunion:

                st.divider()

                st.markdown(
                    f"## {reunion.get('titulo', '')}"
                )

                st.caption(
                    f"Fecha: {reunion.get('fecha', '')}"
                )

                if reunion.get(
                    "observaciones"
                ):

                    st.write(
                        reunion[
                            "observaciones"
                        ]
                    )

                mostrar_resumen_reunion(
                    reunion
                )

                st.divider()

                mostrar_registro_avance(
                    reunion,
                    proyectos
                )

                st.divider()

                mostrar_movimientos(
                    reunion
                )

                st.divider()

                mostrar_informe(
                    reunion
                )

    # ========================================================
    # COMPROMISOS
    # ========================================================

    with tab2:

        mostrar_compromisos(
            reuniones
        )

    # ========================================================
    # NUEVA REUNIÓN
    # ========================================================

    with tab3:

        mostrar_crear_reunion(
            reuniones
        )
