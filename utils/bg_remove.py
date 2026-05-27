from io import BytesIO

from rembg import remove
from PIL import Image


def build_background_removed_image(image_bytes):
    if not image_bytes:
        return None, "No image data received."

    try:
        result = remove(image_bytes)
    except Exception:
        return None, "Unable to remove background. Try a different photo."

    if isinstance(result, bytes):
        return result, None

    output_buffer = BytesIO()
    try:
        result.save(output_buffer, format="PNG")
    except Exception:
        return None, "Unable to encode the processed image."

    return output_buffer.getvalue(), None
