#!/bin/bash
"""
Script de teste local rápido para validar a integração com S3
"""

set -e

# ============================================
# 1. CONFIGURAR VARIÁVEIS DE AMBIENTE
# ============================================
echo "🔧 Configurando variáveis de ambiente..."

# Você precisa adicionar suas credenciais aqui
export S3_BUCKET_NAME="vapor-stock-predictor-logs"
export S3_LOG_PREFIX="logs/"
export AWS_REGION="us-east-1"
export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-}"

# Validar se as credenciais estão setadas
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "❌ Erro: AWS_ACCESS_KEY_ID ou AWS_SECRET_ACCESS_KEY não estão definidas!"
    echo ""
    echo "Configure assim antes de rodar este script:"
    echo "  export AWS_ACCESS_KEY_ID='sua-chave'"
    echo "  export AWS_SECRET_ACCESS_KEY='sua-senha'"
    echo ""
    exit 1
fi

echo "✅ Variáveis de ambiente configuradas:"
echo "   S3_BUCKET_NAME: $S3_BUCKET_NAME"
echo "   AWS_REGION: $AWS_REGION"
echo ""

# ============================================
# 2. TESTAR CONEXÃO COM S3
# ============================================
echo "🧪 Testando conexão com S3..."
if aws s3 ls s3://$S3_BUCKET_NAME --region $AWS_REGION &>/dev/null; then
    echo "✅ Bucket S3 acessível!"
else
    echo "❌ Erro ao acessar o bucket. Verifique as credenciais."
    exit 1
fi

echo ""

# ============================================
# 3. LISTAR LOGS EXISTENTES NO S3
# ============================================
echo "📋 Logs existentes no S3:"
aws s3 ls s3://$S3_BUCKET_NAME/$S3_LOG_PREFIX --recursive --region $AWS_REGION || echo "   (nenhum log ainda)"

echo ""
echo "✅ Teste concluído!"
echo ""
echo "Próximos passos:"
echo "1. Inicie a API: cd api && python -m uvicorn app:app --reload"
echo "2. Faça uma previsão: curl -X POST http://localhost:8000/api/predict ..."
echo "3. Verifique os logs no S3"
