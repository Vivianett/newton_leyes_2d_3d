import bpy
import math
from mathutils import Vector
from pathlib import Path


# ============================================================
# SEGUNDA LEY DE NEWTON — ESCENA 3D
# F = m × a
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
MODELOS_DIR = BASE_DIR / "modelos"
MODELOS_DIR.mkdir(parents=True, exist_ok=True)

SALIDA = MODELOS_DIR / "ley2.blend"


# ============================================================
# LIMPIAR ESCENA
# ============================================================

def limpiar():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        # No eliminar materiales/cámaras/lights si están en uso
        pass


# ============================================================
# MATERIALES
# ============================================================

def material(nombre, color, metalico=0.0, rugosidad=0.45):
    mat = bpy.data.materials.get(nombre)

    if mat is None:
        mat = bpy.data.materials.new(nombre)

    mat.diffuse_color = (*color, 1.0)

    try:
        mat.metallic = metalico
        mat.roughness = rugosidad
    except:
        pass

    return mat


# ============================================================
# CREAR CUBO
# ============================================================

def cubo(nombre, ubicacion, escala, mat=None, bevel=0.08):
    bpy.ops.mesh.primitive_cube_add(
        location=ubicacion
    )

    obj = bpy.context.object
    obj.name = nombre
    obj.scale = escala

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True
    )

    if bevel > 0:
        modifier = obj.modifiers.new(
            name="Bisel",
            type="BEVEL"
        )
        modifier.width = bevel
        modifier.segments = 3

    if mat:
        obj.data.materials.append(mat)

    return obj


# ============================================================
# CILINDRO
# ============================================================

def cilindro(nombre, ubicacion, radio, profundidad, mat=None, rotacion=None):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=radio,
        depth=profundidad,
        location=ubicacion,
        rotation=rotacion or (0, 0, 0)
    )

    obj = bpy.context.object
    obj.name = nombre

    if mat:
        obj.data.materials.append(mat)

    return obj


# ============================================================
# ESFERA
# ============================================================

def esfera(nombre, ubicacion, radio, mat=None):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32,
        ring_count=16,
        radius=radio,
        location=ubicacion
    )

    obj = bpy.context.object
    obj.name = nombre

    if mat:
        obj.data.materials.append(mat)

    return obj


# ============================================================
# TEXTO 3D
# ============================================================

def texto(
    nombre,
    contenido,
    ubicacion,
    tamaño,
    mat,
    rotacion=(math.radians(90), 0, 0)
):
    curva = bpy.data.curves.new(
        nombre,
        type="FONT"
    )

    curva.body = contenido
    curva.align_x = "CENTER"
    curva.align_y = "CENTER"
    curva.size = tamaño
    curva.extrude = 0.015
    curva.bevel_depth = 0.005

    obj = bpy.data.objects.new(
        nombre,
        curva
    )

    bpy.context.collection.objects.link(obj)

    obj.location = ubicacion
    obj.rotation_euler = rotacion

    if mat:
        obj.data.materials.append(mat)

    return obj


# ============================================================
# FLECHA
# ============================================================

def flecha(nombre, inicio, fin, radio, mat):
    inicio = Vector(inicio)
    fin = Vector(fin)

    direccion = fin - inicio
    longitud = direccion.length

    if longitud <= 0:
        return None

    medio = (inicio + fin) / 2

    # Cuerpo
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24,
        radius=radio,
        depth=longitud * 0.75,
        location=medio
    )

    cuerpo = bpy.context.object
    cuerpo.name = nombre + "_CUERPO"

    cuerpo.data.materials.append(mat)

    # Orientar cilindro hacia la dirección
    cuerpo.rotation_mode = "QUATERNION"
    cuerpo.rotation_quaternion = direccion.to_track_quat(
        "Z",
        "Y"
    )

    # Punta
    punta_inicio = inicio + direccion.normalized() * (
        longitud * 0.72
    )

    bpy.ops.mesh.primitive_cone_add(
        vertices=24,
        radius1=radio * 2.5,
        radius2=0,
        depth=longitud * 0.28,
        location=fin
    )

    punta = bpy.context.object
    punta.name = nombre + "_PUNTA"

    punta.data.materials.append(mat)

    punta.rotation_mode = "QUATERNION"
    punta.rotation_quaternion = direccion.to_track_quat(
        "Z",
        "Y"
    )

    return cuerpo


# ============================================================
# CARRITO
# ============================================================

def crear_carrito(
    prefijo,
    x,
    y,
    color_carrito,
    color_rueda,
    masa,
    lleno=False
):

    piezas = []

    # Base
    base = cubo(
        prefijo + "_BASE",
        (x, y, 0.65),
        (1.45, 0.75, 0.25),
        color_carrito,
        0.12
    )

    piezas.append(base)

    # Parte superior
    superior = cubo(
        prefijo + "_CAJA",
        (x, y, 1.25),
        (1.25, 0.68, 0.45),
        color_carrito,
        0.10
    )

    piezas.append(superior)

    # Ruedas
    posiciones_ruedas = [
        (x - 0.9, y - 0.82, 0.35),
        (x + 0.9, y - 0.82, 0.35),
        (x - 0.9, y + 0.82, 0.35),
        (x + 0.9, y + 0.82, 0.35),
    ]

    for i, pos in enumerate(posiciones_ruedas):
        rueda = cilindro(
            f"{prefijo}_RUEDA_{i}",
            pos,
            0.34,
            0.20,
            color_rueda,
            rotacion=(math.radians(90), 0, 0)
        )

        piezas.append(rueda)

    # Pesos dentro del carrito
    if lleno:
        for i in range(8):
            px = x - 0.75 + (i % 4) * 0.5
            py = y - 0.45 + (i // 4) * 0.9

            peso = cubo(
                f"{prefijo}_PESO_{i}",
                (px, py, 1.82),
                (0.18, 0.18, 0.18),
                color_rueda,
                0.04
            )

            piezas.append(peso)

    # Etiqueta
    texto(
        prefijo + "_ETIQUETA",
        f"{masa} kg",
        (x, y - 1.15, 2.25),
        0.42,
        color_rueda
    )

    return piezas


# ============================================================
# PISO
# ============================================================

def crear_piso(mat):
    piso = cubo(
        "PISTA",
        (0, 0, -0.15),
        (14, 7, 0.15),
        mat,
        0.03
    )

    return piso


# ============================================================
# ILUMINACIÓN
# ============================================================

def crear_luces():
    bpy.ops.object.light_add(
        type="AREA",
        location=(0, -6, 10)
    )

    luz = bpy.context.object
    luz.name = "LUZ_PRINCIPAL"
    luz.data.energy = 1600
    luz.data.shape = "DISK"
    luz.data.size = 8

    luz.rotation_euler = (
        math.radians(25),
        0,
        0
    )

    bpy.ops.object.light_add(
        type="AREA",
        location=(0, 5, 6)
    )

    relleno = bpy.context.object
    relleno.name = "LUZ_RELLENO"
    relleno.data.energy = 900
    relleno.data.size = 6

    relleno.rotation_euler = (
        math.radians(-45),
        0,
        math.radians(180)
    )


# ============================================================
# CÁMARA
# ============================================================

def crear_camara():
    bpy.ops.object.camera_add(
        location=(18, -24, 15)
    )

    camara = bpy.context.object
    camara.name = "CAMARA"

    objetivo = Vector((2, 0, 1.2))

    direccion = objetivo - camara.location

    camara.rotation_euler = direccion.to_track_quat(
        "-Z",
        "Y"
    ).to_euler()

    camara.data.lens = 48

    bpy.context.scene.camera = camara

    return camara


# ============================================================
# ANIMACIÓN
# ============================================================

def animar_carrito(piezas, desplazamiento, frame_final):
    for obj in piezas:
        if obj.animation_data:
            obj.animation_data_clear()

        posicion_original = obj.location.copy()

        obj.location = posicion_original

        obj.keyframe_insert(
            data_path="location",
            frame=1
        )

        obj.location.x += desplazamiento

        obj.keyframe_insert(
            data_path="location",
            frame=frame_final
        )

        # Blender 5.2 usa una API de Action diferente.
        # Buscamos los canales disponibles sin asumir fcurves.
        if obj.animation_data and obj.animation_data.action:
            action = obj.animation_data.action

            # Blender 4/5
            if hasattr(action, "layers"):
                for layer in action.layers:
                    if hasattr(layer, "strips"):
                        for strip in layer.strips:
                            if hasattr(strip, "channelbag"):
                                try:
                                    bag = strip.channelbag(
                                        action_slot_handle=action.slots[0].handle
                                    )

                                    if bag and hasattr(bag, "fcurves"):
                                        for fc in bag.fcurves:
                                            for key in fc.keyframe_points:
                                                key.interpolation = "LINEAR"
                                except Exception:
                                    pass

            # Compatibilidad con versiones anteriores
            if hasattr(action, "fcurves"):
                for fc in action.fcurves:
                    for key in fc.keyframe_points:
                        key.interpolation = "LINEAR"


# ============================================================
# CONFIGURAR ESCENA
# ============================================================

def configurar_escena():
    escena = bpy.context.scene

    escena.frame_start = 1
    escena.frame_end = 180
    escena.render.resolution_x = 1280
    escena.render.resolution_y = 720
    escena.render.resolution_percentage = 100

    # Blender 5.2
    try:
        escena.render.engine = "BLENDER_EEVEE_NEXT"
    except:
        try:
            escena.render.engine = "BLENDER_EEVEE"
        except:
            escena.render.engine = "BLENDER_WORKBENCH"

    escena.world.color = (0.008, 0.01, 0.025)

    # Fondo
    try:
        escena.world.use_nodes = True
        fondo = escena.world.node_tree.nodes.get("Background")

        if fondo:
            fondo.inputs["Color"].default_value = (
                0.008,
                0.01,
                0.025,
                1
            )

            fondo.inputs["Strength"].default_value = 0.25

    except:
        pass


# ============================================================
# CREAR ESCENA LEY 2
# ============================================================

def crear_ley2():

    print("[INFO] Creando Ley 2 — Fuerza")

    limpiar()
    configurar_escena()

    # --------------------------------------------------------
    # MATERIALES
    # --------------------------------------------------------

    naranja = material(
        "NARANJA",
        (1.0, 0.25, 0.03),
        0.1,
        0.35
    )

    naranja_claro = material(
        "NARANJA_CLARO",
        (1.0, 0.55, 0.08),
        0.05,
        0.35
    )

    azul = material(
        "AZUL",
        (0.03, 0.35, 1.0),
        0.15,
        0.3
    )

    amarillo = material(
        "AMARILLO",
        (1.0, 0.75, 0.05),
        0.05,
        0.3
    )

    blanco = material(
        "BLANCO",
        (0.9, 0.95, 1.0),
        0,
        0.4
    )

    gris = material(
        "PISTA",
        (0.055, 0.06, 0.10),
        0,
        0.7
    )

    negro = material(
        "RUEDAS",
        (0.015, 0.015, 0.02),
        0.1,
        0.5
    )

    # --------------------------------------------------------
    # PISTA
    # --------------------------------------------------------

    crear_piso(gris)

    # Líneas de pista
    for x in range(-12, 13, 2):
        cubo(
            f"LINEA_{x}",
            (x, 0, 0.02),
            (0.03, 6.5, 0.02),
            blanco,
            0
        )

    # --------------------------------------------------------
    # CARRITO VACÍO — 5 KG
    # --------------------------------------------------------

    carrito_vacio = crear_carrito(
        "CARRITO_5KG",
        -7,
        2.4,
        naranja,
        negro,
        5,
        lleno=False
    )

    # --------------------------------------------------------
    # CARRITO LLENO — 40 KG
    # --------------------------------------------------------

    carrito_lleno = crear_carrito(
        "CARRITO_40KG",
        -7,
        -2.4,
        naranja_claro,
        negro,
        40,
        lleno=True
    )

    # --------------------------------------------------------
    # TÍTULO
    # --------------------------------------------------------

    texto(
        "TITULO",
        "SEGUNDA LEY DE NEWTON",
        (0, 0, 5.8),
        0.85,
        naranja_claro
    )

    texto(
        "FORMULA",
        "F = m x a",
        (0, 0, 4.8),
        0.65,
        blanco
    )

    texto(
        "EXPLICACION",
        "A MAYOR MASA, MENOR ACELERACION CON LA MISMA FUERZA",
        (0, 0, 4.0),
        0.38,
        blanco
    )

    # --------------------------------------------------------
    # DATOS DEL CARRITO 5 KG
    # --------------------------------------------------------

    texto(
        "DATOS_5KG",
        "F = 50 N     m = 5 kg     a = 10 m/s2",
        (-3.5, 2.4, 3.1),
        0.38,
        naranja_claro
    )

    # --------------------------------------------------------
    # DATOS DEL CARRITO 40 KG
    # --------------------------------------------------------

    texto(
        "DATOS_40KG",
        "F = 50 N     m = 40 kg     a = 1.25 m/s2",
        (-2.5, -2.4, 3.1),
        0.34,
        blanco
    )

    # --------------------------------------------------------
    # FLECHA DE FUERZA — 5 KG
    # --------------------------------------------------------

    flecha(
        "FUERZA_5KG",
        (-5.0, 2.4, 1.2),
        (-1.5, 2.4, 1.2),
        0.16,
        amarillo
    )

    texto(
        "FLECHA_TEXTO_5KG",
        "50 N",
        (-3.25, 2.4, 1.75),
        0.42,
        amarillo
    )

    # --------------------------------------------------------
    # FLECHA DE FUERZA — 40 KG
    # --------------------------------------------------------

    flecha(
        "FUERZA_40KG",
        (-5.0, -2.4, 1.2),
        (-1.5, -2.4, 1.2),
        0.16,
        amarillo
    )

    texto(
        "FLECHA_TEXTO_40KG",
        "50 N",
        (-3.25, -2.4, 1.75),
        0.42,
        amarillo
    )

    # --------------------------------------------------------
    # ETIQUETAS
    # --------------------------------------------------------

    texto(
        "ETIQUETA_VACIO",
        "CARRITO VACIO — 5 KG",
        (-7, 2.4, 2.8),
        0.40,
        naranja_claro
    )

    texto(
        "ETIQUETA_LLENO",
        "CARRITO LLENO — 40 KG",
        (-7, -2.4, 2.8),
        0.40,
        naranja_claro
    )

    # --------------------------------------------------------
    # ANIMACIONES
    # --------------------------------------------------------

    # 5 kg:
    # a = 50 / 5 = 10 m/s²
    # Se desplaza mucho más rápido.
    animar_carrito(
        carrito_vacio,
        13,
        180
    )

    # 40 kg:
    # a = 50 / 40 = 1.25 m/s²
    # Se desplaza mucho menos.
    animar_carrito(
        carrito_lleno,
        4.0,
        180
    )

    # --------------------------------------------------------
    # MARCADORES DE RECORRIDO
    # --------------------------------------------------------

    texto(
        "RESULTADO_5KG",
        "a = 50 / 5 = 10 m/s2",
        (4, 2.4, 2.9),
        0.38,
        naranja_claro
    )

    texto(
        "RESULTADO_40KG",
        "a = 50 / 40 = 1.25 m/s2",
        (-3, -2.4, 2.9),
        0.38,
        blanco
    )

    # --------------------------------------------------------
    # CÁMARA Y LUCES
    # --------------------------------------------------------

    crear_luces()
    crear_camara()

    # --------------------------------------------------------
    # CONFIGURACIÓN DE REPRODUCCIÓN
    # --------------------------------------------------------

    escena = bpy.context.scene

    escena.frame_set(1)

    try:
        escena.render.fps = 30
    except:
        pass

    # --------------------------------------------------------
    # GUARDAR
    # --------------------------------------------------------

    bpy.ops.wm.save_as_mainfile(
        filepath=str(SALIDA)
    )

    print("")
    print("==============================================")
    print(" GENERACION LEY 2 COMPLETADA")
    print("==============================================")
    print(f"Archivo: {SALIDA}")
    print(f"Tamaño: {SALIDA.stat().st_size:,} bytes")
    print("")


# ============================================================
# MAIN
# ============================================================

def main():
    print("")
    print("==============================================")
    print(" GENERADOR 3D — SEGUNDA LEY DE NEWTON")
    print("==============================================")

    crear_ley2()

    print("Blender quit")


if __name__ == "__main__":
    main()