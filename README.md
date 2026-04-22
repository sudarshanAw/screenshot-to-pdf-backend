# Screenshot to PDF API

A production-ready Python FastAPI backend for converting images to PDF.

## Folder Structure

```
screenshot-to-pdf-backend/
├── src/
│   └── index.py         # Main FastAPI application and endpoints
├── requirements.txt     # Python dependencies
├── vercel.json          # Vercel deployment configuration
└── README.md            # This file
```

## Running Locally

1. **Prerequisites**
   - Python 3.9+
   - pip (Python package installer)

2. **Setup Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Server**
   ```bash
   uvicorn src.index:app --reload
   ```
   The API will be available at `http://127.0.0.1:8000`.
   - Health check: `GET http://127.0.0.1:8000/`
   - Interactive API Docs: `http://127.0.0.1:8000/docs`

## Deploying to Vercel

This project is pre-configured to be deployed to Vercel as a Serverless Function using the `@vercel/python` builder.

1. **Prerequisites**
   - Install the Vercel CLI: `npm i -g vercel`
   - Log in to Vercel: `vercel login`

2. **Deploy**
   Navigate to the `screenshot-to-pdf-backend` directory and run:
   ```bash
   vercel
   ```
   Follow the prompts to set up and deploy the project.

3. **Production Deploy**
   To deploy to production, run:
   ```bash
   vercel --prod
   ```

## API Reference

### `POST /convert`
Converts an uploaded screenshot to a PDF file.

- **Content-Type**: `multipart/form-data`
- **Body**: 
  - `file`: The image file (PNG, JPG, JPEG, WEBP)
- **Response**:
  - `200 OK`: A downloadable PDF file (`application/pdf`)
  - `400 Bad Request`: Missing file or unsupported file format
  - `500 Internal Server Error`: Conversion failure
