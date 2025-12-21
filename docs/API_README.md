# 🚀 FastAPI Stock Predictor

API em FastAPI para previsão de preços de ações usando modelo LSTM.

## 📁 Estrutura

```
api/
├── app.py                    # Aplicação FastAPI principal
├── prediction_utils.py       # Funções helper para previsão
├── templates/
│   └── index.html           # Interface web
└── Dockerfile
```

## ⚙️ Instalação

As dependências devem estar no `requirements.txt` raiz do projeto:

```bash
pip install fastapi uvicorn torch yfinance scikit-learn joblib matplotlib
```

## 🎯 Como Rodar

### Opção 1: Desenvolvimento Local

```bash
cd api
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Acesse: `http://localhost:8000`

### Opção 2: Produção

```bash
cd api
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Opção 3: Docker

```bash
docker build -t stock-predictor .
docker run -p 8000:8000 stock-predictor
```

## 📚 Estrutura da API

### Endpoints

#### `GET /`
Retorna a página HTML da interface web.

#### `GET /health`
Health check da API.

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "scaler_loaded": true
}
```

#### `POST /api/predict`
Faz previsão de preço de ação.

**Request:**
```json
{
  "ticker": "ABEV3",
  "start_date": "2024-01-01",
  "end_date": "2025-12-21"
}
```

**Response:**
```json
{
  "ticker": "ABEV3",
  "start_date": "2024-01-01",
  "end_date": "2025-12-21",
  "last_close": 12.50,
  "next_price": 12.75,
  "price_change": 0.25,
  "price_change_pct": 2.00,
  "metrics": {
    "MSE": 0.123456,
    "MAE": 0.234567,
    "RMSE": 0.351234,
    "MAPE": 1.95,
    "R2": 0.8567
  },
  "data_points": 350,
  "plot": "data:image/png;base64,..."
}
```

#### `GET /api/info`
Informações sobre o modelo.

## 🔧 Estrutura do Arquivo `prediction_utils.py`

Contém todas as funções auxiliares:

### Classes
- **`StockLSTM`** - Modelo LSTM PyTorch

### Funções
- **`load_model_and_scaler(model_path, scaler_path)`** - Carrega modelo e scaler
- **`load_stock_data(ticker, start, end)`** - Baixa dados do Yahoo Finance
- **`create_sequences(data, seq_length)`** - Cria sequências para LSTM
- **`generate_plot_base64(y_true, y_pred, ticker, start, end)`** - Gera gráfico em base64
- **`predict_stock(ticker, start_date, end_date, model, scaler)`** - Faz previsão completa

## 📊 Fluxo da Previsão

1. **Recebe requisição POST** com ticker e datas
2. **Valida datas** (inicial < final)
3. **Carrega dados** do Yahoo Finance
4. **Normaliza dados** com MinMaxScaler
5. **Cria sequências** de 50 dias
6. **Faz previsões** com o modelo LSTM
7. **Calcula métricas** (MSE, MAE, RMSE, MAPE, R²)
8. **Gera gráfico** (PNG em base64)
9. **Retorna resultado** como JSON

## 🎯 Interpretação das Métricas

- **R²**: Coeficiente de determinação (0-1, maior é melhor)
- **MAE**: Erro médio em R$ entre previsão e real
- **MAPE**: Erro percentual médio
- **RMSE**: Raiz do erro quadrático médio

## 📝 Exemplo de Uso com curl

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "ABEV3",
    "start_date": "2024-01-01",
    "end_date": "2025-12-21"
  }'
```

## 🐍 Exemplo de Uso com Python

```python
import requests

url = "http://localhost:8000/api/predict"
data = {
    "ticker": "VALE3",
    "start_date": "2024-01-01",
    "end_date": "2025-12-21"
}

response = requests.post(url, json=data)
result = response.json()

print(f"Próximo preço: R$ {result['next_price']:.2f}")
print(f"R² Score: {result['metrics']['R2']:.4f}")
```

## 🔍 Variáveis de Caminho

As paths dos arquivos de modelo estão hardcoded em `app.py`:
- Model: `/workspaces/stock_predictor_lstm_model/models/stock_lstm.pt`
- Scaler: `/workspaces/stock_predictor_lstm_model/models/scaler.joblib`

Se precisar mudar, edite as linhas no `app.py`:
```python
MODEL_PATH = "/seu/caminho/stock_lstm.pt"
SCALER_PATH = "/seu/caminho/scaler.joblib"
```

## 📖 Documentação Interativa

FastAPI gera documentação automática:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## ⚠️ Tratamento de Erros

- **400**: Dados insuficientes, datas inválidas, ticker não encontrado
- **500**: Modelo não carregado, erro interno

Todos os erros retornam com detalhes úteis:
```json
{
  "detail": "Mensagem de erro específica"
}
```

## 🚀 Deployment

Para produção recomenda-se usar:
- **Gunicorn**: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app`
- **Nginx**: Como reverse proxy
- **Docker Compose**: Com PostgreSQL/Redis se necessário

## 📞 Suporte

Para dúvidas sobre a API, verifique:
1. `http://localhost:8000/docs` (Documentação Swagger)
2. Logs do console (`--log-level debug`)
3. Verificar se modelo está carregado: `GET /health`
