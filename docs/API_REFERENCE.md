# API Reference

Documentação completa dos endpoints da API.

## Base URL

```
http://localhost:8000          # Local
http://seu-ip:8000            # EC2
https://seu-dominio.com       # Com SSL
```

## Health Check

### GET `/health`

Verifica saúde da aplicação e se modelo está carregado.

**Response (200):**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "scaler_loaded": true,
  "version": "1.0.0"
}
```

---

## Previsão

### POST `/api/predict`

Fazer previsão de preço para uma ação.

**Request Body:**
```json
{
  "ticker": "ABEV3",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

**Parameters:**
- `ticker` (string, required): Código da ação (ex: ABEV3, VALE5)
- `start_date` (string, required): Data inicial (YYYY-MM-DD)
- `end_date` (string, required): Data final (YYYY-MM-DD)

**Response (200):**
```json
{
  "ticker": "ABEV3",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "current_price": 18.50,
  "predicted_price": 19.25,
  "confidence": 0.87,
  "volatility": 0.025,
  "r2_score": 0.92,
  "mae": 0.45,
  "execution_time_ms": 234,
  "chart": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "timestamp": "2024-12-20T15:30:45.123Z"
}
```

**Response (400):**
```json
{
  "detail": "Erro: ticker não encontrado ou datas inválidas"
}
```

**Response (500):**
```json
{
  "detail": "Erro interno ao processar previsão"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "ABEV3",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }'
```

**Python Example:**
```python
import requests
import json

url = "http://localhost:8000/api/predict"
payload = {
    "ticker": "ABEV3",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
}

response = requests.post(url, json=payload)
print(response.json())
```

---

## Logs

### GET `/api/logs/recent`

Últimos logs de previsões.

**Query Parameters:**
- `limit` (int, default: 10): Quantidade de logs

**Response (200):**
```json
{
  "total": 42,
  "limit": 10,
  "logs": [
    {
      "timestamp": "2024-12-20T15:30:45.123Z",
      "ticker": "ABEV3",
      "predicted_price": 19.25,
      "r2_score": 0.92,
      "execution_time_ms": 234
    },
    ...
  ]
}
```

**cURL Example:**
```bash
curl http://localhost:8000/api/logs/recent?limit=20
```

---

### GET `/api/logs/stats`

Estatísticas agregadas dos logs.

**Response (200):**
```json
{
  "total_predictions": 42,
  "unique_tickers": 8,
  "avg_r2_score": 0.88,
  "avg_execution_time_ms": 245,
  "success_rate": 0.95,
  "last_prediction": "2024-12-20T15:30:45.123Z",
  "predictions_today": 5,
  "predictions_this_week": 23,
  "predictions_this_month": 42
}
```

**cURL Example:**
```bash
curl http://localhost:8000/api/logs/stats
```

---

### GET `/api/logs/ticker/{ticker}`

Logs específicos de uma ação.

**Path Parameters:**
- `ticker` (string): Código da ação

**Query Parameters:**
- `limit` (int, default: 10): Quantidade de logs

**Response (200):**
```json
{
  "ticker": "ABEV3",
  "total_predictions": 5,
  "avg_r2_score": 0.89,
  "logs": [...]
}
```

**cURL Example:**
```bash
curl http://localhost:8000/api/logs/ticker/ABEV3?limit=5
```

---

## Info

### GET `/api/info`

Informações sobre o modelo.

**Response (200):**
```json
{
  "model_type": "LSTM",
  "framework": "PyTorch",
  "input_sequence_length": 50,
  "total_parameters": 145920,
  "hidden_size": 64,
  "num_layers": 2,
  "training_date": "2024-11-15",
  "training_data_points": 1500,
  "supported_tickers": ["ABEV3", "BBDC4", "BBAS3", "VALE5", ...],
  "model_file_size_mb": 1.2
}
```

**cURL Example:**
```bash
curl http://localhost:8000/api/info
```

---

## Web Interface

### GET `/`

Página principal com interface de previsão.

### GET `/dashboard`

Dashboard com visualizações e logs.

### GET `/docs`

Documentação interativa Swagger (auto-gerada por FastAPI).

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Requisição bem-sucedida |
| 400 | Bad Request - Parâmetros inválidos |
| 404 | Not Found - Recurso não encontrado |
| 500 | Internal Server Error - Erro do servidor |

---

## Rate Limiting

Não há rate limiting configurado, mas é recomendado não fazer >10 requisições/segundo.

---

## Autenticação

Sem autenticação (aberto). Para produção, considere adicionar:

```python
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.get("/api/predict")
async def predict(credentials: HTTPAuthCredentials = Depends(security)):
    token = credentials.credentials
    # Validar token
    ...
```

---

## CORS

CORS habilitado para todos os origins. Personalizar em `api/app.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://seu-dominio.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## WebSocket (Futuro)

Para atualizações em tempo real:

```python
@app.websocket("/ws/predict")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Streaming de previsões
```

---

## Swagger Playground

Abra http://localhost:8000/docs para testar todos os endpoints interativamente.

---

**API pronta! 🚀**
