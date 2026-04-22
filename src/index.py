import os
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException, Header, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import img2pdf

app = FastAPI(title="Screenshot to PDF API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPPORTED_FORMATS = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp"
}

@app.get("/")
async def root():
    return {"status": "ok", "message": "Screenshot to PDF API is running"}

@app.post("/convert")
async def convert_to_pdf(
    request: Request,
    files: List[UploadFile] = File(...),
    x_rapidapi_proxy_secret: str = Header(None)
):
    # Security: Check for RapidAPI Proxy Secret
    expected_secret = os.environ.get("RAPIDAPI_PROXY_SECRET")
    
    # We allow the specific frontend origin to bypass the RapidAPI check
    # so your own website continues to work!
    frontend_origin = "https://screenshot-to-pdf.vercel.app" # You can update this later
    request_origin = request.headers.get("origin")
    
    if expected_secret and request_origin != frontend_origin:
        if x_rapidapi_proxy_secret != expected_secret:
            raise HTTPException(status_code=401, detail="Unauthorized. Please use RapidAPI to access this service.")

    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="No files uploaded")
        
    image_bytes_list = []
    
    for file in files:
        if file.content_type not in SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file.content_type}. Please upload PNG, JPG, JPEG, or WEBP."
            )
            
        try:
            image_bytes = await file.read()
            if not image_bytes:
                continue
            image_bytes_list.append(image_bytes)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read file {file.filename}: {str(e)}")

    if not image_bytes_list:
        raise HTTPException(status_code=400, detail="No valid images provided")
        
    try:
        pdf_bytes = img2pdf.convert(image_bytes_list)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="converted.pdf"'
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")
