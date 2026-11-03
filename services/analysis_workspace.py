
# ============================================================
# INTI PROJECTS ENTERPRISE
# INTILED SAS BIC
#
# Archivo: services/analysis_workspace.py
#
# Gestión independiente de análisis por convocatoria.
# Compatible con services/opportunity_workspace.py
# ============================================================

from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

from services.opportunity_workspace import (
    iniciar_workspace,
    oportunidad_activa,
    guardar_datos_modulo,
    obtener_datos_modulo,
    registrar_evento,
)


ZONA_HORARIA = ZoneInfo("America/Bogota")

MODULO = "analisis_intiled"


# ============================================================
# ESTRUCTURA INICIAL DE UN ANÁLISIS
# ============================================================

def estructura_analisis():

    return {
        "identificador": None,

        "fecha_creacion": None,
        "fecha_actualizacion": None,

        "informacion_general": {
            "objeto": "",
            "entidad": "",
            "pais": "Colombia",
            "departamento": "",
            "municipio": "",
            "presupuesto": None,
            "fecha_cierre": None,
        },

        "analisis_tecnico": {
            "estado": "Pendiente",
            "observaciones": "",
            "experiencia_requerida": "",
            "experiencia_acreditada": "",
            "capacidad_operativa": "",
            "cumplimiento": None,
        },

        "analisis_juridico": {
            "estado": "Pendiente",
            "observaciones": "",
            "requisitos_habilitantes": "",
            "documentos_pendientes": "",
            "permite_consorcio": None,
            "cumplimiento": None,
        },

        "analisis_financiero": {
            "estado": "Pendiente",
            "observaciones": "",
            "indicadores_requeridos": "",
            "capacidad_financiera": "",
            "garantias": "",
            "cumplimiento": None,
        },

        "analisis_comercial": {
            "estado": "Pendiente",
            "observaciones": "",
            "competidores": "",
            "aliados_potenciales": "",
            "riesgos": "",
            "cumplimiento": None,
        },

        "decision": {
            "resultado": "Pendiente de verificación",
            "justificacion": "",
            "responsable": "",
            "fecha_decision": None,
        },

        "historial": [],
    }


# ============================================================
# FECHAS
# ============================================================

def fecha_actual():

    return datetime.now(
        ZONA_HORARIA
    ).isoformat(timespec="seconds")


# ============================================================
# IDENTIFICACIÓN DEL EXPEDIENTE ACTIVO
# ============================================================

def obtener_expediente_activo():

    expediente = oportunidad_activa()

    if expediente is None:
        return None

    return expediente


def obtener_identificador_activo():

    expediente = obtener_expediente_activo()

    if expediente is None:
        return None

    return expediente.get("id")


# ============================================================
# CREACIÓN DE ANÁLISIS
# ============================================================

def crear_analisis():

    expediente = obtener_expediente_activo()

    if expediente is None:
        return None

    oportunidad = expediente.get(
        "oportunidad", {}
    )

    analisis = estructura_analisis()

    analisis["identificador"] = expediente["id"]

    analisis["fecha_creacion"] = fecha_actual()

    analisis["fecha_actualizacion"] = (
        fecha_actual()
    )

    analisis["informacion_general"] = {
        "objeto": oportunidad.get(
            "titulo", ""
        ),
        "entidad": oportunidad.get(
            "entidad", ""
        ),
        "pais": oportunidad.get(
            "pais", "Colombia"
        ),
        "departamento": oportunidad.get(
            "region", ""
        ),
        "municipio": oportunidad.get(
            "localidad", ""
        ),
        "presupuesto": oportunidad.get(
            "presupuesto"
        ),
        "fecha_cierre": oportunidad.get(
            "fecha_cierre"
        ),
    }

    analisis["historial"].append({
        "fecha": fecha_actual(),
        "evento": "Análisis inicial creado",
    })

    return analisis


# ============================================================
# OBTENER ANÁLISIS DE LA CONVOCATORIA ACTIVA
# ============================================================

def cargar_analisis():

    identificador = obtener_identificador_activo()

    if identificador is None:
        return None

    guardado = obtener_datos_modulo(
        MODULO,
        defecto=None,
    )

    if guardado is not None:

        # Protección adicional: el análisis debe
        # pertenecer al expediente activo.
        if (
            guardado.get("identificador")
            == identificador
        ):
            return deepcopy(guardado)

    return crear_analisis()


# ============================================================
# GUARDAR ANÁLISIS
# ============================================================

def guardar_analisis(analisis):

    identificador = obtener_identificador_activo()

    if identificador is None:
        return False, (
            "Debes seleccionar una convocatoria "
            "antes de guardar el análisis."
        )

    if not isinstance(analisis, dict):
        return False, (
            "El análisis tiene un formato inválido."
        )

    identificador_recibido = analisis.get(
        "identificador"
    )

    if identificador_recibido != identificador:
        return False, (
            "El análisis pertenece a otra "
            "convocatoria. No se guardaron cambios."
        )

    nuevo_analisis = deepcopy(analisis)

    nuevo_analisis["fecha_actualizacion"] = (
        fecha_actual()
    )

    nuevo_analisis.setdefault(
        "historial", []
    )

    nuevo_analisis["historial"].append({
        "fecha": fecha_actual(),
        "evento": "Análisis actualizado",
    })

    correcto = guardar_datos_modulo(
        MODULO,
        nuevo_analisis,
    )

    if correcto:

        registrar_evento(
            identificador,
            "Análisis INTILED guardado",
        )

        return True, (
            "Análisis guardado correctamente "
            "en el expediente activo."
        )

    return False, (
        "No fue posible guardar el análisis."
    )


# ============================================================
# ACTUALIZAR COMPONENTE INDIVIDUAL
# ============================================================

def actualizar_componente(
    nombre_componente,
    datos,
):

    componentes_permitidos = [
        "analisis_tecnico",
        "analisis_juridico",
        "analisis_financiero",
        "analisis_comercial",
    ]

    if nombre_componente not in componentes_permitidos:

        return False, (
            "El componente solicitado "
            "no está permitido."
        )

    if not isinstance(datos, dict):
        return False, (
            "Los datos deben tener "
            "formato de diccionario."
        )

    analisis = cargar_analisis()

    if analisis is None:
        return False, (
            "No hay una convocatoria activa."
        )

    componente = analisis[
        nombre_componente
    ]

    componente.update(
        deepcopy(datos)
    )

    analisis["historial"].append({
        "fecha": fecha_actual(),
        "evento": (
            "Componente actualizado: "
            + nombre_componente
        ),
    })

    return guardar_analisis(analisis)


# ============================================================
# RECOMENDACIÓN PRELIMINAR
# ============================================================

def recomendar_participacion(analisis):

    """
    Evalúa los cumplimientos registrados
    manualmente.

    True: cumplimiento verificado.
    False: incumplimiento verificado.
    None: información insuficiente.

    No sustituye la revisión de pliegos.
    """

    tecnico = analisis[
        "analisis_tecnico"
    ].get("cumplimiento")

    juridico = analisis[
        "analisis_juridico"
    ].get("cumplimiento")

    financiero = analisis[
        "analisis_financiero"
    ].get("cumplimiento")

    resultados = [
        tecnico,
        juridico,
        financiero,
    ]

    # No se puede afirmar viabilidad
    # si hay información por verificar.
    if any(
        resultado is None
        for resultado in resultados
    ):
        return {
            "resultado": (
                "Pendiente de verificación"
            ),
            "justificacion": (
                "Todavía faltan verificaciones "
                "técnicas, jurídicas o financieras."
            ),
        }

    if all(
        resultado is True
        for resultado in resultados
    ):
        return {
            "resultado": (
                "Evaluar participación individual"
            ),
            "justificacion": (
                "Los componentes evaluados fueron "
                "marcados como cumplidos. "
                "Debe confirmarse documentalmente "
                "la habilitación antes de postular."
            ),
        }

    permite_consorcio = analisis[
        "analisis_juridico"
    ].get("permite_consorcio")

    if permite_consorcio is True:
        return {
            "resultado": "Evaluar alianza",
            "justificacion": (
                "Se identificaron incumplimientos "
                "y se registró que el proceso "
                "admite participación conjunta. "
                "Debe verificarse si una alianza "
                "puede subsanar esas deficiencias."
            ),
        }

    return {
        "resultado": (
            "No recomendar postulación individual"
        ),
        "justificacion": (
            "Se identificaron requisitos "
            "incumplidos. No hay información "
            "suficiente para confirmar una "
            "alternativa de participación conjunta."
        ),
    }


# ============================================================
# GUARDAR DECISIÓN
# ============================================================

def actualizar_decision(
    resultado,
    justificacion,
    responsable="",
):

    analisis = cargar_analisis()

    if analisis is None:
        return False, (
            "No hay convocatoria activa."
        )

    analisis["decision"] = {
        "resultado": str(resultado),
        "justificacion": str(
            justificacion
        ),
        "responsable": str(
            responsable
        ),
        "fecha_decision": fecha_actual(),
    }

    analisis["historial"].append({
        "fecha": fecha_actual(),
        "evento": (
            "Decisión registrada: "
            + str(resultado)
        ),
    })

    return guardar_analisis(analisis)


# ============================================================
# RESUMEN DE ANÁLISIS
# ============================================================

def resumen_analisis():

    workspace = iniciar_workspace()

    resumen = []

    for identificador, expediente in (
        workspace.get(
            "expedientes", {}
        ).items()
    ):

        modulos = expediente.get(
            "modulos", {}
        )

        analisis = modulos.get(
            MODULO
        )

        if analisis is None:
            continue

        decision = analisis.get(
            "decision", {}
        )

        oportunidad = expediente.get(
            "oportunidad", {}
        )

        resumen.append({
            "id": identificador,
            "convocatoria": oportunidad.get(
                "titulo", ""
            ),
            "entidad": oportunidad.get(
                "entidad", ""
            ),
            "estado_gestion": expediente.get(
                "estado", ""
            ),
            "decision": decision.get(
                "resultado",
                "Pendiente de verificación"
            ),
            "ultima_actualizacion": (
                analisis.get(
                    "fecha_actualizacion"
                )
            ),
        })

    return resumen
