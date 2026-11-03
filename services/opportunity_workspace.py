
# services/opportunity_workspace.py
# INTI Projects Enterprise - INTILED SAS BIC

import hashlib
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st


ZONA_HORARIA = ZoneInfo("America/Bogota")
CLAVE = "inti_workspace_v1"

ESTADOS = [
    "Por revisar",
    "En evaluación",
    "Participación individual",
    "Evaluando alianza",
    "Preparando propuesta",
    "Propuesta presentada",
    "No participar",
    "Finalizada",
]


def ahora():
    return datetime.now(ZONA_HORARIA).isoformat(
        timespec="seconds"
    )


def iniciar_workspace():
    if CLAVE not in st.session_state:
        st.session_state[CLAVE] = {
            "version": 1,
            "activa": None,
            "expedientes": {},
        }

    return st.session_state[CLAVE]


def obtener_id(oportunidad):
    pais = str(
        oportunidad.get("pais", "Colombia")
    ).strip()

    codigo = str(
        oportunidad.get("codigo", "")
    ).strip()

    if codigo:
        return f"{pais}:{codigo}"

    base = "|".join([
        pais,
        str(oportunidad.get("titulo", "")),
        str(oportunidad.get("entidad", "")),
        str(oportunidad.get("fecha_publicacion", "")),
    ])

    huella = hashlib.sha256(
        base.encode("utf-8")
    ).hexdigest()[:20]

    return f"{pais}:SIN-CODIGO:{huella}"


def sincronizar_legacy():
    """
    Entrega al resto de módulos la oportunidad activa.

    No elimina ni modifica los expedientes guardados.
    """
    workspace = iniciar_workspace()
    identificador = workspace["activa"]

    expediente = workspace["expedientes"].get(
        identificador
    )

    if expediente is None:
        st.session_state[
            "oportunidad_seleccionada"
        ] = None

        st.session_state[
            "inti_oportunidad_id"
        ] = None

        return None

    st.session_state[
        "oportunidad_seleccionada"
    ] = dict(expediente["oportunidad"])

    st.session_state[
        "inti_oportunidad_id"
    ] = identificador

    return expediente


def guardar_oportunidad(oportunidad):
    workspace = iniciar_workspace()
    identificador = obtener_id(oportunidad)

    if identificador not in workspace["expedientes"]:
        workspace["expedientes"][identificador] = {
            "id": identificador,
            "oportunidad": dict(oportunidad),
            "estado": "Por revisar",
            "notas": "",
            "creado": ahora(),
            "actualizado": ahora(),
            "historial": [
                {
                    "fecha": ahora(),
                    "accion": "Oportunidad incorporada",
                }
            ],
            "modulos": {},
        }

    else:
        expediente = workspace["expedientes"][
            identificador
        ]

        # Actualizamos datos de la fuente, pero
        # conservamos notas, estado e historial.
        expediente["oportunidad"].update(
            dict(oportunidad)
        )
        expediente["actualizado"] = ahora()

    return identificador


def activar_oportunidad(identificador):
    workspace = iniciar_workspace()

    if identificador not in workspace["expedientes"]:
        return False

    anterior = workspace["activa"]

    workspace["activa"] = identificador

    if anterior != identificador:
        registrar_evento(
            identificador,
            "Expediente activado",
        )

    sincronizar_legacy()
    return True


def guardar_y_activar(oportunidad):
    identificador = guardar_oportunidad(oportunidad)
    activar_oportunidad(identificador)
    return identificador


def oportunidad_activa():
    workspace = iniciar_workspace()

    identificador = workspace["activa"]

    return workspace["expedientes"].get(
        identificador
    )


def listar_oportunidades():
    workspace = iniciar_workspace()

    return sorted(
        workspace["expedientes"].values(),
        key=lambda expediente: expediente[
            "actualizado"
        ],
        reverse=True,
    )


def registrar_evento(identificador, accion):
    workspace = iniciar_workspace()
    expediente = workspace["expedientes"].get(
        identificador
    )

    if expediente is None:
        return False

    expediente["historial"].append({
        "fecha": ahora(),
        "accion": str(accion),
    })

    expediente["actualizado"] = ahora()
    return True


def actualizar_estado(identificador, estado):
    if estado not in ESTADOS:
        return False

    workspace = iniciar_workspace()
    expediente = workspace["expedientes"].get(
        identificador
    )

    if expediente is None:
        return False

    if expediente["estado"] != estado:
        expediente["estado"] = estado

        registrar_evento(
            identificador,
            f"Estado actualizado: {estado}",
        )

    return True


def actualizar_notas(identificador, notas):
    workspace = iniciar_workspace()
    expediente = workspace["expedientes"].get(
        identificador
    )

    if expediente is None:
        return False

    notas = str(notas)

    if expediente["notas"] != notas:
        expediente["notas"] = notas
        registrar_evento(
            identificador,
            "Notas de seguimiento actualizadas",
        )

    return True


def guardar_datos_modulo(nombre_modulo, datos):
    """
    API para guardar resultados separados
    por convocatoria y por módulo.
    """
    expediente = oportunidad_activa()

    if expediente is None:
        return False

    expediente["modulos"][nombre_modulo] = datos

    registrar_evento(
        expediente["id"],
        f"Información guardada: {nombre_modulo}",
    )

    return True


def obtener_datos_modulo(
    nombre_modulo,
    defecto=None,
):
    expediente = oportunidad_activa()

    if expediente is None:
        return defecto

    return expediente["modulos"].get(
        nombre_modulo,
        defecto,
    )


def exportar_workspace():
    workspace = iniciar_workspace()

    return json.dumps(
        workspace,
        ensure_ascii=False,
        indent=2,
        default=str,
    )


def importar_workspace(contenido):
    """
    Restaura un respaldo JSON exportado por INTI.
    No ejecuta instrucciones del archivo.
    """
    try:
        datos = json.loads(contenido)

        if not isinstance(datos, dict):
            return False, "Formato no válido."

        expedientes = datos.get("expedientes")

        if not isinstance(expedientes, dict):
            return False, (
                "El archivo no contiene expedientes."
            )

        for identificador, expediente in (
            expedientes.items()
        ):
            if not isinstance(expediente, dict):
                return False, (
                    "Se encontró un expediente no válido."
                )

            if not isinstance(
                expediente.get("oportunidad"),
                dict,
            ):
                return False, (
                    "Faltan datos de una oportunidad."
                )

            if not isinstance(
                expediente.get("historial", []),
                list,
            ):
                return False, (
                    "El historial tiene un formato inválido."
                )

        workspace = iniciar_workspace()

        for identificador, expediente in (
            expedientes.items()
        ):
            expediente.setdefault(
                "estado", "Por revisar"
            )
            expediente.setdefault("notas", "")
            expediente.setdefault("historial", [])
            expediente.setdefault("modulos", {})
            expediente.setdefault("creado", ahora())
            expediente.setdefault(
                "actualizado", ahora()
            )
            expediente["id"] = identificador

            workspace["expedientes"][
                identificador
            ] = expediente

        activa = datos.get("activa")

        if activa in workspace["expedientes"]:
            workspace["activa"] = activa

        sincronizar_legacy()

        return True, (
            f"Se restauraron {len(expedientes)} "
            "expedientes."
        )

    except (
        ValueError,
        TypeError,
        UnicodeDecodeError,
    ):
        return False, (
            "No fue posible interpretar el respaldo."
        )


def retirar_oportunidad(identificador):
    workspace = iniciar_workspace()

    if identificador not in workspace["expedientes"]:
        return False

    del workspace["expedientes"][identificador]

    if workspace["activa"] == identificador:
        workspace["activa"] = None

    sincronizar_legacy()
    return True
