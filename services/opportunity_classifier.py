
import re
import unicodedata


LINEAS_INTILED = {
    "Alumbrado público": [
        "alumbrado publico",
        "luminarias",
        "iluminacion vial",
        "iluminacion led",
        "telegestion",
    ],
    "Energía solar": [
        "fotovoltaico",
        "energia solar",
        "paneles solares",
        "sistema solar",
    ],
    "Eficiencia energética": [
        "eficiencia energetica",
        "ahorro energetico",
        "gestion energetica",
    ],
    "Ingeniería eléctrica": [
        "subestacion",
        "redes electricas",
        "instalaciones electricas",
    ],
    "Consultoría e interventoría": [
        "interventoria",
        "consultoria tecnica",
        "estudios y disenos",
        "estructuracion de proyectos",
        "formulacion de proyectos",
    ],
    "Tecnología y monitoreo": [
        "monitoreo remoto",
        "sensores",
        "ciudad inteligente",
        "smart city",
        "automatizacion",
        "telemetria",
    ],
}

SECTORES_ALEJADOS = [
    "suministro de medicamentos",
    "vigilancia privada",
    "alimentacion escolar",
    "dotacion de uniformes",
    "transporte de pacientes",
]

SENALES_ALIANZA = [
    "experiencia especifica",
    "experiencia acreditada",
    "consorcio",
    "union temporal",
    "capacidad financiera",
    "indicadores financieros",
]


def normalizar(texto):
    texto = str(texto or "").lower()
    texto = unicodedata.normalize("NFKD", texto)

    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )

    return re.sub(r"\s+", " ", texto).strip()


def evaluar_oportunidad(oportunidad):

    titulo = oportunidad.get("titulo", "")
    descripcion = oportunidad.get("descripcion", "")

    texto = normalizar(
        f"{titulo} {descripcion}"
    )

    coincidencias = []

    for linea, palabras in LINEAS_INTILED.items():

        if any(
            palabra in texto
            for palabra in palabras
        ):
            coincidencias.append(linea)

    alejadas = [
        termino
        for termino in SECTORES_ALEJADOS
        if termino in texto
    ]

    senales = [
        termino
        for termino in SENALES_ALIANZA
        if termino in texto
    ]

    if alejadas and not coincidencias:

        return {
            "decision": "No participar",
            "nivel": "Baja afinidad",
            "lineas": [],
            "motivo": (
                "El objeto contractual identificado "
                "se encuentra fuera de las líneas "
                "priorizadas de INTILED."
            ),
            "pendientes": [
                "Confirmar el alcance contractual."
            ],
        }

    if not coincidencias:

        return {
            "decision": "Pendiente de verificación",
            "nivel": "Afinidad no determinada",
            "lineas": [],
            "motivo": (
                "La información disponible no permite "
                "establecer una coincidencia técnica suficiente."
            ),
            "pendientes": [
                "Revisar el objeto contractual.",
                "Consultar las especificaciones técnicas.",
            ],
        }

    if senales:

        return {
            "decision": "Evaluar alianza",
            "nivel": "Afinidad técnica identificada",
            "lineas": coincidencias,
            "motivo": (
                "Existe afinidad técnica, pero se "
                "identificaron requisitos que requieren "
                "verificación antes de recomendar "
                "una postulación individual."
            ),
            "pendientes": [
                "Verificar experiencia contractual.",
                "Comprobar habilitantes jurídicos.",
                "Revisar capacidad financiera.",
                "Confirmar si se permiten alianzas.",
            ],
        }

    return {
        "decision": "Evaluar participación individual",
        "nivel": "Afinidad técnica identificada",
        "lineas": coincidencias,
        "motivo": (
            "La oportunidad coincide con líneas "
            "de trabajo de INTILED. Se recomienda "
            "revisar primero la posibilidad "
            "de participación individual."
        ),
        "pendientes": [
            "Validar experiencia empresarial certificada.",
            "Revisar requisitos jurídicos y financieros.",
            "Verificar capacidad operativa.",
            "Confirmar los requisitos del país.",
        ],
    }
