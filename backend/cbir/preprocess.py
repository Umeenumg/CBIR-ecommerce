from PIL import Image
import io
 
 
def load_image(path):
    """Ouvre une image et la convertit en RGB."""
    return Image.open(path).convert("RGB")


def load_image_bytes(data):
    """Verifie que `data` (bytes) est une vraie image, puis la convertit en RGB.
    Leve une exception si ce n'est pas une image valide."""
    Image.open(io.BytesIO(data)).verify()       # verify() "consomme" l'objet...
    img = Image.open(io.BytesIO(data))          # ...donc on rouvre
    img.load()
    return img.convert("RGB")