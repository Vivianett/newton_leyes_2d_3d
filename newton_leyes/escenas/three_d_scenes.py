"""Punto de entrada para las ventanas 3D nativas (Ursina)."""

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPTS = {
    "inercia": "ley1_inercia_3d.py",
    "fuerza": "ley2_fuerza_3d.py",
    "accion": "ley3_accion_reaccion_3d.py",
}


def ejecutar_inercia(state_file=None, friction=False):
    subprocess.Popen([sys.executable, str(Path(__file__).parent / SCRIPTS["inercia"])])


def ejecutar_fuerza(state_file=None, masa=10.0, fuerza=50.0):
    subprocess.Popen([sys.executable, str(Path(__file__).parent / SCRIPTS["fuerza"])])


def ejecutar_accion_reaccion(state_file=None):
    subprocess.Popen([sys.executable, str(Path(__file__).parent / SCRIPTS["accion"])])


def main() -> None:
    parser = argparse.ArgumentParser(description="Escenas 3D para las leyes de Newton")
    parser.add_argument("--mode", choices=["inercia", "fuerza", "accion"], required=True)
    args = parser.parse_args()
    script = Path(__file__).parent / SCRIPTS[args.mode]
    subprocess.run([sys.executable, str(script)], check=False)


if __name__ == "__main__":
    main()
