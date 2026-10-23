from datetime import datetime


TIPOS_AVANCE = [
    "🟢 Avance",
    "🔵 Nueva iniciativa",
    "🟡 Gestión pendiente",
    "🟠 Cambio importante",
    "🔴 Bloqueo",
    "⏸️ Aplazamiento",
    "🏆 Hito cumplido",
    "💰 Cambio presupuestal",
    "📅 Cambio de fecha",
    "👤 Cambio de responsable"
]


def crear_reunion(
    fecha,
    titulo,
    responsable="",
    observaciones=""
):
    return {
        "id": f"REU-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "fecha": str(fecha),
        "titulo": titulo,
        "responsable": responsable,
        "observaciones": observaciones,
        "fecha_registro": datetime.now().isoformat(),
        "avances": []
    }


def crear_avance(
    proyecto,
    tipo,
    descripcion,
    responsable="",
    proxima_accion="",
    fecha_compromiso=None
):
    return {
        "id": f"AV-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "proyecto": proyecto,
        "tipo": tipo,
        "descripcion": descripcion,
        "responsable": responsable,
        "proxima_accion": proxima_accion,
        "fecha_compromiso": (
            str(fecha_compromiso)
            if fecha_compromiso
            else None
        ),
        "fecha_registro": datetime.now().isoformat()
    }


def resumen_reunion(reunion):

    avances = reunion.get("avances", [])

    resumen = {
        "total": len(avances),
        "avances": 0,
        "nuevos": 0,
        "pendientes": 0,
        "bloqueos": 0,
        "aplazados": 0,
        "hitos": 0
    }

    for avance in avances:

        tipo = avance.get("tipo", "")

        if "Avance" in tipo:
            resumen["avances"] += 1

        if "Nueva iniciativa" in tipo:
            resumen["nuevos"] += 1

        if "Gestión pendiente" in tipo:
            resumen["pendientes"] += 1

        if "Bloqueo" in tipo:
            resumen["bloqueos"] += 1

        if "Aplazamiento" in tipo:
            resumen["aplazados"] += 1

        if "Hito cumplido" in tipo:
            resumen["hitos"] += 1

    return resumen


def obtener_compromisos(reuniones):

    compromisos = []

    for reunion in reuniones:

        for avance in reunion.get("avances", []):

            accion = avance.get("proxima_accion")

            if accion:

                compromisos.append({
                    "reunion": reunion.get("titulo", ""),
                    "fecha_reunion": reunion.get("fecha", ""),
                    "proyecto": avance.get("proyecto", ""),
                    "accion": accion,
                    "responsable": avance.get("responsable", ""),
                    "fecha_compromiso": avance.get(
                        "fecha_compromiso"
                    ),
                    "tipo": avance.get("tipo", "")
                })

    return compromisos


def generar_resumen_texto(reunion):

    avances = reunion.get("avances", [])

    if not avances:
        return "La reunión no tiene avances registrados."

    grupos = {}

    for avance in avances:

        tipo = avance.get("tipo", "Otro")

        if tipo not in grupos:
            grupos[tipo] = []

        grupos[tipo].append(avance)

    lineas = []

    lineas.append(
        f"REUNIÓN: {reunion.get('titulo', '')}"
    )

    lineas.append(
        f"FECHA: {reunion.get('fecha', '')}"
    )

    lineas.append("")

    for tipo, elementos in grupos.items():

        lineas.append(tipo.upper())

        for elemento in elementos:

            proyecto = elemento.get(
                "proyecto",
                "Proyecto"
            )

            descripcion = elemento.get(
                "descripcion",
                ""
            )

            lineas.append(
                f"- {proyecto}: {descripcion}"
            )

            proxima = elemento.get(
                "proxima_accion"
            )

            if proxima:

                lineas.append(
                    f"  Próxima acción: {proxima}"
                )

        lineas.append("")

    return "\n".join(lineas)
