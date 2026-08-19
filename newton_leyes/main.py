"""
Simulador de las Leyes de Newton
=================================
Aplicación de escritorio educativa que presenta las tres leyes del
movimiento de Isaac Newton, cada una en su propia ventana
independiente, para evitar cualquier interferencia entre ellas.

Requisitos: Python 3.9+, customtkinter
Instalar:   pip install -r requirements.txt
Ejecutar:   python main.py
"""

import customtkinter as ctk

from core.theme import (
    BG_APP, BG_CARD, BORDE_CARD, TEXT_MUTED, TEXT_DIM,
    COLOR_LEY1, COLOR_LEY1_DARK,
    COLOR_LEY2, COLOR_LEY2_DARK,
    COLOR_LEY3, COLOR_LEY3_DARK,
)
from leyes.ley1_inercia import VentanaInercia
from leyes.ley2_fuerza import VentanaFuerza
from leyes.ley3_accion_reaccion import VentanaAccionReaccion

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MenuPrincipal(ctk.CTk):
    """Ventana principal / punto de entrada.

    Da acceso a las tres leyes de Newton. Cada ley vive en su propia
    clase (VentanaInercia, VentanaFuerza, VentanaAccionReaccion), con
    su propio estado y su propio ciclo de animación, por lo que se
    pueden abrir simultáneamente sin que se interfieran entre sí.
    """

    def __init__(self):
        super().__init__()
        self.title("Leyes de Newton — Simulador Interactivo")
        self.geometry("580x580")
        self.minsize(580, 580)
        self.configure(fg_color=BG_APP)

        # Registro de ventanas ya abiertas: si el usuario vuelve a
        # pulsar "Abrir" sobre una ley ya abierta, simplemente se le
        # da foco en vez de crear una segunda instancia.
        self._ventanas = {}

        self._construir_interfaz()

    def _construir_interfaz(self):
        ctk.CTkLabel(
            self, text="⚛️  Leyes del Movimiento de Newton",
            font=ctk.CTkFont(size=25, weight="bold"), text_color="white",
        ).pack(pady=(30, 4))
        ctk.CTkLabel(
            self, text="Selecciona una ley para abrir su simulación interactiva",
            font=ctk.CTkFont(size=13), text_color=TEXT_MUTED,
        ).pack(pady=(0, 26))

        self._crear_tarjeta(
            "⚪", "Primera Ley — Inercia",
            "Un objeto en reposo o en movimiento no cambia su estado, "
            "salvo que una fuerza externa actúe sobre él. Ahora incluye una "
            "escena 3D con cámara interactiva.",
            COLOR_LEY1, COLOR_LEY1_DARK, self._abrir_ley1,
        )
        self._crear_tarjeta(
            "🛒", "Segunda Ley — Fuerza (F = m·a)",
            "La aceleración de un objeto depende de la fuerza aplicada "
            "y de su masa. También puedes abrir una vista 3D del carrito.",
            COLOR_LEY2, COLOR_LEY2_DARK, self._abrir_ley2,
        )
        self._crear_tarjeta(
            "👣", "Tercera Ley — Acción y Reacción",
            "Toda fuerza aplicada genera una fuerza igual y opuesta "
            "en sentido contrario. La nueva vista 3D muestra el par de fuerzas "
            "en perspectiva.",
            COLOR_LEY3, COLOR_LEY3_DARK, self._abrir_ley3,
        )

        ctk.CTkLabel(
            self,
            text="Cada ley se abre en una ventana propia e independiente:\n"
                 "puedes tener las tres abiertas al mismo tiempo.",
            font=ctk.CTkFont(size=10, slant="italic"), text_color=TEXT_DIM,
            justify="center",
        ).pack(side="bottom", pady=18)

    def _crear_tarjeta(self, icono, titulo, descripcion, color, color_hover, comando):
        card = ctk.CTkFrame(
            self, fg_color=BG_CARD, corner_radius=14,
            border_width=1, border_color=BORDE_CARD,
        )
        card.pack(padx=30, pady=9, fill="x")

        contenido = ctk.CTkFrame(card, fg_color="transparent")
        contenido.pack(fill="x", padx=16, pady=14)
        contenido.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(contenido, text=icono, font=ctk.CTkFont(size=28)).grid(
            row=0, column=0, rowspan=2, padx=(0, 14)
        )
        ctk.CTkLabel(
            contenido, text=titulo, font=ctk.CTkFont(size=16, weight="bold"),
            text_color=color, anchor="w",
        ).grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(
            contenido, text=descripcion, font=ctk.CTkFont(size=11),
            text_color="#aaaabf", anchor="w", justify="left", wraplength=320,
        ).grid(row=1, column=1, sticky="w")

        ctk.CTkButton(
            contenido, text="Abrir →", width=90, fg_color=color,
            hover_color=color_hover, command=comando,
        ).grid(row=0, column=2, rowspan=2, padx=(14, 0))

    # ------------------------------------------------------------
    # Cada método abre (o enfoca, si ya existe) su propia ventana
    # Toplevel de forma totalmente aislada del resto de la app.
    def _abrir_ventana(self, clave, clase):
        ventana = self._ventanas.get(clave)
        if ventana is not None and ventana.winfo_exists():
            ventana.focus()
            ventana.lift()
            return
        nueva = clase(self)
        self._ventanas[clave] = nueva

    def _abrir_ley1(self):
        self._abrir_ventana("ley1", VentanaInercia)

    def _abrir_ley2(self):
        self._abrir_ventana("ley2", VentanaFuerza)

    def _abrir_ley3(self):
        self._abrir_ventana("ley3", VentanaAccionReaccion)


if __name__ == "__main__":
    app = MenuPrincipal()
    app.mainloop()
