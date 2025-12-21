# 🎉 Stock Price Predictor - FastAPI Web App

Sua aplicação web FastAPI foi criada com sucesso! 

## 📋 Arquivos Criados/Modificados

### 1. **API Principal**
- **`api/app.py`** ✅ 
  - Aplicação FastAPI completa
  - Endpoints: `/`, `/health`, `/api/predict`, `/api/info`
  - CORS habilitado
  - Carrega modelo ao iniciar

### 2. **Funções Auxiliares** 
- **`api/prediction_utils.py`** ✅ (Novo)
  - `StockLSTM` - Classe do modelo
  - `load_model_and_scaler()` - Carrega artifacts
  - `load_stock_data()` - Baixa dados Yahoo Finance
  - `create_sequences()` - Cria sequências para LSTM
  - `generate_plot_base64()` - Gera gráfico em base64
  - `predict_stock()` - Função principal de previsão

### 3. **Interface Web**
- **`api/templates/index.html`** ✅ (Novo)
  - Interface responsiva (desktop/mobile)
  - Design moderno com gradiente
  - Validação de formulário
  - Exibe gráfico e métricas
  - JavaScript vanilla (sem dependências)

### 4. **Documentação**
- **`API_README.md`** ✅ (Novo)
  - Como rodar a API
  - Documentação de endpoints
  - Exemplos de uso (curl, Python)
  - Interpretação de métricas

- **`run_api.sh`** ✅ (Novo)
  - Script para fácil inicialização
  - Opções: dev, produção, docker

---

## 🚀 Como Rodar

### Opção 1: Desenvolvimento (Recomendado para testar)
```bash
chmod +x run_api.sh
./run_api.sh
# Escolha opção 1
```

Ou manualmente:
```bash
cd api
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Acesse: **http://localhost:8000**

### Opção 2: Produção
```bash
./run_api.sh
# Escolha opção 2
```

Ou manualmente:
```bash
cd api
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Opção 3: Docker
```bash
./run_api.sh
# Escolha opção 3
```

Ou manualmente:
```bash
docker-compose up --build
```

---

## 🎯 O que a Aplicação Faz

1. **Entrada do Usuário:**
   - Ticker da ação (ex: ABEV3)
   - Data inicial
   - Data final

2. **Processamento:**
   - Baixa dados do Yahoo Finance
   - Normaliza com MinMaxScaler
   - Cria sequências de 50 dias
   - Faz previsão com LSTM
   - Calcula métricas

3. **Saída:**
   - 💰 Preço atual e previsto
   - 📈 Gráfico (Previsto vs Real)
   - 📊 Métricas detalhadas:
     - MSE, MAE, RMSE
     - MAPE, R² Score
   - 📝 Resumo executivo

---

## 📱 Interface

```
┌─────────────────────────────────────┐
│  📈 Stock Price Predictor           │
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │   INPUTS     │  │  RESULTS    │ │
│  │ • Ticker     │  │ • Gráfico   │ │
│  │ • Data ini   │  │ • Métricas  │ │
│  │ • Data fim   │  │ • Resumo    │ │
│  │              │  │             │ │
│  │ [Prever] 🚀 │  │             │ │
│  └──────────────┘  └─────────────┘ │
└─────────────────────────────────────┘
```

---

## 🔌 Endpoints da API

### 1. `GET /`
Retorna a página HTML

### 2. `GET /health`
```bash
curl http://localhost:8000/health
# Resposta: { "status": "ok", "model_loaded": true, ... }
```

### 3. `POST /api/predict`
```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "ABEV3",
    "start_date": "2024-01-01",
    "end_date": "2025-12-21"
  }'
```

### 4. `GET /api/info`
Informações sobre o modelo

---

## 📊 Estrutura do Projeto

```
stock_predictor_lstm_model/
├── api/
│   ├── app.py                    ✅ FastAPI principal
│   ├── prediction_utils.py       ✅ Funções helper
│   ├── templates/
│   │   └── index.html           ✅ Interface web
│   ├── Dockerfile
│   └── __init__.py
│
├── models/
│   ├── stock_lstm.pt            (Seu modelo)
│   └── scaler.joblib            (Seu scaler)
│
├── notebooks/                   (Seus notebooks)
├── data/                        (Seus dados)
├── requirements.txt             (Dependências)
├── docker-compose.yml           (Docker Compose)
│
├── API_README.md               ✅ Documentação API
├── run_api.sh                  ✅ Script launcher
└── README.md                   (Original)
```

---

## 🎨 Features da Interface

✅ Design responsivo (mobile-friendly)
✅ Tema escuro/gradiente
✅ Validação de entrada
✅ Loading spinner
✅ Mensagens de sucesso/erro
✅ Gráfico interativo
✅ Cards de métricas
✅ Resumo executivo
✅ Sem JavaScript frameworks (apenas vanilla JS)

---

## 📖 Documentação Automática

FastAPI gera documentação interativa automaticamente:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔧 Troubleshooting

### Erro: "Modelos não encontrados"
```
Copie seus arquivos para models/:
- stock_lstm.pt
- scaler.joblib
```

### Erro: "Porta 8000 em uso"
```bash
# Usar outra porta
uvicorn app:app --port 8001
```

### Erro: "Ticker não encontrado"
```
Verifique:
- Ação brasileira usa .SA (ABEV3 → ABEV3.SA)
- A ação existe no Yahoo Finance
- Período tem dados disponíveis
```

---

## 📝 Próximos Passos (Opcional)

1. **Melhorar o modelo:**
   - Use `notebooks/train_ibov_lstm.ipynb`
   - Fine-tune com dados mais recentes

2. **Deploy em produção:**
   - Usar Nginx como reverse proxy
   - PM2 para gerenciar processo
   - Certbot para HTTPS

3. **Adicionar features:**
   - Autenticação de usuários
   - Banco de dados para histórico
   - Notificações de preço
   - Comparação entre ações

4. **Monitoramento:**
   - Prometheus + Grafana
   - Logs estruturados
   - Alertas

---

## 🎓 Para Aprender Mais

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **LSTM Tutorial**: https://colah.github.io/posts/2015-08-Understanding-LSTMs/
- **PyTorch**: https://pytorch.org
- **Uvicorn**: https://www.uvicorn.org

---

## ✨ Bom desenvolvimento!

Qualquer dúvida, consulte:
- `API_README.md` - Documentação técnica
- `http://localhost:8000/docs` - Swagger interativo
- Logs do console durante execução

---

**Versão:** 1.0.0  
**Data:** Dezembro 2025  
**Status:** ✅ Pronto para usar
