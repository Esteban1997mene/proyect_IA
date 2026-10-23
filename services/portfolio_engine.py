from datetime import datetime, date


# ============================================================
# INTI PROJECTS AI
# MOTOR DE PORTAFOLIO
# ============================================================


ESTADOS_PROYECTO = [
    "🔵 Iniciativa",
    "🟣 En formulación",
    "🟡 En gestión",
    "🟠 Propuesta en preparación",
    "📤 Propuesta presentada",
    "🟢 Avanzando",
    "🏆 Contratado",
    "🔴 Bloqueado",
    "⏸️ Aplazado",
    "⚫ Finalizado"
]


PRIORIDADES = [
    "P1 - Crítica",
    "P2 - Alta",
    "P3 - Media",
    "P4 - Exploratoria"
]


TIPOS_PROYECTO = [
    "Alumbrado público",
    "Energía solar FV",
    "Eficiencia energética",
    "Infraestructura eléctrica",
    "Automatización / IoT",
    "Consultoría",
    "Interventoría",
    "Smart Cities",
    "Investigación e innovación",
    "Otro"
]


def crear_proyecto_vacio():

    return {
        "id": None,
        "nombre": "",
        "entidad": "",
        "municipio": "",
        "departamento": "",
        "tipo": "Otro",
        "valor_estimado": 0,
        "estado": "🔵 Iniciativa",
        "prioridad": "P3 - Media",
        "probabilidad": 0,
        "responsable": "",
        "situacion_actual": "",
        "proxima_accion": "",
        "fecha_proxima_accion": None,
        "fecha_creacion": datetime.now().isoformat(),
        "ultima_actualizacion": datetime.now().isoformat(),
        "historial": []
    }


def calcular_valor_ponderado(
    valor,
    probabilidad
):

    try:
        valor = float(valor)
        probabilidad = float(probabilidad)

        return valor * (
            probabilidad / 100
        )

    except Exception:
        return 0


def calcular_metricas(
    proyectos
):

    total = len(proyectos)

    valor_total = sum(
        float(
            p.get(
                "valor_estimado",
                0
            ) or 0
        )
        for p in proyectos
    )

    valor_ponderado = sum(
        calcular_valor_ponderado(
            p.get(
                "valor_estimado",
                0
            ),
            p.get(
                "probabilidad",
                0
            )
        )
        for p in proyectos
    )

    prioridad_1 = sum(
        1
        for p in proyectos
        if str(
            p.get(
                "prioridad",
                ""
            )
        ).startswith(
            "P1"
        )
    )

    bloqueados = sum(
        1
        for p in proyectos
        if "Bloqueado" in str(
            p.get(
                "estado",
                ""
            )
        )
    )

    contratados = sum(
        1
        for p in proyectos
        if "Contratado" in str(
            p.get(
                "estado",
                ""
            )
        )
    )

    return {
        "total": total,
        "valor_total": valor_total,
        "valor_ponderado": valor_ponderado,
        "prioridad_1": prioridad_1,
        "bloqueados": bloqueados,
        "contratados": contratados
    }


def formatear_moneda(valor):

    try:
        valor = float(valor)

    except Exception:
        valor = 0

    if valor >= 1_000_000_000:

        return (
            f"${valor / 1_000_000_000:,.2f} mil M"
        )

    if valor >= 1_000_000:

        return (
            f"${valor / 1_000_000:,.1f} M"
        )

    return (
        f"${valor:,.0f}"
    )


def obtener_proyectos_criticos(
    proyectos
):

    resultado = []

    for proyecto in proyectos:

        estado = str(
            proyecto.get(
                "estado",
                ""
            )
        )

        prioridad = str(
            proyecto.get(
                "prioridad",
                ""
            )
        )

        if (
            "Bloqueado" in estado
            or prioridad.startswith("P1")
        ):

            resultado.append(
                proyecto
            )

    return resultado


def registrar_cambio(
    proyecto,
    descripcion,
    responsable=""
):

    if "historial" not in proyecto:
        proyecto["historial"] = []

    proyecto[
        "historial"
    ].append({

        "fecha":
            datetime.now().isoformat(),

        "descripcion":
            descripcion,

        "responsable":
            responsable
    })

    proyecto[
        "ultima_actualizacion"
    ] = datetime.now().isoformat()


def obtener_acciones_pendientes(
    proyectos
):

    acciones = []

    for proyecto in proyectos:

        accion = proyecto.get(
            "proxima_accion"
        )

        if not accion:
            continue

        acciones.append({

            "proyecto":
                proyecto.get(
                    "nombre",
                    ""
                ),

            "accion":
                accion,

            "responsable":
                proyecto.get(
                    "responsable",
                    ""
                ),

            "fecha":
                proyecto.get(
                    "fecha_proxima_accion"
                ),

            "prioridad":
                proyecto.get(
                    "prioridad",
                    ""
                ),

            "estado":
                proyecto.get(
                    "estado",
                    ""
                )
        })

    return acciones
