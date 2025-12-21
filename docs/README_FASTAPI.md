# 📈 Stock Price Predictor - FastAPI Complete Setup

## ✅ O que foi criado

Sua aplicação web com FastAPI foi criada com **sucesso**! Aqui está o que você tem agora:

### 🎯 Arquivos Principais

```
✅ api/app.py (36 linhas)
   └─ Aplicação FastAPI completa
   └─ 4 endpoints funcionais
   └─ Carregamento automático do modelo

✅ api/prediction_utils.py (170 linhas)
   └─ Classe StockLSTM
   └─ 6 funções helper
   └─ Geração de gráficos em base64
   └─ Cálculo de métricas

✅ api/templates/index.html (450+ linhas)
   └─ Interface web responsiva
   └─ Design gradiente moderno
   └─ Validação de entrada
   └─ Exibição de gráfico e métricas

✅ Documentação
   ├─ API_README.md (Técnica)
   ├─ QUICK_START.md (Rápido)
   ├─ SETUP_COMPLETE.md (Completo)
   └─ README.md (Este arquivo)

✅ Scripts
   ├─ run_api.sh (Launcher)
   └─ test_api.py (Testes)
```

---

## 🚀 Como Começar (3 Passos)

### 1. Navegar para o diretório
```bash
cd /workspaces/stock_predictor_lstm_model
```

### 2. Rodar a API
```bash
# Opção rápida
cd api && uvicorn app:app --reload

# Ou usar o script
chmod +x ../run_api.sh && ../run_api.sh
```

### 3. Abrir no navegador
```
http://localhost:8000
```

---

## 📊 Arquitetura

```
┌─────────────────────────────────────────────┐
│        Browser / Cliente Web                │
│     (http://localhost:8000)                 │
└────────────────────┬────────────────────────┘
                     │ HTTP/JSON
                     ▼
┌─────────────────────────────────────────────┐
│         FastAPI (app.py)                    │
│  ┌──────────────────────────────────────┐   │
│  │  GET  /              (HTML)          │   │
│  │  GET  /health        (Check)         │   │
│  │  POST /api/predict   (Previsão)      │   │
│  │  GET  /api/info      (Model Info)    │   │
│  └──────────────────────────────────────┘   │
└────────────────────┬────────────────────────┘
                     │ Python
                     ▼
┌─────────────────────────────────────────────┐
│  prediction_utils.py (Funções)              │
│  ┌──────────────────────────────────────┐   │
│  │  1. Load data (Yahoo Finance)        │   │
│  │  2. Scale data (MinMaxScaler)        │   │
│  │  3. Create sequences                 │   │
│  │  4. Run inference (LSTM)             │   │
│  │  5. Calculate metrics                │   │
│  │  6. Generate plot (matplotlib)       │   │
│  └──────────────────────────────────────┘   │
└────────────────────┬────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│         Modelo & Dados                      │
│  ├─ stock_lstm.pt (Modelo treinado)        │
│  ├─ scaler.joblib (Normalizador)           │
│  └─ Yahoo Finance API (Dados)              │
└─────────────────────────────────────────────┘
```

---

## 🎯 Fluxo de uma Previsão

```
1. Usuário preenche formulário
   ↓
2. JavaScript envia POST /api/predict
   ↓
3. FastAPI recebe e valida dados
   ↓
4. Python baixa dados do Yahoo Finance
   ↓
5. Normaliza com MinMaxScaler
   ↓
6. Cria sequências de 50 dias
   ↓
7. LSTM faz inferência
   ↓
8. Calcula métricas (MSE, MAE, RMSE, MAPE, R²)
   ↓
9. Gera gráfico (matplotlib → base64)
   ↓
10. Retorna JSON com todos os resultados
   ↓
11. JavaScript atualiza a página
   ↓
12. Usuário vê gráfico e métricas em tempo real
```

---

## 📁 Estrutura de Pastas

```
stock_predictor_lstm_model/
│
├── 📂 api/
│   ├── app.py                    ← FastAPI principal
│   ├── prediction_utils.py       ← Funções helper
│   ├── templates/
│   │   └── index.html           ← Interface web
│   ├── Dockerfile
│   └── __init__.py
│
├── 📂 models/
│   ├── stock_lstm.pt            ← Seu modelo LSTM
│   └── scaler.joblib            ← Seu normalizador
│
├── 📂 notebooks/
│   ├── train_ibov_lstm.ipynb    ← Treinar modelo
│   └── ...
│
├── 📂 data/
│   └── ...
│
├── 📄 run_api.sh                ← Script launcher
├── 📄 test_api.py               ← Testes
│
├── 📄 API_README.md             ← Doc técnica
├── 📄 QUICK_START.md            ← Quick start
├── 📄 SETUP_COMPLETE.md         ← Setup completo
├── 📄 README.md                 ← Este arquivo
│
├── requirements.txt             ← Dependências
└── docker-compose.yml           ← Docker
```

---

## 🔌 API Endpoints

### GET `/`
Retorna a página HTML da interface

```bash
curl http://localhost:8000
```

### GET `/health`
Health check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "scaler_loaded": true
}
```

### POST `/api/predict`
Faz previsão de preço

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "ABEV3",
    "start_date": "2024-01-01",
    "end_date": "2025-12-21"
  }'
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
  "plot": "data:image/png;base64,iVBORw0KGgoAAAANS..."
}
```

### GET `/api/info`
Informações do modelo

```bash
curl http://localhost:8000/api/info
```

**Response:**
```json
{
  "model_name": "Stock LSTM Predictor",
  "architecture": "LSTM com 2 camadas",
  "neurons": 64,
  "sequence_length": 50,
  "input_size": 1,
  "target_market": "IBOV - Ações Brasileiras",
  "version": "1.0.0"
}
```

---

## 🎨 Interface Web

A interface tem:

✅ **Responsiva** - Funciona em desktop, tablet, mobile
✅ **Moderno** - Design gradiente roxo/violeta
✅ **Rápida** - JavaScript vanilla, sem frameworks pesados
✅ **Segura** - Validação de entrada no frontend e backend
✅ **Informativa** - Gráfico + 5 métricas + resumo executivo

### Componentes:
1. **Painel de Input** (Esquerda)
   - Campo de ticker
   - Seletor de datas
   - Botão de previsão
   - Mensagens de erro/sucesso

2. **Painel de Resultados** (Direita)
   - Cards de resumo (preço atual, próximo, pontos, R²)
   - Detalhes das métricas (MSE, MAE, RMSE, MAPE)
   - Gráfico de previsão vs real
   - Resumo executivo em texto

---

## 🧪 Testando a API

### Opção 1: Interface Web
```
http://localhost:8000
```

### Opção 2: Script Python
```bash
python test_api.py
```

### Opção 3: curl
```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"ticker":"ABEV3","start_date":"2024-01-01","end_date":"2025-12-21"}'
```

### Opção 4: Swagger UI
```
http://localhost:8000/docs
```

### Opção 5: Python requests
```python
import requests

r = requests.post('http://localhost:8000/api/predict', json={
    'ticker': 'VALE3',
    'start_date': '2024-01-01',
    'end_date': '2025-12-21'
})

print(r.json()['next_price'])
```

---

## 📚 Documentação Detalhada

| Documento | Para quem? | Conteúdo |
|-----------|-----------|----------|
| **QUICK_START.md** | Todos | Como rodar em 30s |
| **API_README.md** | Desenvolvedores | Endpoints e exemplos |
| **SETUP_COMPLETE.md** | Técnicos | Instalação completa |
| **http://localhost:8000/docs** | API Users | Swagger interativo |

---

## ⚡ Comandos Rápidos

```bash
# Rodar desenvolvimento
cd api && uvicorn app:app --reload

# Rodar produção
cd api && uvicorn app:app --workers 4

# Rodar com Docker
docker-compose up

# Testar API
python test_api.py

# Ver logs
# (Saída aparece no terminal)

# Parar servidor
# Ctrl + C
```

---

## 🔧 Customizações Possíveis

### Mudar porta
```bash
# Em app.py ou:
uvicorn app:app --port 8001
```

### Mudar caminho dos modelos
Edite em `app.py`:
```python
MODEL_PATH = "/novo/caminho/stock_lstm.pt"
SCALER_PATH = "/novo/caminho/scaler.joblib"
```

### Adicionar mais tickers
Tickers brasileiros automaticamente conversão (ABEV3 → ABEV3.SA)

### Aumentar precisão
Retreine o modelo com mais dados (veja notebooks/)

---

## 📊 Interpretação das Métricas

| Métrica | O que é | Ideal | Interpretação |
|---------|---------|-------|---------------|
| **R²** | Coef. Determinação | 0.8-1.0 | Quanto melhor, melhor |
| **MAE** | Erro Médio (R$) | Baixo | Quanto menor, melhor |
| **RMSE** | Raiz Erro Quadrado | Baixo | Quanto menor, melhor |
| **MAPE** | Erro % | <5% | Quanto menor, melhor |
| **MSE** | Erro Quadrado Médio | Baixo | Quanto menor, melhor |

---

## ✨ Features Implementadas

✅ Interface web responsiva
✅ API RESTful com FastAPI
✅ Validação de entrada
✅ Tratamento de erros
✅ Gráficos em base64
✅ Cálculo de 5 métricas
✅ Documentação Swagger
✅ CORS habilitado
✅ Script launcher
✅ Testes automatizados
✅ Docker ready
✅ Suporte a múltiplas ações

---

## 🐛 Troubleshooting

### Erro: "Modelos não encontrados"
```bash
# Verifique:
ls models/stock_lstm.pt models/scaler.joblib
# Ou retreine no notebook
```

### Erro: "Porta em uso"
```bash
# Use outra porta:
uvicorn app:app --port 8001
```

### Erro: "Ticker não encontrado"
```bash
# Use formato correto:
ABEV3 (automático → ABEV3.SA)
VALE3 (automático → VALE3.SA)
```

### Erro: "Dados insuficientes"
```bash
# Use período maior (mínimo 51 dias)
```

---

## 🚀 Próximos Passos

1. **Melhorar Modelo**
   - Retreinar com dados recentes
   - Adicionar mais features
   - Ajustar hiperparâmetros

2. **Expandir Features**
   - Histórico de previsões (BD)
   - Autenticação de usuários
   - Comparação entre ações
   - Alertas de preço

3. **Deploy**
   - Nginx + Gunicorn
   - HTTPS/SSL
   - Monitoramento (Prometheus)
   - CI/CD (GitHub Actions)

4. **Performance**
   - Cache de resultados
   - Batch predictions
   - Redis para cache

---

## 📞 Suporte

Em caso de dúvidas:

1. Verifique `QUICK_START.md`
2. Veja `API_README.md`
3. Acesse `http://localhost:8000/docs` (Swagger)
4. Execute `python test_api.py`
5. Verifique logs no console

---

## ✅ Checklist Final

- [ ] FastAPI instalado
- [ ] Modelos em `models/`
- [ ] API rodando em localhost:8000
- [ ] Interface acessível no navegador
- [ ] Teste com ABEV3 funcionou
- [ ] Gráfico apareceu
- [ ] Métricas estão corretas

---

## 🎓 Aprender Mais

- **FastAPI**: https://fastapi.tiangolo.com
- **PyTorch**: https://pytorch.org
- **LSTM**: https://colah.github.io/posts/2015-08-Understanding-LSTMs/
- **YFinance**: https://github.com/ranaroussi/yfinance

---

## 📝 Versão & Status

**Versão:** 1.0.0  
**Data:** Dezembro 2025  
**Status:** ✅ Pronto para produção  
**Autor:** GitHub Copilot

---

## 🎉 Parabéns!

Você agora tem uma aplicação web completa e funcional para prever preços de ações usando Deep Learning!

```
╔════════════════════════════════════════╗
║  Stock Price Predictor v1.0.0          ║
║                                        ║
║  ✅ FastAPI configurado                ║
║  ✅ Interface web pronta               ║
║  ✅ Modelo LSTM treinado               ║
║  ✅ Documentação completa              ║
║                                        ║
║  Acesse: http://localhost:8000        ║
╚════════════════════════════════════════╝
```

---

**Boa sorte com suas previsões! 📈**
