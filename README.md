# Stock Predictor LSTM (FastAPI)

Aplicação web para prever preços de ações usando um modelo LSTM treinado.

## Requisitos
- Python 3.8+
- Dependências: `pip install -r requirements.txt`
- Artefatos do modelo: `models/stock_lstm.pt` e `models/scaler.joblib`

## Como rodar
```bash
cd /workspaces/stock_predictor_lstm_model
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd api
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```
Acesse:
- Site: http://localhost:8000
- Docs: http://localhost:8000/docs

## Endpoints principais
- `GET /` – página web
- `GET /health` – status e carregamento do modelo
- `POST /api/predict` – previsão com métricas e gráfico base64
- `GET /api/info` – informações do modelo

## Estrutura do projeto
- api/ → app FastAPI (`app.py`), funções (`prediction_utils.py`), HTML (`templates/index.html`)
- models/ → artefatos treinados (modelo e scaler)
- data/, notebooks/, src/ → código e dados de treino
- docs/ → documentação detalhada
- run_api.sh, test_api.py → utilitários (opcional)
- streamlit_app.py → app Streamlit opcional

## Documentação extra
Consulte a pasta docs/ para guias detalhados (quick start, referências e diagrama de pastas).
