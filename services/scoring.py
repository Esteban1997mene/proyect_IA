# ============================================================
# INTI PROJECTS AI
# INTILED OPPORTUNITY ENGINE V1
# ============================================================
#
# OBJETIVO:
# Calcular la compatibilidad estratégica de una oportunidad
# con INTILED y generar una recomendación.
#
# IMPORTANTE:
# Un Score alto NO puede ocultar un requisito crítico.
# ============================================================

from data.intiled_profile import INTILED_PROFILE


# ============================================================
# PESOS DEL INTILED SCORE
# ============================================================

PESOS = {
    "afinidad": 0.20,
    "experiencia": 0.20,
    "personal": 0.15,
    "tecnologia": 0.15,
    "habilitantes": 0.10,
    "economico": 0.05,
    "ubicacion": 0.05,
    "tiempo": 0.05,
    "competitividad": 0.05
}


# ============================================================
# NORMALIZAR PUNTAJE
# ============================================================

def normalizar(valor):

    try:
        valor = float(valor)

    except (TypeError, ValueError):
        return 0

    if valor < 0:
        return 0

    if valor > 100:
        return 100

    return valor


# ============================================================
# CALCULAR SCORE
# ============================================================

def calcular_intiled_score(factores):

    score = 0

    detalle = {}

    for factor, peso in PESOS.items():

        valor = normalizar(
            factores.get(
                factor,
                0
            )
        )

        aporte = valor * peso

        detalle[factor] = {
            "valor": round(valor, 1),
            "peso": peso,
            "aporte": round(aporte, 1)
        }

        score += aporte

    return {
        "score": round(score, 1),
        "detalle": detalle
    }


# ============================================================
# CLASIFICAR SCORE
# ============================================================

def clasificar_score(score):

    if score >= 85:
        return "MUY_ALTA"

    if score >= 70:
        return "ALTA"

    if score >= 55:
        return "MEDIA"

    if score >= 40:
        return "BAJA"

    return "MUY_BAJA"


# ============================================================
# IDENTIFICAR BRECHAS CRÍTICAS
# ============================================================

def obtener_brechas_criticas(
    resultados_requisitos
):

    brechas = []

    for requisito in resultados_requisitos:

        critico = requisito.get(
            "critico",
            False
        )

        estado = requisito.get(
            "estado",
            ""
        )

        if (
            critico
            and estado != "CUMPLE"
        ):

            brechas.append(
                requisito
            )

    return brechas


# ============================================================
# IDENTIFICAR INCUMPLIMIENTOS
# ============================================================

def obtener_incumplimientos(
    resultados_requisitos
):

    return [

        requisito

        for requisito in resultados_requisitos

        if requisito.get(
            "estado"
        ) == "NO_CUMPLE"
    ]


# ============================================================
# IDENTIFICAR PENDIENTES
# ============================================================

def obtener_pendientes(
    resultados_requisitos
):

    return [

        requisito

        for requisito in resultados_requisitos

        if requisito.get(
            "estado"
        ) in [
            "PENDIENTE",
            "CUMPLE_PARCIAL"
        ]
    ]


# ============================================================
# DETERMINAR SI LA BRECHA PUEDE SOLUCIONARSE CON ALIADO
# ============================================================

def brecha_potencialmente_asociable(
    requisito
):

    tipo = requisito.get(
        "tipo",
        ""
    )

    tipos_asociables = [
        "experiencia_empresa",
        "personal",
        "capacidad_tecnica"
    ]

    return tipo in tipos_asociables


# ============================================================
# TOMAR DECISIÓN
# ============================================================

def determinar_decision(
    score,
    resultados_requisitos
):

    criticos = obtener_brechas_criticas(
        resultados_requisitos
    )

    incumplimientos = obtener_incumplimientos(
        resultados_requisitos
    )

    pendientes = obtener_pendientes(
        resultados_requisitos
    )

    # ========================================================
    # 1. BRECHAS CRÍTICAS
    # ========================================================

    if criticos:

        asociables = [

            requisito

            for requisito in criticos

            if brecha_potencialmente_asociable(
                requisito
            )
        ]

        no_asociables = [

            requisito

            for requisito in criticos

            if not brecha_potencialmente_asociable(
                requisito
            )
        ]

        # ----------------------------------------------------
        # Score alto + brecha solucionable
        # ----------------------------------------------------

        if (
            score >= 70
            and asociables
            and not no_asociables
        ):

            return {
                "codigo": "ALIADO",
                "decision": "PRESENTARSE CON ALIADO",
                "semaforo": "🟡",
                "prioridad": "ALTA"
            }

        # ----------------------------------------------------
        # Información crítica todavía pendiente
        # ----------------------------------------------------

        estados_criticos = [

            requisito.get("estado")

            for requisito in criticos
        ]

        if (
            score >= 55
            and all(
                estado in [
                    "PENDIENTE",
                    "CUMPLE_PARCIAL"
                ]
                for estado in estados_criticos
            )
        ):

            return {
                "codigo": "REVISION",
                "decision": "REVISIÓN ESTRATÉGICA",
                "semaforo": "🟠",
                "prioridad": "MEDIA"
            }

        # ----------------------------------------------------
        # Brecha crítica fuerte
        # ----------------------------------------------------

        return {
            "codigo": "NO_PRIORIZAR",
            "decision": "NO PRIORIZAR",
            "semaforo": "🔴",
            "prioridad": "BAJA"
        }

    # ========================================================
    # 2. SIN BRECHAS CRÍTICAS
    # ========================================================

    if score >= 80:

        return {
            "codigo": "PRESENTARSE",
            "decision": "PRESENTARSE",
            "semaforo": "🟢",
            "prioridad": "MUY ALTA"
        }

    if score >= 65:

        return {
            "codigo": "PRESENTARSE",
            "decision": "PRESENTARSE",
            "semaforo": "🟢",
            "prioridad": "ALTA"
        }

    if score >= 50:

        return {
            "codigo": "REVISION",
            "decision": "REVISIÓN ESTRATÉGICA",
            "semaforo": "🟠",
            "prioridad": "MEDIA"
        }

    return {
        "codigo": "NO_PRIORIZAR",
        "decision": "NO PRIORIZAR",
        "semaforo": "🔴",
        "prioridad": "BAJA"
    }


# ============================================================
# GENERAR FORTALEZAS
# ============================================================

def generar_fortalezas(
    factores,
    resultados_requisitos
):

    fortalezas = []

    nombres = {
        "afinidad": "Alta afinidad con las líneas INTILED",
        "experiencia": "Experiencia relacionada",
        "personal": "Equipo profesional compatible",
        "tecnologia": "Compatibilidad tecnológica",
        "habilitantes": "Buen nivel de cumplimiento habilitante",
        "economico": "Viabilidad económica favorable",
        "ubicacion": "Ubicación operativamente favorable",
        "tiempo": "Tiempo suficiente para preparar oferta",
        "competitividad": "Condiciones competitivas favorables"
    }

    for factor, valor in factores.items():

        valor = normalizar(valor)

        if (
            factor in nombres
            and valor >= 75
        ):

            fortalezas.append(
                nombres[factor]
            )

    for requisito in resultados_requisitos:

        if requisito.get(
            "estado"
        ) == "CUMPLE":

            descripcion = requisito.get(
                "requisito"
            )

            if descripcion:

                fortalezas.append(
                    descripcion
                )

    return list(
        dict.fromkeys(
            fortalezas
        )
    )


# ============================================================
# GENERAR BRECHAS
# ============================================================

def generar_brechas(
    resultados_requisitos
):

    brechas = []

    for requisito in resultados_requisitos:

        estado = requisito.get(
            "estado"
        )

        if estado in [
            "NO_CUMPLE",
            "PENDIENTE",
            "CUMPLE_PARCIAL"
        ]:

            brechas.append({

                "requisito":
                    requisito.get(
                        "requisito",
                        ""
                    ),

                "tipo":
                    requisito.get(
                        "tipo",
                        ""
                    ),

                "estado":
                    estado,

                "riesgo":
                    requisito.get(
                        "riesgo",
                        ""
                    ),

                "critico":
                    requisito.get(
                        "critico",
                        False
                    ),

                "observacion":
                    requisito.get(
                        "observacion",
                        ""
                    )
            })

    return brechas


# ============================================================
# GENERAR ESTRATEGIA
# ============================================================

def generar_estrategia(
    decision,
    brechas
):

    codigo = decision[
        "codigo"
    ]

    if codigo == "PRESENTARSE":

        return (
            "Priorizar la oportunidad y avanzar "
            "a la revisión documental completa. "
            "Preparar matriz de cumplimiento, "
            "estrategia técnica, económica y "
            "documentación habilitante."
        )

    if codigo == "ALIADO":

        tipos_brecha = [

            brecha.get(
                "tipo"
            )

            for brecha in brechas

            if brecha.get(
                "critico"
            )
        ]

        if "experiencia_empresa" in tipos_brecha:

            return (
                "La oportunidad presenta alta afinidad "
                "con INTILED, pero existe una brecha "
                "de experiencia empresarial. Evaluar "
                "consorcio, unión temporal o alianza "
                "con una empresa que aporte la "
                "experiencia específica requerida."
            )

        if "personal" in tipos_brecha:

            return (
                "La oportunidad es atractiva, pero "
                "requiere fortalecer el equipo "
                "profesional. Identificar especialista "
                "o aliado que cumpla exactamente "
                "los requisitos del proceso."
            )

        return (
            "La oportunidad es estratégica, pero "
            "presenta una brecha solucionable. "
            "Evaluar participación mediante aliado."
        )

    if codigo == "REVISION":

        return (
            "No tomar todavía una decisión de "
            "participación. Completar información "
            "pendiente y verificar los requisitos "
            "habilitantes antes de comprometer "
            "recursos en la preparación de la oferta."
        )

    return (
        "No destinar recursos significativos a esta "
        "oportunidad en su estado actual. Revisarla "
        "únicamente si cambian los requisitos o se "
        "identifica una alianza estratégica viable."
    )


# ============================================================
# MOTOR PRINCIPAL
# ============================================================

def evaluar_oportunidad(
    factores,
    resultados_requisitos
):

    calculo = calcular_intiled_score(
        factores
    )

    score = calculo[
        "score"
    ]

    nivel = clasificar_score(
        score
    )

    decision = determinar_decision(
        score,
        resultados_requisitos
    )

    fortalezas = generar_fortalezas(
        factores,
        resultados_requisitos
    )

    brechas = generar_brechas(
        resultados_requisitos
    )

    estrategia = generar_estrategia(
        decision,
        brechas
    )

    return {

        "score": score,

        "nivel_compatibilidad": nivel,

        "decision": decision,

        "fortalezas": fortalezas,

        "brechas": brechas,

        "estrategia": estrategia,

        "detalle_score": calculo[
            "detalle"
        ],

        "requiere_aliado": (
            decision["codigo"]
            == "ALIADO"
        ),

        "puede_priorizarse": (
            decision["codigo"]
            in [
                "PRESENTARSE",
                "ALIADO"
            ]
        )
    }
