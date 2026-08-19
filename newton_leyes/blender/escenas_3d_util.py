"""Utilidades compartidas para las ventanas 3D nativas."""

from __future__ import annotations

import json
import os
from typing import Any

from core.theme import (
    COLOR_ACCION,
    COLOR_LEY1,
    COLOR_LEY2,
    COLOR_LEY3,
    COLOR_REACCION,
)


def hex_a_rgb(hex_color: str) -> tuple[float, float, float]:
    hex_color = hex_color.lstrip("#")
    return (
        int(hex_color[0:2], 16) / 255.0,
        int(hex_color[2:4], 16) / 255.0,
        int(hex_color[4:6], 16) / 255.0,
    )


COLORES = {
    "ley1": hex_a_rgb(COLOR_LEY1),
    "ley2": hex_a_rgb(COLOR_LEY2),
    "ley3": hex_a_rgb(COLOR_LEY3),
    "accion": hex_a_rgb(COLOR_ACCION),
    "reaccion": hex_a_rgb(COLOR_REACCION),
}


def ruta_estado(modo: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), f".{modo}_3d_state.json")


def leer_estado(modo: str) -> dict[str, Any]:
    path = ruta_estado(modo)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def escribir_estado(modo: str, datos: dict[str, Any]) -> None:
    """Actualiza el archivo de estado (fusiona con lo existente).

    Se usa desde las propias escenas 3D para 'apagar' banderas de un solo
    uso (patear, simulate, step, reset) justo después de aplicarlas, para
    que no se repitan solas la próxima vez que se abra la ventana 3D.
    """
    path = ruta_estado(modo)
    state = leer_estado(modo)
    state.update(datos)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(state, handle)


def escena_base(titulo: str, color_fondo: tuple[float, float, float] = (0.04, 0.04, 0.07)):
    """Configura suelo, cámara orbital y luz para cualquier escena."""
    from ursina import AmbientLight, DirectionalLight, EditorCamera, Entity, color, window

    Entity(
        model="plane",
        scale=(24, 1, 12),
        texture="white_cube",
        texture_scale=(24, 12),
        color=color.rgb(35, 35, 55),
        collider="box",
    )
    Entity(
        model="cube",
        scale=(24, 0.15, 0.4),
        position=(0, 0.08, 5.8),
        color=color.rgb(50, 50, 70),
    )
    Entity(
        model="cube",
        scale=(24, 0.15, 0.4),
        position=(0, 0.08, -5.8),
        color=color.rgb(50, 50, 70),
    )

    EditorCamera()
    DirectionalLight(y=2, z=3, rotation=(45, -30, 0))
    AmbientLight(color=color.rgba(120, 120, 140, 0.35))
    window.title = titulo
    window.color = color.rgb(*[int(c * 255) for c in color_fondo])
    window.borderless = False
    window.exit_button.visible = False


def crear_flecha(
    origen,
    direccion,
    largo: float,
    rgb: tuple[float, float, float],
    grosor: float = 0.08,
):
    """Flecha 3D simple: cilindro + cono."""
    from ursina import Entity, Vec3, color

    # `origen` llega como tupla normal desde las escenas (p. ej. (x, y, z)).
    # Hay que convertirlo a Vec3 antes de sumarlo con dir_norm (un Vec3),
    # porque tupla + Vec3 no es una operación válida en Python.
    origen = Vec3(*origen)
    dir_norm = Vec3(*direccion).normalized()
    cuerpo = Entity(
        model="cube",
        color=color.rgb(*[int(v * 255) for v in rgb]),
        scale=(grosor, largo * 0.75, grosor),
        position=origen + dir_norm * (largo * 0.375),
    )
    cuerpo.look_at(origen + dir_norm * largo)
    punta = Entity(
        model="cone",
        color=color.rgb(*[int(v * 255) for v in rgb]),
        scale=(grosor * 2.5, largo * 0.25, grosor * 2.5),
        position=origen + dir_norm * (largo * 0.875),
    )
    punta.look_at(origen + dir_norm * (largo + 0.5))
    return cuerpo, punta
