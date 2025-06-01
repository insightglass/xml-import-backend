print("✅ app/main.py loaded at startup")

from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.xml_parser import parse_xml_and_push_to_monday
from app.monday_sync import push_to_monday_quotes_board

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-xml/")
async def upload_xml(file: UploadFile, vendor: str = Form(...), markup: float = Form(...), job_number: str = Form(...)):
    file_bytes = await file.read()
    result = parse_xml_and_push_to_monday(file_bytes, vendor, markup, job_number)
    print("🧪 Reached sync trigger in main.py")
    push_to_monday_quotes_board(result)
    return JSONResponse(content=result)
