import os
import random
import re
import sys
import time
import tkinter as tk
import unicodedata

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageTk

text_cache = None
collected_fonts = []
last_update_time = 0
current_sentence = None
current_word_index = 0
max_blur = 6.0


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def load_text():
    global text_cache
    if text_cache is None:
        with open(resource_path('Pride_and_Prejudice.txt'), 'r', encoding='utf-8') as file:
            text_cache = file.read()
    sentences = re.split(r'(?<=[.!?]) +', text_cache)
    return [sentence.split() for sentence in sentences if len(sentence.split()) >= 3]


def get_next_word():
    global current_sentence, current_word_index
    if current_sentence is None or current_word_index >= len(current_sentence):
        current_sentence = random.choice(sentences)
        current_word_index = 0
    word = current_sentence[current_word_index]
    word = word.strip("\"“”")
    current_word_index += 1
    return word


def test_font(font_path, size=30):
    # Create a new image
    img = Image.new('RGB', (size * 3, size), color='white')
    draw = ImageDraw.Draw(img)

    try:
        # Try to load the font
        font = ImageFont.truetype(font_path, size)
    except IOError:
        print(f"Could not load font: {font_path}")
        return False

    # Test with multiple characters
    test_chars = "AÖ1"  # Basic Latin, Hiragana, Latin-1 Supplement
    for i, char in enumerate(test_chars):
        draw.text((i * size, 0), char, font=font, fill='black')

    # Convert image to numpy array
    img_array = np.array(img)

    # Check if anything was drawn
    if np.all(img_array == 255):
        print(f"Font {font_path} failed: nothing was drawn")
        return False

    # Check for uniform rectangles or question mark patterns
    first_slice = None
    for i in range(3):
        char_slice = img_array[:, i * size:(i + 1) * size]
        if first_slice is None:
            first_slice = char_slice

        # Check for uniform rectangles
        if np.all(char_slice == char_slice[0, 0]):
            print(f"Font {font_path} failed: uniform rectangle detected")
            return False

        # Check for question mark pattern (simplified)
        if np.sum(char_slice < 255) < 0.1 * size * size:
            print(f"Font {font_path} failed: possible question mark or minimal glyph detected")
            return False

        # Check if the slices are too similar
        if i > 0:
            if np.all(char_slice == first_slice):
                print(f"Font {font_path} failed: too similar characters detected")
                return False

    # Check for diversity in pixel values
    if len(np.unique(img_array)) < 10:
        print(f"Font {font_path} failed: not enough pixel value diversity")
        return False

    return True


def get_font_files(directories):
    working_fonts = []
    for directory in directories:
        print(f"Searching for fonts in: {directory}")
        font_extensions = ('.ttf', '.otf', '.ttc')
        all_fonts = [os.path.join(directory, f) for f in os.listdir(directory)
                     if f.lower().endswith(font_extensions)]
        print(f"Total fonts found: {len(all_fonts)}")
        working_fonts.extend([font for font in all_fonts if test_font(font)])
        print(f"Working fonts: {len(working_fonts)}")
    return working_fonts


def update_blur():
    global last_update_time
    current_time = time.time()

    if current_time - last_update_time >= 1:
        current_blur = slider.get()
        if current_blur > 0:
            slider.set(current_blur - 0.1)
        last_update_time = current_time

    generate_image()
    root.after(300, update_blur)  # Schedule the next update


def generate_image():
    global image, image_container
    image.paste("white", [0, 0, image_width, image_height])  # Clear previous text

    draw = ImageDraw.Draw(image)
    blur_value = slider.get()

    try:
        font = ImageFont.truetype(current_font, 40)
    except IOError:
        print(f"Font not found: {current_font}")
        font = ImageFont.load_default()

    current_word = get_next_word()

    # Normalize the Unicode string
    current_word = unicodedata.normalize('NFC', current_word)

    # Create a separate image for the word, blur it, then paste onto the main image
    text_image = Image.new("RGB", (image_width, 120), color="white")
    text_draw = ImageDraw.Draw(text_image)

    left, top, right, bottom = text_draw.textbbox((0, 0), current_word, font=font)
    text_width = right - left
    text_height = bottom - top

    text_position = ((image_width - text_width) // 2, (120 - text_height) // 2)
    text_draw.text(text_position, current_word, font=font, fill="black")
    blurred_text = text_image.filter(ImageFilter.GaussianBlur(radius=blur_value))
    image.paste(blurred_text, (0, image_height // 2 - 60))

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

    slider.set(max_blur)
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
    global collected_fonts, current_font, current_sentence, current_word_index
    collected_fonts = []
    slider.set(max_blur)
    current_font = random.choice(fonts)
    current_sentence = None
    current_word_index = 0
    update_collected_fonts_display()
    generate_image()


root = tk.Tk()
root.title("Font Legibility Evaluation")
root.bind("<Left>", keypress)
root.bind("<Right>", keypress)
root.bind("<space>", keypress)

image_width = 800
image_height = 200
image = Image.new("RGB", (image_width, image_height), color="white")

canvas = tk.Canvas(root, width=image_width, height=image_height)
canvas.pack()

image_container = None

slider = tk.Scale(root, resolution=0.1, from_=0.0, to=max_blur, orient="horizontal",
                  label="Blur level (automatically decreases, adjust with ← →)",
                  length=400, command=update_blur_manually)
slider.set(max_blur)
slider.pack(pady=(10, 10))

tk.Label(root, text="Press spacebar to mark as legible").pack(pady=(0, 10))

# Add a text widget to display collected fonts
collected_fonts_text = tk.Text(root, height=10, width=60)
collected_fonts_text.pack(pady=(0, 10))

reset_button = tk.Button(root, text="Reset Collection", command=reset_all)
reset_button.pack(pady=(0, 10))

# Get user directory
user_dir = os.path.expanduser('~')
print(f"User directory: {user_dir}")
fonts = get_font_files(['/System/Library/Fonts', '/System/Library/Fonts/Supplemental', f'{user_dir}/Library/Fonts'])
print(f"Final list of fonts: {fonts}")
current_font = random.choice(fonts) if fonts else None
if current_font is None:
    print("No working fonts found!")
    quit()

sentences = load_text()

update_blur()

root.mainloop()
