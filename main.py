import os
import random
import re
import time
import tkinter as tk

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageTk

text_cache = None
collected_fonts = []
last_update_time = 0


def random_text(length=3):
    global text_cache

    if text_cache is None:
        with open('Ruumiin_Elimista.txt', 'r') as file:
            text_cache = file.read()

    sentences = re.split(r'(?<=[.!?]) +', text_cache)
    sentences = [sentence for sentence in sentences if len(sentence.split()) >= length]
    return random.choice(sentences).strip()


def get_font_files(directory):
    font_extensions = ('.ttf', '.otf', '.ttc')
    return [os.path.join(directory, f) for f in os.listdir(directory)
            if f.lower().endswith(font_extensions)]


def update_blur():
    global last_update_time
    current_time = time.time()

    if current_time - last_update_time >= 1:
        current_blur = slider.get()
        if current_blur > 0:
            slider.set(current_blur - 0.1)
        last_update_time = current_time

    generate_image()
    root.after(100, update_blur)  # Schedule the next update


def generate_image():
    global image, image_container, current_text
    image.paste("white", [0, 0, image_width, image_height])  # Clear previous text

    draw = ImageDraw.Draw(image)
    blur_value = slider.get()

    try:
        font = ImageFont.truetype(current_font, 30)
    except IOError:
        print(f"Font not found: {current_font}")
        font = ImageFont.load_default()

    current_text = random_text()

    # Create a separate image for the text, blur it, then paste onto the main image
    text_image = Image.new("RGB", (image_width, 60), color="white")
    text_draw = ImageDraw.Draw(text_image)
    text_draw.text((0, 0), current_text, font=font, fill="black")
    blurred_text = text_image.filter(ImageFilter.GaussianBlur(radius=blur_value))
    image.paste(blurred_text, (20, image_height // 2 - 30))

    # Display the current font name
    font_name = os.path.basename(current_font).split('.')[0]
    draw.text((20, 20), f"Current Font: {font_name}", font=ImageFont.truetype(fonts[0], 16), fill="blue")

    # Display current blur level
    draw.text((20, 50), f"Current Blur: {blur_value:.1f}", font=ImageFont.truetype(fonts[0], 16), fill="red")

    tk_image = ImageTk.PhotoImage(image)

    if image_container is None:
        image_container = canvas.create_image(0, 0, anchor="nw", image=tk_image)
    else:
        canvas.itemconfig(image_container, image=tk_image)

    canvas.image = tk_image  # Keep reference to avoid GC


def collect_font_and_reset():
    global current_font, collected_fonts
    current_blur = slider.get()
    collected_fonts.append((current_font, current_blur))
    update_collected_fonts_display()

    # Reset blur to 5.0 and select a new random font
    slider.set(5.0)
    current_font = random.choice(fonts)
    generate_image()


def update_collected_fonts_display():
    collected_fonts_text.delete('1.0', tk.END)
    # Sort collected fonts by blur value in descending order
    sorted_fonts = sorted(collected_fonts, key=lambda x: x[1], reverse=True)
    for i, (font, blur) in enumerate(sorted_fonts, 1):
        font_name = os.path.basename(font).split('.')[0]
        collected_fonts_text.insert(tk.END, f"{i}. Font: {font_name}, Blur: {blur:.1f}\n")


def update_blur_manually(event=None):
    generate_image()


def keypress(event):
    if event.keysym == 'Left':
        slider.set(slider.get() - 0.1)
    elif event.keysym == 'Right':
        slider.set(slider.get() + 0.1)
    elif event.keysym == 'space':
        collect_font_and_reset()


def reset_all():
    global collected_fonts, current_font
    collected_fonts = []
    slider.set(5.0)
    current_font = random.choice(fonts)
    update_collected_fonts_display()
    generate_image()


root = tk.Tk()
root.title("Font Legibility Evaluation")
root.bind("<Left>", keypress)
root.bind("<Right>", keypress)
root.bind("<space>", keypress)

image_width = root.winfo_screenwidth()
image_height = 400
image = Image.new("RGB", (image_width, image_height), color="white")

canvas = tk.Canvas(root, width=image_width, height=image_height)
canvas.pack()

image_container = None
current_text = ""

slider = tk.Scale(root, resolution=0.1, from_=0.0, to=5.0, orient="horizontal",
                  label="Blur level (automatically decreases, adjust with ← →)",
                  length=400, command=update_blur_manually)
slider.set(5.0)
slider.pack(pady=(10, 10))

# Add a text widget to display collected fonts
collected_fonts_text = tk.Text(root, height=10, width=60)
collected_fonts_text.pack(pady=(0, 10))

reset_button = tk.Button(root, text="Reset Collection", command=reset_all)
reset_button.pack(pady=(0, 10))

fonts = get_font_files('/Library/Fonts/')
current_font = random.choice(fonts)

update_blur()

root.mainloop()
