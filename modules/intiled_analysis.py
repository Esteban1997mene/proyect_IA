import streamlit as st

from services.requirements_engine import (
    analizar_requisitos,
    generar_resumen_requisitos
)

from services.scoring import (
    evaluar_oportunidad
)


# ============================================================
# COLORES / ICONOS DE ESTADO
# ============================================================

def icono_estado(estado):

    if estado == "CUMPLE":
        return "🟢"

    if estado == "CUMPLE_PARCIAL":
        return "🟡"

    if estado == "NO_CUMPLE":
        return "🔴"

    return "⚪"


# ============================================================
# PANTALLA PRINCIPAL
# ============================================================

def mostrar_analisis_intiled():

    st.title("🧠 Análisis Estratégico INTILED")

    st.caption(
        "Evaluación de oportunidades mediante el ADN "
        "empresarial de INTILED SAS BIC."
    )

    st.divider()

    # ========================================================
    # CONVOCATORIA DE PRUEBA
    # ========================================================

    st.subheader("📋 Oportunidad analizada")

    st.info(
        "Esta primera versión utiliza una oportunidad "
        "de prueba para validar el motor INTILED. "
        "Posteriormente los datos llegarán directamente "
        "desde el Radar."
    )

    with st.container(border=True):

        st.markdown(
            "### Modernización de alumbrado público "
            "con tecnología solar fotovoltaica"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**País**")
            st.write("🇨🇴 Colombia")

        with col2:
            st.write("**Sector**")
            st.write("Alumbrado público")

        with col3:
            st.write("**Tecnología**")
            st.write("Solar fotovoltaica + LED")

    # ========================================================
    # REQUISITOS DE PRUEBA
    # ========================================================

    requisitos = [

        {
            "tipo": "experiencia_empresa",

            "descripcion": (
                "Acreditar mínimo 2 contratos relacionados "
                "con alumbrado público y sistemas fotovoltaicos."
            ),

            "componentes": [
                "alumbrado_publico",
                "sistemas_fotovoltaicos"
            ],

            "cantidad_contratos": 2,

            "valor_minimo": 0,

            "critico": True
        },

        {
            "tipo": "personal",

            "descripcion": (
                "Ingeniero electricista con experiencia "
                "en alumbrado público."
            ),

            "profesion": "ingeniero electricista",

            "areas": [
                "alumbrado_publico"
            ],

            "critico": False
        },

        {
            "tipo": "capacidad_tecnica",

            "descripcion": (
                "Capacidad para implementar alumbrado "
                "solar y sistemas de automatización."
            ),

            "keywords": [
                "alumbrado solar",
                "automatización",
                "sistemas solares fotovoltaicos"
            ],

            "critico": False
        },

        {
            "tipo": "financiero",

            "descripcion": (
                "Cumplimiento de indicadores financieros "
                "habilitantes."
            ),

            "critico": True
        }
    ]

    # ========================================================
    # MOTOR DE REQUISITOS
    # ========================================================

    resultados = analizar_requisitos(
        requisitos
    )

    resumen = generar_resumen_requisitos(
        resultados
    )

    # ========================================================
    # FACTORES TEMPORALES DE PRUEBA
    # ========================================================
    #
    # IMPORTANTE:
    # Estos valores son únicamente para probar la interfaz.
    # Después serán calculados automáticamente.
    # ========================================================

    factores = {

        "afinidad": 95,

        "experiencia": 60,

        "personal": 80,

        "tecnologia": 95,

        "habilitantes": 55,

        "economico": 70,

        "ubicacion": 95,

        "tiempo": 80,

        "competitividad": 80
    }

    # ========================================================
    # OPPORTUNITY ENGINE
    # ========================================================

    analisis = evaluar_oportunidad(
        factores,
        resultados
    )

    score = analisis["score"]

    decision = analisis["decision"]

    # ========================================================
    # SCORE PRINCIPAL
    # ========================================================

    st.write("")
    st.subheader("🎯 Evaluación estratégica")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "INTILED Score",
            f"{score}/100"
        )

    with col2:

        st.metric(
            "Compatibilidad",
            analisis[
                "nivel_compatibilidad"
            ].replace("_", " ")
        )

    with col3:

        st.metric(
            "Brechas críticas",
            resumen["criticos"]
        )

    # ========================================================
    # DECISIÓN
    # ========================================================

    st.write("")

    codigo_decision = decision["codigo"]

    mensaje_decision = (
        f"{decision['semaforo']} "
        f"{decision['decision']}"
    )

    if codigo_decision == "PRESENTARSE":

        st.success(
            mensaje_decision
        )

    elif codigo_decision == "ALIADO":

        st.warning(
            mensaje_decision
        )

    elif codigo_decision == "REVISION":

        st.warning(
            mensaje_decision
        )

    else:

        st.error(
            mensaje_decision
        )

    st.write(
        f"**Prioridad:** "
        f"{decision['prioridad']}"
    )

    st.divider()

    # ========================================================
    # FACTORES DEL SCORE
    # ========================================================

    st.subheader(
        "📊 Factores de compatibilidad"
    )

    nombres_factores = {

        "afinidad":
            "Afinidad con INTILED",

        "experiencia":
            "Experiencia empresarial",

        "personal":
            "Equipo profesional",

        "tecnologia":
            "Compatibilidad tecnológica",

        "habilitantes":
            "Requisitos habilitantes",

        "economico":
            "Viabilidad económica",

        "ubicacion":
            "Capacidad territorial",

        "tiempo":
            "Tiempo de preparación",

        "competitividad":
            "Competitividad"
    }

    for factor, datos in analisis[
        "detalle_score"
    ].items():

        nombre = nombres_factores.get(
            factor,
            factor
        )

        valor = datos["valor"]

        st.write(
            f"**{nombre}: {valor}/100**"
        )

        st.progress(
            int(valor)
        )

    st.divider()

    # ========================================================
    # MATRIZ DE REQUISITOS
    # ========================================================

    st.subheader(
        "📋 Matriz de requisitos"
    )

    for resultado in resultados:

        estado = resultado[
            "estado"
        ]

        icono = icono_estado(
            estado
        )

        with st.container(
            border=True
        ):

            col1, col2 = st.columns(
                [4, 1]
            )

            with col1:

                st.markdown(
                    f"**{icono} "
                    f"{resultado['requisito']}**"
                )

                st.write(
                    f"**Evidencia:** "
                    f"{resultado['evidencia']}"
                )

                if resultado[
                    "observacion"
                ]:

                    st.caption(
                        resultado[
                            "observacion"
                        ]
                    )

            with col2:

                st.write(
                    f"**{estado.replace('_', ' ')}**"
                )

                st.write(
                    f"Riesgo: "
                    f"{resultado['riesgo']}"
                )

                if resultado[
                    "critico"
                ]:

                    st.error(
                        "CRÍTICO"
                    )

    st.divider()

    # ========================================================
    # FORTALEZAS Y BRECHAS
    # ========================================================

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "💪 Fortalezas"
        )

        fortalezas = analisis[
            "fortalezas"
        ]

        if fortalezas:

            for fortaleza in fortalezas:

                st.success(
                    f"✓ {fortaleza}"
                )

        else:

            st.info(
                "No se identificaron "
                "fortalezas suficientes."
            )

    with col2:

        st.subheader(
            "⚠️ Brechas"
        )

        brechas = analisis[
            "brechas"
        ]

        if brechas:

            for brecha in brechas:

                if brecha[
                    "critico"
                ]:

                    st.error(
                        f"🔴 "
                        f"{brecha['requisito']}"
                    )

                else:

                    st.warning(
                        f"🟡 "
                        f"{brecha['requisito']}"
                    )

        else:

            st.success(
                "No se detectaron "
                "brechas relevantes."
            )

    st.divider()

    # ========================================================
    # ESTRATEGIA INTI
    # ========================================================

    st.subheader(
        "🤖 Estrategia recomendada por INTI"
    )

    st.info(
        analisis[
            "estrategia"
        ]
    )

    st.write("")

    # ========================================================
    # ACCIONES
    # ========================================================

    st.subheader(
        "🚀 Próximas acciones"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.button(
            "📄 Revisar documentos",
            use_container_width=True
        )

    with col2:

        st.button(
            "🤝 Analizar alianza",
            use_container_width=True
        )

    with col3:

        st.button(
            "🏗️ Iniciar estructuración",
            use_container_width=True
        )
