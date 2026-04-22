from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException
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
async def convert_to_pdf(files: List[UploadFile] = File(...)):
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
