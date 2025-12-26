# 🧪 Como Testar Localmente com S3

## Resumo Rápido

✅ **NÃO salva mais logs localmente**
✅ **APENAS salva no S3** (`vapor-stock-predictor-logs`)
✅ **Logs organizados por data:** `logs/2025/01/15/123045_ABEV3.json`
✅ **Dashboard lê do S3**
✅ **API endpoints lêem do S3**

---

## Teste 1: Visualizar Estrutura (SEM credenciais)

```bash
python test_logger_mock.py
```

Isso mostra:
- Formato dos logs
- Onde ficariam no S3
- Exemplos de múltiplos logs
- Estrutura do bucket

---

## Teste 2: Teste Completo (COM credenciais AWS)

### Passo 1: Configure as credenciais

```bash
export AWS_ACCESS_KEY_ID='sua-chave-aqui'
export AWS_SECRET_ACCESS_KEY='sua-senha-aqui'
export AWS_REGION='us-east-1'
export S3_BUCKET_NAME='vapor-stock-predictor-logs'
```

Ou crie um arquivo `.env` na pasta `api/`:

```bash
cat > api/.env << EOF
AWS_ACCESS_KEY_ID=sua-chave-aqui
AWS_SECRET_ACCESS_KEY=sua-senha-aqui
AWS_REGION=us-east-1
S3_BUCKET_NAME=vapor-stock-predictor-logs
EOF
```

### Passo 2: Rode o teste completo

```bash
python test_s3_logger.py
```

Isso vai:
1. ✅ Testar conexão com S3
2. ✅ Simular uma previsão bem-sucedida
3. ✅ Simular uma previsão com erro
4. ✅ Recuperar logs do S3
5. ✅ Mostrar estatísticas

### Passo 3: Verifique os logs no S3

```bash
# Via AWS CLI
aws s3 ls s3://vapor-stock-predictor-logs/logs/ --recursive

# Saída esperada:
# 2025-12-26 19:32:45        342 logs/2025/12/26/193245_ABEV3.json
# 2025-12-26 19:33:10        298 logs/2025/12/26/193310_VALE3.json
```

---

## Teste 3: Teste Completo da API

### Passo 1: Inicie a API

```bash
cd api
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Saída esperada:
```
✅ S3 Logger initialized with bucket: vapor-stock-predictor-logs
Uvicorn running on http://127.0.0.1:8000
```

### Passo 2: Faça uma previsão (em outro terminal)

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "ABEV3",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }'
```

Resposta esperada:
```json
{
  "ticker": "ABEV3",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "last_close": 15.5,
  "next_price": 16.2,
  "price_change": 0.7,
  "price_change_pct": 4.52,
  "metrics": {"R2": 0.8765},
  "data_points": 252,
  "plot": "..."
}
```

Você verá no terminal da API:
```
📝 Log uploaded to S3: s3://vapor-stock-predictor-logs/logs/2025/12/26/193245_ABEV3.json
```

### Passo 3: Consulte os logs via API

```bash
# Logs recentes
curl http://localhost:8000/api/logs/recent?limit=5

# Estatísticas
curl http://localhost:8000/api/logs/stats

# Dashboard
curl http://localhost:8000/dashboard
```

### Passo 4: Verifique no S3

```bash
aws s3 ls s3://vapor-stock-predictor-logs/logs/ --recursive
```

---

## Estrutura dos Logs no S3

Cada log tem este formato:

```json
{
  "timestamp": "2025-12-26T19:32:45.123Z",
  "request": {
    "ticker": "ABEV3",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  },
  "execution": {
    "duration_seconds": 2.345,
    "success": true
  },
  "result": {
    "last_close": 15.5,
    "next_price": 16.2,
    "price_change": 0.7,
    "price_change_pct": 4.52,
    "data_points": 252,
    "metrics": {
      "R2": 0.8765
    }
  }
}
```

---

## Comparação: Antes vs Depois

### ❌ ANTES (com logs locais)

```
api/
├── logs/  ← Pasta de logs local
│   ├── prediction_ABEV3_20251226_222800.json
│   ├── prediction_ABEV3_20251226_222806.json
│   ├── prediction_VALE3_20251226_222824.json
│   └── ...
├── app.py
└── log_utils.py
```

- Logs salvos localmente
- Ocupa espaço no disco
- Difícil de organizar
- GitHub workflows deletavam os logs

### ✅ DEPOIS (apenas S3)

```
S3: vapor-stock-predictor-logs/
└── logs/
    ├── 2025/01/15/123045_ABEV3.json
    ├── 2025/01/15/123120_VALE3.json
    ├── 2025/01/16/090015_ABEV3.json
    └── ...

api/
├── app.py
├── log_utils.py
└── (SEM pasta logs/)
```

- ✅ Logs salvos APENAS no S3
- ✅ Sem pasta local
- ✅ Organizado por data
- ✅ Dashboard lê do S3
- ✅ API endpoints lêem do S3
- ✅ Sem GitHub workflows

---

## Troubleshooting

### ❌ "S3_BUCKET_NAME environment variable is required"

**Solução:**
```bash
export S3_BUCKET_NAME='vapor-stock-predictor-logs'
export AWS_ACCESS_KEY_ID='sua-chave'
export AWS_SECRET_ACCESS_KEY='sua-senha'
```

### ❌ "Failed to initialize S3 client"

**Solução:**
- Verifique se as credenciais AWS estão corretas
- Verifique se boto3 está instalado: `pip install boto3`
- Verifique a conexão com a internet

### ❌ "Unable to locate credentials"

**Solução:**
```bash
# Configure as variáveis de ambiente corretamente
export AWS_ACCESS_KEY_ID='sua-chave'
export AWS_SECRET_ACCESS_KEY='sua-senha'

# Ou use o AWS CLI para configurar
aws configure
```

### ❌ "NoSuchBucket: The specified bucket does not exist"

**Solução:**
- Verifique se o bucket existe no S3
- Verifique o nome exato: `vapor-stock-predictor-logs`
- Verifique se a região está correta

---

## Próximos Passos

1. ✅ Configure as credenciais AWS
2. ✅ Rode o teste mock: `python test_logger_mock.py`
3. ✅ Rode o teste completo: `python test_s3_logger.py`
4. ✅ Inicie a API: `cd api && python -m uvicorn app:app --reload`
5. ✅ Faça previsões e veja os logs no S3
6. ✅ Faça push para o EC2 e teste lá também

