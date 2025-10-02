# coding: utf-8

import tensorflow as tf
from keras.models import load_model
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw
import os
import customtkinter as ctk
import PIL

# =============================
# Load Model
# =============================
model = tf.keras.models.load_model('example.h5')
print("Model loaded successfully")

# =============================
# Helper Functions
# =============================
def testing(img):
    img = cv2.bitwise_not(img)
    img = cv2.resize(img, (28, 28))
    img = img.reshape(1, 28, 28, 1)
    img = img.astype('float32') / 255.0
    return model.predict(img)

def num_to_sym(x):
    symbols = {10: '+', 11: '-', 12: '*', 13: '/', 14: '(', 15: ')', 16: '.'}
    return symbols.get(x, str(x))

def solve_exp(preds):
    ans = ""
    for ind, acc in preds:
        ans += ind
        print(num_to_sym(int(ind)) + " " + str(acc))
    try:
        fin = eval(ans)
        fin = float(f"{fin:.4f}")
        txt.delete('1.0', ctk.END)
        sol.delete('1.0', ctk.END)
        txt.insert(ctk.INSERT, "{}".format(ans))
        sol.insert(ctk.INSERT, "= {}".format(fin))
    except Exception:
        txt.delete('1.0', ctk.END)
        sol.delete('1.0', ctk.END)
        txt.insert(ctk.INSERT, "{}".format(ans))
        sol.insert(ctk.INSERT, "Invalid expression")

def img_change():
    labimg = Image.open('Contours.png')
    labimg = ctk.CTkImage(dark_image=labimg, size=(width//5, height//5))
    image_label.configure(image=labimg)
    image_label.image = labimg

# =============================
# Settings
# =============================
width = 3500
height = 750
red = (0, 0, 225)
green = (0, 230, 0)
blue = (225, 0, 0)

directory = os.getcwd()
imsave = os.path.join(directory, "imgs")
if not os.path.exists(imsave):
    os.makedirs(imsave)
print("Images will be saved here:", imsave)

# =============================
# Canvas & Image Handling
# =============================
def mod():
    # Save canvas as image and read 
    image1.save('image.png')
    img = cv2.imread('image.png')

    # Add padding around the original image
    pad = 5
    h, w = img.shape[:2]
    im2 = ~(np.ones((h + pad*2, w + pad*2, 3), dtype=np.uint8))
    im2[pad:pad+h, pad:pad+w] = img[:]
    img = im2

    # Blur & B/W conversion
    img = cv2.GaussianBlur(img, (5, 5), 5)
    im = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bw = cv2.threshold(im, 200, 255, cv2.THRESH_BINARY)[1]

    # Find contours
    bw = cv2.bitwise_not(bw)
    cnts, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[0] + cv2.boundingRect(x)[2])

    i = 0    
    preds = []

    for cnt in cnts:
        x, y, w, h = cv2.boundingRect(cnt)
        i += 1
        cropped_img = im[y:y+h, x:x+w]

        # Special padding for '1' or '-'
        if abs(h) > 1.25 * abs(w):
            pad = 3*(h//w)**3
            cropped_img = cv2.copyMakeBorder(cropped_img, 0, 0, pad, pad, cv2.BORDER_CONSTANT, value=255)
        if abs(w) > 1.1 * abs(h):
            pad = 3*(w//h)**3
            cropped_img = cv2.copyMakeBorder(cropped_img, pad, pad, 0, 0, cv2.BORDER_CONSTANT, value=255)

        resized_img = cv2.resize(cropped_img, (28, 28))
        padded_img = cv2.copyMakeBorder(resized_img, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=255)
        cv2.imwrite(os.path.join(imsave, f'img_{i}.png'), padded_img)

        predi = testing(padded_img)
        ind = np.argmax(predi[0])
        acc = float(f"{predi[0][ind]*100:.2f}")
        preds.append((num_to_sym(ind), acc))

        # Draw rectangle and prediction on canvas
        cv2.rectangle(img, (x, y), (x+w, y+h), green, 7)
        yim = y + h + 85 if y < 80 else y - 25
        cv2.putText(img, f"{num_to_sym(ind)}", (x, yim), cv2.FONT_HERSHEY_SIMPLEX, 3, blue, 10)
        cv2.putText(img, f"{acc}%", (x+75, yim), cv2.FONT_HERSHEY_DUPLEX, 1.75, red, 3)

    cv2.imwrite('Contours.png', img)
    img_change()
    solve_exp(preds)

def paint(event):
    d = 15
    x1, y1 = event.x - d, event.y - d
    x2, y2 = event.x + d, event.y + d
    canv.create_oval(x1, y1, x2, y2, fill="black", width=25)
    draw.line([x1, y1, x2, y2], fill="black", width=35)

def clear():
    canv.delete('all')
    draw.rectangle((0, 0, width, height), fill=(255, 255, 255, 0))
    txt.delete('1.0', ctk.END)
    sol.delete('1.0', ctk.END)

# =============================
# GUI Setup
# =============================
root = ctk.CTk()
root.resizable(0, 0)
root.title('HANDWRITING CALCULATOR')

# Canvas for drawing
canv = ctk.CTkCanvas(root, width=width, height=height, bg='white')
canv.grid(row=0, column=0, columnspan=2, padx=10, pady=17)
canv.bind("<B1-Motion>", paint)

# Initialize drawing image
image1 = PIL.Image.new("RGB", (width, height), (255, 255, 255))
draw = ImageDraw.Draw(image1)

your_font = "Bahnschrift"

# Text boxes
text_font = ctk.CTkFont(family=your_font, size=27)
txt = ctk.CTkTextbox(root, exportselection=0, padx=10, pady=10, height=height//10, width=width//5, font=text_font)
txt.grid(row=2, column=0, padx=0, pady=3)

text_font = ctk.CTkFont(family=your_font, size=30, weight='bold')
sol = ctk.CTkTextbox(root, exportselection=0, padx=10, pady=10, height=height//10, width=width//5, font=text_font, text_color='#3085ff')
sol.grid(row=3, column=0, padx=0, pady=3)

# Blank image creation if missing
if not os.path.exists("Blank.png"):
    blank = Image.new("RGB", (200, 200), "white")
    blank.save("Blank.png")
    print("Blank.png created automatically")

# Image box
labimg = Image.open("Blank.png")
labimg = ctk.CTkImage(dark_image=labimg, size=(width//5, height//5))
image_label = ctk.CTkLabel(root, image=labimg, text="")
image_label.image = labimg
image_label.grid(row=2, column=1, padx=10, pady=5, rowspan=2)

# Buttons
button_font = ctk.CTkFont(family=your_font, size=15)
Pred = ctk.CTkButton(root, text="Calculate", command=mod, fg_color='#0056C4', hover_color='#007dfe', font=button_font, height=height//22.5)
Clr = ctk.CTkButton(root, text="Clear", command=clear, fg_color='#B50000', hover_color='#dd0000', font=button_font, height=height//22.5)

Pred.grid(row=1, column=0, padx=10, pady=1, sticky='ew')
Clr.grid(row=1, column=1, padx=10, pady=1, sticky='ew')

print("GUI starting...")
root.mainloop()
