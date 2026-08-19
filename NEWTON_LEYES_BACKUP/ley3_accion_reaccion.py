"""
Tercera Ley de Newton — Acción y Reacción
===========================================
"Con toda acción ocurre siempre una reacción igual y contraria. Las
fuerzas siempre vienen en parejas, actuando sobre cuerpos distintos."

Escena: un cohete enciende su motor y expulsa gas hacia abajo. Esa
expulsión es la acción — el cohete empuja al gas — y tiene como
contraparte exacta el impulso que el gas ejerce sobre el cohete: la
reacción, que lo empuja hacia arriba. Las dos flechas nacen del mismo
punto (la tobera del motor) y miden siempre lo mismo, para que quede
claro que es un único par de fuerzas actuando sobre dos cuerpos
distintos — el gas y el cohete —, no dos flechas sueltas sin relación
entre sí (que era el problema de la versión anterior, con la persona
caminando).

Ventana totalmente independiente: su propia clase, su propio estado
y su propio ciclo de animación, aislada de las otras dos leyes.
"""

import math
import random
import tkinter as tk
import customtkinter as ctk

from theme import COLOR_LEY3, COLOR_LEY3_DARK, COLOR_ACCION, COLOR_REACCION, BG_APP, BG_CANVAS
from three_d import abrir_escena_3d, escribir_estado_3d


class VentanaAccionReaccion(ctk.CTkToplevel):
    ANCHO_CANVAS = 620
    ALTO_CANVAS = 400
    SUELO_Y = 360          # línea de la plataforma de lanzamiento
    CENTRO_X = 320          # posición horizontal fija del cohete
    ALTURA_COHETE = 90
    ANCHO_COHETE = 34
    LARGO_FLECHA = 40       # misma longitud para acción y reacción: refuerza que son iguales
    FUERZA_N = 4500         # valor de ejemplo, idéntico para ambas fuerzas del par

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Tercera Ley: Acción y Reacción")
        self.geometry("700x880")
        self.minsize(700, 880)
        self.configure(fg_color=BG_APP)

        # --- Estado propio de esta ventana ---
        self.rocket_y = self.SUELO_Y - 40   # posición vertical de la base del cohete (tobera)
        self.velocidad = 0.0
        self.motor_encendido = False
        self.fase = "reposo"                # reposo | ignicion | fuera
        self.animando = False
        self._after_id = None
        self._tiempo_anim = 0
        self.particulas = []                # gas expulsado: [x, y, vx, vy, vida]

        self._construir_interfaz()
        self._dibujar_escena()

        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    # ---------------------------------------------------------- UI
    def _construir_interfaz(self):
        ctk.CTkLabel(
            self, text="🚀  Tercera Ley: Acción y Reacción",
            font=ctk.CTkFont(size=22, weight="bold"), text_color=COLOR_LEY3,
        ).pack(pady=(22, 4))

        texto = (
            "Con toda acción ocurre siempre una reacción igual y contraria. "
            "Las fuerzas siempre vienen en parejas, actuando sobre cuerpos "
            "distintos.\n\n"
            "Ejemplo: el motor del cohete expulsa gas hacia abajo — el cohete "
            "empuja al gas (acción). El gas, a su vez, empuja al cohete hacia "
            "arriba con exactamente la misma fuerza (reacción). Por eso un "
            "cohete puede despegar incluso en el vacío del espacio: no "
            "necesita 'apoyarse' en el aire ni en nada externo, solo en el "
            "gas que él mismo expulsa."
        )
        ctk.CTkLabel(
            self, text=texto, font=ctk.CTkFont(size=13), justify="left",
            wraplength=620, text_color="#c9c9d9",
        ).pack(padx=30, pady=(0, 12))

        self.canvas = tk.Canvas(
            self, width=self.ANCHO_CANVAS, height=self.ALTO_CANVAS,
            bg=BG_CANVAS, highlightthickness=0,
        )
        self.canvas.pack(pady=6)

        self.lbl_info = ctk.CTkLabel(
            self, text="En la plataforma. Presiona «Encender motor» para despegar.",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white",
            wraplength=620,
        )
        self.lbl_info.pack(pady=(10, 2))

        self.lbl_fuerzas = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLOR_LEY3,
        )
        self.lbl_fuerzas.pack(pady=(0, 6))

        frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones.pack(pady=10)
        ctk.CTkButton(
            frame_botones, text="🔥 Encender motor (acción-reacción)",
            fg_color=COLOR_LEY3, hover_color=COLOR_LEY3_DARK,
            command=self._encender_motor, width=280,
        ).grid(row=0, column=0, padx=8)
        ctk.CTkButton(
            frame_botones, text="↺ Reiniciar", fg_color="#444455",
            hover_color="#333344", command=self._reiniciar, width=140,
        ).grid(row=0, column=1, padx=8)
        ctk.CTkButton(
            frame_botones, text="🌐 Abrir vista 3D",
            fg_color=COLOR_LEY3, hover_color=COLOR_LEY3_DARK,
            command=self._abrir_vista_3d,
            width=220,
        ).grid(row=1, column=0, columnspan=2, pady=(12, 0))

        nota = (
            "💡 Las dos flechas nacen del mismo punto: la tobera del motor. La "
            "roja (acción) es la fuerza que el cohete ejerce sobre el gas, "
            "empujándolo hacia abajo. La verde (reacción) es la fuerza que ese "
            "gas ejerce sobre el cohete, empujándolo hacia arriba. Miden "
            "exactamente lo mismo — por eso ambas flechas tienen el mismo "
            "tamaño — pero actúan sobre cuerpos distintos (el gas y el "
            "cohete), así que nunca se cancelan entre sí ni impiden el "
            "despegue."
        )
        ctk.CTkLabel(
            self, text=nota, font=ctk.CTkFont(size=11, slant="italic"),
            text_color="#8a8aa3", wraplength=620, justify="left",
        ).pack(padx=30, pady=(14, 10))

    # ------------------------------------------------------ dibujo
    def _dibujar_escena(self):
        self.canvas.delete("all")

        # Plataforma / suelo
        self.canvas.create_line(
            0, self.SUELO_Y, self.ANCHO_CANVAS, self.SUELO_Y,
            fill="#44445a", width=3,
        )
        self.canvas.create_rectangle(
            self.CENTRO_X - 46, self.SUELO_Y, self.CENTRO_X + 46, self.SUELO_Y + 10,
            fill="#2a2a3f", outline="",
        )

        # Torre de referencia a la izquierda, con marcas de altura
        self.canvas.create_line(60, self.SUELO_Y, 60, 40, fill="#33334a", width=6)
        for i in range(0, 8):
            y = self.SUELO_Y - i * 40
            self.canvas.create_line(50, y, 70, y, fill="#33334a", width=2)

        cx = self.CENTRO_X
        base_y = self.rocket_y
        top_y = base_y - self.ALTURA_COHETE
        w = self.ANCHO_COHETE

        # Partículas de gas expulsado (se dibujan primero, quedan "detrás")
        for x, y, _vx, _vy, vida in self.particulas:
            radio = max(1.0, 5 * vida)
            color = "#ffb347" if vida > 0.5 else "#8a4a1a"
            self.canvas.create_oval(
                x - radio, y - radio, x + radio, y + radio,
                fill=color, outline="",
            )

        # Llama del motor, solo mientras está encendido
        if self.motor_encendido:
            largo_llama = 24 + 8 * math.sin(self._tiempo_anim * 0.6)
            self.canvas.create_polygon(
                cx - 8, base_y, cx + 8, base_y, cx, base_y + largo_llama,
                fill="#ffb347", outline="",
            )

        # Cuerpo del cohete (rectángulo + nariz triangular)
        self.canvas.create_polygon(
            cx - w / 2, base_y, cx + w / 2, base_y,
            cx + w / 2, top_y + 18, cx, top_y, cx - w / 2, top_y + 18,
            fill="#e5e7eb", outline=COLOR_LEY3, width=2,
        )
        # Ventanilla
        self.canvas.create_oval(
            cx - 6, top_y + 30, cx + 6, top_y + 42,
            fill=COLOR_LEY3, outline="white",
        )
        # Aletas
        self.canvas.create_polygon(
            cx - w / 2, base_y, cx - w / 2 - 14, base_y + 16, cx - w / 2, base_y - 14,
            fill=COLOR_LEY3_DARK, outline="",
        )
        self.canvas.create_polygon(
            cx + w / 2, base_y, cx + w / 2 + 14, base_y + 16, cx + w / 2, base_y - 14,
            fill=COLOR_LEY3_DARK, outline="",
        )

        # Flechas de acción/reacción: ambas nacen en la tobera (mismo cx,
        # mismo base_y ± un pequeño margen), misma longitud, sentidos opuestos.
        if self.motor_encendido:
            label_x = cx + w / 2 + 14

            # Acción: el cohete empuja el gas hacia ABAJO
            self.canvas.create_line(
                cx, base_y + 6, cx, base_y + 6 + self.LARGO_FLECHA,
                fill=COLOR_ACCION, width=5, arrow=tk.LAST,
            )
            self.canvas.create_text(
                label_x, base_y + 6 + self.LARGO_FLECHA,
                text=f"Acción: {self.FUERZA_N} N ↓\n(sobre el gas)",
                fill=COLOR_ACCION, anchor="w", justify="left",
                font=("Arial", 10, "bold"),
            )

            # Reacción: el gas empuja el cohete hacia ARRIBA (misma magnitud)
            self.canvas.create_line(
                cx, base_y - 6, cx, base_y - 6 - self.LARGO_FLECHA,
                fill=COLOR_REACCION, width=5, arrow=tk.LAST,
            )
            self.canvas.create_text(
                label_x, base_y - 6 - self.LARGO_FLECHA,
                text=f"Reacción: {self.FUERZA_N} N ↑\n(sobre el cohete)",
                fill=COLOR_REACCION, anchor="w", justify="left",
                font=("Arial", 10, "bold"),
            )

    # --------------------------------------------------- lógica
    def _abrir_vista_3d(self):
        abrir_escena_3d("accion", parent=self)

    def _encender_motor(self):
        if self.fase != "reposo":
            return
        self.motor_encendido = True
        self.fase = "ignicion"
        self.velocidad = 0.0
        self._tiempo_anim = 0
        self.animando = True
        self.lbl_info.configure(
            text="Motor encendido: el cohete empuja el gas hacia abajo (acción) "
                 "y el gas empuja al cohete hacia arriba (reacción)."
        )
        self.lbl_fuerzas.configure(text=f"F acción = F reacción = {self.FUERZA_N} N")
        self._animar()
        escribir_estado_3d("accion", {"step": True})

    def _emitir_particulas(self):
        if not self.motor_encendido:
            return
        for _ in range(2):
            vx = random.uniform(-0.6, 0.6)
            vy = random.uniform(2.0, 3.4)
            self.particulas.append([self.CENTRO_X, self.rocket_y, vx, vy, 1.0])

    def _actualizar_particulas(self):
        vivas = []
        for p in self.particulas:
            p[0] += p[2]
            p[1] += p[3]
            p[4] -= 0.03
            if p[4] > 0:
                vivas.append(p)
        self.particulas = vivas

    def _animar(self):
        self._tiempo_anim += 1

        # Mientras el motor siga empujando gas hacia abajo (acción), la
        # reacción sobre el cohete sigue actuando: por eso la velocidad de
        # ascenso crece de forma continua, igual que un objeto sometido a
        # una fuerza neta constante (F = m·a), hasta que el cohete sale de
        # la escena.
        self.velocidad = min(self.velocidad + 0.06, 6.0)
        self.rocket_y -= self.velocidad

        self._emitir_particulas()
        self._actualizar_particulas()
        self._dibujar_escena()

        if self.rocket_y < -60:
            self.motor_encendido = False
            self.fase = "fuera"
            self.animando = False
            self.lbl_info.configure(
                text="El cohete salió de la escena: mientras el motor empujó gas "
                     "hacia abajo, el gas siguió empujándolo hacia arriba, sin "
                     "necesitar nada más. Reinicia para verlo de nuevo."
            )
            return

        self._after_id = self.after(16, self._animar)

    def _reiniciar(self):
        if self._after_id:
            self.after_cancel(self._after_id)
        self.animando = False
        self.motor_encendido = False
        self.fase = "reposo"
        self.rocket_y = self.SUELO_Y - 40
        self.velocidad = 0.0
        self.particulas = []
        self._tiempo_anim = 0
        self._dibujar_escena()
        self.lbl_info.configure(text="En la plataforma. Presiona «Encender motor» para despegar.")
        self.lbl_fuerzas.configure(text="")
        escribir_estado_3d("accion", {"reset": True})

    def _cerrar(self):
        if self._after_id:
            self.after_cancel(self._after_id)
        self.destroy()