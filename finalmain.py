# ==============================
# Handwriting Calculator - main.py
# ==============================

import customtkinter as ctk
from tkinter import *
from PIL import Image, ImageDraw, ImageOps
import numpy as np
import cv2
import tensorflow as tf

# -------------------------------
# Load Trained Model
# -------------------------------
model = tf.keras.models.load_model("example.h5")

# -------------------------------
# Symbol Mapping
# -------------------------------
def num_to_sym(num):
    mapping = {
        10: "+",
        11: "-",
        12: "*",   # Python needs * instead of x
        13: "/",
        14: "(",
        15: ")",
        16: ","
    }
    return mapping.get(num, str(num))

# -------------------------------
# GUI Window
# -------------------------------
width, height = 400, 200

root = ctk.CTk()
root.title("Handwriting Calculator")
root.resizable(False, False)

# Canvas for drawing
canv = ctk.CTkCanvas(root, width=width, height=height, bg="white")
canv.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

white = (255, 255, 255)
image1 = Image.new("RGB", (width, height), white)
draw = ImageDraw.Draw(image1)

def paint(event):
    x1, y1 = (event.x - 6), (event.y - 6)
    x2, y2 = (event.x + 6), (event.y + 6)
    canv.create_oval(x1, y1, x2, y2, fill="black", width=15)
    draw.ellipse([x1, y1, x2, y2], fill="black")

canv.bind("<B1-Motion>", paint)

# -------------------------------
# Prediction Function
# -------------------------------
def testing(img):
    img = cv2.bitwise_not(img)  # invert
    img = cv2.resize(img, (28, 28))
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    img = img.astype("float32") / 255.0
    img = np.expand_dims(img, axis=0)

    pred = model.predict(img, verbose=0)
    ind = np.argmax(pred)
    acc = round(np.max(pred) * 100, 2)
    return num_to_sym(ind), acc

# -------------------------------
# Expression Solver
# -------------------------------
def solve_exp(preds):
    ans = ""
    for ind, acc in preds:
        ans += ind
        print(ind, acc)

    try:
        fin = eval(ans)
        fin = float(f"{fin:.4f}")
        txt.delete("1.0", ctk.END)
        sol.delete("1.0", ctk.END)
        txt.insert(ctk.INSERT, ans)
        sol.insert(ctk.INSERT, "= {}".format(fin))
    except:
        txt.delete("1.0", ctk.END)
        sol.delete("1.0", ctk.END)
        txt.insert(ctk.INSERT, ans)
        sol.insert(ctk.INSERT, "Invalid Expression")

# -------------------------------
# Button Commands
# -------------------------------
def mod():
    # Save canvas drawing to temp image
    filename = "input.png"
    image1.save(filename)
    img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
    blur = cv2.GaussianBlur(img, (5, 5), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Find contours (symbols)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    preds = []

    for cnt in sorted(contours, key=lambda x: cv2.boundingRect(x)[0]):  # left to right
        x, y, w, h = cv2.boundingRect(cnt)
        roi = thresh[y:y+h, x:x+w]
        sym, acc = testing(roi)
        preds.append((sym, acc))

    solve_exp(preds)

def clear():
    canv.delete("all")
    global image1, draw
    image1 = Image.new("RGB", (width, height), white)
    draw = ImageDraw.Draw(image1)
    txt.delete("1.0", ctk.END)
    sol.delete("1.0", ctk.END)

# -------------------------------
# Textboxes & Buttons
# -------------------------------
your_font = "Bahnschrift"

txt_font = ctk.CTkFont(family=your_font, size=24)
txt = ctk.CTkTextbox(root, height=40, width=200, font=txt_font)
txt.grid(row=2, column=0, padx=5, pady=5)

sol_font = ctk.CTkFont(family=your_font, size=26, weight="bold")
sol = ctk.CTkTextbox(root, height=40, width=200, font=sol_font, text_color="#3085ff")
sol.grid(row=3, column=0, padx=5, pady=5)

button_font = ctk.CTkFont(family=your_font, size=15)
Pred = ctk.CTkButton(root, text="Calculate", command=mod, fg_color="#0056C4",
                     hover_color="#007dfe", font=button_font, height=30)
Clr = ctk.CTkButton(root, text="Clear", command=clear, fg_color="#B50000",
                    hover_color="#dd0000", font=button_font, height=30)

Pred.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
Clr.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

root.mainloop()
