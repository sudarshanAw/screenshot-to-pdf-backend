import os
import io
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Header, Request, Form
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import img2pdf
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

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

def create_watermark_overlay(text: str):
    """Creates a temporary PDF in memory with the watermark text."""
    packet = io.BytesIO()
    # Create a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica", 40)
    can.setFillGray(0.5, 0.3) # 50% gray, 30% alpha
    
    # Draw the watermark diagonally
    can.saveState()
    can.translate(300, 400)
    can.rotate(45)
    can.drawCentredString(0, 0, text)
    can.restoreState()
    
    can.save()
    packet.seek(0)
    return packet

@app.post("/convert")
async def convert_to_pdf(
    request: Request,
    files: List[UploadFile] = File(...),
    password: Optional[str] = Form(None),
    watermark_text: Optional[str] = Form(None),
    x_rapidapi_proxy_secret: str = Header(None)
):
    # Security: Check for RapidAPI Proxy Secret
    expected_secret = os.environ.get("RAPIDAPI_PROXY_SECRET")
    
    frontend_origin = "https://screenshot-to-pdf.vercel.app"
    request_origin = request.headers.get("origin")
    
    if expected_secret and request_origin != frontend_origin:
        if x_rapidapi_proxy_secret != expected_secret:
            raise HTTPException(status_code=401, detail="Unauthorized. Please use RapidAPI to access this service.")

    if not files:
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
        # 1. Initial conversion from images to PDF
        pdf_bytes = img2pdf.convert(image_bytes_list)
        
        # 2. Add Watermark and/or Encryption if requested
        if watermark_text or password:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            writer = PdfWriter()
            
            # Prepare watermark overlay
            watermark_pdf = None
            watermark_page = None
            if watermark_text:
                watermark_packet = create_watermark_overlay(watermark_text)
                watermark_pdf = PdfReader(watermark_packet)
                watermark_page = watermark_pdf.pages[0]
            
            for page in reader.pages:
                if watermark_page:
                    page.merge_page(watermark_page)
                writer.add_page(page)
            
            # Encrypt if password is provided
            if password:
                writer.encrypt(password)
            
            # Save the modified PDF to bytes
            output_packet = io.BytesIO()
            writer.write(output_packet)
            pdf_bytes = output_packet.getvalue()
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="converted.pdf"'
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

