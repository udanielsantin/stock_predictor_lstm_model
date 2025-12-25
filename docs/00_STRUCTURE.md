# Guia de Simplificação e Estrutura Final

Projeto reorganizado e simplificado para deploy em EC2 com Docker.

## ✅ O que foi consolidado

### Documentação
- **Antes:** 12 arquivos .md duplicados na raiz e em docs/
- **Depois:** 3 arquivos essenciais em docs/
  - `EC2_DEPLOYMENT.md` - Deploy em produção
  - `SETUP.md` - Setup local
  - `API_REFERENCE.md` - Documentação da API

### Scripts
- **Removido:** `deploy.sh`, `test-docker-build.sh` (desnecessários)
- **Removido:** `.env.aws`, `nginx.conf` (não usamos Nginx para EC2 simples)
- **Mantido:** `run_api.sh` (opcional para local)

### Raiz
- **Mantido:** Apenas o essencial
  - `docker-compose.yml` - Deploy em 1 comando
  - `requirements.txt` - Dependências
  - `README.md` - Documento principal

## 📁 Estrutura Final (Limpa)

```
stock_predictor_lstm_model/
│
├── README.md                           # Documento principal
├── docker-compose.yml                  # Deploy (1 comando)
├── requirements.txt                    # Dependências
├── run_api.sh                          # Script local (opcional)
│
├── docs/                               # Documentação (3 guias)
│   ├── EC2_DEPLOYMENT.md              # Deploy em produção
│   ├── SETUP.md                       # Setup local
│   └── API_REFERENCE.md               # Endpoints
│
├── api/                                # Aplicação FastAPI
│   ├── app.py                         # Rotas
│   ├── prediction_utils.py            # Lógica de previsão
│   ├── log_utils.py                   # Sistema de logs
│   ├── dashboard_utils.py             # Gráficos
│   ├── upload_logs_to_s3.py           # Upload S3 (opcional)
│   ├── Dockerfile                     # Imagem Docker
│   ├── .env.example                   # Template env
│   ├── logs/                          # Logs JSON (gerado)
│   └── templates/                     # Frontend
│       ├── index.html
│       ├── dashboard.html
│       └── static/
│           ├── css/style.css
│           └── js/script.js
│
├── models/                             # Modelos treinados
│   ├── stock_lstm.pt                  # Modelo LSTM
│   └── scaler.joblib                  # Normalizador
│
├── notebooks/                          # Jupyter (desenvolvimento)
│   ├── train_ibov_lstm.ipynb
│   └── ...
│
├── data/                               # Dados brutos
│   ├── data.py
│   └── ibov_tickers.csv
│
└── src/                                # Código auxiliar
    └── model_utils.py
```

## 🎯 Fluxo de Uso

### Local (Desenvolvimento)
```bash
source venv/bin/activate
cd api && uvicorn app:app --reload
```

### Docker Local
```bash
docker-compose up
```

### EC2 (Produção)
```bash
# 1. SSH na instância
ssh -i key.pem ubuntu@IP

# 2. Instalar Docker
curl -fsSL https://get.docker.com | sh

# 3. Clone e deploy
git clone seu-repo
cd stock_predictor_lstm_model
docker-compose up -d
```

## 📚 Documentação

### Para começar rápido
→ Leia [README.md](../README.md)

### Para setup local
→ Leia [docs/SETUP.md](SETUP.md)

### Para deploy em EC2
→ Leia [docs/EC2_DEPLOYMENT.md](EC2_DEPLOYMENT.md)

### Para entender API
→ Leia [docs/API_REFERENCE.md](API_REFERENCE.md)

## ✨ Decisões de Design

1. **Docker é padrão** - Eliminamos scripts de deploy manuais
2. **EC2 simples** - Sem Nginx, apenas Docker na porta 8000
3. **Documentação focada** - 3 guias ao invés de 12 pages
4. **Estrutura clara** - Separação nítida entre api/ models/ docs/
5. **S3 opcional** - Log local é padrão, S3 é complementar

## 🔧 Customizações Futuras

Se precisar:
- **SSL com HTTPS** - Adicione Nginx conforme [EC2_DEPLOYMENT.md](EC2_DEPLOYMENT.md)
- **Banco de dados** - Adicione serviço no docker-compose.yml
- **Load balancer** - Escalabilidade fora do escopo
- **Kubernetes** - Não recomendado para EC2 single instance

## ⏱️ Tempos de Deploy

| Ambiente | Setup | Deploy | Ready |
|----------|-------|--------|-------|
| Local | 5 min | 3 min | ✅ |
| Docker | - | 3 min | ✅ |
| EC2 | 10 min | 5 min | ✅ |

## 📊 Checklist Final

- [x] README.md limpo e direto
- [x] 3 guias de documentação essenciais
- [x] docker-compose.yml pronto
- [x] Estrutura clara e simples
- [x] Sem redundâncias
- [x] Sem scripts complexos
- [x] Pronto para produção

---

**Projeto simplificado e organizado para EC2 + Docker! 🚀**
