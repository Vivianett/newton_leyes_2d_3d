"""
Segunda Ley de Newton — Ley de la Fuerza (F = m · a)
======================================================
"La aceleración de un objeto depende de la fuerza neta que se le
aplica y de su masa: F = m · a"

Ventana totalmente independiente: su propia clase, su propio estado
(masa, fuerza, animación) y su propio ciclo de actualización. No
comparte variables con las otras ventanas de ley.
"""

import math
import tkinter as tk
import customtkinter as ctk

from theme import COLOR_LEY2, COLOR_LEY2_DARK, BG_APP, BG_CANVAS
from three_d import abrir_escena_3d, escribir_estado_3d


class VentanaFuerza(ctk.CTkToplevel):
    ANCHO_CANVAS = 620
    ALTO_CANVAS = 220
    SUELO_Y = 160
    DT = 0.016  # segundos por frame (~60 fps), para calcular la velocidad real v = a·t

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Segunda Ley: F = m · a")
        self.geometry("680x720")
        self.minsize(680, 720)
        self.configure(fg_color=BG_APP)

        # --- Estado propio de esta ventana ---
        self.masa = tk.DoubleVar(value=10)
        self.fuerza = tk.DoubleVar(value=50)
        self.pos_x = 50
        self.velocidad = 0.0            # velocidad "visual" (px/frame), ya escalada para animar
        self.tiempo_transcurrido = 0.0  # segundos reales simulados, para mostrar v = a·t
        self.animando = False
        self._after_id = None

        self._construir_interfaz()
        self._dibujar_escena()
        self._actualizar_calculo()
        self.masa.trace_add("write", self._sincronizar_escena_3d)
        self.fuerza.trace_add("write", self._sincronizar_escena_3d)

        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    # ---------------------------------------------------------- UI
    def _construir_interfaz(self):
        ctk.CTkLabel(
            self, text="🛒  Segunda Ley: Ley de la Fuerza",
            font=ctk.CTkFont(size=22, weight="bold"), text_color=COLOR_LEY2,
        ).pack(pady=(22, 4))

        texto = (
            "La aceleración de un objeto depende de la fuerza neta que se le "
            "aplica y de su masa:  F = m × a\n\n"
            "Ejemplo: empujar un carrito de compras vacío es fácil con poca "
            "fuerza, pero si está muy lleno y pesado, necesitas mucha más "
            "fuerza para lograr la misma aceleración."
        )
        ctk.CTkLabel(
            self, text=texto, font=ctk.CTkFont(size=13), justify="left",
            wraplength=600, text_color="#c9c9d9",
        ).pack(padx=30, pady=(0, 14))

        frame_presets = ctk.CTkFrame(self, fg_color="transparent")
        frame_presets.pack(pady=(0, 10))
        ctk.CTkButton(
            frame_presets, text="Carrito vacío (5 kg)", width=190,
            fg_color="#333344", hover_color=COLOR_LEY2_DARK,
            command=lambda: self._preset(5, 40),
        ).grid(row=0, column=0, padx=6)
        ctk.CTkButton(
            frame_presets, text="Carrito lleno (40 kg)", width=190,
            fg_color="#333344", hover_color=COLOR_LEY2_DARK,
            command=lambda: self._preset(40, 40),
        ).grid(row=0, column=1, padx=6)

        frame_sliders = ctk.CTkFrame(self, fg_color="#22223a", corner_radius=12)
        frame_sliders.pack(padx=30, pady=6, fill="x")

        self.lbl_masa = ctk.CTkLabel(frame_sliders, text="Masa: 10 kg", font=ctk.CTkFont(size=13))
        self.lbl_masa.pack(pady=(14, 0))
        ctk.CTkSlider(
            frame_sliders, from_=1, to=100, variable=self.masa,
            progress_color=COLOR_LEY2, command=lambda v: self._actualizar_calculo(),
        ).pack(padx=24, pady=(4, 14), fill="x")

        self.lbl_fuerza = ctk.CTkLabel(frame_sliders, text="Fuerza: 50 N", font=ctk.CTkFont(size=13))
        self.lbl_fuerza.pack()
        ctk.CTkSlider(
            frame_sliders, from_=1, to=200, variable=self.fuerza,
            progress_color=COLOR_LEY2, command=lambda v: self._actualizar_calculo(),
        ).pack(padx=24, pady=(4, 16), fill="x")

        self.lbl_resultado = ctk.CTkLabel(
            self, text="a = F / m  =  5.00 m/s²", font=ctk.CTkFont(size=17, weight="bold"),
            text_color=COLOR_LEY2,
        )
        self.lbl_resultado.pack(pady=10)

        self.canvas = tk.Canvas(
            self, width=self.ANCHO_CANVAS, height=self.ALTO_CANVAS,
            bg=BG_CANVAS, highlightthickness=0,
        )
        self.canvas.pack(pady=6)

        self.lbl_velocidad_actual = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=12), text_color="#c9c9d9",
        )
        self.lbl_velocidad_actual.pack(pady=(0, 4))

        frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones.pack(pady=12)
        ctk.CTkButton(
            frame_botones, text="▶ Simular empuje", fg_color=COLOR_LEY2,
            hover_color=COLOR_LEY2_DARK, command=self._simular, width=200,
        ).grid(row=0, column=0, padx=8)
        ctk.CTkButton(
            frame_botones, text="↺ Reiniciar", fg_color="#444455",
            hover_color="#333344", command=self._reiniciar, width=140,
        ).grid(row=0, column=1, padx=8)
        ctk.CTkButton(
            frame_botones, text="🌐 Abrir vista 3D",
            fg_color=COLOR_LEY2, hover_color=COLOR_LEY2_DARK,
            command=self._abrir_vista_3d,
            width=220,
        ).grid(row=1, column=0, columnspan=2, pady=(12, 0))

        nota = (
            "💡 A igual fuerza, una masa mayor produce menos aceleración. Prueba "
            "los dos presets con la misma fuerza (40 N) y compara qué tan rápido "
            "arranca el carrito vacío frente al carrito lleno.\n\n"
            "⚠️ Esta simulación no tiene fricción, así que una fuerza constante "
            "nunca deja de acelerar el carrito: la velocidad sigue subiendo "
            "mientras dure la simulación — eso es lo correcto según F = m·a, no "
            "un error. Con masas grandes y fuerzas pequeñas (p. ej. 100 kg y "
            "1 N) ese aumento es real pero muy lento; el contador de velocidad "
            "bajo el carrito lo muestra en números para que se note aunque el "
            "movimiento en pantalla sea sutil."
        )
        ctk.CTkLabel(
            self, text=nota, font=ctk.CTkFont(size=11, slant="italic"),
            text_color="#8a8aa3", wraplength=600, justify="left",
        ).pack(padx=30, pady=(6, 10))

    # --------------------------------------------------- lógica
    def _abrir_vista_3d(self):
        abrir_escena_3d(
            "fuerza",
            parent=self,
            mass=self.masa.get(),
            force=self.fuerza.get(),
        )

    def _preset(self, m, f):
        self.masa.set(m)
        self.fuerza.set(f)
        self._actualizar_calculo()

    def _sincronizar_escena_3d(self, *_):
        escribir_estado_3d("fuerza", {"mass": self.masa.get(), "force": self.fuerza.get()})

    def _actualizar_calculo(self):
        m = self.masa.get()
        f = self.fuerza.get()
        a = f / m if m else 0
        self.lbl_masa.configure(text=f"Masa: {m:.0f} kg")
        self.lbl_fuerza.configure(text=f"Fuerza: {f:.0f} N")
        self.lbl_resultado.configure(text=f"a = F / m  =  {f:.0f} / {m:.0f}  =  {a:.2f} m/s²")
        self._sincronizar_escena_3d()

    def _dibujar_escena(self):
        self.canvas.delete("all")
        self.canvas.create_line(
            0, self.SUELO_Y + 30, self.ANCHO_CANVAS, self.SUELO_Y + 30,
            fill="#44445a", width=3,
        )
        x = self.pos_x
        self.carrito = self.canvas.create_rectangle(
            x, self.SUELO_Y - 10, x + 70, self.SUELO_Y + 20,
            fill=COLOR_LEY2, outline="white", width=2,
        )
        self.rueda1 = self.canvas.create_oval(
            x + 6, self.SUELO_Y + 16, x + 22, self.SUELO_Y + 32, fill="#222", outline="white"
        )
        self.rueda2 = self.canvas.create_oval(
            x + 48, self.SUELO_Y + 16, x + 64, self.SUELO_Y + 32, fill="#222", outline="white"
        )

    def _simular(self):
        if self.animando:
            return
        self.velocidad = 0.0
        self.pos_x = 50
        self.tiempo_transcurrido = 0.0
        self.animando = True
        self._dibujar_escena()
        self._animar()
        escribir_estado_3d("fuerza", {"simulate": True, "mass": self.masa.get(), "force": self.fuerza.get()})

    def _animar(self):
        a = self.fuerza.get() / self.masa.get()  # aceleración real (m/s²), F = m·a
        self.tiempo_transcurrido += self.DT
        v_real = a * self.tiempo_transcurrido  # velocidad real acumulada (parte de 0, a constante)

        # La masa (1-100 kg) y la fuerza (1-200 N) permiten aceleraciones reales
        # entre 0.01 y 200 m/s²: un rango de 20.000 veces. Escalando de forma
        # lineal (como antes: a * 0.03), una combinación como 100 kg / 1 N era
        # invisible en pantalla (crecía en milésimas de píxel por frame), mientras
        # que 1 kg / 200 N saldría disparada en un instante. Por eso el paso
        # visual se comprime con un logaritmo: el orden se conserva (a mayor
        # aceleración real, más rápido se ve el carrito) pero ambos extremos
        # quedan dentro de un rango observable.
        paso_visual = 0.03 + 0.07 * math.log1p(a)
        self.velocidad += paso_visual
        self.pos_x += self.velocidad

        for item in (self.carrito, self.rueda1, self.rueda2):
            self.canvas.move(item, self.velocidad, 0)

        self.lbl_velocidad_actual.configure(
            text=f"v ≈ {v_real:.3f} m/s tras t = {self.tiempo_transcurrido:.2f} s "
                 f"— sigue acelerando mientras la fuerza actúa (sin fricción)"
        )

        if self.pos_x > self.ANCHO_CANVAS - 20:
            self.animando = False
            self.lbl_velocidad_actual.configure(
                text=self.lbl_velocidad_actual.cget("text") + "  ·  salió del cuadro"
            )
            return

        self._after_id = self.after(16, self._animar)

    def _reiniciar(self):
        if self._after_id:
            self.after_cancel(self._after_id)
        self.animando = False
        self.pos_x = 50
        self.velocidad = 0
        self.tiempo_transcurrido = 0.0
        self._dibujar_escena()
        self.lbl_velocidad_actual.configure(text="")
        escribir_estado_3d("fuerza", {"reset": True, "mass": self.masa.get(), "force": self.fuerza.get()})

    def _cerrar(self):
        if self._after_id:
            self.after_cancel(self._after_id)
        self.destroy()