"""
Tercera Ley de Newton — Vista 3D (Acción y Reacción)
======================================================
Cohete en plataforma: al encender el motor, el gas es empujado hacia abajo
(acción) y el cohete hacia arriba (reacción), con la misma magnitud.
Sincroniza con la ventana 2D mediante .accion_3d_state.json
"""

from __future__ import annotations

import random

from blender.escenas_3d_util import COLORES, crear_flecha, escena_base, escribir_estado, leer_estado


def main() -> None:
    from ursina import Button, Entity, Text, Ursina, color, destroy, time, window

    app = Ursina(vsync=True)
    escena_base("Tercera Ley — Acción y Reacción (3D)", COLORES["ley3"])
    rgb = COLORES["ley3"]
    fuerza_n = 4500

    altura_base = 0.5
    velocidad = 0.0
    motor_on = False
    fase = "reposo"
    particulas: list[tuple[Entity, float]] = []
    flechas: list = []

    Entity(model="cube", scale=(2.5, 0.2, 2.5), position=(0, 0.1, 0), color=color.rgb(42, 42, 63))
    torre = Entity(model="cube", scale=(0.25, 4, 0.25), position=(-4, 2, -2), color=color.rgb(51, 51, 74))

    cohete = Entity(position=(0, altura_base, 0))
    Entity(parent=cohete, model="cube", color=color.rgb(229, 231, 235), scale=(0.5, 1.6, 0.5), y=0.8)
    Entity(parent=cohete, model="cone", color=color.rgb(*[int(v * 255) for v in rgb]), scale=(0.45, 0.5, 0.45), y=1.65)
    Entity(parent=cohete, model="sphere", color=color.rgb(*[int(v * 255) for v in rgb]), scale=0.18, y=1.0, z=0.26)
    Entity(parent=cohete, model="cube", color=color.rgb(*[int(v * 255) for v in COLORES["ley3"]]), scale=(0.15, 0.35, 0.05), y=0.2, x=-0.32, rotation_z=20)
    Entity(parent=cohete, model="cube", color=color.rgb(*[int(v * 255) for v in COLORES["ley3"]]), scale=(0.15, 0.35, 0.05), y=0.2, x=0.32, rotation_z=-20)

    lbl_info = Text(
        text="En la plataforma. Enciende el motor para despegar.",
        position=window.top_left,
        origin=(-0.5, 0.5),
        scale=1.0,
        color=color.white,
    )
    lbl_fuerzas = Text(text="", position=(0, 0.44), origin=(0, 0), scale=1.0, color=color.rgb(*[int(v * 255) for v in rgb]))
    Text(
        text="Las flechas roja (acción) y verde (reacción) tienen la misma magnitud.",
        position=window.bottom_left,
        origin=(-0.5, -0.5),
        scale=0.85,
        color=color.light_gray,
    )

    def limpiar_flechas() -> None:
        nonlocal flechas
        for parte in flechas:
            destroy(parte)
        flechas = []

    def mostrar_flechas() -> None:
        limpiar_flechas()
        base = cohete.world_position
        origen = (base.x, base.y, base.z)
        flechas.extend(crear_flecha((origen[0], origen[1] - 0.2, origen[2]), (0, -1, 0), 1.6, COLORES["accion"]))
        flechas.extend(crear_flecha((origen[0], origen[1] + 0.2, origen[2]), (0, 1, 0), 1.6, COLORES["reaccion"]))

    def emitir_particula() -> None:
        p = Entity(
            model="sphere",
            color=color.orange,
            scale=0.12,
            position=(cohete.x + random.uniform(-0.15, 0.15), cohete.y, cohete.z + random.uniform(-0.1, 0.1)),
        )
        particulas.append((p, 1.0))

    def reiniciar() -> None:
        nonlocal altura_base, velocidad, motor_on, fase, particulas
        motor_on = False
        fase = "reposo"
        velocidad = 0.0
        altura_base = 0.5
        cohete.y = altura_base
        for p, _ in particulas:
            destroy(p)
        particulas = []
        limpiar_flechas()
        lbl_info.text = "En la plataforma. Enciende el motor para despegar."
        lbl_fuerzas.text = ""

    def encender() -> None:
        nonlocal motor_on, fase, velocidad
        if fase != "reposo":
            return
        motor_on = True
        fase = "ignicion"
        velocidad = 0.0
        lbl_info.text = "Motor encendido: acción ↓ sobre el gas, reacción ↑ sobre el cohete."
        lbl_fuerzas.text = f"F acción = F reacción = {fuerza_n} N"
        mostrar_flechas()

    ultimo_estado: dict = {}

    def aplicar_estado_externo(state: dict) -> None:
        limpiar = {}
        if state.get("reset"):
            reiniciar()
            limpiar["reset"] = False
        if state.get("step"):
            encender()
            limpiar["step"] = False
        if limpiar:
            escribir_estado("accion", limpiar)

    Button(
        text="🔥 Encender motor",
        color=color.rgb(*[int(v * 255) for v in rgb]),
        scale=(0.32, 0.06),
        y=0.36,
        on_click=encender,
    )
    Button(text="↺ Reiniciar", color=color.gray, scale=(0.22, 0.06), y=0.36, x=0.32, on_click=reiniciar)

    def update() -> None:
        nonlocal velocidad, motor_on, fase, particulas, ultimo_estado

        state = leer_estado("accion")
        if state != ultimo_estado:
            aplicar_estado_externo(state)
            ultimo_estado = dict(state)

        if not motor_on:
            return

        velocidad = min(velocidad + 0.06, 6.0)
        cohete.y += velocidad * time.dt * 8
        mostrar_flechas()

        if random.random() < 0.6:
            emitir_particula()

        vivas = []
        for ent, vida in particulas:
            ent.y -= 2.5 * time.dt
            ent.scale *= 0.98
            vida -= time.dt * 0.8
            if vida > 0:
                vivas.append((ent, vida))
            else:
                destroy(ent)
        particulas = vivas

        if cohete.y > 12:
            motor_on = False
            fase = "fuera"
            limpiar_flechas()
            lbl_info.text = "El cohete salió de escena. Reinicia para repetir la demostración."

    # Ursina busca el callback por frame como atributo del módulo __main__.
    # Como update() vive dentro de main() (para usar closures con el estado
    # local), hay que registrarlo explícitamente o nunca se llamaría — y el
    # despegue del cohete, las partículas y el polling del archivo de
    # estado (sincronía con la ventana 2D) se quedarían sin ejecutar.
    import __main__ as _entry
    _entry.update = update

    app.run()


if __name__ == "__main__":
    main()
