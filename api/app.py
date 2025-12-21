from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import time
import os
from prediction_utils import load_model_and_scaler, predict_stock

# ==================== LOAD MODEL ====================
MODEL_PATH = "/workspaces/stock_predictor_lstm_model/models/stock_lstm.pt"
SCALER_PATH = "/workspaces/stock_predictor_lstm_model/models/scaler.joblib"

try:
    model, scaler = load_model_and_scaler(MODEL_PATH, SCALER_PATH)
except Exception as e:
    print(f"Error loading model: {e}")
    model = None
    scaler = None

# ==================== FASTAPI APP ====================
app = FastAPI(
    title="Stock LSTM Predictor",
    description="API para previsão de preços de ações usando LSTM",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== REQUEST/RESPONSE MODELS ====================
class PredictionRequest(BaseModel):
    ticker: str
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD

class PredictionResponse(BaseModel):
    ticker: str
    start_date: str
    end_date: str
    last_close: float
    next_price: float
    price_change: float
    price_change_pct: float
    metrics: dict
    data_points: int
    plot: str

# ==================== ENDPOINTS ====================
@app.get("/")
def root():
    """Retorna o arquivo HTML da interface"""
    return FileResponse("templates/index.html")

@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "scaler_loaded": scaler is not None
    }

@app.post("/api/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """
    Faz previsão de preço de ação
    
    Args:
        ticker: Símbolo da ação (ex: ABEV3, VALE3)
        start_date: Data inicial (YYYY-MM-DD)
        end_date: Data final (YYYY-MM-DD)
    
    Returns:
        PredictionResponse com resultados e gráfico
    """
    
    if model is None or scaler is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Validate dates
        if request.start_date >= request.end_date:
            raise HTTPException(
                status_code=400,
                detail="Data inicial deve ser anterior à data final"
            )
        
        # Make prediction
        start_time = time.time()
        result = predict_stock(
            ticker=request.ticker.upper(),
            start_date=request.start_date,
            end_date=request.end_date,
            model=model,
            scaler=scaler
        )
        duration = time.time() - start_time
        
        print(f"✅ Prediction completed in {duration:.2f}s")
        
        return PredictionResponse(**result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/info")
def info():
    """Retorna informações sobre o modelo"""
    return {
        "model_name": "Stock LSTM Predictor",
        "architecture": "LSTM com 2 camadas",
        "neurons": 64,
        "sequence_length": 50,
        "input_size": 1,
        "target_market": "IBOV - Ações Brasileiras",
        "version": "1.0.0"
    }
