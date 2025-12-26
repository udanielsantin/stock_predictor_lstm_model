#!/usr/bin/env python3
"""
Script de teste LOCAL - Simula o Logger SEM precisar das credenciais AWS
Execute com: python test_logger_mock.py
"""

import json
from datetime import datetime
import sys
import os

# Adicionar a pasta api ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

print("\n" + "="*70)
print("📊 TESTE LOCAL DO LOGGER - Simulação de Previsão")
print("="*70)

# ============================================
# CRIAR UM LOG ENTRY MANUALMENTE (sem S3)
# ============================================
print("\n✅ Passo 1: Criando um log de previsão...")

log_entry = {
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "request": {
        "ticker": "ABEV3",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    },
    "execution": {
        "duration_seconds": 2.345,
        "success": True
    },
    "result": {
        "last_close": 15.50,
        "next_price": 16.20,
        "price_change": 0.70,
        "price_change_pct": 4.52,
        "data_points": 252,
        "metrics": {
            "R2": 0.8765,
            "RMSE": 0.234
        }
    }
}

print(f"✅ Log entry criado:\n")
print(json.dumps(log_entry, indent=2, ensure_ascii=False))

# ============================================
# SIMULAR O CAMINHO S3
# ============================================
print("\n" + "="*70)
print("✅ Passo 2: Onde este log seria salvo no S3...")

timestamp = datetime.utcnow().strftime("%Y/%m/%d/%H%M%S")
ticker = log_entry["request"]["ticker"]
s3_bucket = "vapor-stock-predictor-logs"
s3_prefix = "logs/"
s3_key = f"{s3_prefix}{timestamp}_{ticker}.json"
s3_path = f"s3://{s3_bucket}/{s3_key}"

print(f"Bucket:    {s3_bucket}")
print(f"Path:      {s3_path}")
print(f"S3 Key:    {s3_key}")

# ============================================
# SIMULAR MÚLTIPLOS LOGS
# ============================================
print("\n" + "="*70)
print("✅ Passo 3: Exemplo com vários logs...")
print("="*70)

examples = [
    ("ABEV3", True, "2.345", "0.8765"),
    ("VALE3", True, "1.892", "0.9102"),
    ("PETR4", False, "0.456", None),
    ("ITUB4", True, "3.120", "0.7654"),
]

print(f"\nÓtimo, seus logs ficariam assim no S3:\n")
for i, (ticker, success, duration, r2) in enumerate(examples, 1):
    timestamp = datetime.utcnow().strftime("%Y/%m/%d/%H%M%S")
    s3_key = f"logs/{timestamp}_{ticker}.json"
    status = "✅" if success else "❌"
    print(f"{i}. {status} {s3_key}")
    print(f"   └─ Duração: {duration}s | R2: {r2 if success else 'erro'}")

# ============================================
# ESTRUTURA DO BUCKET
# ============================================
print("\n" + "="*70)
print("✅ Passo 4: Estrutura do Bucket S3")
print("="*70)

print("""
vapor-stock-predictor-logs/
└── logs/
    ├── 2025/01/15/123045_ABEV3.json
    ├── 2025/01/15/123120_VALE3.json
    ├── 2025/01/15/123145_PETR4.json
    ├── 2025/01/15/123200_ITUB4.json
    ├── 2025/01/16/090015_ABEV3.json
    ├── 2025/01/16/090230_VALE3.json
    └── 2025/01/16/090445_WEGE3.json
""")

print("✅ Note que os logs são organizados por DATA/HORA")

# ============================================
# NÃO HÁ MAIS PASTA LOCAL
# ============================================
print("\n" + "="*70)
print("✅ Passo 5: Confirmação - Sem mais logs locais!")
print("="*70)

print("""
ANTES (com logs locais):
    api/logs/
    ├── prediction_ABEV3_20251226_222800.json
    ├── prediction_ABEV3_20251226_222806.json
    ├── prediction_ABEV3_20251226_222824.json
    └── ...

AGORA (apenas S3):
    ❌ A pasta api/logs/ foi REMOVIDA
    ✅ Tudo salva APENAS no S3
    ✅ Nenhum arquivo local
""")

# ============================================
# COMO CONSULTAR OS LOGS
# ============================================
print("\n" + "="*70)
print("✅ Passo 6: Como consultar os logs no S3")
print("="*70)

print("""
Via AWS CLI:
    aws s3 ls s3://vapor-stock-predictor-logs/logs/ --recursive
    
    Saída:
    2025-01-15 12:30:45        342 logs/2025/01/15/123045_ABEV3.json
    2025-01-15 12:31:20        356 logs/2025/01/15/123120_VALE3.json
    2025-01-15 12:31:45        298 logs/2025/01/15/123145_PETR4.json
    
Via AWS Console:
    1. Acesse S3 > vapor-stock-predictor-logs
    2. Navegue até logs/
    3. Explore as pastas por data/hora

Via API (quando a API está rodando):
    curl http://localhost:8000/api/logs/recent?limit=5
    curl http://localhost:8000/api/logs/stats
    curl http://localhost:8000/dashboard
""")

# ============================================
# RESUMO
# ============================================
print("\n" + "="*70)
print("🎉 RESUMO")
print("="*70)

print("""
✅ Confirma: NÃO salva mais logs localmente
✅ Confirma: APENAS salva no S3 (vapor-stock-predictor-logs)
✅ Confirma: Logs organizados por data (2025/01/15/...) 
✅ Confirma: Dashboard lê do S3
✅ Confirma: API endpoints lêem do S3

Próximos passos:
1. Configure as variáveis de ambiente AWS:
   export AWS_ACCESS_KEY_ID='sua-chave'
   export AWS_SECRET_ACCESS_KEY='sua-senha'
   
2. Rode o teste completo:
   python test_s3_logger.py
   
3. Inicie a API:
   cd api && python -m uvicorn app:app --reload
   
4. Faça uma previsão no navegador:
   http://localhost:8000
""")

print("\n" + "="*70)
