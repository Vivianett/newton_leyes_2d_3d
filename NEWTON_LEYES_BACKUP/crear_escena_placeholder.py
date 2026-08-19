import os
from pathlib import Path

import bpy


def _configurar_render() -> None:
    available_engines = {
        item.identifier for item in bpy.context.scene.render.bl_rna.properties["engine"].enum_items
    }
    for candidate in ("BLENDER_EEVEE", "BLENDER_WORKBENCH", "CYCLES"):
        if candidate in available_engines:
            bpy.context.scene.render.engine = candidate
            break
    else:
        bpy.context.scene.render.engine = "BLENDER_EEVEE"

    bpy.context.scene.render.film_transparent = False
    bpy.context.scene.render.resolution_x = 1280
    bpy.context.scene.render.resolution_y = 720


def _configurar_mundo() -> None:
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.color = (0.03, 0.03, 0.04)


def _limpiar_escena() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def _crear_plano() -> None:
    bpy.ops.mesh.primitive_plane_add(size=10.0, location=(0.0, 0.0, 0.0))
    plane = bpy.context.active_object
    if plane is not None:
        plane.name = "plano"
        plane.rotation_euler = (0.0, 0.0, 0.0)


def _crear_camara(nombre: str, location: tuple[float, float, float], rotation: tuple[float, float, float]) -> None:
    bpy.ops.object.camera_add(location=location, rotation=rotation)
    camera = bpy.context.active_object
    if camera is not None:
        camera.name = nombre
        bpy.context.scene.camera = camera


def _crear_luz(location: tuple[float, float, float]) -> None:
    bpy.ops.object.light_add(type="SUN", location=location)
    light = bpy.context.active_object
    if light is not None:
        light.name = "luz_principal"
        light.data.energy = 3.0


def _crear_escena_ley(ley: str) -> None:
    _limpiar_escena()
    _configurar_render()
    _configurar_mundo()
    _crear_plano()
    _crear_luz((4.0, 4.0, 8.0))

    if ley == "ley1":
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.6))
        obj = bpy.context.active_object
        if obj is not None:
            obj.name = "cuerpo_inercia"
        _crear_camara("camara_inercia", (0.0, -7.0, 4.0), (1.2, 0.0, 0.0))
    elif ley == "ley2":
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.6))
        obj = bpy.context.active_object
        if obj is not None:
            obj.name = "cuerpo_fuerza"
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=2.0, location=(0.0, 0.0, 1.2))
        arrow = bpy.context.active_object
        if arrow is not None:
            arrow.name = "fuerza"
            arrow.rotation_euler = (0.0, 0.0, 0.0)
        _crear_camara("camara_fuerza", (0.0, -8.0, 4.0), (1.2, 0.0, 0.0))
    elif ley == "ley3":
        bpy.ops.mesh.primitive_cube_add(size=0.8, location=(-1.0, 0.0, 0.4))
        obj_a = bpy.context.active_object
        if obj_a is not None:
            obj_a.name = "cuerpo_a"
        bpy.ops.mesh.primitive_cube_add(size=0.8, location=(1.0, 0.0, 0.4))
        obj_b = bpy.context.active_object
        if obj_b is not None:
            obj_b.name = "cuerpo_b"
        _crear_camara("camara_accion", (0.0, -8.0, 4.0), (1.2, 0.0, 0.0))
    else:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.6))
        obj = bpy.context.active_object
        if obj is not None:
            obj.name = "modelo_placeholder"
        _crear_camara("camara_default", (0.0, -7.0, 4.0), (1.2, 0.0, 0.0))

    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)


def crear_escena_placeholder(output_path: Path, escena: str | None = None) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ley = (escena or "default").lower()
    if ley not in {"ley1", "ley2", "ley3"}:
        ley = "default"
    _crear_escena_ley(ley)
    bpy.ops.wm.save_as_mainfile(filepath=str(output_path), copy=True)


if __name__ == "__main__":
    output_path_str = os.environ.get("BLENDER_OUTPUT_PATH")
    if not output_path_str:
        raise SystemExit("Falta BLENDER_OUTPUT_PATH")

    escena = os.environ.get("BLENDER_ESCENA", "default")
    output_path = Path(output_path_str).expanduser()
    crear_escena_placeholder(output_path, escena=escena)
