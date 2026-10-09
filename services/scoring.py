def calcular_intiled_score(
    tecnico,
    experiencia,
    capacidad,
    habilitantes,
    economico,
    tiempo
):

    """
    Calcula el nivel de compatibilidad de una
    oportunidad con INTILED.

    Cada parámetro debe tener un valor
    entre 0 y 100.
    """

    pesos = {
        "tecnico": 0.20,
        "experiencia": 0.20,
        "capacidad": 0.20,
        "habilitantes": 0.15,
        "economico": 0.15,
        "tiempo": 0.10
    }

    score = (
        tecnico * pesos["tecnico"]
        + experiencia * pesos["experiencia"]
        + capacidad * pesos["capacidad"]
        + habilitantes * pesos["habilitantes"]
        + economico * pesos["economico"]
        + tiempo * pesos["tiempo"]
    )

    return round(score, 1)


def clasificar_score(score):

    if score >= 80:
        return "Alta oportunidad"

    elif score >= 60:
        return "Requiere análisis"

    elif score >= 40:
        return "Baja compatibilidad"

    else:
        return "No recomendada"
def verificar_requisitos_criticos(requisitos):

    """
    Recibe una lista de requisitos críticos.

    Ejemplo:

    [
        {
            "requisito": "Experiencia mínima",
            "cumple": True
        },
        {
            "requisito": "Certificación RETIE",
            "cumple": False
        }
    ]
    """

    incumplimientos = []

    for requisito in requisitos:

        if not requisito["cumple"]:

            incumplimientos.append(
                requisito["requisito"]
            )

    return incumplimientos
