import io
import re
import unicodedata
from datetime import datetime

from openpyxl import load_workbook


# ============================================================
# INTI PROJECTS AI
# IMPORTADOR HISTÓRICO DE PROYECTOS
# ============================================================


def limpiar_texto(valor):
    if valor is None:
        return ""

    return str(valor).strip()


def normalizar_texto(texto):
    texto = limpiar_texto(texto).lower()

    texto = unicodedata.normalize(
        "NFKD",
        texto
    )

    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


def convertir_fecha(valor):
    if not valor:
        return None

    if isinstance(valor, datetime):
        return valor.date().isoformat()

    return limpiar_texto(valor)


def convertir_valor(valor):
    if valor is None or valor == "":
        return 0

    try:
        return float(valor)
    except Exception:
        return 0


def convertir_prioridad(valor):
    try:
        numero = int(valor)
    except Exception:
        numero = 3

    mapa = {
        1: "P1 - Crítica",
        2: "P2 - Alta",
        3: "P3 - Media",
        4: "P4 - Exploratoria"
    }

    return mapa.get(
        numero,
        "P3 - Media"
    )


def determinar_estado(
    actividades,
    observaciones
):
    texto = normalizar_texto(
        f"{actividades} {observaciones}"
    )

    if "aplazado" in texto:
        return "⏸️ Aplazado"

    if (
        "bloqueado" in texto
        or "detenido" in texto
        or "suspendido" in texto
    ):
        return "🔴 Bloqueado"

    if (
        "preparar propuesta" in texto
        or "propuesta" in texto
    ):
        return "🟠 Propuesta en preparación"

    if (
        "formular proyecto" in texto
        or "formulacion" in texto
    ):
        return "🟣 En formulación"

    if (
        "hablar con" in texto
        or "revisar" in texto
        or "gestionar" in texto
        or "replantear" in texto
    ):
        return "🟡 En gestión"

    return "🔵 Iniciativa"


def detectar_tipo(nombre):
    texto = normalizar_texto(nombre)

    if (
        "iluminacion" in texto
        or "alumbrado" in texto
    ):
        return "Alumbrado público"

    if (
        "solar" in texto
        or "fotovolta" in texto
    ):
        return "Energía solar FV"

    if (
        "subestacion" in texto
        or "electrico" in texto
        or "electrica" in texto
        or "red electrica" in texto
    ):
        return "Infraestructura eléctrica"

    if "bombeo" in texto:
        return "Infraestructura eléctrica"

    return "Otro"


def crear_id_proyecto(
    nombre,
    entidad
):
    base = normalizar_texto(
        f"{nombre}-{entidad}"
    )

    base = re.sub(
        r"[^a-z0-9]+",
        "-",
        base
    )

    return base.strip("-")


# ============================================================
# LEER UNA HOJA
# ============================================================

def leer_hoja(hoja):
    proyectos = []

    # En el archivo actual:
    # fila 1 = título
    # fila 2 = encabezados
    # fila 3+ = proyectos

    for fila in hoja.iter_rows(
        min_row=3,
        values_only=True
    ):

        nombre = limpiar_texto(
            fila[0] if len(fila) > 0 else ""
        )

        if not nombre:
            continue

        prioridad_original = (
            fila[1]
            if len(fila) > 1
            else None
        )

        entidad = limpiar_texto(
            fila[2]
            if len(fila) > 2
            else ""
        )

        valor = convertir_valor(
            fila[3]
            if len(fila) > 3
            else 0
        )

        responsable = limpiar_texto(
            fila[4]
            if len(fila) > 4
            else ""
        )

        observaciones = limpiar_texto(
            fila[5]
            if len(fila) > 5
            else ""
        )

        actividades = limpiar_texto(
            fila[6]
            if len(fila) > 6
            else ""
        )

        plazo = convertir_fecha(
            fila[7]
            if len(fila) > 7
            else None
        )

        fecha_inicio = convertir_fecha(
            fila[8]
            if len(fila) > 8
            else None
        )

        desembolso = convertir_fecha(
            fila[9]
            if len(fila) > 9
            else None
        )

        finalizacion = convertir_fecha(
            fila[10]
            if len(fila) > 10
            else None
        )

        proyecto = {
            "id": crear_id_proyecto(
                nombre,
                entidad
            ),

            "nombre": nombre,

            "entidad": entidad,

            "municipio": "",

            "departamento": "",

            "tipo": detectar_tipo(
                nombre
            ),

            "valor_estimado": valor,

            "estado": determinar_estado(
                actividades,
                observaciones
            ),

            "prioridad": convertir_prioridad(
                prioridad_original
            ),

            # El Excel no trae probabilidad comercial.
            # No debemos inventarla.
            "probabilidad": 0,

            "responsable": responsable,

            "situacion_actual": (
                observaciones
            ),

            "proxima_accion": (
                actividades
            ),

            "fecha_proxima_accion": (
                plazo
            ),

            "fecha_inicio_contrato": (
                fecha_inicio
            ),

            "desembolso_anticipo": (
                desembolso
            ),

            "fecha_finalizacion": (
                finalizacion
            ),

            "fecha_creacion": (
                datetime.now().isoformat()
            ),

            "ultima_actualizacion": (
                datetime.now().isoformat()
            ),

            "historial": []
        }

        proyectos.append(
            proyecto
        )

    return proyectos


# ============================================================
# LEER LIBRO COMPLETO
# ============================================================

def importar_excel(bytes_archivo):
    libro = load_workbook(
        filename=io.BytesIO(
            bytes_archivo
        ),
        data_only=True
    )

    hojas = []

    for indice, nombre_hoja in enumerate(
        libro.sheetnames
    ):
        hoja = libro[
            nombre_hoja
        ]

        proyectos = leer_hoja(
            hoja
        )

        hojas.append({
            "indice": indice,
            "nombre": nombre_hoja,
            "proyectos": proyectos
        })

    return hojas


# ============================================================
# NORMALIZACIÓN PARA COMPARAR PROYECTOS
# ============================================================

def clave_comparacion(proyecto):
    nombre = normalizar_texto(
        proyecto.get(
            "nombre",
            ""
        )
    )

    entidad = normalizar_texto(
        proyecto.get(
            "entidad",
            ""
        )
    )

    return (
        nombre,
        entidad
    )


# ============================================================
# CONSTRUIR PORTAFOLIO ACTUAL
# ============================================================

def construir_portafolio_actual(
    hojas,
    hoja_actual=None
):
    if not hojas:
        return []

    # Si no indicamos hoja,
    # tomamos la primera del Excel.
    #
    # En el archivo suministrado la primera hoja:
    # 17-10-2026
    # contiene el seguimiento más actualizado.
    if hoja_actual is None:
        hoja_actual = hojas[0]

    proyectos_actuales = []

    for proyecto in hoja_actual[
        "proyectos"
    ]:
        proyecto_actual = dict(
            proyecto
        )

        proyecto_actual[
            "historial"
        ] = []

        proyectos_actuales.append(
            proyecto_actual
        )

    return proyectos_actuales


# ============================================================
# BUSCAR PROYECTO SIMILAR
# ============================================================

def buscar_proyecto(
    proyecto_objetivo,
    proyectos
):
    nombre_objetivo = normalizar_texto(
        proyecto_objetivo.get(
            "nombre",
            ""
        )
    )

    entidad_objetivo = normalizar_texto(
        proyecto_objetivo.get(
            "entidad",
            ""
        )
    )

    # Primero coincidencia exacta
    for proyecto in proyectos:
        if (
            normalizar_texto(
                proyecto.get(
                    "nombre",
                    ""
                )
            )
            == nombre_objetivo
            and
            normalizar_texto(
                proyecto.get(
                    "entidad",
                    ""
                )
            )
            == entidad_objetivo
        ):
            return proyecto

    # Segunda opción:
    # mismo nombre aunque la entidad
    # haya sido escrita diferente.
    for proyecto in proyectos:
        if (
            normalizar_texto(
                proyecto.get(
                    "nombre",
                    ""
                )
            )
            == nombre_objetivo
        ):
            return proyecto

    return None


# ============================================================
# COMPARAR DOS VERSIONES
# ============================================================

def comparar_proyectos(
    anterior,
    actual
):
    cambios = []

    campos = [
        (
            "valor_estimado",
            "Valor estimado"
        ),
        (
            "prioridad",
            "Prioridad"
        ),
        (
            "responsable",
            "Responsable"
        ),
        (
            "situacion_actual",
            "Observaciones"
        ),
        (
            "proxima_accion",
            "Actividad / próxima acción"
        ),
        (
            "fecha_inicio_contrato",
            "Fecha inicio"
        ),
        (
            "desembolso_anticipo",
            "Desembolso"
        ),
        (
            "fecha_finalizacion",
            "Finalización"
        )
    ]

    for campo, etiqueta in campos:
        valor_anterior = anterior.get(
            campo
        )

        valor_actual = actual.get(
            campo
        )

        if valor_anterior != valor_actual:
            cambios.append({
                "campo": campo,
                "etiqueta": etiqueta,
                "anterior": valor_anterior,
                "actual": valor_actual
            })

    return cambios


# ============================================================
# CONSTRUIR HISTORIAL
# ============================================================

def construir_historial(
    hojas,
    proyectos_actuales
):
    if not hojas:
        return proyectos_actuales

    # Recorremos las demás hojas como antecedentes.
    for proyecto_actual in proyectos_actuales:

        historial = []

        versiones = []

        for hoja in reversed(
            hojas
        ):
            proyecto_version = buscar_proyecto(
                proyecto_actual,
                hoja["proyectos"]
            )

            if proyecto_version:
                versiones.append({
                    "hoja": hoja["nombre"],
                    "proyecto": proyecto_version
                })

        if versiones:
            anterior = None

            for version in versiones:
                proyecto = version[
                    "proyecto"
                ]

                evento = {
                    "fecha": version[
                        "hoja"
                    ],

                    "fuente": (
                        "Importación histórica Excel"
                    ),

                    "descripcion": (
                        "Registro histórico del proyecto."
                    ),

                    "responsable": (
                        proyecto.get(
                            "responsable",
                            ""
                        )
                    ),

                    "valor_estimado": (
                        proyecto.get(
                            "valor_estimado",
                            0
                        )
                    ),

                    "estado": (
                        proyecto.get(
                            "estado",
                            ""
                        )
                    ),

                    "cambios": []
                }

                if anterior:
                    evento[
                        "cambios"
                    ] = comparar_proyectos(
                        anterior,
                        proyecto
                    )

                historial.append(
                    evento
                )

                anterior = proyecto

        proyecto_actual[
            "historial"
        ] = historial

    return proyectos_actuales


# ============================================================
# PROCESO COMPLETO
# ============================================================

def procesar_excel_proyectos(
    bytes_archivo
):
    hojas = importar_excel(
        bytes_archivo
    )

    proyectos_actuales = (
        construir_portafolio_actual(
            hojas
        )
    )

    proyectos_actuales = (
        construir_historial(
            hojas,
            proyectos_actuales
        )
    )

    return {
        "hojas": hojas,
        "proyectos": proyectos_actuales,
        "total_hojas": len(
            hojas
        ),
        "total_proyectos": len(
            proyectos_actuales
        )
    }
