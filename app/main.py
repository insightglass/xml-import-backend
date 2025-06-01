from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Literal
from .xml_parser import parse_xml_and_push_to_monday

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-xml/")
async def upload_xml(
    file: UploadFile,
    vendor: Literal["Amsco", "Andersen", "Milgard"] = Form(...),
    markup: float = Form(...),
    job_number: str = Form(...)
):
    content = await file.read()
    result = parse_xml_and_push_to_monday(content, vendor, markup, job_number)
    return {"status": "success", "details": result}
