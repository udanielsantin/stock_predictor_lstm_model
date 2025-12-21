# 🚀 Quick Start - FastAPI Stock Predictor

## ⚡ 30 Segundos para Começar

### 1️⃣ Navegar para a pasta
```bash
cd /workspaces/stock_predictor_lstm_model
```

### 2️⃣ Iniciar a API
```bash
# Opção A: Desenvolvimento (com reload)
cd api
uvicorn app:app --reload

# Opção B: Usar o script launcher
chmod +x run_api.sh
./run_api.sh
# Escolha opção 1
```

### 3️⃣ Abrir no navegador
```
http://localhost:8000
```

### 4️⃣ Usar a aplicação
1. Digite um ticker: `ABEV3`
2. Escolha datas: `2024-01-01` a `2025-12-21`
3. Clique em **"🚀 Fazer Previsão"**
4. Veja o resultado com gráfico e métricas!

---

## 📚 Estrutura Criada

```
✅ api/app.py                    - FastAPI principal
✅ api/prediction_utils.py       - Funções de previsão
✅ api/templates/index.html      - Interface web
✅ API_README.md                 - Documentação técnica
✅ SETUP_COMPLETE.md             - Guia completo
✅ QUICK_START.md                - Este arquivo
```

---

## 🎯 Endpoints Disponíveis

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Abre a interface web |
| GET | `/health` | Health check |
| POST | `/api/predict` | Faz previsão |
| GET | `/api/info` | Info do modelo |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc |

---

## 💡 Exemplo de Requisição (curl)

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "ABEV3",
    "start_date": "2024-01-01",
    "end_date": "2025-12-21"
  }'
```

---

## 🐍 Exemplo em Python

```python
import requests

response = requests.post('http://localhost:8000/api/predict', json={
    'ticker': 'VALE3',
    'start_date': '2024-01-01',
    'end_date': '2025-12-21'
})

data = response.json()
print(f"Próximo preço: R$ {data['next_price']:.2f}")
print(f"R² Score: {data['metrics']['R2']:.4f}")
print(f"Gráfico: {data['plot'][:50]}...")  # base64 truncado
```

---

## 📊 Resposta da API

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
  "plot": "data:image/png;base64,iVBORw0K..."
}
```

---

## 🎨 Tela da Aplicação

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃        📈 Stock Price Predictor          ┃
┃  Utilize IA para prever preços de ações  ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                          ┃
┃  ┌──────────────────┐  ┌──────────────┐  ┃
┃  │  CONFIGURAÇÕES   │  │  RESULTADOS  │  ┃
┃  ├──────────────────┤  ├──────────────┤  ┃
┃  │ Ticker: ABEV3   │  │ 💰 Preço: R$ │  ┃
┃  │ De: 2024-01-01  │  │ 📊 Próximo:  │  ┃
┃  │ Até: 2025-12-21 │  │ 📈 Gráfico   │  ┃
┃  │                 │  │ 📋 Métricas  │  ┃
┃  │ 🚀 Prever       │  │ 📝 Resumo    │  ┃
┃  └──────────────────┘  └──────────────┘  ┃
┃                                          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## ⚙️ Requisitos

- ✅ Python 3.8+
- ✅ FastAPI
- ✅ PyTorch
- ✅ YFinance
- ✅ Scikit-learn
- ✅ Matplotlib

Todas as dependências estão em `requirements.txt`

---

## 🐳 Docker (Opcional)

```bash
docker-compose up
# Acesse: http://localhost:8000
```

---

## 📂 Arquivos Importantes

| Arquivo | Descrição |
|---------|-----------|
| `api/app.py` | Aplicação FastAPI com endpoints |
| `api/prediction_utils.py` | Funções de previsão e LSTM |
| `api/templates/index.html` | Interface web interativa |
| `models/stock_lstm.pt` | Modelo treinado |
| `models/scaler.joblib` | Normalizador de dados |

---

## 🆘 Problemas Comuns

### ❌ "ModuleNotFoundError: yfinance"
```bash
pip install yfinance
```

### ❌ "Porta 8000 já em uso"
```bash
uvicorn app:app --port 8001
```

### ❌ "Arquivo HTML não encontrado"
```bash
# Certifique-se que está em api/
cd api
uvicorn app:app --reload
```

### ❌ "Modelo não carregado"
- Verifique: `models/stock_lstm.pt` existe?
- Verifique: `models/scaler.joblib` existe?

---

## 🎓 Documentação Completa

Para mais detalhes, veja:
- **API_README.md** - Documentação técnica
- **SETUP_COMPLETE.md** - Guia de instalação
- **http://localhost:8000/docs** - Swagger (ao rodar)

---

## ✅ Checklist

- [ ] Python 3.8+ instalado
- [ ] Dependências instaladas
- [ ] Modelos em `models/`
- [ ] API em `api/`
- [ ] HTML em `api/templates/`
- [ ] FastAPI rodando ✅
- [ ] Navegador em `localhost:8000` ✅
- [ ] Teste com ABEV3 ✅

---

## 🎉 Pronto!

Você agora tem uma aplicação web completa para prever preços de ações com LSTM!

**Próximas ideias:**
- Adicionar mais tickers brasileiras
- Retreinar modelo com dados recentes
- Adicionar histórico de previsões
- Deploy em servidor real

---

**Versão:** 1.0.0  
**Última atualização:** Dezembro 2025  
**Status:** ✅ Pronto para usar
