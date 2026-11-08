# PDF-to-Base64 Image Microservice

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Production%20Ready-2496ED?logo=docker&logoColor=white)
![Architecture](https://img.shields.io/badge/Architecture-Stateless%20%7C%20In--Memory-6C5CE7)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A lightweight, stateless, production-ready REST microservice that converts multi-page PDF documents into page-indexed **Base64-encoded JPEG images** entirely in memory. Built with **FastAPI**, **Poppler**, and **Pillow**, it provides a clean HTTP boundary for cloud applications, automation workflows, and AI document pipelines without local disk persistence.

---

## Why This Microservice?

Extracting or rendering content directly from PDF files is notoriously fragile across modern cloud stacks. Standard text parsers frequently break on custom font encodings, scanned documents, mathematical notation, multi-column layouts, and Right-to-Left (RTL) scripts. Meanwhile, serverless functions and low-code platforms rarely include native PDF rendering binaries such as Poppler.

By offloading PDF rasterization to an isolated, container-native microservice, any application can turn raw PDF binaries into uniform, ready-to-consume image payloads via a single HTTPS request:

* **Document Ingestion & OCR Pipelines:** Pre-renders complex, scanned, or encoding-damaged PDFs into crisp page images for downstream optical character recognition and archival indexing.
* **Workflow Automation (`n8n`, Make, Zapier):** Serves as a drop-in HTTP node for low-code orchestrators that need reliable multi-page PDF splitting and image conversion without managing temporary storage.
* **Multimodal & Vision LLM Pipelines:** Converts uploaded PDFs directly into structured Base64 image arrays ready for Vision-capable LLMs to perform layout-aware extraction, summarization, or Q&A.
* **Web Previews & Backend Offloading:** Decouples CPU-intensive PDF rasterization from core application servers, enabling instant document previews and horizontal autoscaling.

---

## Key Features

* **Zero Disk Footprint (100% In-Memory):** Processes incoming PDF byte streams and encodes JPEG buffers strictly in RAM (`io.BytesIO`), ensuring sensitive documents are never written to persistent storage.
* **Stateless & Serverless-Native:** Designed for scale-to-zero and rapid horizontal scaling on container platforms such as Google Cloud Run, AWS App Runner, Azure Container Apps, and Kubernetes.
* **Header-Based API Key Security:** Protects endpoints via an `X-API-Key` dependency validated against environment configuration.
* **Deterministic JSON Output:** Returns an ordered, 1-indexed array of page objects (`page_number` and `base64_data`) for straightforward downstream iteration.
* **Hardened Container Image:** Built on `python:3.11-slim` with `poppler-utils`, running under an unprivileged non-root user (`appuser`) with `exec` PID 1 signal handling for graceful shutdowns.

---

## Architecture & Request Flow

```mermaid
flowchart LR
    Client["Client / Backend / n8n"] -->|"POST /convert (PDF + X-API-Key)"| Auth["FastAPI Auth & MIME Check"]
    Auth -->|"Raw PDF Bytes (RAM)"| Renderer["Poppler + Pillow Engine"]
    Renderer -->|"Ordered Base64 JPEGs"| Response["JSON Response (200 OK)"]
```

### Project Structure

```text
.
├── main.py            # FastAPI application, API key authentication, and /convert route
├── converter.py       # In-memory PDF-to-JPEG rasterization and Base64 encoding logic
├── requirements.txt   # Pinned Python dependencies
├── Dockerfile         # Production container definition with Poppler and non-root user
├── .dockerignore      # Excludes local environments and non-runtime files from image builds
└── README.md          # Service documentation
```

---

## API Reference

### Convert PDF to Base64 Images

```http
POST /convert
```

#### Request Headers

| Header | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `X-API-Key` | `string` | Yes | Secret key matching the server's `API_KEY` environment variable. |
| `Content-Type` | `string` | Yes | `multipart/form-data` (set automatically by HTTP clients when uploading files). |

#### Form Data Parameters

| Field | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `file` | `file` | Yes | Binary PDF document (`application/pdf`). |

#### Example Request (`cURL`)

```bash
curl -X POST "https://your-service-url.example.com/convert" \
  -H "X-API-Key: <YOUR_API_KEY>" \
  -F "file=@/path/to/document.pdf;type=application/pdf"
```

#### Example Request (`Python`)

```python
import requests

url = "https://your-service-url.example.com/convert"
headers = {"X-API-Key": "<YOUR_API_KEY>"}

with open("document.pdf", "rb") as pdf_file:
    files = {"file": ("document.pdf", pdf_file, "application/pdf")}
    response = requests.post(url, headers=headers, files=files, timeout=60)

response.raise_for_status()
pages = response.json()["pages"]
print(f"Converted {len(pages)} pages.")
```

#### Success Response (`200 OK`)

```json
{
  "pages": [
    {
      "page_number": 1,
      "base64_data": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgK..."
    },
    {
      "page_number": 2,
      "base64_data": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgK..."
    }
  ]
}
```

#### Response Status Codes

| Status Code | Condition |
| :---: | :--- |
| `200 OK` | PDF successfully converted into Base64-encoded JPEG pages. |
| `400 Bad Request` | Uploaded file MIME type is not `application/pdf`. |
| `401 Unauthorized` | Missing or invalid `X-API-Key` header, or server `API_KEY` is unset. |
| `422 Unprocessable Entity` | Missing required `file` field in the multipart form payload. |
| `500 Internal Server Error` | Corrupted PDF stream or internal rendering failure. |

---

## Getting Started

### Environment Variables

| Variable | Required | Default | Description |
| :--- | :---: | :---: | :--- |
| `API_KEY` | **Yes** | — | Secret token required in the `X-API-Key` request header. |
| `PORT` | No | `8080` | TCP port on which Uvicorn listens inside the container. |

### Option 1: Run with Docker (Recommended)

Docker encapsulates both Python dependencies and the native `poppler-utils` binary.

1. **Build the image:**
   ```bash
   docker build -t pdf-to-base64-service .
   ```

2. **Run the container:**
   ```bash
   docker run --rm -p 8080:8080 \
     -e API_KEY="your-strong-secret-key" \
     pdf-to-base64-service
   ```

The service will be available at `http://localhost:8080/convert`, with interactive OpenAPI documentation at `http://localhost:8080/docs`.

### Option 2: Local Python Development

#### Prerequisites
* **Python 3.11+**
* **Poppler** installed on your host system and available in `PATH`:
  * **Ubuntu / Debian:** `sudo apt-get install -y poppler-utils`
  * **macOS (Homebrew):** `brew install poppler`
  * **Windows:** Install Poppler binaries (e.g., via `winget` or Conda) and add the `bin/` folder to your system `PATH`.

#### Setup & Run

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # On Windows (PowerShell): .\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set the required API key and launch Uvicorn
export API_KEY="your-strong-secret-key"   # On Windows (PowerShell): $env:API_KEY="your-strong-secret-key"
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

---

## Cloud Deployment

Because the container listens dynamically on `${PORT}` (defaulting to `8080`) and keeps zero local state, it deploys directly to any serverless container platform. For example, on **Google Cloud Run**:

```bash
gcloud run deploy pdf-to-base64 \
  --source . \
  --region <REGION> \
  --allow-unauthenticated \
  --set-env-vars API_KEY="<YOUR_API_KEY>"
```

> **Security Note:** Even when the Cloud Run service ingress is public (`--allow-unauthenticated`) so external webhooks or orchestrators can reach it, every request to `/convert` remains protected at the application layer by `X-API-Key` verification. Store production keys using a secret manager (e.g., Google Secret Manager) rather than plaintext scripts.

---

## License

Distributed under the **MIT License**.
