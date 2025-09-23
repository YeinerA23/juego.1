# -*- coding: utf-8 -*-
# Juego estilo "¿Quién quiere ser millonario?" con intro de video usando tkvideo + audio con pygame

import tkinter as tk
from tkinter import messagebox
import json, random, os
import pygame
from PIL import Image, ImageTk
from tkvideo import tkvideo
import serial 

pygame.init()
try:
    pygame.mixer.init()
except Exception as e:
    print("⚠️ pygame.mixer no pudo inicializar:", e)

# ------------------- Conexión con Arduino -------------------
try:
    arduino = serial.Serial("COM6", 9600, timeout=1)  # 👈 CAMBIA COM3 por tu puerto
    print("✅ Arduino conectado en", arduino.port)
except Exception as e:
    print("⚠️ No se pudo conectar con Arduino:", e)
    arduino = None

# ------------------- Cargar sonidos -------------------
def cargar_sonido(nombre):
    if pygame and os.path.exists(nombre):
        try:
            return pygame.mixer.Sound(nombre)
        except Exception as e:
            print(f"⚠️ Error cargando sonido {nombre}:", e)
            return None
    return None

snd_correcto   = cargar_sonido("correcto.mp3")
snd_incorrecto = cargar_sonido("sonido_incorrecto.mp3")
snd_fin        = cargar_sonido("fin_juego.mp3")
snd_perdedor   = cargar_sonido("perdedor.mp3")
snd_reloj      = cargar_sonido("tic_toc.mp3")  # sonido del reloj

def play(s):
    if s:
        try: s.play()
        except Exception: pass

# ------------------- Cargar preguntas -------------------
def cargar_preguntas():
    try:
        with open("preguntas.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            val = []
            for q in data:
                if {"pregunta", "opciones", "respuesta"} <= set(q.keys()):
                    val.append(q)
            return val if val else []
    except Exception:
        return []

preguntas = cargar_preguntas()
if not preguntas:
    preguntas = [
        {"pregunta": "¿Capital de Colombia?",
         "opciones": ["A) Bogotá","B) Lima","C) Quito","D) Caracas"],
         "respuesta": "A"}
    ]

# ------------------- Variables -------------------
puntaje = 0
indice_pregunta = 0
tiempo_restante = 20
timer_job = None
aceptando_respuesta = False

ventana = tk.Tk()
ventana.title("¿Quién quiere ser millonario?")
ventana.geometry("900x620")
ventana.configure(bg="black")

fuente_titulo    = ("Arial Black", 24, "bold")
fuente_pregunta  = ("Arial", 20, "bold")
fuente_opcion    = ("Arial", 16, "bold")
fuente_marcador  = ("Arial", 14, "bold")

# ------------------- Intro con tkvideo + audio -------------------
def reproducir_intro():
    intro_lbl = tk.Label(ventana, bg="black")
    intro_lbl.place(x=0, y=0, relwidth=1, relheight=1)

    player = tkvideo("INTRO.mp4", intro_lbl, loop=0, size=(900, 620))
    player.play()

    # reproducir audio separado de la intro
    if os.path.exists("introo.mp3"):
        pygame.mixer.music.load("introo.mp3")
        pygame.mixer.music.play()

    # función interna para ocultar intro
    def quitar_intro():
        intro_lbl.place_forget()
        pygame.mixer.music.stop()

    # después de 15s, ocultar intro y parar audio
    ventana.after(15000, quitar_intro)

# ------------------- Fondo -------------------
try:
    imagen_fondo = Image.open("LOGO_SPAIN_2021.jpg")
    imagen_fondo = imagen_fondo.resize((900, 620))
    fondo_tk = ImageTk.PhotoImage(imagen_fondo)
    fondo_lbl = tk.Label(ventana, image=fondo_tk, bg="black")
    fondo_lbl.place(x=0, y=0, relwidth=1, relheight=1)
except Exception as e:
    print("⚠️ No se pudo cargar imagen de fondo:", e)
    fondo_lbl = tk.Label(ventana, bg="black")

# ------------------- Elementos pantalla inicio -------------------
titulo_inicio = tk.Label(ventana, text="¿QUIÉN QUIERE SER MILLONARIO?",
                         font=fuente_titulo, bg="black", fg="gold")
titulo_inicio.place(relx=0.5, rely=0.35, anchor="center")

btn_inicio = tk.Button(ventana, text="▶️ Comenzar", font=fuente_opcion,
                       bg="green", fg="white", command=lambda: iniciar_juego())
btn_inicio.place(relx=0.5, rely=0.55, anchor="center")

# ------------------- Elementos juego -------------------
titulo_lbl = tk.Label(ventana, text="¿QUIÉN QUIERE SER MILLONARIO?",
                      font=fuente_titulo, bg="black", fg="gold")

pregunta_lbl = tk.Label(ventana, text="", font=fuente_pregunta,
                        wraplength=820, bg="black", fg="white",
                        justify="center")

tiempo_lbl = tk.Label(ventana, text="⏱ 15s", font=("Arial Black", 20),
                      bg="black", fg="lime")

frame_opciones = tk.Frame(ventana, bg="black")
botones = []
letras = ["A","B","C","D"]
for i in range(4):
    b = tk.Button(frame_opciones, text="", width=35, height=2,
                  font=fuente_opcion, bg="#0b1d5b", fg="white",
                  activebackground="#153b9b",
                  command=lambda x=letras[i]: verificar_respuesta(x))
    b.grid(row=i//2, column=i%2, padx=18, pady=18)
    botones.append(b)

resultado_lbl = tk.Label(ventana, text="", font=("Arial", 16, "bold"),
                         bg="black", fg="white")

marcador_lbl = tk.Label(ventana, text="Puntos: 0", font=fuente_marcador,
                        bg="black", fg="gold")

reiniciar_btn = tk.Button(ventana, text="🔄 Volver a jugar", font=fuente_opcion,
                          bg="green", fg="white", command=lambda: reiniciar_juego())


# ------------------- Lectura desde Arduino -------------------
def leer_arduino():
    if arduino and arduino.in_waiting > 0:
        try:
            dato = arduino.readline().decode("utf-8").strip()
            if dato in ["A", "B", "C", "D"]:
                verificar_respuesta(dato)
        except Exception as e:
            print("⚠️ Error leyendo Arduino:", e)
    ventana.after(100, leer_arduino)  # vuelve a llamar cada 100ms


# ------------------- Cronómetro -------------------
def cancelar_timer_job():
    global timer_job
    try:
        if timer_job is not None:
            ventana.after_cancel(timer_job)
    except Exception:
        pass
    timer_job = None

def detener_sonido():
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass
    
    try:
        if snd_reloj:
            snd_reloj.stop()
    except Exception:
        pass
    

def actualizar_cronometro():
    global tiempo_restante, timer_job, aceptando_respuesta
    if not aceptando_respuesta:
        return
    if tiempo_restante > 0:
        tiempo_lbl.config(text=f"⏱ {tiempo_restante}s")
        if tiempo_restante > 9:
            tiempo_lbl.config(fg="lime")
        elif tiempo_restante > 5:
            tiempo_lbl.config(fg="yellow")
        else:
            tiempo_lbl.config(fg="red")
        tiempo_restante -= 1
        timer_job = ventana.after(1000, actualizar_cronometro)
    else:
        aceptando_respuesta = False
        cancelar_timer_job()
        detener_sonido()

        tiempo_lbl.config(text="⏱ 0s", fg="red")

        # ✅ Mostrar respuesta correcta cuando se acaba el tiempo
        correcta = preguntas[indice_pregunta]["respuesta"].strip().upper()
        resultado_lbl.config(
            text=f"⏰ Tiempo agotado. La respuesta correcta era {correcta}",
            fg="orange"
        )

        for b in botones:
            b.config(state="disabled")

        # esperar 2 segundos antes de terminar el juego
        ventana.after(2000, lambda: finalizar_juego(False))

# ------------------- Lógica del juego -------------------
def mostrar_pregunta():
    global indice_pregunta, tiempo_restante, aceptando_respuesta
    cancelar_timer_job()
    detener_sonido()
    if indice_pregunta >= len(preguntas):
        finalizar_juego(True)
        return

    p = preguntas[indice_pregunta]
    pregunta_lbl.config(text=p["pregunta"])
    for i, opcion in enumerate(p["opciones"]):
        botones[i].config(text=opcion, state="normal")
    resultado_lbl.config(text="")
    marcador_lbl.config(text=f"Puntos: {puntaje}")

    tiempo_restante = 20
    aceptando_respuesta = True
    actualizar_cronometro()

    # iniciar sonido de reloj en loop
    if snd_reloj:
        snd_reloj.play(-1)

def verificar_respuesta(letra):
    global puntaje, indice_pregunta, aceptando_respuesta
    if not aceptando_respuesta:
        return
    aceptando_respuesta = False

    cancelar_timer_job()
    detener_sonido()
    for b in botones: 
        b.config(state="disabled")

    correcta = preguntas[indice_pregunta]["respuesta"].strip().upper()
    if letra == correcta:
        puntaje += 100
        play(snd_correcto)
        resultado_lbl.config(text="✅ ¡Correcto! +100", fg="#00d084")

        # 🔹 Enviar señal a Arduino → encender verdes
        arduino.write(b"CORRECTO\n")

        indice_pregunta += 1
        ventana.after(900, mostrar_pregunta)
    else:
        play(snd_incorrecto)
        resultado_lbl.config(text=f"❌ Incorrecto. Era {correcta}", fg="#ff6868")

        # 🔹 Enviar señal a Arduino → encender rojas
        arduino.write(b"INCORRECTO\n")

        ventana.after(900, lambda: finalizar_juego(False))


def finalizar_juego(ganador):
    global aceptando_respuesta
    aceptando_respuesta = False
    cancelar_timer_job()
    detener_sonido()
    for b in botones: b.config(state="disabled")
    play(snd_fin if ganador else snd_perdedor)
    titulo = "🎉 ¡Ganaste!" if ganador else "Juego terminado"
    messagebox.showinfo(titulo, f"Puntaje final: {puntaje}")
    reiniciar_btn.pack(pady=18)

def reiniciar_juego():
    global puntaje, indice_pregunta, preguntas, aceptando_respuesta
    cancelar_timer_job()
    detener_sonido()
    puntaje = 0
    indice_pregunta = 0
    aceptando_respuesta = False
    random.shuffle(preguntas)
    reiniciar_btn.pack_forget()
    mostrar_pregunta()

# ------------------- Inicio del juego -------------------
def iniciar_juego():
    titulo_inicio.place_forget()
    btn_inicio.place_forget()
    fondo_lbl.place_forget()

    titulo_lbl.pack(pady=16)
    pregunta_lbl.pack(pady=28)
    tiempo_lbl.place(relx=0.95, rely=0.05, anchor="ne")
    frame_opciones.pack()
    resultado_lbl.pack(pady=8)
    marcador_lbl.pack(pady=4)

    random.shuffle(preguntas)
    mostrar_pregunta()

    leer_arduino()  

# ------------------- MAIN -------------------
if __name__ == "__main__":
    reproducir_intro()  # 🎬 Intro con video y audio separado
    ventana.mainloop()
