from io import BytesIO

from PIL import Image, ImageFilter


def build_sharpened_image(image_bytes):
    if not image_bytes:
        return None, "No image data received."

    try:
        image = Image.open(BytesIO(image_bytes))
    except Exception:
        return None, "Unable to read the image."

    try:
        sharpened = image.filter(
            ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3)
        )
    except Exception:
        return None, "Unable to sharpen the image."

    output_buffer = BytesIO()
    try:
        sharpened.save(output_buffer, format="PNG")
    except Exception:
        return None, "Unable to encode the processed image."

    return output_buffer.getvalue(), None
