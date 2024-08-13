import os
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


def draw_checkmark(image, x, y, size=20):
    draw = ImageDraw.Draw(image)
    draw.line((x, y + size // 2, x + size // 3, y + size), fill="green", width=6)
    draw.line((x + size // 3, y + size, x + size, y), fill="green", width=6)


def generate_image():
    global image, image_container, current_text, frozen_text, frozen_blur_levels, slider, fonts, frozen_fonts
    image.paste("white", [0, 0, image_width, image_height])  # Clear previous text

    y_position = 10
    for index in range(5):  # Always generate 5 text lines
        font_path = frozen_fonts.get(index, fonts[index])
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

        # Add checkmark if text is frozen
        if index in frozen_text:
            draw_checkmark(blurred_temp, 170, 15)

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
    global current_text, frozen_text, frozen_blur_levels, frozen_fonts
    y_click = event.y
    index = y_click // 100
    if 0 <= index < 5:  # Changed to 5 to match the number of text lines
        if index not in frozen_text:  # Only freeze if not already frozen
            frozen_text[index] = current_text[index]
            frozen_blur_levels[index] = slider.get()  # Freeze the current blur level
            frozen_fonts[index] = fonts[index]  # Freeze the current font
            update_frozen_info()
            generate_image()


def update_frozen_info():
    frozen_info.delete(1.0, tk.END)  # Clear previous content
    for index, text in frozen_text.items():
        font_name = os.path.basename(frozen_fonts[index]).split('.')[0]  # Extract font name from path
        blur_level = frozen_blur_levels[index]
        frozen_info.insert(tk.END, f"Font: {font_name}, Blur: {blur_level:.1f}\n")


def keypress(event):
    if event.keysym == 'Left':
        slider.set(slider.get() - 0.1)
    elif event.keysym == 'Right':
        slider.set(slider.get() + 0.1)
    elif event.keysym == 'space':
        generate_image()


def get_font_files(directory):
    font_extensions = ('.ttf', '.otf', '.ttc')
    return [os.path.join(directory, f) for f in os.listdir(directory)
            if f.lower().endswith(font_extensions)]


def select_random_fonts():
    global fonts
    all_fonts = get_font_files('/Library/Fonts/')
    fonts = random.sample(all_fonts, 5)
    generate_image()


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
root.bind("<space>", keypress)

image_width = root.winfo_screenwidth()
image_height = 5 * 100 + 20  # Changed to always have 5 text lines
image = Image.new("RGB", (image_width, image_height), color="white")

canvas = tk.Canvas(root, width=image_width, height=image_height)
canvas.pack()
canvas.bind("<Button-1>", reveal_font)

image_container = None
current_text = {}
frozen_text = {}
frozen_fonts = {}
frozen_blur_levels = {}

slider = tk.Scale(root, resolution=0.1, from_=0.0, to=5.0, orient="horizontal", label="Blur", command=update_blur)
slider.set(5.0)
slider.pack(pady=(0, 10))

# Add a text widget to display frozen text information
frozen_info = tk.Text(root, height=5, width=40)
frozen_info.pack(pady=(0, 10))

# Add a button to select random fonts
random_fonts_button = tk.Button(root, text="Select Random Fonts", command=select_random_fonts)
random_fonts_button.pack(pady=(0, 10))

generate_image()

root.mainloop()
