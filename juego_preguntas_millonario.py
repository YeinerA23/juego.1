# -*- coding: utf-8 -*-
# Juego estilo "¿Quién quiere ser millonario?"
# Con pantalla de inicio en loop

import tkinter as tk
from tkinter import messagebox
import json, random, os
import pygame  # <-- Asegúrate de agregar esta línea


pygame.init()
pygame.mixer.init()

# --------- Música de fondo ---------
pygame.mixer.music.load("music_fondo.mp3")   # Asegúrate que esté en la misma carpeta
pygame.mixer.music.set_volume(0.5)           # Volumen (0.0 a 1.0)
pygame.mixer.music.play(-1)                  # -1 = loop infinito


# -------- Sonido con pygame --------
try:
    import pygame
    pygame.mixer.init()
except Exception as e:
    pygame = None
    print("⚠️ Sonido deshabilitado:", e)

def cargar_sonido(nombre):
    if pygame and os.path.exists(nombre):
        try:
            return pygame.mixer.Sound(nombre)
        except:
            return None
    return None

snd_correcto   = cargar_sonido("correcto.mp3")
snd_incorrecto = cargar_sonido("incorrecto.mp3")
snd_fin        = cargar_sonido("fin_juego.mp3")
snd_perdedor = cargar_sonido("fin_perdido.mp3")




def play(s):
    if s: 
        try: s.play()
        except: pass

# -------- Cargar preguntas --------
def cargar_preguntas():
    try:
        with open("preguntas.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            val = []
            for q in data:
                if {"pregunta","opciones","respuesta"} <= set(q.keys()):
                    val.append(q)
            return val if val else []
    except:
        return []

preguntas = cargar_preguntas()
if not preguntas:
    preguntas = [
        {"pregunta": "¿Capital de Colombia?",
         "opciones": ["A) Bogotá","B) Lima","C) Quito","D) Caracas"],
         "respuesta": "A"}
    ]

# -------- Variables --------
puntaje = 0
indice_pregunta = 0

# -------- Funciones --------
def mostrar_pregunta():
    global indice_pregunta
    if indice_pregunta >= len(preguntas):
        finalizar_juego(True)
        return
    p = preguntas[indice_pregunta]
    pregunta_lbl.config(text=p["pregunta"])
    for i, opcion in enumerate(p["opciones"]):
        botones[i].config(text=opcion, state="normal")
    resultado_lbl.config(text="")
    marcador_lbl.config(text=f"Puntos: {puntaje}")

def verificar_respuesta(letra):
    global puntaje, indice_pregunta
    correcta = preguntas[indice_pregunta]["respuesta"].strip().upper()
    if letra == correcta:
        puntaje += 100
        play(snd_correcto)
        resultado_lbl.config(text="✅ ¡Correcto! +100", fg="#00d084")
        indice_pregunta += 1
        ventana.after(900, mostrar_pregunta)
    else:
        play(snd_incorrecto)
        resultado_lbl.config(text=f"❌ Incorrecto. Era {correcta}", fg="#ff6868")
        for b in botones: b.config(state="disabled")
        ventana.after(900, lambda: finalizar_juego(False))

def finalizar_juego(ganador):
    for b in botones: b.config(state="disabled")
    play(snd_fin if ganador else snd_perdedor)

    titulo = "🎉 ¡Ganaste!" if ganador else "Juego terminado"
    messagebox.showinfo(titulo, f"Puntaje final: {puntaje}")
    reiniciar_btn.pack(pady=18)

def reiniciar_juego():
    global puntaje, indice_pregunta, preguntas
    puntaje = 0
    indice_pregunta = 0
    random.shuffle(preguntas)
    reiniciar_btn.pack_forget()
    mostrar_pregunta()

# -------- Pantalla de inicio --------
def iniciar_juego():
    # Detener música de fondo al iniciar el juego
    pygame.mixer.music.stop()

    # Ocultar pantalla de inicio
    titulo_inicio.pack_forget()
    btn_inicio.pack_forget()

    # Mostrar pantalla del juego
    titulo_lbl.pack(pady=16)
    pregunta_lbl.pack(pady=28)
    frame_opciones.pack()
    resultado_lbl.pack(pady=8)
    marcador_lbl.pack(pady=4)

    random.shuffle(preguntas)
    mostrar_pregunta()


# -------- Interfaz --------
ventana = tk.Tk()
ventana.title("¿Quién quiere ser millonario?")
ventana.geometry("900x620")
ventana.configure(bg="black")

fuente_titulo    = ("Arial Black", 24, "bold")
fuente_pregunta  = ("Arial", 20, "bold")
fuente_opcion    = ("Arial", 16, "bold")
fuente_marcador  = ("Arial", 14, "bold")

# --- Pantalla de inicio ---
titulo_inicio = tk.Label(ventana, text="¿QUIÉN QUIERE SER MILLONARIO?",
                         font=fuente_titulo, bg="black", fg="gold")
titulo_inicio.pack(pady=200)

btn_inicio = tk.Button(ventana, text="▶️ Comenzar", font=fuente_opcion,
                       bg="green", fg="white", command=iniciar_juego)
btn_inicio.pack()

# --- Juego ---
titulo_lbl = tk.Label(ventana, text="¿QUIÉN QUIERE SER MILLONARIO?",
                      font=fuente_titulo, bg="black", fg="gold")

pregunta_lbl = tk.Label(ventana, text="", font=fuente_pregunta,
                        wraplength=820, bg="black", fg="white",
                        justify="center")

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
                          bg="green", fg="white", command=reiniciar_juego)

# Atajos teclado
def on_key(e):
    k = e.keysym.upper()
    if k in ("A","B","C","D"):
        verificar_respuesta(k)
    elif k == "R" and reiniciar_btn.winfo_ismapped():
        reiniciar_juego()
ventana.bind("<KeyPress>", on_key)

ventana.mainloop()
