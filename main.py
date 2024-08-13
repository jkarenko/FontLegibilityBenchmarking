import random
import re
import tkinter as tk

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageTk


def update_blur(value):
    global current_text, frozen_text, frozen_blur_levels
    generate_image()


text_cache = None


def random_text(length=3):
    global text_cache

    if text_cache is None:
        with open('Ruumiin_Elimista.txt', 'r') as file:
            text_cache = file.read()

    sentences = re.split(r'(?<=[.!?]) +', text_cache)
    sentences = [sentence for sentence in sentences if len(sentence.split()) >= length]
    selected_sentence = random.choice(sentences).strip()

    return selected_sentence


def generate_image():
    global image, image_container, current_text, frozen_text, frozen_blur_levels, slider
    draw = ImageDraw.Draw(image)
    image.paste("white", [0, 0, image_width, image_height])  # Clear previous text

    y_position = 10
    for index, font_path in enumerate(fonts):
        try:
            font = ImageFont.truetype(font_path, 20)
        except IOError:
            print(f"Font not found: {font_path}")
            font = ImageFont.load_default()

        text = frozen_text.get(index, random_text())
        current_text[index] = text

        # Create a temporary image for this text
        temp_image = Image.new("RGB", (image_width, 50), color="white")
        temp_draw = ImageDraw.Draw(temp_image)
        temp_draw.text((200, 20), text, font=font, fill="black")

        # Apply individual blur if frozen, otherwise use global blur
        blur_value = frozen_blur_levels.get(index, slider.get())
        blurred_temp = temp_image.filter(ImageFilter.GaussianBlur(radius=blur_value))

        # Paste the blurred text onto the main image
        image.paste(blurred_temp, (0, y_position))

        y_position += 100

    tk_image = ImageTk.PhotoImage(image)

    if image_container is None:
        image_container = canvas.create_image(0, 0, anchor="nw", image=tk_image)
    else:
        canvas.itemconfig(image_container, image=tk_image)

    canvas.image = tk_image  # Keep reference to avoid GC


def reveal_font(event):
    global current_text, frozen_text, frozen_blur_levels
    y_click = event.y
    index = y_click // 100
    if 0 <= index < len(fonts):
        if index not in frozen_text:  # Only freeze if not already frozen
            frozen_text[index] = current_text[index]
            frozen_blur_levels[index] = slider.get()  # Freeze the current blur level
        else:
            # If already frozen, unfreeze
            frozen_text.pop(index, None)
            frozen_blur_levels.pop(index, None)
        generate_image()


def keypress(event):
    if event.keysym == 'Left':
        slider.set(slider.get() - 0.1)
    elif event.keysym == 'Right':
        slider.set(slider.get() + 0.1)


fonts = [
    "/Library/Fonts/Arial.ttf",
    "/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Times New Roman.ttf",
    "/Library/Fonts/Courier New.ttf",
    "/Library/Fonts/Comic Sans MS.ttf"
]

root = tk.Tk()
root.title("Font Legibility Evaluation")
root.bind("<Left>", keypress)
root.bind("<Right>", keypress)

image_width = root.winfo_screenwidth()
image_height = len(fonts) * 100 + 20
image = Image.new("RGB", (image_width, image_height), color="white")

canvas = tk.Canvas(root, width=image_width, height=image_height)
canvas.pack()
canvas.bind("<Button-1>", reveal_font)

image_container = None
current_text = {}
frozen_text = {}
frozen_blur_levels = {}

slider = tk.Scale(root, resolution=0.1, from_=0.0, to=5.0, orient="horizontal", label="Blur", command=update_blur)
slider.set(5.0)
slider.pack(pady=(0, 20))

generate_image()

root.mainloop()
