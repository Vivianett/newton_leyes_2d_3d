from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional

import customtkinter as ctk

from theme import BG_APP, BG_CARD, BORDE_CARD, COLOR_LEY1, TEXT_MUTED

DEFAULT_BLENDER_PATHS = [
    r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 3.4\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 3.3\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 2.93\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 2.9\blender.exe",
]
CUSTOM_BLENDER_PATH: Optional[str] = None
MODELOS_DIR = Path(__file__).resolve().parent / "modelos"
SCENES = {
    "ley1": "ley1.blend",
    "ley2": "ley2.blend",
    "ley3": "ley3.blend",
}


class CTkMessageBox(ctk.CTkToplevel):
    """Cuadro de diálogo modal con estilo CustomTkinter para mensajes simples."""

    def __init__(self, parent: Optional[ctk.CTk] | ctk.CTkToplevel, title: str, message: str):
        super().__init__(parent)
        self.title(title)
        self.geometry("460x200")
        self.minsize(460, 200)
        self.configure(fg_color=BG_APP)
        self.transient(parent)
        self.grab_set()

        ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED,
            wraplength=400,
            justify="center",
        ).pack(padx=24, pady=(24, 16))

        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDE_CARD)
        card.pack(padx=24, pady=(0, 24), fill="x")

        ctk.CTkButton(
            card,
            text="Aceptar",
            fg_color=COLOR_LEY1,
            hover_color="#3a6f7f",
            command=self.destroy,
            width=140,
        ).pack(pady=12)

        self.bind("<Return>", lambda _event: self.destroy())
        self.after(100, self.lift)


class BlenderLauncher:
    """Gestor modular para abrir escenas 3D en Blender desde Python."""

    def __init__(self) -> None:
        self._active_processes: dict[str, subprocess.Popen[str]] = {}

    def abrir(self, escena: str, parent: Optional[ctk.CTk] | ctk.CTkToplevel = None) -> bool:
        """Abre una escena Blender si la ruta es válida y no está ya activa."""
        if escena not in SCENES:
            self._mostrar_error(parent, "Escena no válida", f"La escena '{escena}' no está soportada.")
            return False

        if escena in self._active_processes and self._active_processes[escena].poll() is None:
            return False

        blender_exe = self._resolver_blender(parent)
        if blender_exe is None:
            self._mostrar_error(
                parent,
                "No se encontró Blender",
                "No se encontró Blender.\nConfigure la ruta de Blender en blender_launcher.py",
            )
            return False

        blend_path = self._resolver_modelo(escena)
        if blend_path is None:
            self._mostrar_error(
                parent,
                "No existe el modelo 3D",
                f"No existe el modelo 3D correspondiente para '{escena}'.",
            )
            return False

        if not blender_exe.is_file():
            self._mostrar_error(parent, "Ruta inválida", "La ruta de Blender no apunta a un archivo válido.")
            return False

        if not blend_path.is_file() or blend_path.stat().st_size <= 0:
            if not self._generar_escena_placeholder(blender_exe, blend_path, parent):
                return False

        command_variants = [
            [str(blender_exe), str(blend_path)],
            [str(blender_exe), "--factory-startup"],
            [str(blender_exe)],
        ]

        last_error: Optional[Exception] = None
        for index, command in enumerate(command_variants):
            try:
                process = subprocess.Popen(
                    command,
                    cwd=str(blend_path.parent),
                    stdin=None,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    start_new_session=True,
                    close_fds=True,
                )
            except OSError as exc:
                last_error = exc
                continue

            time.sleep(1.5)
            if process.poll() is None:
                self._active_processes[escena] = process
                return True

            output = ""
            if process.stdout is not None:
                output = process.stdout.read()

            if index == 0 and process.returncode not in (0, None):
                if self._generar_escena_placeholder(blender_exe, blend_path, parent):
                    return self.abrir(escena, parent=parent)

            last_error = RuntimeError(
                f"Blender cerró inmediatamente con código {process.returncode}.\n{output.strip()}".strip()
            )

        if last_error is not None:
            self._mostrar_error(parent, "No se pudo abrir Blender", f"Ocurrió un error al intentar abrir Blender.\n{last_error}")
            return False

        self._active_processes[escena] = process
        return True

    def _resolver_blender(self, parent: Optional[ctk.CTk] | ctk.CTkToplevel) -> Optional[Path]:
        """Busca una ruta válida de Blender siguiendo un orden de prioridad."""
        if CUSTOM_BLENDER_PATH:
            path = Path(CUSTOM_BLENDER_PATH).expanduser()
            if path.is_file():
                return path

        for candidate in DEFAULT_BLENDER_PATHS:
            path = Path(candidate).expanduser()
            if path.is_file():
                return path

        path_from_env = os.environ.get("BLENDER_EXE")
        if path_from_env:
            env_path = Path(path_from_env).expanduser()
            if env_path.is_file():
                return env_path

        which_blender = shutil.which("blender")
        if which_blender:
            return Path(which_blender)

        search_roots = [
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Blender",
            Path(os.environ.get("USERPROFILE", "")) / "AppData" / "Local" / "Programs" / "Blender",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Blender Foundation",
            Path(os.environ.get("USERPROFILE", "")) / "AppData" / "Local" / "Programs" / "Blender Foundation",
            Path("C:/Program Files/Blender Foundation"),
            Path("C:/Program Files (x86)/Blender Foundation"),
            Path("C:/Program Files"),
            Path("C:/Program Files (x86)"),
        ]
        for base in search_roots:
            if not base.exists():
                continue
            for match in sorted(base.rglob("blender.exe")):
                if match.is_file():
                    return match

        return None

    def _resolver_modelo(self, escena: str) -> Optional[Path]:
        """Devuelve la ruta del modelo Blender asociado a una escena."""
        model_name = SCENES.get(escena)
        if not model_name:
            return None
        return MODELOS_DIR / model_name

    def _generar_escena_placeholder(
        self,
        blender_exe: Path,
        blend_path: Path,
        parent: Optional[ctk.CTk] | ctk.CTkToplevel,
    ) -> bool:
        """Genera una escena Blender mínima cuando el archivo .blend está ausente o vacío."""
        script_path = Path(__file__).resolve().parent / "crear_escena_placeholder.py"
        if not script_path.is_file():
            self._mostrar_error(
                parent,
                "No se pudo preparar la escena 3D",
                "No se encontró el script auxiliar para crear una escena 3D mínima.",
            )
            return False

        command = [str(blender_exe), "-b", "--python", str(script_path)]

        env = os.environ.copy()
        env["BLENDER_OUTPUT_PATH"] = str(blend_path)

        try:
            completed = subprocess.run(
                command,
                cwd=str(blend_path.parent),
                stdin=None,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError as exc:
            self._mostrar_error(parent, "No se pudo preparar la escena 3D", f"Ocurrió un error al intentar crear la escena 3D.\n{exc}")
            return False

        if completed.returncode != 0:
            output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
            if output:
                self._mostrar_error(parent, "No se pudo preparar la escena 3D", f"Blender no pudo generar la escena.\n{output}")
            else:
                self._mostrar_error(parent, "No se pudo preparar la escena 3D", "Blender no pudo generar la escena.")
            return False

        return True

    def _mostrar_error(self, parent: Optional[ctk.CTk] | ctk.CTkToplevel, title: str, message: str) -> None:
        if parent is not None and parent.winfo_exists():
            CTkMessageBox(parent=parent, title=title, message=message)
            return
        CTkMessageBox(parent=None, title=title, message=message)


launcher = BlenderLauncher()


def abrir_blender(escena: str, parent: Optional[ctk.CTk] | ctk.CTkToplevel = None) -> bool:
    """API pública para abrir una escena Blender desde otras ventanas."""
    return launcher.abrir(escena, parent=parent)
