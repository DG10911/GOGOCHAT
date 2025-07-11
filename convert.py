import os, sys
from PIL import Image

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

img = Image.open(resource_path("gogo.png"))
img.save("gogo.ico", format="ICO", sizes=[(64, 64)])