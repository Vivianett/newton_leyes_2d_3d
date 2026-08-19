import json
import os
from typing import Any

from blender_launcher import abrir_blender


def _state_path(modo: str) -> str:
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        f".{modo}_3d_state.json",
    )


def _leer_estado(modo: str) -> dict[str, Any]:
    path = _state_path(modo)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def escribir_estado_3d(modo: str, datos: dict[str, Any]) -> None:
    state = _leer_estado(modo)
    state.update(datos)
    path = _state_path(modo)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(state, handle)


def abrir_escena_3d(modo: str, parent=None, **params: Any):
    """Abre la ventana 3D nativa (Ursina) y sincroniza el estado con la simulación 2D."""
    escribir_estado_3d(modo, params)
    from escena_3d_launcher import abrir_escena_3d_native

    return abrir_escena_3d_native(modo, parent=parent)


def abrir_escena_blender(modo: str, parent=None, **params: Any):
    """Compatibilidad: abre la escena en Blender externo si está instalado."""
    escribir_estado_3d(modo, params)
    escenas = {
        "inercia": "ley1",
        "fuerza": "ley2",
        "accion": "ley3",
    }
    escena = escenas.get(modo)
    if escena is None:
        return None
    return abrir_blender(escena, parent=parent)
