from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.backend.pipeline import pipeline

app = FastAPI()

class GenerateMangaRequest(BaseModel):
    is_colorization: bool

class GenerateResponse(BaseModel):
    is_success: bool

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/generate-manga", response_model=GenerateResponse)
def get_response(data: GenerateMangaRequest):
    try:
        is_colorization = data.is_colorization
        print(f"Received isColorization: {data.is_colorization}")
        is_success = pipeline(is_colorization)
        print(f"Response answer: {is_success}")
        return GenerateResponse(
            is_success
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))