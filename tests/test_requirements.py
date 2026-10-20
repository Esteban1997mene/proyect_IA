from services.requirements_engine import (
    analizar_requisitos,
    generar_resumen_requisitos,
    identificar_brechas,
    identificar_criticos
)


# ============================================================
# CONVOCATORIA DE PRUEBA
# ============================================================

requisitos_prueba = [

    {
        "tipo": "experiencia_empresa",

        "descripcion": (
            "Acreditar mínimo 2 contratos "
            "relacionados con alumbrado público "
            "y sistemas fotovoltaicos."
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
            "Ingeniero electricista con "
            "experiencia en alumbrado público."
        ),

        "profesion": (
            "ingeniero electricista"
        ),

        "areas": [
            "alumbrado_publico"
        ]
    },

    {
        "tipo": "capacidad_tecnica",

        "descripcion": (
            "Capacidad para implementar "
            "alumbrado solar y automatización."
        ),

        "keywords": [
            "alumbrado solar",
            "automatización",
            "sistemas solares fotovoltaicos"
        ]
    },

    {
        "tipo": "certificacion",

        "descripcion": (
            "Certificación requerida "
            "por el proceso."
        ),

        "certificacion": (
            "certificacion_ejemplo"
        ),

        "critico": True
    },

    {
        "tipo": "financiero",

        "descripcion": (
            "Cumplimiento de indicadores "
            "financieros habilitantes."
        ),

        "critico": True
    }
]


# ============================================================
# EJECUCIÓN
# ============================================================

resultados = analizar_requisitos(
    requisitos_prueba
)


# ============================================================
# MOSTRAR RESULTADOS
# ============================================================

print("\n")
print("=" * 70)
print("INTI PROJECTS AI")
print("ANÁLISIS DE REQUISITOS")
print("=" * 70)


for resultado in resultados:

    print("\n")

    print(
        "REQUISITO:",
        resultado["requisito"]
    )

    print(
        "TIPO:",
        resultado["tipo"]
    )

    print(
        "ESTADO:",
        resultado["estado"]
    )

    print(
        "RIESGO:",
        resultado["riesgo"]
    )

    print(
        "CRÍTICO:",
        resultado["critico"]
    )

    print(
        "EVIDENCIA:",
        resultado["evidencia"]
    )

    print(
        "OBSERVACIÓN:",
        resultado["observacion"]
    )


# ============================================================
# RESUMEN
# ============================================================

resumen = generar_resumen_requisitos(
    resultados
)

brechas = identificar_brechas(
    resultados
)

criticos = identificar_criticos(
    resultados
)


print("\n")
print("=" * 70)
print("RESUMEN")
print("=" * 70)

print(resumen)

print(
    "Brechas:",
    len(brechas)
)

print(
    "Requisitos críticos pendientes:",
    len(criticos)
)
