from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.backend.pipeline import pipeline  # Ensure pipeline is correctly imported

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
        print(f"Received isColorization: {is_colorization}", flush=True)
        is_success = pipeline(is_colorization)
        print(f"Response answer: {is_success}", flush=True)
        if is_success:
            return GenerateResponse(is_success=True)
        else:
            return GenerateResponse(is_success=False)
    except Exception as e:
        print(f"Exception during pipeline execution: {e}", flush=True) 
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")