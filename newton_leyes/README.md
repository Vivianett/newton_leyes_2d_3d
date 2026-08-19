# Leyes de Newton — Simulador Interactivo

Aplicación de escritorio en **Python** que presenta las tres leyes del
movimiento de Isaac Newton, cada una con su propia ventana y su propia
simulación interactiva.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-orange)

---

## ¿Por qué este lenguaje / estas librerías?

| Necesidad del proyecto | Solución elegida | Motivo |
|---|---|---|
| Ventanas múltiples e independientes | **Python + Tkinter** (`Toplevel`) | Cada ley abre su propia ventana real del sistema operativo, con su propio estado; cerrar o interactuar con una no afecta a las demás. |
| Que se vea profesional/moderno | **CustomTkinter** | Es una capa sobre Tkinter con bordes redondeados, modo oscuro, tipografías y controles (sliders, switches) con estética moderna, sin la pesadez de instalar Qt. |
| Animaciones simples (balón, carrito, pasos) | `tkinter.Canvas` + `after()` | Suficiente para animaciones 2D fluidas sin depender de un motor gráfico externo. |
| Escenas 3D interactivas | **Ursina** (motor 3D en Python) | Permite abrir ventanas 3D nativas de Python desde la aplicación, con cámara orbital interactiva, sin necesidad de Blender. Cada ley tiene su propia escena 3D (`*_3d.py`) que se sincroniza en tiempo real con la simulación 2D. |
| Fácil de instalar y ejecutar desde VS Code | `customtkinter`, `autobahn` y `ursina` | `tkinter` ya viene incluido con Python; Ursina se instala con `pip` y no requiere Blender. |

---

## Estructura del proyecto

```
newton_leyes/
├── main.py                    # Punto de entrada: menú principal
├── theme.py                   # Paleta de colores compartida (identidad visual)
├── ley1_inercia.py             # Ventana independiente — Primera Ley (2D)
├── ley2_fuerza.py              # Ventana independiente — Segunda Ley (2D)
├── ley3_accion_reaccion.py     # Ventana independiente — Tercera Ley (2D)
├── ley1_inercia_3d.py          # Escena 3D (Ursina) — Primera Ley
├── ley2_fuerza_3d.py           # Escena 3D (Ursina) — Segunda Ley
├── ley3_accion_reaccion_3d.py  # Escena 3D (Ursina) — Tercera Ley
├── escenas_3d_util.py          # Utilidades compartidas de las ventanas 3D
├── three_d.py                  # Lanzador de las ventanas 3D (Ursina)
├── three_d_scenes.py           # Compatibilidad para escenas antiguas
├── escena_3d_launcher.py       # Lanza cada script *_3d.py en subproceso
├── blender_launcher.py         # Lanzador opcional de Blender (legado)
├── modelos/                    # Archivos .blend de cada ley (opcionales)
├── requirements.txt
└── README.md
```

**Cada ley vive en su propio archivo y su propia clase** (`VentanaInercia`,
`VentanaFuerza`, `VentanaAccionReaccion`). Ninguna comparte variables,
temporizadores ni estado con las otras: puedes abrir las tres al mismo
tiempo, patear el balón, mover los sliders de fuerza y dar un paso, todo
en simultáneo, sin que una ventana interfiera con otra. `main.py` solo
las orquesta: sabe abrirlas y darles foco si ya están abiertas, pero no
conoce sus detalles internos.

---

## Instalación y ejecución (en Visual Studio Code)

1. Abre la carpeta `newton_leyes` en VS Code (`File → Open Folder…`).
2. Abre una terminal integrada (`` Ctrl+` ``) y crea un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS / Linux
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
   (incluye `customtkinter`, `autobahn` y `ursina` para el 3D).
4. Ejecuta la aplicación:
   ```bash
   python main.py
   ```
5. En VS Code, instala la extensión **Python** (de Microsoft) si no la
   tienes, para tener autocompletado y poder ejecutar con el botón ▶.

> **Nota:** en Linux, si `tkinter` no está instalado con tu Python,
> instálalo con `sudo apt install python3-tk` antes del paso 3.
>
> Las escenas 3D se abren en ventanas nativas de **Ursina** (un motor 3D
> en Python puro), así que no necesitas instalar Blender. Existe un lanzador
> opcional de Blender como legado, pero la vista 3D predeterminada usa Ursina.

---

## Qué hace cada ventana

- **Primera Ley (Inercia):** un balón permanece quieto hasta que lo
  "pateas". Puedes activar fricción para ver cómo una fuerza externa
  continua lo va frenando, en contraste con el movimiento indefinido
  sin fricción. Desde la ventana puedes abrir la escena 3D en **Ursina**,
  con cámara orbital que se sincroniza con la simulación 2D.
- **Segunda Ley (F = m·a):** mueve los sliders de masa y fuerza (o usa
  los presets de carrito vacío/lleno) y observa cómo cambia la
  aceleración calculada y la velocidad con la que arranca el carrito.
  La vista 3D en **Ursina** muestra el carrito con una cámara que puedes
  rotar y hacer zoom.
- **Tercera Ley (Acción y reacción):** simula un cohete al encender el
  motor, mostrando con flechas la fuerza de acción (el cohete empuja el
  gas hacia abajo) y la de reacción (el gas empuja el cohete hacia
  arriba), iguales en magnitud y opuestas en sentido. La escena 3D en
  **Ursina** revela el par de fuerzas en perspectiva con cámara orbital.

---

## Ideas para extender el proyecto (opcional)

Si quieres llevar el proyecto más lejos, aquí tienes ideas listas para
pedírselas a la IA integrada de VS Code (Copilot Chat u otra) sin tener
que empezar de cero. Puedes copiar y pegar directamente algo como:

> *"Sobre este proyecto de las Leyes de Newton en Python/CustomTkinter,
> agrega una gráfica de velocidad vs. tiempo con matplotlib dentro de
> la ventana de la Segunda Ley, actualizada en tiempo real durante la
> simulación del carrito, sin romper la estructura de clases existente."*

Otras ideas que puedes pedir de la misma forma:
- Guardar los resultados de cada simulación en un archivo CSV.
- Agregar efectos de sonido al patear el balón o al dar un paso.
- Un modo claro/oscuro alternable desde el menú principal.
- Pruebas unitarias (`pytest`) para la lógica de cálculo (`F = m·a`).
- Traducir la interfaz a inglés como opción de idioma.

---

*Proyecto generado con la asistencia de Claude (Anthropic) — código
probado y verificado en ejecución antes de la entrega.*
