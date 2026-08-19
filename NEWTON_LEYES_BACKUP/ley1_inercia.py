"""
Primera Ley de Newton — Ley de la Inercia
==========================================
"Todo objeto se mantiene en su estado de reposo o de movimiento en
línea recta y a velocidad constante. Esto cambia solo si una fuerza
externa actúa sobre él."

Esta ventana es completamente independiente de las demás leyes: tiene
su propia clase, su propio estado (posición, velocidad, fricción) y
su propio ciclo de animación. Puede abrirse junto a las otras dos sin
que exista ninguna interferencia entre ellas.
"""

import tkinter as tk
import customtkinter as ctk

from theme import COLOR_LEY1, COLOR_LEY1_DARK, BG_APP, BG_CANVAS, TEXT_LIGHT
from three_d import abrir_escena_3d, escribir_estado_3d


class VentanaInercia(ctk.CTkToplevel):
    ANCHO_CANVAS = 620
    ALTO_CANVAS = 260
    RADIO_BALON = 18
    SUELO_Y = 200

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Primera Ley: Ley de la Inercia")
        self.geometry("680x660")
        self.minsize(680, 660)
        self.configure(fg_color=BG_APP)

        # --- Estado propio de esta ventana ---
        self.velocidad = 0.0
        self.friccion_activa = tk.BooleanVar(value=False)
        self.animando = False
        self._after_id = None
        self.pos_x = 60

        self._construir_interfaz()
        self._dibujar_escena()
        self.friccion_activa.trace_add("write", self._sincronizar_escena_3d)

        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    # ---------------------------------------------------------- UI
    def _construir_interfaz(self):
        ctk.CTkLabel(
            self, text="⚪  Primera Ley: Ley de la Inercia",
            font=ctk.CTkFont(size=22, weight="bold"), text_color=COLOR_LEY1,
        ).pack(pady=(22, 4))

        texto = (
            "Todo objeto se mantiene en su estado de reposo o de movimiento en "
            "línea recta y a velocidad constante. Esto cambia solo si una fuerza "
            "externa actúa sobre él.\n\n"
            "Ejemplo: un balón en el suelo no se mueve solo; necesita que alguien "
            "lo patee para cambiar de estado."
        )
        ctk.CTkLabel(
            self, text=texto, font=ctk.CTkFont(size=13), justify="left",
            wraplength=600, text_color="#c9c9d9",
        ).pack(padx=30, pady=(0, 16))

        self.canvas = tk.Canvas(
            self, width=self.ANCHO_CANVAS, height=self.ALTO_CANVAS,
            bg=BG_CANVAS, highlightthickness=0,
        )
        self.canvas.pack(pady=6)

        self.lbl_estado = ctk.CTkLabel(
            self, text="Estado: en reposo (ninguna fuerza actúa)",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white",
        )
        self.lbl_estado.pack(pady=(12, 6))

        frame_controles = ctk.CTkFrame(self, fg_color="transparent")
        frame_controles.pack(pady=10)

        ctk.CTkButton(
            frame_controles, text="⚡ Patear balón (aplicar fuerza)",
            fg_color=COLOR_LEY1, hover_color=COLOR_LEY1_DARK,
            command=self._patear, width=240,
        ).grid(row=0, column=0, padx=8)

        ctk.CTkButton(
            frame_controles, text="↺ Reiniciar", fg_color="#444455",
            hover_color="#333344", command=self._reiniciar, width=140,
        ).grid(row=0, column=1, padx=8)

        ctk.CTkButton(
            frame_controles, text="🌐 Abrir vista 3D",
            fg_color=COLOR_LEY1, hover_color=COLOR_LEY1_DARK,
            command=self._abrir_vista_3d,
            width=240,
        ).grid(row=1, column=0, columnspan=2, pady=(14, 0))

        ctk.CTkSwitch(
            frame_controles, text="Simular fricción (fuerza externa continua)",
            variable=self.friccion_activa, progress_color=COLOR_LEY1,
        ).grid(row=2, column=0, columnspan=2, pady=(16, 0))

        nota = (
            "💡 Sin fricción, el balón se mueve en línea recta indefinidamente: "
            "nada lo detiene, solo rebota al chocar contra una pared (otra fuerza "
            "externa). Con fricción activada, el suelo ejerce una fuerza continua "
            "que lo frena de a poco, hasta devolverlo al reposo."
        )
        ctk.CTkLabel(
            self, text=nota, font=ctk.CTkFont(size=11, slant="italic"),
            text_color="#8a8aa3", wraplength=600, justify="left",
        ).pack(padx=30, pady=(18, 10))

    # ------------------------------------------------------ dibujo
    def _dibujar_escena(self):
        self.canvas.delete("all")
        self.canvas.create_line(
            0, self.SUELO_Y + self.RADIO_BALON, self.ANCHO_CANVAS,
            self.SUELO_Y + self.RADIO_BALON, fill="#44445a", width=3,
        )
        self.balon = self.canvas.create_oval(
            self.pos_x - self.RADIO_BALON, self.SUELO_Y - self.RADIO_BALON,
            self.pos_x + self.RADIO_BALON, self.SUELO_Y + self.RADIO_BALON,
            fill=COLOR_LEY1, outline="white", width=2,
        )

    # --------------------------------------------------- lógica
    def _abrir_vista_3d(self):
        abrir_escena_3d(
            "inercia",
            parent=self,
            friction=self.friccion_activa.get(),
        )

    def _sincronizar_escena_3d(self, *_):
        escribir_estado_3d("inercia", {"friction": self.friccion_activa.get()})

    def _patear(self):
        if self.velocidad == 0:
            self.velocidad = 6.0
        if not self.animando:
            self.animando = True
            self._animar()
        escribir_estado_3d("inercia", {"patear": True, "friction": self.friccion_activa.get()})

    def _reiniciar(self):
        if self._after_id:
            self.after_cancel(self._after_id)
        self.animando = False
        self.velocidad = 0.0
        self.pos_x = 60
        self._dibujar_escena()
        self.lbl_estado.configure(text="Estado: en reposo (ninguna fuerza actúa)")
        escribir_estado_3d("inercia", {"reset": True, "friction": self.friccion_activa.get()})

    def _animar(self):
        self.pos_x += self.velocidad
        if self.pos_x >= self.ANCHO_CANVAS - self.RADIO_BALON or self.pos_x <= self.RADIO_BALON:
            self.velocidad *= -1  # el choque contra la pared es una fuerza externa

        if self.friccion_activa.get() and self.velocidad != 0:
            signo = 1 if self.velocidad > 0 else -1
            self.velocidad -= signo * 0.05
            if abs(self.velocidad) < 0.15:
                self.velocidad = 0

        self.canvas.coords(
            self.balon,
            self.pos_x - self.RADIO_BALON, self.SUELO_Y - self.RADIO_BALON,
            self.pos_x + self.RADIO_BALON, self.SUELO_Y + self.RADIO_BALON,
        )

        if self.velocidad == 0:
            self.animando = False
            self.lbl_estado.configure(text="Estado: en reposo (la fricción lo detuvo)")
            return

        self.lbl_estado.configure(
            text=f"Estado: movimiento rectilíneo uniforme — v ≈ {abs(self.velocidad):.1f} px/frame"
        )
        self._after_id = self.after(16, self._animar)

    def _cerrar(self):
        if self._after_id:
            self.after_cancel(self._after_id)
        self.destroy()
