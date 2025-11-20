from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import PyPDF2
import io
import os
from dotenv import load_dotenv
from openai import OpenAI
import aiofiles

load_dotenv()

app = FastAPI(title="PDF Summarizer API")

# Configurazione CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inizializzazione client OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", 10)) * 1024 * 1024  # MB to bytes


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Estrae il testo da un file PDF."""
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Errore durante l'estrazione del testo: {str(e)}")


def generate_summary(text: str) -> str:
    """Genera un riassunto usando OpenAI GPT."""
    try:
        if len(text) > 15000:  # Limita il testo per evitare token eccessivi
            text = text[:15000] + "..."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sei un assistente che crea riassunti chiari, concisi e ben strutturati di documenti. Mantieni i punti chiave e le informazioni essenziali."},
                {"role": "user", "content": f"Riassumi il seguente testo in modo chiaro e conciso (massimo 300 parole):\n\n{text}"}
            ],
            temperature=0.5,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante la generazione del riassunto: {str(e)}")


@app.get("/")
async def root():
    return {"message": "PDF Summarizer API is running", "version": "1.0.0"}


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Endpoint per caricare un PDF e ottenere il riassunto."""
    
    # Validazione estensione file
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Solo file PDF sono accettati")
    
    # Leggi il contenuto del file
    contents = await file.read()
    
    # Validazione dimensione file
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"Il file supera la dimensione massima consentita di {MAX_FILE_SIZE // (1024*1024)} MB"
        )
    
    try:
        # Estrai testo dal PDF
        extracted_text = extract_text_from_pdf(contents)
        
        if not extracted_text or len(extracted_text.strip()) < 50:
            raise HTTPException(
                status_code=400, 
                detail="Il PDF non contiene testo sufficiente o è protetto"
            )
        
        # Genera riassunto
        summary = generate_summary(extracted_text)
        
        return JSONResponse(content={
            "success": True,
            "filename": file.filename,
            "extracted_text": extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text,
            "summary": summary,
            "text_length": len(extracted_text)
        })
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno del server: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)