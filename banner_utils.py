import io
from PIL import Image

MAX_IMAGE_SIZE_MB = 5
MAX_IMAGE_DIMENSION = 1024

def validate_and_resize_image(uploaded_file) -> Image.Image:
    """
    Valida o tamanho do arquivo e redimensiona a imagem para otimizar
    o envio via API, evitando estouro de payload e economizando tokens.
    """
    uploaded_file.seek(0, 2)
    file_size_mb = uploaded_file.tell() / (1024 * 1024)
    uploaded_file.seek(0)

    if file_size_mb > MAX_IMAGE_SIZE_MB:
        raise ValueError(f"A imagem excede o tamanho máximo permitido de {MAX_IMAGE_SIZE_MB}MB.")

    try:
        img = Image.open(uploaded_file)
        if img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')
        img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.Resampling.LANCZOS)
        return img
    except Exception as e:
        raise ValueError("Arquivo de imagem inválido ou corrompido.") from e
