# 📈 Stock LSTM Predictor

Aplicação FastAPI para prever preços de ações brasileiras usando modelo LSTM neural.

> **Modelo LSTM treinado** com dados históricos de 1500+ dias | **Dashboard com logs** | **Deploy simples com Docker**

## 🚀 Quick Start

### 1. Local (5 min)

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cd api && uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Acesse: http://localhost:8000

### 2. Docker (3 min)

```bash
docker-compose up
```

Acesse: http://localhost:8000

### 3. EC2 (10 min)

```bash
# Na instância EC2
curl -fsSL https://get.docker.com | sh
git clone <seu-repo> && cd stock_predictor_lstm_model
docker-compose up -d
```

Acesse: http://seu-ip:8000

👉 **[Ver guia EC2 completo →](docs/EC2_DEPLOYMENT.md)**

## ✨ Features

✅ **Previsão LSTM** - Modelo neural com 2 camadas, 64 neurônios  
✅ **Dashboard** - Visualizações Matplotlib + logs em tempo real  
✅ **API REST** - FastAPI com Swagger docs automático  
✅ **Logs JSON** - Histórico de todas as previsões  
✅ **Docker** - Pronto para produção  
✅ **S3 Opcional** - Backup automático de logs  

## 📊 O que você obtém

| Endpoint | Descrição |
|----------|-----------|
| `GET /` | Interface web de previsões |
| `GET /dashboard` | Dashboard com 4 gráficos |
| `POST /api/predict` | Fazer previsão (JSON) |
| `GET /api/logs/recent` | Últimos 10 logs |
| `GET /api/logs/stats` | Estatísticas agregadas |
| `GET /docs` | Swagger UI (testes interativos) |
| `GET /health` | Status de saúde |

## 🗂️ Estrutura

```
api/                    ← Aplicação FastAPI
├── app.py             
├── prediction_utils.py
├── log_utils.py
├── dashboard_utils.py
├── templates/         ← HTML/CSS/JS separados
├── Dockerfile
└── logs/              ← Gerado automaticamente

models/                ← Modelos treinados
├── stock_lstm.pt
└── scaler.joblib

notebooks/             ← Treino e experimentos
data/                  ← Dados brutos
docs/                  ← Documentação

docker-compose.yml     ← Deploy 1 comando
requirements.txt
README.md
```

## 📖 Documentação

| Guia | Para... |
|------|---------|
| [EC2_DEPLOYMENT.md](docs/EC2_DEPLOYMENT.md) | Deploy em produção (AWS EC2) |
| [SETUP.md](docs/SETUP.md) | Setup local + desenvolvimento |
| [API_REFERENCE.md](docs/API_REFERENCE.md) | Todos os endpoints documentados |

## 🧪 Teste Rápido

```bash
# Request com curl
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "ABEV3",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }'

# Ou abra Swagger
http://localhost:8000/docs
```

## ⚙️ Configuração (Opcional)

### S3 Logs

Editar `api/.env`:
```bash
ENABLE_S3_LOGGING=True
S3_BUCKET_NAME=seu-bucket
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
```

## 🐛 Troubleshooting

```bash
# Ver logs do Docker
docker-compose logs -f

# Entrar no container
docker exec -it stock-lstm-api bash

# Restart
docker-compose restart
```

## 📊 Exemplo de Resposta

```json
{
  "ticker": "ABEV3",
  "current_price": 18.50,
  "predicted_price": 19.25,
  "confidence": 0.87,
  "r2_score": 0.92,
  "execution_time_ms": 234,
  "timestamp": "2024-12-20T15:30:45.123Z"
}
```

## 🚀 Próximos Passos

1. Clone e rode local ✅
2. Explore `/dashboard` ✅
3. Teste `/docs` (Swagger)
4. Deploy em EC2 (veja [EC2_DEPLOYMENT.md](docs/EC2_DEPLOYMENT.md))

---

**Pronto para usar! 🎉**
