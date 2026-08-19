# Simulación Interactiva de las Leyes de Newton (2D y 3D)

Aplicación educativa de escritorio desarrollada en Python para explorar las tres leyes de Newton mediante simulaciones visuales e interactivas. Integra animaciones en tiempo real (2D) con vistas tridimensionales generadas en Blender.

## Características Principales
- **Menú principal intuitivo** con tarjetas visuales para cada ley.
- **Ventanas independientes** para la Primera Ley (Inercia), Segunda Ley (Fuerza) y Tercera Ley (Acción-Reacción).
- Controles deslizantes para ajustar **masa, fuerza y fricción** en tiempo real.
- Visualización 2D con objetos animados (balón, carrito, cohete).
- **Integración 3D**: Botón para abrir la misma simulación en un entorno Blender.
- Persistencia de estado mediante archivos JSON.

## 🛠️ Tecnologías Utilizadas
- **Python 3.x**
- **Tkinter** y **CustomTkinter** (Interfaz gráfica moderna)
- **Blender API** (Generación de escenas 3D)
- **JSON** (Persistencia de datos)
- **Subprocess** (Lanzamiento de procesos independientes)

## 🚀 Cómo ejecutarlo
1. Clona el repositorio:
   ```bash
   git clone https://github.com/Vivianett/newton_leyes_2d_3d.git

## Instala las dependencias
pip install -r requirements.txt

## Ejecuta la aplicación
python main.py

## Estructura del Proyecto
newton_leyes_3d_corregido/
├── main.py                     # Lanzador del menú principal
├── NEWTON_LEYES_BACKUP/        # Respaldo de módulos
├── newton_leyes/               # Núcleo de la aplicación
│   ├── blender/                # Scripts para generar escenas 3D
│   ├── core/                   # Temas y utilidades (three_d.py)
│   ├── escenas/                # Lanzador de escenas 3D
│   └── leyes/                  # Lógica de cada ley (inercia, fuerza, acción-reacción)
├── config/                     # Archivos JSON de estado
└── requirements.txt            # Dependencias del proyecto

## Autores
Jhonatan David Riascos Mosquera
Vivian Natalia Montaño Olaya

## Nota
Para la vista 3D es necesario tener Blender 4.5 instalado en el sistema.

  
