import cv2
from cv2 import dnn_superres
import numpy as np


class Upscaler:
    def __init__(self, model_path: str = 'EDSR_x2.pb'):
        self.scaler = dnn_superres.DnnSuperResImpl_create()
        self.scaler.readModel(model_path)
        self.scaler.setModel("edsr", 2)

    def upscale(self, image_bytes: bytes) -> bytes:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Upscale
        result = self.scaler.upsample(image)

        # Convert back to bytes
        _, buffer = cv2.imencode('.png', result)
        return buffer.tobytes()


# Global instance to be reused
_upscaler = None


def get_upscaler(model_path: str = 'EDSR_x2.pb'):
    global _upscaler
    if _upscaler is None:
        _upscaler = Upscaler(model_path)
    return _upscaler


def upscale(input_path: str, output_path: str, model_path: str = 'EDSR_x2.pb') -> None:
    """
    Legacy function for backward compatibility or simple CLI use.
    """
    upscaler = get_upscaler(model_path)
    with open(input_path, 'rb') as f:
        input_bytes = f.read()
    output_bytes = upscaler.upscale(input_bytes)
    with open(output_path, 'wb') as f:
        f.write(output_bytes)


def example():
    upscale('lama_300px.png', 'lama_600px.png')


if __name__ == '__main__':
    example()