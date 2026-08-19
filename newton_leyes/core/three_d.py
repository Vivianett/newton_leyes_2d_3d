import json
import os
from typing import Any

from blender.blender_launcher import abrir_blender


def _state_path(modo: str) -> str:
    """
    Devuelve la ruta donde se guarda el estado de la escena 3D.
    """
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        f".{modo}_3d_state.json",
    )


def _leer_estado(modo: str) -> dict[str, Any]:
    """
    Lee el estado guardado de una escena 3D.
    """
    path = _state_path(modo)

    if not os.path.exists(path):
        return {}

    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def escribir_estado_3d(modo: str, datos: dict[str, Any]) -> None:
    """
    Guarda o actualiza el estado de una escena 3D.
    """
    state = _leer_estado(modo)
    state.update(datos)

    path = _state_path(modo)

    with open(path, "w", encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2)


def abrir_escena_3d(
    modo: str,
    parent=None,
    **params: Any,
):
    """
    Abre directamente la escena correspondiente en Blender.

    inercia -> ley1.blend
    fuerza  -> ley2.blend
    accion  -> ley3.blend
    """

    # Guardar el estado antes de abrir Blender
    escribir_estado_3d(modo, params)

    escenas = {
        "inercia": "ley1",
        "fuerza": "ley2",
        "accion": "ley3",
    }

    escena = escenas.get(modo)

    if escena is None:
        return False

    # Abrir directamente el archivo .blend
    return abrir_blender(escena, parent=parent)


def abrir_escena_blender(
    modo: str,
    parent=None,
    **params: Any,
):
    """
    Compatibilidad con código anterior.
    También abre directamente Blender.
    """

    escribir_estado_3d(modo, params)

    escenas = {
        "inercia": "ley1",
        "fuerza": "ley2",
        "accion": "ley3",
    }

    escena = escenas.get(modo)

    if escena is None:
        return False

    return abrir_blender(escena, parent=parent)
