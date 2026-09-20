import os
from fastapi import FastAPI, UploadFile, File, Header, HTTPException, Depends
from converter import convert_pdf_to_base64_dict

app = FastAPI(title="PDF to Image Converter Microservice")

API_KEY = os.environ.get("API_KEY")

# Validates the API key from the request header against the configured environment variable.
# param x_api_key: The API key provided in the request header.
# raises HTTPException: If the key is invalid or missing.
def verify_api_key(x_api_key: str = Header(None)) -> None:
    if not API_KEY or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing API Key")

# Receives a PDF file, converts its pages to Base64 encoded images, and returns them.
# param file: The uploaded PDF file.
# returns: A dictionary containing a list of Base64 strings mapped to page numbers (automatically serialized to JSON).
@app.post("/convert", dependencies=[Depends(verify_api_key)])
async def convert_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF is supported.")
    
    try:
        pdf_bytes = await file.read()
        return convert_pdf_to_base64_dict(pdf_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

