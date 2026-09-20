import base64
import io
from pdf2image import convert_from_bytes
from PIL import Image
from typing import List, Dict, Any

# Converts a single PIL Image object to a Base64 encoded JPEG string.
# param image: The PIL Image object to convert.
# returns: Base64 encoded string representing the image.
def _image_to_base64(image: Image.Image) -> str:
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# Extracts pages from a PDF bytes object, converts them to Base64 images, and maps them to page numbers.
# param pdf_bytes: The raw bytes of the PDF file.
# returns: A dictionary containing a list of page objects with their numbers and Base64 data.
def convert_pdf_to_base64_dict(pdf_bytes: bytes) -> Dict[str, List[Dict[str, Any]]]:
    pages = convert_from_bytes(pdf_bytes)
    result = {"pages": []}
    
    for index, page_image in enumerate(pages):
        page_number = index + 1
        base64_str = _image_to_base64(page_image)
        
        result["pages"].append({
            "page_number": page_number,
            "base64_data": base64_str
        })
        
    return result

