# ============================================================
# GENERADOR 3D — LEYES DE NEWTON
# Blender 5.2 LTS
#
# Genera:
#   blender/modelos/ley1.blend
#   blender/modelos/ley2.blend
#   blender/modelos/ley3.blend
#
# Ley 1: Pelota quieta -> patada -> movimiento rectilíneo
# Ley 2: Carrito + masa + fuerza -> aceleración
# Ley 3: Cohete -> gas hacia abajo / reacción hacia arriba
# ============================================================

import bpy
import math
import os
from mathutils import Vector

# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELOS_DIR = os.path.join(BASE_DIR, "modelos")
os.makedirs(MODELOS_DIR, exist_ok=True)

FPS = 30

# ============================================================
# COLORES
# ============================================================

COLORES = {
    "fondo": (0.025, 0.03, 0.06, 1.0),
    "suelo": (0.08, 0.09, 0.14, 1.0),
    "gris": (0.35, 0.38, 0.45, 1.0),
    "gris_oscuro": (0.18, 0.20, 0.28, 1.0),
    "azul": (0.08, 0.42, 1.0, 1.0),
    "azul_claro": (0.20, 0.60, 1.0, 1.0),
    "amarillo": (1.0, 0.65, 0.05, 1.0),
    "naranja": (1.0, 0.32, 0.04, 1.0),
    "rojo": (1.0, 0.12, 0.12, 1.0),
    "verde": (0.10, 0.85, 0.35, 1.0),
    "verde_agua": (0.05, 0.80, 0.55, 1.0),
    "blanco": (0.95, 0.97, 1.0, 1.0),
    "negro": (0.01, 0.01, 0.015, 1.0),
}

# ============================================================
# UTILIDADES
# ============================================================

def limpiar_escena():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    # Limpiar datos huérfanos sin depender de APIs nuevas.
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.cameras,
        bpy.data.lights,
        bpy.data.materials,
    ):
        for datablock in list(datablocks):
            try:
                if datablock.users == 0:
                    datablocks.remove(datablock)
            except Exception:
                pass


def material(nombre, color, metallic=0.0, roughness=0.45):
    mat = bpy.data.materials.get(nombre)

    if mat is None:
        mat = bpy.data.materials.new(nombre)

    mat.diffuse_color = color

    # Blender 5.2: no necesitamos use_nodes para estas escenas.
    try:
        mat.metallic = metallic
        mat.roughness = roughness
    except Exception:
        pass

    return mat


def aplicar_material(obj, mat):
    if obj.data and hasattr(obj.data, "materials"):
        obj.data.materials.clear()
        obj.data.materials.append(mat)


def crear_cubo(nombre, ubicacion, escala, mat):
    bpy.ops.mesh.primitive_cube_add(location=ubicacion)

    obj = bpy.context.object
    obj.name = nombre
    obj.scale = escala

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True,
    )

    aplicar_material(obj, mat)
    return obj


def crear_esfera(nombre, ubicacion, radio, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=40,
        ring_count=24,
        radius=radio,
        location=ubicacion,
    )

    obj = bpy.context.object
    obj.name = nombre

    aplicar_material(obj, mat)

    try:
        bpy.ops.object.shade_smooth()
    except Exception:
        pass

    return obj


def crear_cilindro(nombre, ubicacion, radio, profundidad, mat):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=40,
        radius=radio,
        depth=profundidad,
        location=ubicacion,
    )

    obj = bpy.context.object
    obj.name = nombre

    aplicar_material(obj, mat)

    try:
        bpy.ops.object.shade_smooth()
    except Exception:
        pass

    return obj


def crear_cono(nombre, ubicacion, radio, profundidad, mat):
    bpy.ops.mesh.primitive_cone_add(
        vertices=40,
        radius1=radio,
        radius2=0.0,
        depth=profundidad,
        location=ubicacion,
    )

    obj = bpy.context.object
    obj.name = nombre
    aplicar_material(obj, mat)

    try:
        bpy.ops.object.shade_smooth()
    except Exception:
        pass

    return obj


# ============================================================
# TEXTO 3D
# ============================================================

def crear_texto(
    nombre,
    texto,
    ubicacion,
    tamaño,
    mat,
    rotacion=(math.radians(90), 0, 0),
):
    curva = bpy.data.curves.new(
        name=nombre + "_CURVE",
        type="FONT",
    )

    curva.body = texto
    curva.align_x = "CENTER"
    curva.align_y = "CENTER"
    curva.size = tamaño
    curva.extrude = 0.012
    curva.bevel_depth = 0.003

    obj = bpy.data.objects.new(nombre, curva)
    bpy.context.collection.objects.link(obj)

    obj.location = ubicacion
    obj.rotation_euler = rotacion

    aplicar_material(obj, mat)
    return obj


# ============================================================
# FLECHAS
# ============================================================

def crear_flecha(nombre, inicio, fin, grosor, mat):
    inicio = Vector(inicio)
    fin = Vector(fin)

    direccion = fin - inicio
    longitud = direccion.length

    if longitud <= 0.001:
        return None

    direccion.normalize()

    # Cuerpo
    cuerpo_longitud = longitud * 0.72
    cuerpo_centro = inicio + direccion * (cuerpo_longitud / 2.0)

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24,
        radius=grosor,
        depth=cuerpo_longitud,
        location=cuerpo_centro,
    )

    cuerpo = bpy.context.object
    cuerpo.name = nombre + "_CUERPO"
    cuerpo.rotation_mode = "QUATERNION"
    cuerpo.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(
        direccion
    )
    aplicar_material(cuerpo, mat)

    # Punta
    punta_longitud = longitud * 0.28
    punta_centro = fin - direccion * (punta_longitud / 2.0)

    bpy.ops.mesh.primitive_cone_add(
        vertices=28,
        radius1=grosor * 2.4,
        radius2=0.0,
        depth=punta_longitud,
        location=punta_centro,
    )

    punta = bpy.context.object
    punta.name = nombre + "_PUNTA"
    punta.rotation_mode = "QUATERNION"
    punta.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(
        direccion
    )
    aplicar_material(punta, mat)

    return cuerpo, punta


def ocultar_entre_frames(obj, frame_visible_inicio, frame_visible_fin):
    """
    Hace que un objeto aparezca solamente dentro de un intervalo.
    Compatible con Blender 5.2 porque no toca Action.fcurves.
    """
    obj.hide_render = True
    obj.hide_viewport = True
    obj.keyframe_insert(data_path="hide_render", frame=1)
    obj.keyframe_insert(data_path="hide_viewport", frame=1)

    obj.hide_render = True
    obj.hide_viewport = True
    obj.keyframe_insert(
        data_path="hide_render",
        frame=max(1, frame_visible_inicio - 1),
    )
    obj.keyframe_insert(
        data_path="hide_viewport",
        frame=max(1, frame_visible_inicio - 1),
    )

    obj.hide_render = False
    obj.hide_viewport = False
    obj.keyframe_insert(data_path="hide_render", frame=frame_visible_inicio)
    obj.keyframe_insert(data_path="hide_viewport", frame=frame_visible_inicio)

    obj.hide_render = False
    obj.hide_viewport = False
    obj.keyframe_insert(data_path="hide_render", frame=frame_visible_fin)
    obj.keyframe_insert(data_path="hide_viewport", frame=frame_visible_fin)

    obj.hide_render = True
    obj.hide_viewport = True
    obj.keyframe_insert(
        data_path="hide_render",
        frame=frame_visible_fin + 1,
    )
    obj.keyframe_insert(
        data_path="hide_viewport",
        frame=frame_visible_fin + 1,
    )


# ============================================================
# CÁMARA
# ============================================================

def crear_camara(ubicacion=(0, -24, 8), objetivo=(0, 0, 2.8)):
    bpy.ops.object.camera_add(location=ubicacion)

    camara = bpy.context.object
    camara.name = "CAMARA_PRINCIPAL"

    direccion = Vector(objetivo) - camara.location
    camara.rotation_euler = direccion.to_track_quat("-Z", "Y").to_euler()

    camara.data.lens = 50
    bpy.context.scene.camera = camara

    return camara


# ============================================================
# ILUMINACIÓN
# ============================================================

def crear_luces():
    bpy.ops.object.light_add(
        type="AREA",
        location=(0, -6, 12),
    )

    luz = bpy.context.object
    luz.name = "LUZ_PRINCIPAL"
    luz.data.energy = 1200
    luz.data.shape = "DISK"
    luz.data.size = 8

    direccion = Vector((0, 0, 1)) - luz.location
    luz.rotation_euler = direccion.to_track_quat("-Z", "Y").to_euler()

    bpy.ops.object.light_add(
        type="AREA",
        location=(8, 2, 7),
    )

    luz2 = bpy.context.object
    luz2.name = "LUZ_SECUNDARIA"
    luz2.data.energy = 700
    luz2.data.size = 5

    direccion = Vector((0, 0, 2)) - luz2.location
    luz2.rotation_euler = direccion.to_track_quat("-Z", "Y").to_euler()


# ============================================================
# RENDER — BLENDER 5.2
# ============================================================

def configurar_render():
    escena = bpy.context.scene

    # En Blender 5.2 LTS el enum compatible es BLENDER_EEVEE.
    escena.render.engine = "BLENDER_EEVEE"

    escena.render.resolution_x = 1280
    escena.render.resolution_y = 720
    escena.render.resolution_percentage = 100

    escena.render.image_settings.file_format = "PNG"
    escena.render.fps = FPS

    escena.world.color = (
        0.008,
        0.012,
        0.025,
    )


# ============================================================
# BASE COMÚN
# ============================================================

def preparar_base():
    limpiar_escena()
    configurar_render()

    mats = {
        "fondo": material("MAT_FONDO", COLORES["fondo"]),
        "suelo": material("MAT_SUELO", COLORES["suelo"]),
        "gris": material("MAT_GRIS", COLORES["gris"]),
        "gris_oscuro": material("MAT_GRIS_OSCURO", COLORES["gris_oscuro"]),
        "azul": material("MAT_AZUL", COLORES["azul"]),
        "azul_claro": material("MAT_AZUL_CLARO", COLORES["azul_claro"]),
        "amarillo": material("MAT_AMARILLO", COLORES["amarillo"]),
        "naranja": material("MAT_NARANJA", COLORES["naranja"]),
        "rojo": material("MAT_ROJO", COLORES["rojo"]),
        "verde": material("MAT_VERDE", COLORES["verde"]),
        "verde_agua": material("MAT_VERDE_AGUA", COLORES["verde_agua"]),
        "blanco": material("MAT_BLANCO", COLORES["blanco"]),
        "negro": material("MAT_NEGRO", COLORES["negro"]),
    }

    # Piso
    crear_cubo(
        "SUELO",
        (0, 0, -0.25),
        (10, 4, 0.25),
        mats["suelo"],
    )

    crear_cubo(
        "BORDE_SUELO",
        (0, -3.55, 0.03),
        (10, 0.06, 0.06),
        mats["gris"],
    )

    crear_luces()
    crear_camara()

    return mats


# ============================================================
# ANIMACIÓN SEGURA
# ============================================================

def keyframe_location(obj, frame, location):
    obj.location = location
    obj.keyframe_insert(
        data_path="location",
        frame=frame,
    )


# ============================================================
# LEY 1 — INERCIA
#
# Demostración:
#   1-50   pelota quieta
#   50-70  aparece la patada
#   70-220 pelota avanza
#   220    continúa en la misma dirección
#
# Es la versión 3D de la demostración de Python:
# pelota en reposo -> aplicar fuerza -> movimiento.
# ============================================================

def crear_ley1():
    print("[INFO] Creando Ley 1 — Inercia")

    mats = preparar_base()
    escena = bpy.context.scene
    escena.frame_start = 1
    escena.frame_end = 240

    crear_texto(
        "TITULO_LEY1",
        "PRIMERA LEY DE NEWTON — LEY DE LA INERCIA",
        (0, 0.45, 6.0),
        0.48,
        mats["azul_claro"],
    )

    crear_texto(
        "SUBTITULO_LEY1",
        "UN OBJETO MANTIENE SU ESTADO HASTA QUE UNA FUERZA EXTERNA ACTUA",
        (0, 0.42, 5.35),
        0.24,
        mats["blanco"],
    )

    # Pared al final: otra fuerza externa.
    crear_cubo(
        "PARED_FINAL",
        (9.0, 0, 1.7),
        (0.30, 2.4, 1.9),
        mats["rojo"],
    )

    crear_texto(
        "TEXTO_PARED",
        "FUERZA EXTERNA",
        (8.45, -0.02, 4.0),
        0.25,
        mats["rojo"],
    )

    # Pelota.
    pelota = crear_esfera(
        "PELOTA_INERCIA",
        (-6.5, 0, 0.82),
        0.82,
        mats["azul"],
    )

    # Aro visual alrededor de la pelota.
    aro = crear_torus = None
    try:
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.82,
            minor_radius=0.035,
            major_segments=48,
            minor_segments=12,
            location=(-6.5, 0, 0.82),
            rotation=(math.radians(90), 0, 0),
        )
        aro = bpy.context.object
        aro.name = "ARO_PELOTA"
        aplicar_material(aro, mats["azul_claro"])
    except Exception:
        aro = None

    # Reposo.
    keyframe_location(pelota, 1, (-6.5, 0, 0.82))
    keyframe_location(pelota, 50, (-6.5, 0, 0.82))

    if aro:
        keyframe_location(aro, 1, (-6.5, 0, 0.82))
        keyframe_location(aro, 50, (-6.5, 0, 0.82))

    crear_texto(
        "ESTADO_REPOSO",
        "PELOTA EN REPOSO",
        (-6.0, 0.35, 1.75),
        0.28,
        mats["blanco"],
    )

    # Patada.
    flecha_patada = crear_flecha(
        "FUERZA_PATADA",
        (-8.5, 0, 0.82),
        (-6.9, 0, 0.82),
        0.16,
        mats["amarillo"],
    )

    if flecha_patada:
        for parte in flecha_patada:
            ocultar_entre_frames(parte, 50, 70)

    crear_texto(
        "TEXTO_PATADA",
        "FUERZA EXTERNA → PATADA",
        (-5.9, 0.35, 3.0),
        0.30,
        mats["amarillo"],
    )

    # Movimiento después de la patada.
    keyframe_location(pelota, 70, (-6.5, 0, 0.82))
    keyframe_location(pelota, 150, (-0.5, 0, 0.82))
    keyframe_location(pelota, 220, (6.0, 0, 0.82))
    keyframe_location(pelota, 240, (7.5, 0, 0.82))

    if aro:
        keyframe_location(aro, 70, (-6.5, 0, 0.82))
        keyframe_location(aro, 150, (-0.5, 0, 0.82))
        keyframe_location(aro, 220, (6.0, 0, 0.82))
        keyframe_location(aro, 240, (7.5, 0, 0.82))

    flecha_movimiento = crear_flecha(
        "FLECHA_MOVIMIENTO",
        (-2.8, 0, 2.0),
        (2.0, 0, 2.0),
        0.11,
        mats["verde"],
    )

    if flecha_movimiento:
        for parte in flecha_movimiento:
            ocultar_entre_frames(parte, 71, 240)

    crear_texto(
        "TEXTO_MOVIMIENTO",
        "SIN OTRA FUERZA → EL MOVIMIENTO CONTINUA",
        (0, 0.35, 3.15),
        0.28,
        mats["verde"],
    )

    crear_texto(
        "ESTADO_FINAL",
        "MOVIMIENTO RECTILINEO",
        (3.3, 0.35, 1.75),
        0.28,
        mats["verde"],
    )

    # Marcas visuales del recorrido.
    for x in range(-6, 9, 2):
        crear_cubo(
            f"MARCA_{x}",
            (x, -0.35, 0.02),
            (0.025, 0.18, 0.025),
            mats["gris"],
        )

    escena.frame_set(1)

    ruta = os.path.join(MODELOS_DIR, "ley1.blend")
    bpy.ops.wm.save_as_mainfile(filepath=ruta)
    print("[OK] ley1.blend creado")


# ============================================================
# LEY 2 — F = m × a
#
# Demostración visual:
#   - Carrito naranja.
#   - Fuerza aplicada hacia la derecha.
#   - Dos referencias de masa: 5 kg y 40 kg.
#   - El carrito acelera cuando recibe la fuerza.
# ============================================================

def crear_rueda(nombre, ubicacion, mat):
    rueda = crear_cilindro(
        nombre,
        ubicacion,
        0.28,
        0.18,
        mat,
    )
    rueda.rotation_euler = (math.radians(90), 0, 0)
    return rueda


def crear_carrito(nombre, x, y, z, mat_cuerpo, mat_rueda):
    partes = []

    cuerpo = crear_cubo(
        nombre + "_CUERPO",
        (x, y, z + 0.65),
        (1.05, 0.65, 0.45),
        mat_cuerpo,
    )
    partes.append(cuerpo)

    parte_superior = crear_cubo(
        nombre + "_CABINA",
        (x + 0.15, y, z + 1.18),
        (0.65, 0.55, 0.30),
        mat_cuerpo,
    )
    partes.append(parte_superior)

    for i, wx in enumerate((-0.65, 0.65)):
        rueda = crear_rueda(
            f"{nombre}_RUEDA_{i}",
            (x + wx, y - 0.68, z + 0.30),
            mat_rueda,
        )
        partes.append(rueda)

    return partes


def crear_ley2():
    print("[INFO] Creando Ley 2 — Fuerza")

    mats = preparar_base()
    escena = bpy.context.scene
    escena.frame_start = 1
    escena.frame_end = 220

    crear_texto(
        "TITULO_LEY2",
        "SEGUNDA LEY DE NEWTON — F = m × a",
        (0, 0.45, 6.0),
        0.50,
        mats["naranja"],
    )

    crear_texto(
        "SUBTITULO_LEY2",
        "LA ACELERACION DEPENDE DE LA FUERZA Y DE LA MASA",
        (0, 0.42, 5.35),
        0.27,
        mats["blanco"],
    )

    # Zona superior: comparación de masas.
    crear_texto(
        "MASA_5KG",
        "CARRITO VACIO — 5 kg",
        (-3.8, 0.35, 4.55),
        0.32,
        mats["azul_claro"],
    )

    crear_texto(
        "MASA_40KG",
        "CARRITO LLENO — 40 kg",
        (3.8, 0.35, 4.55),
        0.32,
        mats["rojo"],
    )

    # Carrito principal, inspirado en la demostración 2D.
    carrito = crear_carrito(
        "CARRITO_PRINCIPAL",
        -6.0,
        0,
        0,
        mats["naranja"],
        mats["negro"],
    )

    # Masa representada como cajas encima del carrito.
    for i in range(4):
        crear_cubo(
            f"PESO_{i}",
            (-6.15 + (i % 2) * 0.55, 0, 1.72 + (i // 2) * 0.48),
            (0.24, 0.45, 0.18),
            mats["rojo"],
        )

    crear_texto(
        "MASA_ACTUAL",
        "m = 40 kg",
        (-5.2, 0.35, 2.75),
        0.30,
        mats["rojo"],
    )

    # Fuerza grande hacia la derecha.
    fuerza = crear_flecha(
        "FUERZA_50N",
        (-3.9, 0, 1.0),
        (-0.7, 0, 1.0),
        0.20,
        mats["naranja"],
    )

    crear_texto(
        "FUERZA_TEXTO",
        "F = 50 N",
        (-2.4, 0.35, 2.1),
        0.36,
        mats["naranja"],
    )

    crear_texto(
        "FORMULA_LEY2",
        "a = F / m",
        (0, 0.35, 3.45),
        0.44,
        mats["naranja"],
    )

    crear_texto(
        "CALCULO_LEY2",
        "a = 50 / 40 = 1.25 m/s²",
        (0, 0.35, 2.95),
        0.32,
        mats["blanco"],
    )

    # Animación del carrito: acelera hacia la derecha.
    posiciones = [
        (1, -6.0),
        (50, -5.5),
        (100, -3.8),
        (150, -1.0),
        (200, 3.5),
        (220, 5.5),
    ]

    for frame, x in posiciones:
        delta = x - (-6.0)

        for obj in carrito:
            keyframe_location(
                obj,
                frame,
                (obj.location.x + delta, obj.location.y, obj.location.z),
            )

    # La flecha aparece durante el empuje.
    if fuerza:
        for parte in fuerza:
            ocultar_entre_frames(parte, 30, 75)

    crear_texto(
        "ACELERACION",
        "MAYOR FUERZA → MAYOR ACELERACION",
        (0, 0.35, 4.0),
        0.30,
        mats["verde"],
    )

    # Línea visual de recorrido.
    for x in range(-7, 8, 2):
        crear_cubo(
            f"MARCA_LEY2_{x}",
            (x, -0.35, 0.02),
            (0.025, 0.18, 0.025),
            mats["gris"],
        )

    escena.frame_set(1)

    ruta = os.path.join(MODELOS_DIR, "ley2.blend")
    bpy.ops.wm.save_as_mainfile(filepath=ruta)
    print("[OK] ley2.blend creado")


# ============================================================
# LEY 3 — ACCIÓN Y REACCIÓN
#
# Demostración:
#   COHETE
#       ↑ reacción sobre el cohete
#       |
#       COHETE
#       |
#       ↓ acción sobre el gas
#
# El gas es expulsado hacia abajo y el cohete recibe una fuerza
# igual y opuesta hacia arriba.
# ============================================================

def crear_cohete(mats):
    partes = []

    # Cuerpo principal.
    cuerpo = crear_cilindro(
        "COHETE_CUERPO",
        (0, 0, 2.9),
        0.75,
        2.4,
        mats["blanco"],
    )
    partes.append(cuerpo)

    # Nariz.
    nariz = crear_cono(
        "COHETE_NARIZ",
        (0, 0, 4.35),
        0.75,
        1.25,
        mats["blanco"],
    )
    partes.append(nariz)

    # Ventana.
    ventana = crear_esfera(
        "COHETE_VENTANA",
        (0, -0.73, 3.25),
        0.20,
        mats["verde_agua"],
    )
    partes.append(ventana)

    # Aletas.
    aleta_izq = crear_cubo(
        "COHETE_ALETA_IZQ",
        (-0.85, 0, 2.05),
        (0.38, 0.16, 0.65),
        mats["verde_agua"],
    )
    partes.append(aleta_izq)

    aleta_der = crear_cubo(
        "COHETE_ALETA_DER",
        (0.85, 0, 2.05),
        (0.38, 0.16, 0.65),
        mats["verde_agua"],
    )
    partes.append(aleta_der)

    # Motor.
    motor = crear_cilindro(
        "COHETE_MOTOR",
        (0, 0, 1.65),
        0.40,
        0.35,
        mats["gris_oscuro"],
    )
    partes.append(motor)

    return partes


def crear_gas(nombre, x, y, z, radio, mat):
    gas = crear_esfera(
        nombre,
        (x, y, z),
        radio,
        mat,
    )
    return gas


def crear_ley3():
    print("[INFO] Creando Ley 3 — Acción y Reacción")

    mats = preparar_base()
    escena = bpy.context.scene
    escena.frame_start = 1
    escena.frame_end = 220

    crear_texto(
        "TITULO_LEY3",
        "TERCERA LEY DE NEWTON — ACCION Y REACCION",
        (0, 0.45, 6.0),
        0.48,
        mats["verde_agua"],
    )

    crear_texto(
        "SUBTITULO_LEY3",
        "A TODA ACCION CORRESPONDE UNA REACCION IGUAL Y OPUESTA",
        (0, 0.42, 5.35),
        0.25,
        mats["blanco"],
    )

    # Torre/guía visual.
    crear_cubo(
        "TORRE_GUIA",
        (-5.5, 0, 3.0),
        (0.08, 0.08, 2.8),
        mats["gris_oscuro"],
    )

    for z in (0.8, 1.6, 2.4, 3.2, 4.0, 4.8):
        crear_cubo(
            f"MARCA_ALTURA_{z}",
            (-5.25, 0, z),
            (0.30, 0.08, 0.025),
            mats["gris"],
        )

    # Cohete.
    cohete = crear_cohete(mats)

    # Animación vertical del cohete.
    for frame, z_offset in (
        (1, 0.0),
        (40, 0.0),
        (80, 1.0),
        (120, 2.4),
        (160, 4.0),
        (200, 5.5),
        (220, 6.8),
    ):
        for obj in cohete:
            keyframe_location(
                obj,
                frame,
                (
                    obj.location.x,
                    obj.location.y,
                    obj.location.z + z_offset,
                ),
            )

    # Flecha de reacción: hacia arriba, sobre el cohete.
    reaccion = crear_flecha(
        "REACCION_COhete",
        (0, 0, 3.0),
        (0, 0, 5.3),
        0.14,
        mats["verde"],
    )

    if reaccion:
        for parte in reaccion:
            ocultar_entre_frames(parte, 40, 220)

    crear_texto(
        "TEXTO_REACCION",
        "REACCION: 4500 N ↑",
        (2.2, 0.35, 4.4),
        0.31,
        mats["verde"],
    )

    crear_texto(
        "TEXTO_REACCION_2",
        "(SOBRE EL COHETE)",
        (2.2, 0.35, 3.95),
        0.25,
        mats["verde"],
    )

    # Acción: gas hacia abajo.
    accion = crear_flecha(
        "ACCION_GAS",
        (0, 0, 2.0),
        (0, 0, -0.3),
        0.14,
        mats["amarillo"],
    )

    if accion:
        for parte in accion:
            ocultar_entre_frames(parte, 40, 220)

    crear_texto(
        "TEXTO_ACCION",
        "ACCION: 4500 N ↓",
        (2.2, 0.35, 2.15),
        0.31,
        mats["amarillo"],
    )

    crear_texto(
        "TEXTO_ACCION_2",
        "(SOBRE EL GAS)",
        (2.2, 0.35, 1.70),
        0.25,
        mats["amarillo"],
    )

    # Gas/llama debajo del motor.
    gas_particulas = [
        (-0.30, 0, 1.20),
        (0.00, 0, 1.05),
        (0.30, 0, 1.18),
        (-0.20, 0, 0.72),
        (0.20, 0, 0.65),
        (0.00, 0, 0.45),
        (-0.35, 0, 0.25),
        (0.35, 0, 0.18),
        (0.00, 0, -0.05),
    ]

    for i, (x, y, z) in enumerate(gas_particulas):
        p = crear_gas(
            f"GAS_{i}",
            x,
            y,
            z,
            0.11 if i < 4 else 0.08,
            mats["amarillo"] if i % 2 == 0 else mats["naranja"],
        )

        # El gas se aleja hacia abajo.
        keyframe_location(p, 40, (x, y, z))
        keyframe_location(p, 90, (x * 1.2, y, z - 1.5))
        keyframe_location(p, 140, (x * 1.5, y, z - 3.0))
        keyframe_location(p, 200, (x * 2.0, y, z - 4.5))

    crear_texto(
        "MENSAJE_LEY3",
        "EL GAS SALE HACIA ABAJO Y EL COHETE ES IMPULSADO HACIA ARRIBA",
        (0, 0.35, 0.0),
        0.28,
        mats["blanco"],
    )

    crear_texto(
        "FORMULA_LEY3",
        "F ACCION = F REACCION = 4500 N",
        (0, 0.35, 5.0),
        0.36,
        mats["verde_agua"],
    )

    # Plataforma.
    crear_cubo(
        "PLATAFORMA",
        (0, 0, -0.05),
        (1.5, 1.0, 0.08),
        mats["gris_oscuro"],
    )

    escena.frame_set(1)

    ruta = os.path.join(MODELOS_DIR, "ley3.blend")
    bpy.ops.wm.save_as_mainfile(filepath=ruta)
    print("[OK] ley3.blend creado")


# ============================================================
# GENERACIÓN COMPLETA
# ============================================================

def main():
    print("")
    print("=" * 60)
    print("GENERADOR 3D — LEYES DE NEWTON")
    print("Blender 5.2 LTS")
    print("=" * 60)
    print("")

    crear_ley1()
    crear_ley2()
    crear_ley3()

    print("")
    print("=" * 60)
    print("GENERACION COMPLETADA")
    print("=" * 60)
    print("")
    print("Carpeta:")
    print(MODELOS_DIR)
    print("")

    for nombre in (
        "ley1.blend",
        "ley2.blend",
        "ley3.blend",
    ):
        ruta = os.path.join(MODELOS_DIR, nombre)

        if os.path.isfile(ruta):
            tamaño = os.path.getsize(ruta)
            print(f"[OK] {nombre} ({tamaño:,} bytes)")
        else:
            print(f"[ERROR] No se creó {nombre}")

    print("")


if __name__ == "__main__":
    main()