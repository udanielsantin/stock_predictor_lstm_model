# 📈 Stock LSTM Predictor

Previsão de preços de ações usando modelo LSTM (qualquer ticker do Yahoo Finance, com fallback ".SA" para brasileiros quando precisar).

> 🔗 **[Acesse o site aqui](https://seu-site-aqui.com)** _(adicione o link do seu site)_

---

## 📚 Como foi feito

### Exploração e Treinamento (Pastas `notebooks/` e `data/`)

Essas pastas foram usadas **apenas no desenvolvimento inicial** e não integram o projeto final:

**Pasta `data/`:**
- `ibov_tickers.csv` - Lista de ações do IBOVESPA (usado para baixar dados)
- `data.py` - Script para buscar dados históricos

**Pasta `notebooks/`:**
- `by_hand_model.ipynb` - Primeiros testes (descartado)
- `Light_plus_torch_LSTM.ipynb` - Experimentos com PyTorch
- `train_ibov_lstm.ipynb` - Treino com todo o IBOVESPA
- `stock_prediction_model.ipynb` - **Modelo final** que gerou os arquivos `stock_lstm.pt` e `scaler.joblib`

Depois que o modelo foi treinado e testado, os arquivos finais foram salvos na pasta `models/` para serem usados pela API.

---

## 🧠 O que é o modelo LSTM aqui

- Arquitetura: 2 camadas LSTM (hidden_size=64) + camada linear final para prever o próximo preço de fechamento.
- Janela: usa sequências de 50 preços normalizados (MinMaxScaler) e prevê o 51º.
- Entrada/saída: série univariada (Close); o scaler é salvo junto com o modelo para manter a escala na inferência.
- Treino: feito no notebook `stock_prediction_model.ipynb`, gerando `models/stock_lstm.pt` e `models/scaler.joblib`.
- Execução: a API carrega esses artefatos e reescala os dados do Yahoo Finance antes de inferir.

---

## 🚀 Rodando a Aplicação (API + Interface)

```bash
docker-compose up
```

Acesse: http://localhost:8000

---

## 📂 Estrutura Principal

```
api/                    ← Aplicação FastAPI 
├── app.py
├── templates/          ← Páginas HTML
└── static/             ← CSS e JavaScript

models/                 ← Modelos treinados
├── stock_lstm.pt
└── scaler.joblib
