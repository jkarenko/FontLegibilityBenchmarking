import random
import string
import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageTk


def update_blur(value):
    global current_text, frozen_text, frozen_blur_levels
    generate_image()


def decrease_blur():
    current_value = slider.get()
    if current_value > 0:
        slider.set(current_value - 1)
        generate_image()


def random_text(length=16):
    """Generate a random string of fixed length"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def generate_image():
    global image, tk_image, image_container, current_text, frozen_text, frozen_blur_levels, slider
    draw = ImageDraw.Draw(image)
    image.paste("white", [0, 0, image_width, image_height])  # Clear previous text

    y_position = 10
    for index, font_path in enumerate(fonts):
        try:
            font = ImageFont.truetype(font_path, 40)
        except IOError:
            print(f"Font not found: {font_path}")
            font = ImageFont.load_default()

        text = frozen_text.get(index, random_text())
        current_text[index] = text

        # Create a temporary image for this text
        temp_image = Image.new("RGB", (image_width, 50), color="white")
        temp_draw = ImageDraw.Draw(temp_image)
        temp_draw.text((10, 0), text, font=font, fill="black")

        # Apply individual blur if frozen, otherwise use global blur
        blur_value = frozen_blur_levels.get(index, slider.get())
        blurred_temp = temp_image.filter(ImageFilter.GaussianBlur(radius=blur_value))

        # Paste the blurred text onto the main image
        image.paste(blurred_temp, (0, y_position))

        y_position += 50

    tk_image = ImageTk.PhotoImage(image)

    if image_container is None:
        image_container = canvas.create_image(0, 0, anchor="nw", image=tk_image)
    else:
        canvas.itemconfig(image_container, image=tk_image)

    canvas.image = tk_image  # Keep reference to avoid GC


def reveal_font(event):
    global current_text, frozen_text, frozen_blur_levels
    y_click = event.y
    index = y_click // 50
    if 0 <= index < len(fonts):
        if index not in frozen_text:  # Only freeze if not already frozen
            frozen_text[index] = current_text[index]
            frozen_blur_levels[index] = slider.get()  # Freeze the current blur level
        else:
            # If already frozen, unfreeze
            frozen_text.pop(index, None)
            frozen_blur_levels.pop(index, None)
        generate_image()


# Create an image with different fonts
fonts = [
    "/Library/Fonts/Arial.ttf",
    "/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Times New Roman.ttf",
    "/Library/Fonts/Courier New.ttf",
    "/Library/Fonts/Comic Sans MS.ttf"
]

image_width = 600
image_height = len(fonts) * 50 + 20
image = Image.new("RGB", (image_width, image_height), color="white")

# Setup tkinter window
root = tk.Tk()
root.title("Font Legibility Evaluation")

canvas = tk.Canvas(root, width=image_width, height=image_height)
canvas.pack()
canvas.bind("<Button-1>", reveal_font)

# Initialize variables
image_container = None
current_text = {}
frozen_text = {}
frozen_blur_levels = {}

# Blur slider set to max 10
slider = tk.Scale(root, from_=0, to=10, orient="horizontal", label="Blur", command=update_blur)
slider.set(10)
slider.pack()

# Clarify button
clarify_button = tk.Button(root, text="Clarify", command=decrease_blur)
clarify_button.pack()

# Initial generation of image
generate_image()

root.mainloop()
