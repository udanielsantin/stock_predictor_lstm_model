# Setup Local e Desenvolvimento

Guia para configurar o ambiente local e entender a estrutura do projeto.

## 1. Pré-requisitos

- Python 3.9+
- pip
- Git
- (Opcional) Docker + Docker Compose

## 2. Setup Virtual Environment

```bash
# Clone repo
git clone https://github.com/seu-usuario/stock_predictor_lstm_model.git
cd stock_predictor_lstm_model

# Virtual environment
python3 -m venv venv

# Ativar
# Linux/Mac
source venv/bin/activate
# Windows
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

## 3. Verificar Arquivos do Modelo

A aplicação espera estes arquivos em `models/`:

```bash
ls -la models/
# stock_lstm.pt (modelo PyTorch)
# scaler.joblib (normalizador)
```

Se faltarem:
```bash
# Baixar via git LFS (se estiverem no repositório)
git lfs pull

# Ou treinar modelo (veja notebooks/)
cd notebooks
jupyter notebook train_ibov_lstm.ipynb
```

## 4. Rodar Localmente

### FastAPI (Recomendado)

```bash
cd api
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Acesse:
- http://localhost:8000 (Interface)
- http://localhost:8000/docs (Swagger API)
- http://localhost:8000/dashboard (Dashboard)

### Streamlit (Alternativo)

```bash
streamlit run streamlit_app.py
```

Acesse: http://localhost:8501

## 5. Testar API

```bash
# Terminal 1: Rodar servidor
cd api && uvicorn app:app --reload

# Terminal 2: Fazer request
python test_api.py

# Ou com curl
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "ABEV3",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }'
```

## 6. Estrutura de Pastas

```
stock_predictor_lstm_model/
│
├── api/                         # Aplicação FastAPI
│   ├── app.py                  # Rotas e configuração
│   ├── prediction_utils.py     # Lógica de previsão
│   ├── log_utils.py            # Sistema de logs
│   ├── dashboard_utils.py      # Gráficos do dashboard
│   ├── templates/              # HTML/CSS/JS
│   │   ├── index.html
│   │   ├── dashboard.html
│   │   └── static/
│   │       ├── css/style.css
│   │       └── js/script.js
│   ├── logs/                   # Logs JSON (gerado em runtime)
│   ├── Dockerfile
│   └── .env.example
│
├── models/                      # Modelos treinados
│   ├── stock_lstm.pt           # Modelo PyTorch
│   └── scaler.joblib           # Scaler sklearn
│
├── notebooks/                   # Jupyter notebooks
│   ├── train_ibov_lstm.ipynb   # Treino principal
│   ├── stock_predition_model.ipynb
│   ├── Light_plus_torch_LSTM.ipynb
│   ├── by_hand_model.ipynb
│   └── artifacts/              # Outputs dos notebooks
│
├── data/                        # Dados
│   ├── data.py                 # Funções de dados
│   └── ibov_tickers.csv
│
├── src/                         # Código auxiliar
│   └── model_utils.py
│
├── docs/                        # Documentação
│   ├── EC2_DEPLOYMENT.md
│   ├── SETUP.md
│   ├── API_REFERENCE.md
│   └── FILE_STRUCTURE.txt
│
├── docker-compose.yml           # Orquestração Docker
├── requirements.txt             # Dependências Python
├── README.md                    # Documento principal
└── .env.example                 # Variáveis de ambiente
```

## 7. Arquivo requirements.txt

Principais dependências:

```
fastapi==0.104.1
uvicorn==0.24.0
torch==2.1.2
numpy==1.24.3
joblib==1.3.2
yfinance==0.2.32
matplotlib==3.8.2
scikit-learn==1.3.2
python-multipart==0.0.6
jinja2==3.1.2
boto3==1.28.85  # AWS S3 (opcional)
```

Instalar tudo:
```bash
pip install -r requirements.txt
```

## 8. Variáveis de Ambiente

Copiar `.env.example` para `api/.env`:

```bash
cp api/.env.example api/.env
```

Editar conforme necessário:

```env
# Aplicação
PORT=8000
DEBUG=False

# AWS S3 (opcional)
ENABLE_S3_LOGGING=False
S3_BUCKET_NAME=seu-bucket
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=sua-chave
AWS_SECRET_ACCESS_KEY=seu-secret
```

## 9. Docker Localmente

```bash
# Build
docker-compose build

# Run
docker-compose up

# Parar
docker-compose down

# Logs
docker-compose logs -f
```

Aplicação em: http://localhost:8000

## 10. Desenvolvimento

### Adicionar Endpoint

Editar `api/app.py`:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/meu-endpoint")
async def meu_endpoint():
    return {"mensagem": "Hello"}
```

Reload automático com `--reload` em `uvicorn`.

### Adicionar Modulo Python

```bash
# Novo arquivo em api/ ou src/
# Importar normalmente em app.py

from prediction_utils import get_prediction
```

### Treinar Novo Modelo

```bash
cd notebooks
jupyter notebook train_ibov_lstm.ipynb

# Copiar arquivos de output
cp artifacts/stock_lstm.pt ../models/
cp artifacts/scaler.joblib ../models/
```

## 11. Git e Versionamento

```bash
# Staged
git add .

# Commit
git commit -m "Descricao da mudanca"

# Push
git push origin main

# Arquivos a ignorar (.gitignore já existente):
# __pycache__/, venv/, .env, *.pt, *.joblib, logs/
```

## 12. Troubleshooting Local

### Módulo não encontrado
```bash
# Verificar venv ativado
which python  # Deve conter "venv"

# Reinstalar deps
pip install -r requirements.txt
```

### Erro de modelo
```bash
# Verificar arquivo existe
ls -la models/stock_lstm.pt
ls -la models/scaler.joblib

# Ou baixar via LFS
git lfs pull
```

### Porta 8000 em uso
```bash
# Kill processo
lsof -i :8000
kill -9 PID
```

### Hot reload não funciona
```bash
# Reiniciar manualmente
Ctrl+C
uvicorn app:app --reload
```

## 13. Próximas Etapas

- [ ] Venv configurado e rodando
- [ ] Dependências instaladas
- [ ] Modelos carregados
- [ ] API rodando em localhost:8000
- [ ] Testes passando
- [ ] Ready para deploy! 🚀

---

**Pronto para desenvolver! 💻**
