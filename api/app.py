from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from src.model_utils import load_artifacts, predict_next
import time

app = FastAPI(title="Stock LSTM Predictor")

class PredictRequest(BaseModel):
    close_prices: list  # raw close prices, most recent last
    window: int = 50

class PredictResponse(BaseModel):
    predicted_next_price: float
    duration_ms: float

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    start = time.time()
    model, scaler = load_artifacts()
    # scale input
    arr = np.array(req.close_prices, dtype=np.float32).reshape(-1, 1)
    scaled = scaler.transform(arr)
    if len(scaled) < req.window:
        raise ValueError(f"Need at least {req.window} points, got {len(scaled)}")
    seq = scaled[-req.window:]
    pred = predict_next(model, scaler, seq)
    dur = (time.time() - start) * 1000.0
    return PredictResponse(predicted_next_price=pred, duration_ms=dur)
