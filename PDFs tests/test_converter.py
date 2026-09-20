import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import base64
from PIL import Image
import io

# Inject Poppler into PATH for local testing
poppler_path = r"C:\Users\barno\AppData\Local\Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\poppler-25.07.0\Library\bin"
os.environ["PATH"] += os.pathsep + poppler_path

# Add parent directory to path so we can import the logic file
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from converter import convert_pdf_to_base64_dict

# Tests the PDF conversion and saves the output Base64 strings back to JPEG images.
def test_conversion_and_save():
    # Try with and without extension just in case
    pdf_filename = "בגרות מדמח 2025.pdf"
    if not os.path.exists(pdf_filename):
        pdf_filename = "בגרות מדמח 2025"
        if not os.path.exists(pdf_filename):
            print(f"File {pdf_filename} not found!")
            return

    print(f"Reading {pdf_filename}...")
    with open(pdf_filename, "rb") as f:
        pdf_bytes = f.read()

    print("Running converter logic...")
    result_dict = convert_pdf_to_base64_dict(pdf_bytes)

    # Verifying the structure
    pages = result_dict.get("pages", [])
    assert isinstance(pages, list), "Error: 'pages' is not a list!"
    assert len(pages) > 0, "Error: No pages found in the PDF!"
    
    print(f"Validation passed! The dictionary contains {len(pages)} pages.")
    
    # Save the Base64 back to image files
    for page_obj in pages:
        page_num = page_obj["page_number"]
        base64_str = page_obj["base64_data"]
        
        # Decode Base64 string to bytes
        image_bytes = base64.b64decode(base64_str)
        
        # Open with PIL and save as JPEG
        image = Image.open(io.BytesIO(image_bytes))
        output_file = f"output_page_{page_num}.jpg"
        image.save(output_file, "JPEG")
        print(f"Saved decoded image to {output_file}")

if __name__ == "__main__":
    test_conversion_and_save()
