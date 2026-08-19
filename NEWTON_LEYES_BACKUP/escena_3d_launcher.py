"""Lanzador de ventanas 3D nativas (Ursina) para cada ley de Newton."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Optional

import customtkinter as ctk

from theme import BG_APP, BG_CARD, BORDE_CARD, COLOR_LEY1, TEXT_MUTED

SCRIPTS = {
    "inercia": "ley1_inercia_3d.py",
    "fuerza": "ley2_fuerza_3d.py",
    "accion": "ley3_accion_reaccion_3d.py",
}


class _Mensaje3D(ctk.CTkToplevel):
    def __init__(self, parent, titulo: str, mensaje: str):
        super().__init__(parent)
        self.title(titulo)
        self.geometry("480x220")
        self.configure(fg_color=BG_APP)
        self.transient(parent)
        self.grab_set()
        ctk.CTkLabel(
            self,
            text=mensaje,
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED,
            wraplength=420,
            justify="center",
        ).pack(padx=24, pady=(24, 16))
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDE_CARD)
        card.pack(padx=24, pady=(0, 24), fill="x")
        ctk.CTkButton(card, text="Aceptar", fg_color=COLOR_LEY1, command=self.destroy, width=140).pack(pady=12)
        self.after(100, self.lift)


class Escena3DLauncher:
    def __init__(self) -> None:
        self._procesos: dict[str, subprocess.Popen] = {}
        self._base = Path(__file__).resolve().parent

    def abrir(self, modo: str, parent: Optional[ctk.CTk | ctk.CTkToplevel] = None) -> bool:
        script_name = SCRIPTS.get(modo)
        if script_name is None:
            self._error(parent, "Escena no válida", f"No existe una ventana 3D para '{modo}'.")
            return False

        proceso = self._procesos.get(modo)
        if proceso is not None and proceso.poll() is None:
            return True

        script_path = self._base / script_name
        if not script_path.is_file():
            self._error(parent, "Falta el script 3D", f"No se encontró {script_name}.")
            return False

        try:
            import ursina  # noqa: F401
        except ImportError:
            self._error(
                parent,
                "Falta Ursina",
                "Instala la dependencia 3D con:\n\npip install ursina",
            )
            return False

        try:
            nuevo = subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=str(self._base),
                start_new_session=True,
            )
        except OSError as exc:
            self._error(parent, "No se pudo abrir la escena 3D", str(exc))
            return False

        self._procesos[modo] = nuevo
        return True

    def _error(self, parent, titulo: str, mensaje: str) -> None:
        if parent is not None and parent.winfo_exists():
            _Mensaje3D(parent, titulo, mensaje)
        else:
            _Mensaje3D(None, titulo, mensaje)


_launcher = Escena3DLauncher()


def abrir_escena_3d_native(modo: str, parent: Optional[ctk.CTk | ctk.CTkToplevel] = None) -> bool:
    return _launcher.abrir(modo, parent=parent)
