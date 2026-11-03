
# services/opportunity_classifier.py

import re
import unicodedata

LINEAS_INTILED = {
    "Alumbrado público": [
        "alumbrado publico", "luminarias",
        "iluminacion vial", "iluminacion led",
        "alumbrado solar", "telegestion"
    ],
    "Energía solar": [
        "fotovoltaico", "energia solar",
        "paneles solares", "sistema solar",
        "generacion distribuida"
    ],
    "Eficiencia energética": [
        "eficiencia energetica",
        "ahorro energetico",
        "auditoria energetica",
        "gestion energetica"
    ],
    "Ingeniería eléctrica": [
        "subestacion", "redes electricas",
        "instalaciones electricas",
        "sistemas electricos"
    ],
    "Consultoría e interventoría": [
        "interventoria", "consultoria tecnica",
        "estudios y disenos",
        "estructuracion de proyectos",
        "formulacion de proyectos"
    ],
    "Tecnología y monitoreo": [
        "monitoreo remoto", "sensores",
        "ciudad inteligente", "smart city",
        "automatizacion", "telemetria"
    ],
}

# Señales preliminares, NO pruebas de habilitación.
SENALES_ALIANZA = [
    "experiencia especifica",
    "experiencia acreditada",
    "consorcio",
    "union temporal",
    "capacidad financiera",
    "indicadores financieros",
    "clasificacion de proveedor",
    "registro unico de proponentes",
]

SECTORES_ALEJADOS = [
    "suministro de medicamentos",
    "servicios de vigilancia privada",
    "alimentacion escolar",
    "dotacion de uniformes",
    "transporte de pacientes",
]


def normalizar(texto):
    texto = str(texto or "").lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )
    return re.sub(r"\s+", " ", texto).strip()


def evaluar_oportunidad(oportunidad):
    titulo = oportunidad.get("titulo", "")
    descripcion = oportunidad.get("descripcion", "")
    texto = normalizar(f"{titulo} {descripcion}")

    coincidencias = []
    for linea, palabras in LINEAS_INTILED.items():
        if any(palabra in texto for palabra in palabras):
            coincidencias.append(linea)

    alejadas = [
        termino for termino in SECTORES_ALEJADOS
        if termino in texto
    ]

    senales = [
        termino for termino in SENALES_ALIANZA
        if termino in texto
    ]

    if alejadas and not coincidencias:
        return {
            "decision": "No participar",
            "nivel": "Baja afinidad",
            "lineas": [],
            "motivo": (
                "El objeto identificado está fuera de "
                "las líneas de trabajo priorizadas de INTILED."
            ),
            "pendientes": [
                "Confirmar el objeto y alcance contractual."
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
                "Revisar el objeto contractual completo.",
                "Consultar las especificaciones técnicas."
            ],
        }

    if senales:
        return {
            "decision": "Evaluar alianza",
            "nivel": "Afinidad técnica identificada",
            "lineas": coincidencias,
            "motivo": (
                "La oportunidad coincide con capacidades "
                "técnicas de INTILED, pero contiene señales "
                "de requisitos que deben verificarse antes "
                "de decidir si participa individualmente."
            ),
            "pendientes": [
                "Verificar experiencia contractual acreditada.",
                "Comprobar requisitos jurídicos y financieros.",
                "Revisar si se permiten proponentes plurales."
            ],
        }

    return {
        "decision": "Evaluar participación individual",
        "nivel": "Afinidad técnica identificada",
        "lineas": coincidencias,
        "motivo": (
            "El objeto presenta afinidad con las líneas "
            "de trabajo de INTILED. Conviene revisar "
            "primero la posibilidad de postulación individual."
        ),
        "pendientes": [
            "Validar experiencia empresarial certificada.",
            "Revisar habilitantes jurídicos y financieros.",
            "Verificar capacidad operativa y plazo.",
            "Confirmar los requisitos del país."
        ],
    }
