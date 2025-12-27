from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import time
import os
from .prediction_utils import load_model_and_scaler, predict_stock
from .log_utils import PredictionLogger
from .dashboard_utils import (
    get_dashboard_data,
    create_ticker_distribution_chart,
    create_daily_predictions_chart,
    create_execution_time_chart,
    create_r2_distribution_chart
)

# ==================== LOAD MODEL ====================
MODEL_PATH = "/app/models/stock_lstm.pt"
SCALER_PATH = "/app/models/scaler.joblib"

try:
    model, scaler = load_model_and_scaler(MODEL_PATH, SCALER_PATH)
except Exception as e:
    print(f"Error loading model: {e}")
    model = None
    scaler = None

# ==================== LOGGER ====================
# S3-only logging - all logs are stored in S3
# Required env vars: S3_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
try:
    logger = PredictionLogger()
except ValueError as e:
    print(f"⚠️  Warning: {e}")
    print("Application will continue but logging will fail without S3 configuration")
    logger = None

# ==================== TEMPLATES ====================
templates = Jinja2Templates(directory="/app/api/templates")


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

# Mount static files
app.mount(
    "/static",
    StaticFiles(directory="/app/api/templates/static"),
    name="static"
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
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    """Retorna o dashboard de logs"""
    try:
        # Get dashboard data from S3
        data = get_dashboard_data()
        
        # Generate charts
        chart_ticker_distribution = create_ticker_distribution_chart(data)
        chart_daily_predictions = create_daily_predictions_chart(data)
        chart_execution_time = create_execution_time_chart(data)
        chart_r2_distribution = create_r2_distribution_chart(data)
        
        # Calculate success rate
        total = data["total_predictions"]
        success_rate = round((data["successful"] / total * 100), 1) if total > 0 else 0
        
        # Contexto passado para o template
        context = {
            "request": request,  # OBRIGATÓRIO para Jinja no FastAPI
            "total_predictions": data["total_predictions"],
            "successful": data["successful"],
            "failed": data["failed"],
            "success_rate": success_rate,
            "recent_logs": data["logs"][:10],
            "chart_ticker_distribution": chart_ticker_distribution,
            "chart_daily_predictions": chart_daily_predictions,
            "chart_execution_time": chart_execution_time,
            "chart_r2_distribution": chart_r2_distribution
        }
        
        return templates.TemplateResponse(
            "dashboard.html",
            context
        )
        
    except Exception as e:
        print(f"Error generating dashboard: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating dashboard: {str(e)}"
        )

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
        ticker: Símbolo da ação (ex: ABEV3, VALE3 para brasileiras ou MSFT, AAPL para internacionais)
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
        
        # Log the prediction
        if logger:
            try:
                log_info = logger.log_prediction(
                    ticker=request.ticker.upper(),
                    start_date=request.start_date,
                    end_date=request.end_date,
                    result=result,
                    duration=duration,
                    success=True
                )
            except Exception as log_err:
                print(f"⚠️  Warning: Failed to log prediction: {log_err}")
        
        return PredictionResponse(**result)
    
    except ValueError as e:
        # Log the error
        if logger:
            try:
                logger.log_prediction(
                    ticker=request.ticker.upper(),
                    start_date=request.start_date,
                    end_date=request.end_date,
                    result={},
                    duration=time.time() - start_time if 'start_time' in locals() else 0,
                    success=False,
                    error=str(e)
                )
            except Exception as log_err:
                print(f"⚠️  Warning: Failed to log error: {log_err}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # Log the error
        if logger:
            try:
                logger.log_prediction(
                    ticker=request.ticker.upper(),
                    start_date=request.start_date,
                    end_date=request.end_date,
                    result={},
                    duration=time.time() - start_time if 'start_time' in locals() else 0,
                    success=False,
                    error=str(e)
                )
            except Exception as log_err:
                print(f"⚠️  Warning: Failed to log error: {log_err}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"❌ Error: {e}")
        # Log the error
        if logger:
            try:
                logger.log_prediction(
                    ticker=request.ticker.upper(),
                    start_date=request.start_date,
                    end_date=request.end_date,
                    result={},
                    duration=time.time() - start_time if 'start_time' in locals() else 0,
                    success=False,
                    error=str(e)
                )
            except Exception as log_err:
                print(f"⚠️  Warning: Failed to log error: {log_err}")
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
        "target_market": "Global - Ações de qualquer mercado (IBOV, NYSE, NASDAQ, etc.)",
        "supported_tickers": "Brasileiras (.SA), Americanas (MSFT, AAPL), e outras",
        "version": "1.0.0"
    }

@app.get("/api/logs/recent")
def get_recent_logs(limit: int = 10):
    """
    Retorna logs recentes de previsões
    
    Args:
        limit: Número máximo de logs a retornar (padrão: 10)
    """
    try:
        if not logger:
            raise ValueError("Logger not configured. Please set S3_BUCKET_NAME environment variable.")
        logs = logger.get_recent_logs(limit=limit)
        return {
            "count": len(logs),
            "logs": logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving logs: {str(e)}")

@app.get("/api/logs/stats")
def get_log_stats():
    """Retorna estatísticas dos logs de previsões"""
    try:
        if not logger:
            raise ValueError("Logger not configured. Please set S3_BUCKET_NAME environment variable.")
        stats = logger.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")
