from PIL import Image
import requests as req
import tkinter as tk
import io
import math
import time
import os

def download_image(url: str) -> Image:
    timestamp = time.time()
    resp = req.get(url=url)
    if(resp.ok): 
        bin = resp.content
        image = Image.open(io.BytesIO(bin))
        print(f"downloaded image: {url.split('/')[-1]} ({time.time() - timestamp})")
        return image
    return False

#fit image within a container of a certain size while
#preserving aspect ratio through uniform scale
def resize_image(image: Image, dest_size: int) -> Image:
    image_w, image_h = image.size
    dest_w, dest_h = dest_size

    y_adjacent = (dest_w / image_w) < (dest_h / image_h)
    image_perpendicular = image_w if y_adjacent else image_h
    dest_perpendicular = dest_w if y_adjacent else dest_h
    transform = dest_perpendicular / image_perpendicular
    
    image_w = math.floor(image_w * transform)
    image_h = math.floor(image_h * transform)
    image = image.resize((image_w, image_h), Image.LANCZOS)
    return image

def destroy_widgets(widget: tk.Frame):
    children = widget.winfo_children()
    for child in children:
        if child.winfo_children():
            destroy_widgets(child)
        child.destroy()

def forget_widgets(widget: tk.Frame):
    children = widget.winfo_children()
    for child in children:
        if child.winfo_children():
            forget_widgets(child)
        child.pack_forget()

def get_widget_size(widget: any) -> (int, int):
    widget.update_idletasks()
    width = widget.winfo_width()
    height = widget.winfo_height()
    return (width, height)

def assert_file_exists(path):
    if not os.path.exists(path):
        with open(path, "wb") as f: pass

def assert_dir_exists(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)