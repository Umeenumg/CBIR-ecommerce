import numpy as np
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import config
 
_model = None
 
def get_model():
    global _model
    if _model is None:
        _model = MobileNetV2(weights="imagenet", include_top=False,
                             pooling="avg", input_shape=(224, 224, 3))
    return _model
 
 
def extract_batch(images):
    arrays = [np.asarray(img.resize(config.IMAGE_SIZE), dtype="float32")
              for img in images]
    batch = preprocess_input(np.stack(arrays))
    feats = get_model().predict(batch, verbose=0)
    norms = np.linalg.norm(feats, axis=1, keepdims=True)
    return (feats / norms).astype("float32")