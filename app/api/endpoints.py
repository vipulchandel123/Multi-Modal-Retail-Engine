from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel
from app.ml_models.predictor import predict_text_sentiment, predict_image_voids

router = APIRouter()

class SentimentRequest(BaseModel):
    text: str

@router.post("/predict/sentiment")
def analyze_sentiment(request: SentimentRequest):
    return predict_text_sentiment(request.text)

@router.post("/predict/voids")
async def detect_voids(file: UploadFile = File(...)):
    contents = await file.read()
    return predict_image_voids(contents)