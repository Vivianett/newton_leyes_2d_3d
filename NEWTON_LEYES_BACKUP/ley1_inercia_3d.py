"""
Primera Ley de Newton — Vista 3D (Inercia)
============================================
Balón en un plano: permanece en reposo hasta que se aplica una fuerza.
Con fricción activa, el suelo lo frena gradualmente.
Sincroniza con la ventana 2D mediante .inercia_3d_state.json
"""

from __future__ import annotations

from escenas_3d_util import COLORES, escena_base, escribir_estado, leer_estado


def main() -> None:
    from ursina import (
        Button,
        Entity,
        Text,
        Ursina,
        color,
        time,
        window,
    )

    app = Ursina(vsync=True)
    escena_base("Primera Ley — Inercia (3D)", COLORES["ley1"])
    rgb = COLORES["ley1"]

    limite_x = 10.5
    radio = 0.45
    pos_x = -8.0
    velocidad = 0.0
    friccion = False
    estado_texto = "En reposo — ninguna fuerza actúa"

    balon = Entity(
        model="sphere",
        color=color.rgb(*[int(v * 255) for v in rgb]),
        scale=radio * 2,
        position=(pos_x, radio, 0),
        collider="sphere",
    )
    Entity(parent=balon, model="sphere", color=color.white, scale=0.35, position=(-0.12, 0.08, 0.18))

    lbl_estado = Text(
        text=estado_texto,
        position=window.top_left,
        origin=(-0.5, 0.5),
        scale=1.1,
        color=color.white,
    )
    Text(
        text="[Espacio] Patear   [R] Reiniciar   [F] Fricción   |   Sincroniza con ventana 2D",
        position=window.bottom_left,
        origin=(-0.5, -0.5),
        scale=0.85,
        color=color.light_gray,
    )

    def reiniciar() -> None:
        nonlocal pos_x, velocidad, estado_texto
        pos_x = -8.0
        velocidad = 0.0
        estado_texto = "En reposo — ninguna fuerza actúa"
        balon.x = pos_x
        lbl_estado.text = estado_texto

    def patear() -> None:
        nonlocal velocidad
        if velocidad == 0:
            velocidad = 6.0

    def alternar_friccion() -> None:
        nonlocal friccion
        friccion = not friccion
        btn_friccion.text = f"Fricción: {'ON' if friccion else 'OFF'}"

    btn_patear = Button(text="⚡ Patear balón", color=color.rgb(*[int(v * 255) for v in rgb]), scale=(0.35, 0.06), y=0.42, on_click=patear)
    btn_reiniciar = Button(text="↺ Reiniciar", color=color.gray, scale=(0.25, 0.06), y=0.42, x=0.32, on_click=reiniciar)
    btn_friccion = Button(text="Fricción: OFF", color=color.dark_gray, scale=(0.28, 0.06), y=0.35, on_click=alternar_friccion)

    def input(key: str) -> None:
        if key == "space":
            patear()
        elif key == "r":
            reiniciar()
        elif key == "f":
            alternar_friccion()

    ultimo_estado: dict = {}

    def aplicar_estado_externo(state: dict) -> None:
        nonlocal friccion
        limpiar = {}
        if state.get("reset"):
            reiniciar()
            limpiar["reset"] = False
        if state.get("patear"):
            patear()
            limpiar["patear"] = False
        if "friction" in state and state["friction"] != friccion:
            friccion = bool(state["friction"])
            btn_friccion.text = f"Fricción: {'ON' if friccion else 'OFF'}"
        if limpiar:
            escribir_estado("inercia", limpiar)

    def update() -> None:
        nonlocal pos_x, velocidad, estado_texto, ultimo_estado

        state = leer_estado("inercia")
        if state != ultimo_estado:
            aplicar_estado_externo(state)
            ultimo_estado = dict(state)

        if velocidad != 0:
            pos_x += velocidad * 60 * time.dt
            if pos_x >= limite_x - radio or pos_x <= -limite_x + radio:
                velocidad *= -1
            if friccion:
                signo = 1 if velocidad > 0 else -1
                velocidad -= signo * 0.05
                if abs(velocidad) < 0.15:
                    velocidad = 0.0
                    estado_texto = "En reposo — la fricción lo detuvo"
            else:
                estado_texto = f"Movimiento rectilíneo uniforme — v ≈ {abs(velocidad):.1f}"

            balon.x = pos_x
            lbl_estado.text = estado_texto

    # Ursina descubre los callbacks por frame ('update') y de teclado
    # ('input') buscándolos como atributos del módulo __main__. Como aquí
    # están definidos dentro de main() (para poder usar closures con el
    # estado local), hay que registrarlos explícitamente o Ursina nunca
    # los llamaría — y la animación, el polling del archivo de estado y
    # los atajos de teclado se quedarían "muertos" en silencio.
    import __main__ as _entry
    _entry.update = update
    _entry.input = input

    app.run()


if __name__ == "__main__":
    main()
