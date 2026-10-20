# ============================================================
# INTI PROJECTS AI
# MOTOR DE REQUISITOS Y BRECHAS
# ============================================================
#
# OBJETIVO:
# Comparar requisitos de una convocatoria contra:
#
# 1. ADN empresarial INTILED
# 2. Experiencia empresarial
# 3. Equipo profesional
# 4. Capacidades técnicas
# 5. Productos
# 6. Certificaciones
# 7. Capacidad financiera
#
# ESTADOS:
#
# CUMPLE
# CUMPLE_PARCIAL
# NO_CUMPLE
# PENDIENTE
#
# IMPORTANTE:
# Este motor NO debe asumir cumplimiento cuando no existe
# evidencia suficiente.
# ============================================================


from data.intiled_profile import INTILED_PROFILE

from data.intiled_experience import (
    obtener_experiencia_intiled
)

from data.intiled_team import (
    obtener_equipo_intiled
)


# ============================================================
# CONSTANTES
# ============================================================

ESTADO_CUMPLE = "CUMPLE"

ESTADO_PARCIAL = "CUMPLE_PARCIAL"

ESTADO_NO_CUMPLE = "NO_CUMPLE"

ESTADO_PENDIENTE = "PENDIENTE"


# ============================================================
# NIVELES DE RIESGO
# ============================================================

RIESGO_BAJO = "BAJO"

RIESGO_MEDIO = "MEDIO"

RIESGO_ALTO = "ALTO"

RIESGO_CRITICO = "CRITICO"


# ============================================================
# CREAR RESULTADO ESTÁNDAR
# ============================================================

def crear_resultado(
    requisito,
    tipo,
    estado,
    evidencia="",
    observacion="",
    riesgo=RIESGO_MEDIO,
    critico=False
):

    return {

        "requisito": requisito,

        "tipo": tipo,

        "estado": estado,

        "evidencia": evidencia,

        "observacion": observacion,

        "riesgo": riesgo,

        "critico": critico
    }


# ============================================================
# EVALUAR EXPERIENCIA EMPRESARIAL
# ============================================================

def evaluar_experiencia_empresa(
    requisito
):

    experiencias = obtener_experiencia_intiled()

    componentes_requeridos = requisito.get(
        "componentes",
        []
    )

    cantidad_requerida = requisito.get(
        "cantidad_contratos",
        1
    )

    valor_minimo = requisito.get(
        "valor_minimo",
        0
    )

    coincidencias = []

    for experiencia in experiencias:

        componentes = experiencia.get(
            "componentes",
            []
        )

        componentes_encontrados = [

            componente

            for componente
            in componentes_requeridos

            if componente in componentes
        ]

        if not componentes_encontrados:
            continue

        # ----------------------------------------------------
        # VALOR
        # ----------------------------------------------------

        valor = experiencia.get(
            "valor_acreditable",
            0
        )

        if valor_minimo:

            if valor < valor_minimo:
                continue

        coincidencias.append(
            experiencia
        )

    # ========================================================
    # NO HAY EXPERIENCIA REGISTRADA
    # ========================================================

    if not experiencias:

        return crear_resultado(

            requisito=requisito.get(
                "descripcion",
                "Experiencia empresarial"
            ),

            tipo="experiencia_empresa",

            estado=ESTADO_PENDIENTE,

            evidencia=(
                "No existen contratos registrados "
                "en la base de experiencia INTILED."
            ),

            observacion=(
                "Debe verificarse el RUP, contratos, "
                "certificaciones y actas de INTILED."
            ),

            riesgo=RIESGO_CRITICO,

            critico=True
        )

    # ========================================================
    # CUMPLE
    # ========================================================

    if len(coincidencias) >= cantidad_requerida:

        verificadas = [

            experiencia

            for experiencia in coincidencias

            if experiencia.get(
                "verificado",
                False
            )
        ]

        if len(verificadas) >= cantidad_requerida:

            return crear_resultado(

                requisito=requisito.get(
                    "descripcion",
                    "Experiencia empresarial"
                ),

                tipo="experiencia_empresa",

                estado=ESTADO_CUMPLE,

                evidencia=(
                    f"{len(verificadas)} experiencia(s) "
                    "verificada(s) encontrada(s)."
                ),

                observacion=(
                    "Existe experiencia empresarial "
                    "registrada y verificada."
                ),

                riesgo=RIESGO_BAJO
            )

        return crear_resultado(

            requisito=requisito.get(
                "descripcion",
                "Experiencia empresarial"
            ),

            tipo="experiencia_empresa",

            estado=ESTADO_PARCIAL,

            evidencia=(
                f"{len(coincidencias)} experiencia(s) "
                "relacionada(s), pero falta verificar "
                "documentación."
            ),

            observacion=(
                "Revisar certificados, contratos, "
                "actas y RUP."
            ),

            riesgo=RIESGO_ALTO,

            critico=True
        )

    # ========================================================
    # NO CUMPLE
    # ========================================================

    return crear_resultado(

        requisito=requisito.get(
            "descripcion",
            "Experiencia empresarial"
        ),

        tipo="experiencia_empresa",

        estado=ESTADO_NO_CUMPLE,

        evidencia=(
            f"Solo se encontraron "
            f"{len(coincidencias)} experiencia(s) "
            "compatible(s)."
        ),

        observacion=(
            "Evaluar participación mediante "
            "consorcio, unión temporal o aliado."
        ),

        riesgo=RIESGO_CRITICO,

        critico=True
    )


# ============================================================
# EVALUAR PERSONAL
# ============================================================

def evaluar_personal(
    requisito
):

    equipo = obtener_equipo_intiled()

    profesion_requerida = requisito.get(
        "profesion",
        ""
    ).lower()

    areas_requeridas = requisito.get(
        "areas",
        []
    )

    candidatos = []

    for profesional in equipo:

        profesion = profesional.get(
            "profesion",
            ""
        ).lower()

        areas = profesional.get(
            "areas_experiencia",
            []
        )

        cumple_profesion = True

        if profesion_requerida:

            cumple_profesion = (
                profesion_requerida
                in profesion
            )

        coincidencias_area = [

            area

            for area in areas_requeridas

            if area in areas
        ]

        if (
            cumple_profesion
            and (
                not areas_requeridas
                or coincidencias_area
            )
        ):

            candidatos.append(
                profesional
            )

    # ========================================================
    # BASE VACÍA
    # ========================================================

    if not equipo:

        return crear_resultado(

            requisito=requisito.get(
                "descripcion",
                "Personal profesional"
            ),

            tipo="personal",

            estado=ESTADO_PENDIENTE,

            evidencia=(
                "La base de profesionales "
                "INTILED aún no está cargada."
            ),

            observacion=(
                "Debe verificarse la disponibilidad "
                "y documentación del equipo."
            ),

            riesgo=RIESGO_ALTO
        )

    # ========================================================
    # CANDIDATOS
    # ========================================================

    if candidatos:

        verificados = [

            candidato

            for candidato in candidatos

            if candidato.get(
                "verificado",
                False
            )
        ]

        if verificados:

            return crear_resultado(

                requisito=requisito.get(
                    "descripcion",
                    "Personal profesional"
                ),

                tipo="personal",

                estado=ESTADO_CUMPLE,

                evidencia=(
                    f"{len(verificados)} profesional(es) "
                    "verificado(s) compatible(s)."
                ),

                observacion=(
                    "Existe personal compatible "
                    "registrado."
                ),

                riesgo=RIESGO_BAJO
            )

        return crear_resultado(

            requisito=requisito.get(
                "descripcion",
                "Personal profesional"
            ),

            tipo="personal",

            estado=ESTADO_PARCIAL,

            evidencia=(
                f"{len(candidatos)} posible(s) "
                "profesional(es) encontrado(s)."
            ),

            observacion=(
                "Debe verificarse formación, "
                "experiencia y certificados."
            ),

            riesgo=RIESGO_MEDIO
        )

    # ========================================================
    # SIN CANDIDATO
    # ========================================================

    return crear_resultado(

        requisito=requisito.get(
            "descripcion",
            "Personal profesional"
        ),

        tipo="personal",

        estado=ESTADO_NO_CUMPLE,

        evidencia=(
            "No se encontró un profesional "
            "compatible en la base actual."
        ),

        observacion=(
            "Evaluar contratación, alianza "
            "o incorporación de especialista."
        ),

        riesgo=RIESGO_ALTO
    )


# ============================================================
# EVALUAR CAPACIDAD TÉCNICA
# ============================================================

def evaluar_capacidad_tecnica(
    requisito
):

    capacidades = [

        capacidad.lower()

        for capacidad
        in INTILED_PROFILE[
            "capacidades_tecnicas"
        ]
    ]

    keywords = requisito.get(
        "keywords",
        []
    )

    coincidencias = []

    for keyword in keywords:

        keyword_lower = keyword.lower()

        for capacidad in capacidades:

            if (
                keyword_lower in capacidad
                or capacidad in keyword_lower
            ):

                coincidencias.append(
                    keyword
                )

                break

    if not keywords:

        return crear_resultado(

            requisito=requisito.get(
                "descripcion",
                "Capacidad técnica"
            ),

            tipo="capacidad_tecnica",

            estado=ESTADO_PENDIENTE,

            evidencia=(
                "No se definieron criterios "
                "técnicos comparables."
            ),

            riesgo=RIESGO_MEDIO
        )

    porcentaje = (
        len(set(coincidencias))
        / len(keywords)
    )

    if porcentaje >= 0.75:

        estado = ESTADO_CUMPLE
        riesgo = RIESGO_BAJO

    elif porcentaje >= 0.40:

        estado = ESTADO_PARCIAL
        riesgo = RIESGO_MEDIO

    else:

        estado = ESTADO_NO_CUMPLE
        riesgo = RIESGO_ALTO

    return crear_resultado(

        requisito=requisito.get(
            "descripcion",
            "Capacidad técnica"
        ),

        tipo="capacidad_tecnica",

        estado=estado,

        evidencia=(
            "Coincidencias encontradas: "
            + (
                ", ".join(
                    set(coincidencias)
                )
                if coincidencias
                else "ninguna"
            )
        ),

        observacion=(
            "Este resultado mide afinidad técnica. "
            "No reemplaza certificaciones o "
            "experiencia contractual."
        ),

        riesgo=riesgo
    )


# ============================================================
# EVALUAR CERTIFICACIÓN
# ============================================================

def evaluar_certificacion(
    requisito
):

    certificaciones = INTILED_PROFILE.get(
        "certificaciones",
        []
    )

    requerida = requisito.get(
        "certificacion",
        ""
    ).lower()

    if not certificaciones:

        return crear_resultado(

            requisito=requisito.get(
                "descripcion",
                requerida
            ),

            tipo="certificacion",

            estado=ESTADO_PENDIENTE,

            evidencia=(
                "No existen certificaciones "
                "cargadas en el ADN INTILED."
            ),

            observacion=(
                "Verificar documentación "
                "corporativa."
            ),

            riesgo=RIESGO_ALTO,

            critico=requisito.get(
                "critico",
                False
            )
        )

    for certificacion in certificaciones:

        nombre = str(
            certificacion
        ).lower()

        if requerida in nombre:

            return crear_resultado(

                requisito=requisito.get(
                    "descripcion",
                    requerida
                ),

                tipo="certificacion",

                estado=ESTADO_CUMPLE,

                evidencia=str(
                    certificacion
                ),

                riesgo=RIESGO_BAJO
            )

    return crear_resultado(

        requisito=requisito.get(
            "descripcion",
            requerida
        ),

        tipo="certificacion",

        estado=ESTADO_NO_CUMPLE,

        evidencia=(
            "Certificación no encontrada."
        ),

        observacion=(
            "Verificar si puede obtenerse "
            "o aportarse mediante fabricante "
            "o aliado cuando el proceso lo permita."
        ),

        riesgo=RIESGO_ALTO,

        critico=requisito.get(
            "critico",
            False
        )
    )


# ============================================================
# EVALUAR CAPACIDAD FINANCIERA
# ============================================================

def evaluar_financiero(
    requisito
):

    financiero = INTILED_PROFILE.get(
        "capacidad_financiera",
        {}
    )

    if not financiero.get(
        "disponible",
        False
    ):

        return crear_resultado(

            requisito=requisito.get(
                "descripcion",
                "Requisito financiero"
            ),

            tipo="financiero",

            estado=ESTADO_PENDIENTE,

            evidencia=(
                "Información financiera "
                "no cargada."
            ),

            observacion=(
                "Debe verificarse con estados "
                "financieros y/o RUP vigente."
            ),

            riesgo=RIESGO_CRITICO,

            critico=True
        )

    return crear_resultado(

        requisito=requisito.get(
            "descripcion",
            "Requisito financiero"
        ),

        tipo="financiero",

        estado=ESTADO_PENDIENTE,

        evidencia=(
            "Información financiera disponible."
        ),

        observacion=(
            "La comparación numérica se "
            "implementará cuando se carguen "
            "los indicadores financieros."
        ),

        riesgo=RIESGO_MEDIO
    )


# ============================================================
# ENRUTADOR DE REQUISITOS
# ============================================================

def evaluar_requisito(
    requisito
):

    tipo = requisito.get(
        "tipo",
        ""
    )

    if tipo == "experiencia_empresa":

        return evaluar_experiencia_empresa(
            requisito
        )

    if tipo == "personal":

        return evaluar_personal(
            requisito
        )

    if tipo == "capacidad_tecnica":

        return evaluar_capacidad_tecnica(
            requisito
        )

    if tipo == "certificacion":

        return evaluar_certificacion(
            requisito
        )

    if tipo == "financiero":

        return evaluar_financiero(
            requisito
        )

    return crear_resultado(

        requisito=requisito.get(
            "descripcion",
            "Requisito"
        ),

        tipo=tipo,

        estado=ESTADO_PENDIENTE,

        evidencia=(
            "Tipo de requisito todavía "
            "no soportado por INTI."
        ),

        observacion=(
            "Requiere revisión manual."
        ),

        riesgo=RIESGO_MEDIO
    )


# ============================================================
# ANALIZAR CONVOCATORIA COMPLETA
# ============================================================

def analizar_requisitos(
    requisitos
):

    resultados = []

    for requisito in requisitos:

        resultado = evaluar_requisito(
            requisito
        )

        resultados.append(
            resultado
        )

    return resultados


# ============================================================
# IDENTIFICAR BRECHAS
# ============================================================

def identificar_brechas(
    resultados
):

    brechas = []

    for resultado in resultados:

        if resultado["estado"] in [
            ESTADO_PARCIAL,
            ESTADO_NO_CUMPLE,
            ESTADO_PENDIENTE
        ]:

            brechas.append(
                resultado
            )

    return brechas


# ============================================================
# REQUISITOS CRÍTICOS
# ============================================================

def identificar_criticos(
    resultados
):

    return [

        resultado

        for resultado in resultados

        if resultado.get(
            "critico",
            False
        )

        and resultado["estado"]
        != ESTADO_CUMPLE
    ]


# ============================================================
# RESUMEN
# ============================================================

def generar_resumen_requisitos(
    resultados
):

    resumen = {

        "total": len(resultados),

        "cumple": 0,

        "parcial": 0,

        "no_cumple": 0,

        "pendiente": 0,

        "criticos": 0
    }

    for resultado in resultados:

        estado = resultado[
            "estado"
        ]

        if estado == ESTADO_CUMPLE:
            resumen["cumple"] += 1

        elif estado == ESTADO_PARCIAL:
            resumen["parcial"] += 1

        elif estado == ESTADO_NO_CUMPLE:
            resumen["no_cumple"] += 1

        elif estado == ESTADO_PENDIENTE:
            resumen["pendiente"] += 1

        if (
            resultado.get(
                "critico",
                False
            )
            and estado != ESTADO_CUMPLE
        ):

            resumen["criticos"] += 1

    return resumen
