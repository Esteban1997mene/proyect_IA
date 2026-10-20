# ============================================================
# INTI PROJECTS AI
# STRUCTURING ENGINE V1
# ============================================================
#
# Motor de preestructuración de proyectos.
#
# FUENTES:
# - Oportunidad detectada
# - Radar INTILED
# - ADN INTILED
#
# IMPORTANTE:
# El contenido generado es PROPUESTA INTI.
# No debe interpretarse como información oficial
# de la convocatoria hasta ser validado con TDR/pliegos.
# ============================================================


from data.intiled_profile import INTILED_PROFILE


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def limpiar_texto(valor):

    if valor is None:
        return ""

    return str(valor).strip()


def obtener_dato(
    oportunidad,
    campo,
    default=""
):

    valor = oportunidad.get(
        campo
    )

    if valor is None:
        return default

    return limpiar_texto(
        valor
    )


# ============================================================
# DETECTAR PERFIL DEL PROYECTO
# ============================================================

def detectar_perfil_proyecto(
    oportunidad
):

    texto = " ".join(
        [
            obtener_dato(
                oportunidad,
                "titulo"
            ),
            obtener_dato(
                oportunidad,
                "descripcion"
            ),
            obtener_dato(
                oportunidad,
                "sector"
            )
        ]
    ).lower()

    perfil = {

        "alumbrado_publico":
            False,

        "solar":
            False,

        "fotovoltaico":
            False,

        "eficiencia_energetica":
            False,

        "infraestructura_electrica":
            False,

        "automatizacion":
            False,

        "telegestion":
            False,

        "consultoria":
            False,

        "interventoria":
            False
    }

    # --------------------------------------------------------
    # ALUMBRADO PÚBLICO
    # --------------------------------------------------------

    if (
        "alumbrado publico" in texto
        or "alumbrado público" in texto
        or "luminaria" in texto
        or "iluminacion exterior" in texto
        or "iluminación exterior" in texto
    ):

        perfil[
            "alumbrado_publico"
        ] = True

    # --------------------------------------------------------
    # SOLAR
    # --------------------------------------------------------

    if "solar" in texto:

        perfil[
            "solar"
        ] = True

    # --------------------------------------------------------
    # FOTOVOLTAICO
    # --------------------------------------------------------

    if (
        "fotovoltaico" in texto
        or "fotovoltaica" in texto
    ):

        perfil[
            "fotovoltaico"
        ] = True

    # --------------------------------------------------------
    # EFICIENCIA ENERGÉTICA
    # --------------------------------------------------------

    if (
        "eficiencia energetica" in texto
        or "eficiencia energética" in texto
        or "ahorro energetico" in texto
        or "ahorro energético" in texto
    ):

        perfil[
            "eficiencia_energetica"
        ] = True

    # --------------------------------------------------------
    # INFRAESTRUCTURA ELÉCTRICA
    # --------------------------------------------------------

    if (
        "infraestructura electrica" in texto
        or "infraestructura eléctrica" in texto
        or "red electrica" in texto
        or "red eléctrica" in texto
        or "redes electricas" in texto
        or "redes eléctricas" in texto
    ):

        perfil[
            "infraestructura_electrica"
        ] = True

    # --------------------------------------------------------
    # AUTOMATIZACIÓN
    # --------------------------------------------------------

    if (
        "automatizacion" in texto
        or "automatización" in texto
        or "control inteligente" in texto
    ):

        perfil[
            "automatizacion"
        ] = True

    # --------------------------------------------------------
    # TELEGESTIÓN
    # --------------------------------------------------------

    if (
        "telegestion" in texto
        or "telegestión" in texto
        or "monitoreo remoto" in texto
    ):

        perfil[
            "telegestion"
        ] = True

    # --------------------------------------------------------
    # CONSULTORÍA
    # --------------------------------------------------------

    if (
        "consultoria" in texto
        or "consultoría" in texto
    ):

        perfil[
            "consultoria"
        ] = True

    # --------------------------------------------------------
    # INTERVENTORÍA
    # --------------------------------------------------------

    if (
        "interventoria" in texto
        or "interventoría" in texto
    ):

        perfil[
            "interventoria"
        ] = True

    return perfil


# ============================================================
# GENERAR DIAGNÓSTICO
# ============================================================

def generar_diagnostico(
    oportunidad
):

    titulo = obtener_dato(
        oportunidad,
        "titulo",
        "el proyecto identificado"
    )

    entidad = obtener_dato(
        oportunidad,
        "entidad",
        "la entidad contratante"
    )

    municipio = obtener_dato(
        oportunidad,
        "ciudad",
        ""
    )

    departamento = obtener_dato(
        oportunidad,
        "departamento",
        ""
    )

    ubicacion = ", ".join(
        [
            valor
            for valor in [
                municipio,
                departamento
            ]
            if valor
        ]
    )

    perfil = detectar_perfil_proyecto(
        oportunidad
    )

    # --------------------------------------------------------
    # PROBLEMA
    # --------------------------------------------------------

    if perfil[
        "alumbrado_publico"
    ]:

        problema = (
            "Se identifica preliminarmente una necesidad "
            "relacionada con la cobertura, modernización, "
            "ampliación o desempeño de la infraestructura "
            "de alumbrado público asociada al proceso "
            f"denominado '{titulo}'. "
            "La naturaleza y magnitud exacta del problema "
            "deberán validarse con los estudios previos, "
            "pliegos y documentos técnicos de la entidad."
        )

    elif perfil[
        "infraestructura_electrica"
    ]:

        problema = (
            "El proceso evidencia preliminarmente una "
            "necesidad de intervención sobre infraestructura "
            "eléctrica. Las condiciones actuales, magnitudes, "
            "causas y población beneficiaria deberán "
            "confirmarse mediante la documentación oficial."
        )

    else:

        problema = (
            "La oportunidad identificada plantea una "
            "necesidad de intervención que debe ser "
            "caracterizada técnicamente antes de formular "
            "una solución definitiva."
        )

    # --------------------------------------------------------
    # NECESIDAD
    # --------------------------------------------------------

    necesidad = (
        "Estructurar una alternativa técnica, económica "
        "y operativamente viable que responda al objeto "
        "del proceso y a los requerimientos establecidos "
        f"por {entidad}"
    )

    if ubicacion:

        necesidad += (
            f" para la intervención prevista en {ubicacion}"
        )

    necesidad += (
        ". La solución deberá ajustarse a la normativa "
        "aplicable y a las condiciones definitivas "
        "establecidas por la entidad contratante."
    )

    # --------------------------------------------------------
    # JUSTIFICACIÓN
    # --------------------------------------------------------

    justificacion = (
        "La estructuración previa permite identificar "
        "el alcance técnico, recursos, actividades, "
        "riesgos, costos, tiempos y requisitos necesarios "
        "para determinar la viabilidad de participación "
        "de INTILED y formular una propuesta competitiva. "
        "La versión definitiva deberá construirse con "
        "información validada de la convocatoria."
    )

    return {

        "problema":
            problema,

        "necesidad":
            necesidad,

        "justificacion":
            justificacion,

        "fuente":
            "PROPUESTA_INTI",

        "requiere_validacion":
            True
    }


# ============================================================
# GENERAR OBJETIVOS
# ============================================================

def generar_objetivos(
    oportunidad
):

    perfil = detectar_perfil_proyecto(
        oportunidad
    )

    ubicacion = obtener_dato(
        oportunidad,
        "ciudad",
        ""
    )

    # --------------------------------------------------------
    # OBJETIVO GENERAL
    # --------------------------------------------------------

    if perfil[
        "alumbrado_publico"
    ]:

        objetivo_general = (
            "Desarrollar una solución integral para la "
            "intervención del sistema de alumbrado público"
        )

        if ubicacion:

            objetivo_general += (
                f" en {ubicacion}"
            )

        objetivo_general += (
            ", de acuerdo con el alcance contractual, "
            "las condiciones técnicas del proyecto y "
            "la normativa aplicable."
        )

    elif perfil[
        "infraestructura_electrica"
    ]:

        objetivo_general = (
            "Desarrollar una solución técnica integral "
            "para la intervención de la infraestructura "
            "eléctrica objeto del proceso, garantizando "
            "su adecuada planeación, ejecución y puesta "
            "en operación conforme a los requisitos "
            "contractuales y normativos aplicables."
        )

    else:

        objetivo_general = (
            "Estructurar y ejecutar una solución integral "
            "que responda a las necesidades técnicas "
            "identificadas por la entidad contratante."
        )

    # --------------------------------------------------------
    # OBJETIVOS ESPECÍFICOS
    # --------------------------------------------------------

    objetivos = [

        "Verificar las condiciones técnicas y "
        "contractuales establecidas para el proyecto.",

        "Definir el alcance, actividades, recursos "
        "y entregables requeridos para la ejecución.",

        "Establecer una solución técnica compatible "
        "con los requisitos del proceso y la normativa "
        "aplicable.",

        "Determinar los recursos humanos, tecnológicos "
        "y logísticos necesarios para la intervención.",

        "Estructurar el cronograma, presupuesto, riesgos "
        "e indicadores necesarios para el seguimiento "
        "del proyecto."
    ]

    if (
        perfil["solar"]
        or perfil["fotovoltaico"]
    ):

        objetivos.append(
            "Evaluar la incorporación de soluciones "
            "fotovoltaicas cuando las condiciones "
            "técnicas y los documentos contractuales "
            "lo permitan."
        )

    if perfil[
        "telegestion"
    ]:

        objetivos.append(
            "Definir los requerimientos de monitoreo, "
            "control y telegestión asociados al sistema."
        )

    return {

        "general":
            objetivo_general,

        "especificos":
            objetivos,

        "fuente":
            "PROPUESTA_INTI",

        "requiere_validacion":
            True
    }


# ============================================================
# GENERAR ALCANCE
# ============================================================

def generar_alcance(
    oportunidad
):

    perfil = detectar_perfil_proyecto(
        oportunidad
    )

    componentes = []

    # --------------------------------------------------------
    # COMPONENTES GENERALES
    # --------------------------------------------------------

    componentes.extend(
        [
            "Revisión de la información técnica "
            "y contractual disponible.",

            "Validación del alcance definitivo "
            "del proyecto.",

            "Planeación de actividades y recursos.",

            "Definición de entregables y mecanismos "
            "de control de calidad.",

            "Identificación de riesgos técnicos, "
            "operativos y contractuales."
        ]
    )

    # --------------------------------------------------------
    # ALUMBRADO
    # --------------------------------------------------------

    if perfil[
        "alumbrado_publico"
    ]:

        componentes.extend(
            [
                "Revisión de las condiciones del sistema "
                "de alumbrado público objeto de intervención.",

                "Definición preliminar de equipos, "
                "luminarias, infraestructura y elementos "
                "complementarios requeridos.",

                "Planeación de instalación, pruebas, "
                "puesta en operación y entrega."
            ]
        )

    # --------------------------------------------------------
    # SOLAR
    # --------------------------------------------------------

    if (
        perfil["solar"]
        or perfil["fotovoltaico"]
    ):

        componentes.append(
            "Evaluación técnica de la solución "
            "fotovoltaica y sus componentes asociados."
        )

    # --------------------------------------------------------
    # AUTOMATIZACIÓN
    # --------------------------------------------------------

    if (
        perfil["automatizacion"]
        or perfil["telegestion"]
    ):

        componentes.append(
            "Evaluación de alternativas de automatización, "
            "monitoreo y gestión inteligente."
        )

    return {

        "componentes":
            componentes,

        "fuente":
            "PROPUESTA_INTI",

        "requiere_validacion":
            True
    }


# ============================================================
# GENERAR SOLUCIÓN TÉCNICA
# ============================================================

def generar_solucion_tecnica(
    oportunidad
):

    perfil = detectar_perfil_proyecto(
        oportunidad
    )

    parrafos = []

    parrafos.append(
        "INTI propone desarrollar la solución mediante "
        "un enfoque de ingeniería basado en diagnóstico, "
        "diseño o validación técnica, planeación, ejecución, "
        "control de calidad, puesta en operación y seguimiento."
    )

    # --------------------------------------------------------
    # ALUMBRADO
    # --------------------------------------------------------

    if perfil[
        "alumbrado_publico"
    ]:

        parrafos.append(
            "Para el componente de alumbrado público se "
            "deberán evaluar las condiciones de iluminación, "
            "infraestructura disponible, requerimientos "
            "eléctricos, eficiencia energética, seguridad, "
            "mantenimiento y cumplimiento de la normativa "
            "aplicable."
        )

    # --------------------------------------------------------
    # SOLAR
    # --------------------------------------------------------

    if (
        perfil["solar"]
        or perfil["fotovoltaico"]
    ):

        parrafos.append(
            "Cuando el proceso contemple generación "
            "fotovoltaica, la solución deberá analizar "
            "generación, almacenamiento, control, autonomía, "
            "protecciones, estructuras y condiciones "
            "ambientales del sitio."
        )

    # --------------------------------------------------------
    # AUTOMATIZACIÓN
    # --------------------------------------------------------

    if (
        perfil["automatizacion"]
        or perfil["telegestion"]
    ):

        parrafos.append(
            "Cuando sea permitido por los requisitos del "
            "proceso, podrán evaluarse funcionalidades "
            "de automatización, monitoreo, control y "
            "gestión inteligente."
        )

    parrafos.append(
        "Las referencias, potencias, cantidades, marcas, "
        "equipos y especificaciones definitivas no deben "
        "establecerse hasta revisar los documentos técnicos "
        "oficiales del proceso."
    )

    return {

        "texto":
            "\n\n".join(
                parrafos
            ),

        "fuente":
            "PROPUESTA_INTI",

        "requiere_validacion":
            True
    }


# ============================================================
# GENERAR METODOLOGÍA
# ============================================================

def generar_metodologia(
    oportunidad
):

    fases = [

        {
            "fase":
                1,

            "nombre":
                "Revisión y alistamiento",

            "descripcion":
                "Revisión de documentos, alcance, "
                "requisitos, condiciones contractuales "
                "y planificación inicial."
        },

        {
            "fase":
                2,

            "nombre":
                "Diagnóstico y validación técnica",

            "descripcion":
                "Verificación de información, condiciones "
                "existentes, necesidades, restricciones "
                "y parámetros técnicos."
        },

        {
            "fase":
                3,

            "nombre":
                "Ingeniería y planeación",

            "descripcion":
                "Definición de solución, actividades, "
                "recursos, cronograma, riesgos, controles "
                "y entregables."
        },

        {
            "fase":
                4,

            "nombre":
                "Ejecución",

            "descripcion":
                "Desarrollo de las actividades previstas "
                "con seguimiento técnico, administrativo, "
                "ambiental, SST y de calidad según aplique."
        },

        {
            "fase":
                5,

            "nombre":
                "Pruebas y puesta en operación",

            "descripcion":
                "Verificación de funcionamiento, pruebas, "
                "ajustes, documentación y puesta en servicio."
        },

        {
            "fase":
                6,

            "nombre":
                "Cierre y entrega",

            "descripcion":
                "Consolidación documental, entrega de "
                "resultados, cierre técnico y transferencia "
                "de información."
        }
    ]

    return {

        "fases":
            fases,

        "fuente":
            "PROPUESTA_INTI",

        "requiere_validacion":
            True
    }


# ============================================================
# CONVERTIR LISTA A TEXTO
# ============================================================

def lista_a_texto(
    elementos
):

    return "\n".join(
        [
            f"{indice + 1}. {elemento}"
            for indice, elemento
            in enumerate(elementos)
        ]
    )


# ============================================================
# METODOLOGÍA A TEXTO
# ============================================================

def metodologia_a_texto(
    fases
):

    textos = []

    for fase in fases:

        textos.append(
            f"FASE {fase['fase']} - "
            f"{fase['nombre']}\n"
            f"{fase['descripcion']}"
        )

    return "\n\n".join(
        textos
    )


# ============================================================
# PREESTRUCTURAR PROYECTO
# ============================================================

def generar_prestructuracion(
    oportunidad
):

    diagnostico = generar_diagnostico(
        oportunidad
    )

    objetivos = generar_objetivos(
        oportunidad
    )

    alcance = generar_alcance(
        oportunidad
    )

    solucion = generar_solucion_tecnica(
        oportunidad
    )

    metodologia = generar_metodologia(
        oportunidad
    )

    return {

        "diagnostico":
            diagnostico,

        "objetivos":
            objetivos,

        "alcance":
            alcance,

        "solucion_tecnica":
            solucion,

        "metodologia":
            metodologia,

        "estado":
            "BORRADOR_INTI",

        "requiere_validacion":
            True
    }
