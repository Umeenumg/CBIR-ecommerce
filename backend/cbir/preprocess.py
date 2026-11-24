from PIL import Image
 
 
def load_image(path):
    """Ouvre une image et la convertit en RGB."""
    return Image.open(path).convert("RGB")