"""
Segunda Ley de Newton — Vista 3D (F = m · a)
==============================================
Carrito empujado con fuerza constante: la aceleración depende de masa y fuerza.
Sincroniza con la ventana 2D mediante .fuerza_3d_state.json
"""

from __future__ import annotations

import math

from escenas_3d_util import COLORES, crear_flecha, escena_base, escribir_estado, leer_estado


def main() -> None:
    from ursina import Button, Entity, Slider, Text, Ursina, color, destroy, time, window

    app = Ursina(vsync=True)
    escena_base("Segunda Ley — F = m·a (3D)", COLORES["ley2"])
    rgb = COLORES["ley2"]

    masa = 10.0
    fuerza = 50.0
    pos_x = -8.0
    vel_visual = 0.0
    tiempo = 0.0
    animando = False
    flecha_partes: list = []

    def dibujar_carrito(x: float) -> Entity:
        cuerpo = Entity(position=(x, 0.55, 0))
        Entity(
            parent=cuerpo,
            model="cube",
            color=color.rgb(*[int(v * 255) for v in rgb]),
            scale=(1.4, 0.7, 0.9),
        )
        Entity(parent=cuerpo, model="sphere", color=color.black, scale=0.35, position=(-0.45, -0.3, 0.45))
        Entity(parent=cuerpo, model="sphere", color=color.black, scale=0.35, position=(0.45, -0.3, 0.45))
        Entity(parent=cuerpo, model="cube", color=color.white, scale=(0.5, 0.35, 0.05), position=(-0.15, 0.2, 0.46))
        return cuerpo

    carrito = dibujar_carrito(pos_x)

    lbl_formula = Text(
        text="a = F / m = 5.00 m/s²",
        position=window.top_left,
        origin=(-0.5, 0.5),
        scale=1.2,
        color=color.rgb(*[int(v * 255) for v in rgb]),
    )
    lbl_vel = Text(text="", position=(0, 0.46), origin=(0, 0), scale=1.0, color=color.white)
    Text(
        text="Ajusta masa y fuerza, luego simula el empuje. Sin fricción: la velocidad sigue subiendo.",
        position=window.bottom_left,
        origin=(-0.5, -0.5),
        scale=0.85,
        color=color.light_gray,
    )

    def actualizar_flecha() -> None:
        nonlocal flecha_partes
        for parte in flecha_partes:
            destroy(parte)
        flecha_partes = list(crear_flecha((pos_x - 1.8, 0.55, 0), (1, 0, 0), 1.2 + fuerza / 80, rgb))

    def actualizar_calculo() -> None:
        a = fuerza / masa if masa else 0
        lbl_formula.text = f"a = F / m = {fuerza:.0f} / {masa:.0f} = {a:.2f} m/s²"
        actualizar_flecha()

    def mover_carrito(nuevo_x: float) -> None:
        nonlocal pos_x
        pos_x = nuevo_x
        carrito.x = pos_x
        actualizar_flecha()

    def reiniciar() -> None:
        nonlocal pos_x, vel_visual, tiempo, animando
        animando = False
        vel_visual = 0.0
        tiempo = 0.0
        mover_carrito(-8.0)
        lbl_vel.text = ""

    def simular() -> None:
        nonlocal animando, vel_visual, tiempo
        reiniciar()
        animando = True

    def preset(m: float, f: float) -> None:
        nonlocal masa, fuerza
        masa = m
        fuerza = f
        slider_masa.value = m
        slider_fuerza.value = f
        actualizar_calculo()

    slider_masa = Slider(min=1, max=100, default=masa, x=-0.35, y=0.38, step=1)
    slider_fuerza = Slider(min=1, max=200, default=fuerza, x=-0.35, y=0.32, step=1)
    Text(text="Masa (kg)", x=-0.55, y=0.38, scale=0.9, color=color.light_gray)
    Text(text="Fuerza (N)", x=-0.55, y=0.32, scale=0.9, color=color.light_gray)

    Button(text="▶ Simular empuje", color=color.rgb(*[int(v * 255) for v in rgb]), scale=(0.3, 0.06), y=0.25, on_click=simular)
    Button(text="↺ Reiniciar", color=color.gray, scale=(0.22, 0.06), y=0.25, x=0.3, on_click=reiniciar)
    Button(text="Vacío 5 kg", color=color.dark_gray, scale=(0.18, 0.05), y=0.19, x=-0.28, on_click=lambda: preset(5, 40))
    Button(text="Lleno 40 kg", color=color.dark_gray, scale=(0.18, 0.05), y=0.19, x=0.05, on_click=lambda: preset(40, 40))

    actualizar_calculo()
    ultimo_estado: dict = {}

    def aplicar_estado_externo(state: dict) -> None:
        nonlocal masa, fuerza
        if "mass" in state:
            masa = float(state["mass"])
            slider_masa.value = masa
        if "force" in state:
            fuerza = float(state["force"])
            slider_fuerza.value = fuerza
        actualizar_calculo()
        limpiar = {}
        if state.get("reset"):
            reiniciar()
            limpiar["reset"] = False
        if state.get("simulate"):
            simular()
            limpiar["simulate"] = False
        if limpiar:
            escribir_estado("fuerza", limpiar)

    def update() -> None:
        nonlocal vel_visual, tiempo, animando, masa, fuerza, ultimo_estado

        state = leer_estado("fuerza")
        if state != ultimo_estado:
            aplicar_estado_externo(state)
            ultimo_estado = dict(state)

        masa = slider_masa.value
        fuerza = slider_fuerza.value
        actualizar_calculo()

        if not animando:
            return

        dt = time.dt
        a = fuerza / masa
        tiempo += dt
        v_real = a * tiempo
        paso_visual = 0.03 + 0.07 * math.log1p(a)
        vel_visual += paso_visual
        mover_carrito(pos_x + vel_visual)

        lbl_vel.text = (
            f"v ≈ {v_real:.3f} m/s tras t = {tiempo:.2f} s — sigue acelerando (sin fricción)"
        )

        if pos_x > 9.5:
            animando = False
            lbl_vel.text += " · salió del cuadro"

    # Ursina busca el callback por frame como atributo del módulo __main__.
    # Como update() vive dentro de main() (para usar closures con el estado
    # local), hay que registrarlo explícitamente o nunca se llamaría — y ni
    # los sliders, ni la animación, ni el polling del archivo de estado
    # (sincronía con la ventana 2D) funcionarían.
    import __main__ as _entry
    _entry.update = update

    app.run()


if __name__ == "__main__":
    main()
