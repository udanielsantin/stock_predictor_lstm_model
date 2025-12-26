#!/bin/bash

##########################################################################
# Script de Deploy - Stock LSTM Predictor no EC2
# Execute com: bash deploy.sh
##########################################################################

set -e  # Exit on error

echo ""
echo "=========================================================================="
echo "🚀 Deploy - Stock LSTM Predictor"
echo "=========================================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ==================== STEP 1: Verificar pré-requisitos ====================
echo "📋 PASSO 1: Verificando pré-requisitos..."

check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 não está instalado${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ $1 encontrado${NC}"
    return 0
}

check_command "docker" || exit 1
check_command "docker-compose" || exit 1
check_command "git" || exit 1

echo ""

# ==================== STEP 2: Verificar arquivo .env ====================
echo "📋 PASSO 2: Verificando configuração AWS..."

if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Arquivo .env não encontrado!${NC}"
    echo ""
    echo "Crie um arquivo .env na raiz do projeto com:"
    echo ""
    echo "AWS_ACCESS_KEY_ID=sua-chave"
    echo "AWS_SECRET_ACCESS_KEY=sua-senha"
    echo "AWS_REGION=us-east-1"
    echo "S3_BUCKET_NAME=vapor-stock-predictor-logs"
    echo "S3_LOG_PREFIX=logs/"
    echo ""
    exit 1
fi

# Verificar se tem credenciais
if ! grep -q "AWS_ACCESS_KEY_ID" .env; then
    echo -e "${RED}❌ AWS_ACCESS_KEY_ID não está configurado no .env${NC}"
    exit 1
fi

if ! grep -q "AWS_SECRET_ACCESS_KEY" .env; then
    echo -e "${RED}❌ AWS_SECRET_ACCESS_KEY não está configurado no .env${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Arquivo .env configurado${NC}"

# Verificar permissões
chmod 600 .env
echo -e "${GREEN}✅ Permissões do .env ajustadas${NC}"

echo ""

# ==================== STEP 3: Parar containers existentes ====================
echo "📋 PASSO 3: Limpando containers anteriores..."

if docker ps -a | grep -q "stock-lstm-api"; then
    echo "   Parando container existente..."
    docker-compose down || docker stop stock-lstm-api || true
    echo -e "${GREEN}✅ Container anterior parado${NC}"
else
    echo -e "${GREEN}✅ Nenhum container anterior${NC}"
fi

echo ""

# ==================== STEP 4: Build da imagem ====================
echo "📋 PASSO 4: Fazendo build da imagem Docker..."

docker-compose build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erro no build da imagem${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build concluído${NC}"

echo ""

# ==================== STEP 5: Iniciar container ====================
echo "📋 PASSO 5: Iniciando container..."

docker-compose up -d

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erro ao iniciar container${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Container iniciado${NC}"

echo ""

# ==================== STEP 6: Aguardar startup ====================
echo "📋 PASSO 6: Aguardando inicialização da API..."

sleep 3

# Tentar health check
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo -e "${GREEN}✅ API está saudável${NC}"
        break
    fi
    
    attempt=$((attempt + 1))
    echo -n "."
    sleep 1
done

if [ $attempt -ge $max_attempts ]; then
    echo ""
    echo -e "${RED}❌ Timeout aguardando API${NC}"
    echo "Verifique os logs:"
    echo "  docker-compose logs api"
    exit 1
fi

echo ""

# ==================== STEP 7: Testar conexão com S3 ====================
echo "📋 PASSO 7: Testando conexão com S3..."

# Extrair credenciais do .env
export AWS_ACCESS_KEY_ID=$(grep AWS_ACCESS_KEY_ID .env | cut -d '=' -f2)
export AWS_SECRET_ACCESS_KEY=$(grep AWS_SECRET_ACCESS_KEY .env | cut -d '=' -f2)
export AWS_REGION=$(grep AWS_REGION .env | cut -d '=' -f2 || echo "us-east-1")
export S3_BUCKET=$(grep S3_BUCKET_NAME .env | cut -d '=' -f2)

if aws s3 ls s3://$S3_BUCKET/ --region $AWS_REGION &> /dev/null; then
    echo -e "${GREEN}✅ Bucket S3 acessível${NC}"
else
    echo -e "${YELLOW}⚠️  Aviso: Não foi possível acessar o bucket S3${NC}"
    echo "   Verifique as credenciais AWS"
fi

echo ""

# ==================== STEP 8: Resumo ====================
echo "=========================================================================="
echo -e "${GREEN}🎉 DEPLOY CONCLUÍDO COM SUCESSO!${NC}"
echo "=========================================================================="
echo ""
echo "📊 Status:"
docker ps --filter "name=stock-lstm-api" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "🔗 Endpoints disponíveis:"
echo "   - API: http://localhost:8000"
echo "   - Health: http://localhost:8000/health"
echo "   - Predict: http://localhost:8000/api/predict"
echo "   - Logs: http://localhost:8000/api/logs/recent"
echo "   - Stats: http://localhost:8000/api/logs/stats"
echo "   - Dashboard: http://localhost:8000/dashboard"
echo ""
echo "📝 Próximos passos:"
echo "   1. Teste uma previsão:"
echo "      curl -X POST http://localhost:8000/api/predict \\"
echo "        -H 'Content-Type: application/json' \\"
echo "        -d '{\"ticker\": \"ABEV3\", \"start_date\": \"2024-01-01\", \"end_date\": \"2024-12-31\"}'"
echo ""
echo "   2. Verifique os logs:"
echo "      docker-compose logs -f api"
echo ""
echo "   3. Consulte logs no S3:"
echo "      aws s3 ls s3://$S3_BUCKET/logs/ --recursive --region $AWS_REGION"
echo ""
echo "=========================================================================="
echo ""
