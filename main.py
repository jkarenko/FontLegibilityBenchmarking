import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageTk
import os
import random
import string


def update_blur(value):
    blurred_image = image.filter(ImageFilter.GaussianBlur(radius=int(value)))
    tk_image = ImageTk.PhotoImage(blurred_image)
    canvas.itemconfig(image_container, image=tk_image)
    canvas.image = tk_image


def decrease_blur():
    current_value = slider.get()
    if current_value > 0:
        slider.set(current_value - 1)


def random_text(length=16):
    """Generate a random string of fixed length"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def generate_image():
    global image, tk_image, image_container
    text = random_text()
    y_position = 10
    draw = ImageDraw.Draw(image)
    image.paste("white", [0, 0, image_width, image_height])  # Clear previous text
    for font_path in fonts:
        try:
            font = ImageFont.truetype(font_path, 40)
            draw.text((10, y_position), text, font=font, fill="black")
        except IOError:
            print(f"Font not found: {font_path}")
            default_font = ImageFont.load_default()
            draw.text((10, y_position), text, font=default_font, fill="black")
        y_position += 50

    tk_image = ImageTk.PhotoImage(image)

    if image_container is None:
        image_container = canvas.create_image(0, 0, anchor="nw", image=tk_image)
    else:
        canvas.itemconfig(image_container, image=tk_image)

    canvas.image = tk_image


def reveal_font(event):
    y_click = event.y
    index = y_click // 50
    if 0 <= index < len(fonts):
        font_path = fonts[index]
        font_name = os.path.basename(font_path)
        x_click = event.x
        canvas.create_text(x_click + 10, event.y, text=font_name, fill="red", anchor="nw")

        # Regenerate image with random text
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

# Initialize image_container
image_container = None

# Initial generation of image
generate_image()

# Blur slider set to max 10
slider = tk.Scale(root, from_=0, to=10, orient="horizontal", label="Blur", command=update_blur)
slider.set(10)
slider.pack()

# Clarify button
clarify_button = tk.Button(root, text="Clarify", command=decrease_blur)
clarify_button.pack()

root.mainloop()
