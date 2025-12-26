#!/bin/bash

##########################################################################
# Script de Stop/Cleanup - Stock LSTM Predictor
# Execute com: bash stop.sh
##########################################################################

set -e

echo ""
echo "=========================================================================="
echo "🛑 Parando Stock LSTM Predictor"
echo "=========================================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ==================== STEP 1: Parar containers ====================
echo "📋 PASSO 1: Parando containers..."

if docker ps | grep -q "stock-lstm-api"; then
    echo "   Parando api..."
    docker-compose down
    echo -e "${GREEN}✅ Container parado${NC}"
else
    echo -e "${YELLOW}⚠️  Nenhum container rodando${NC}"
fi

echo ""

# ==================== STEP 2: Listar opções ====================
echo "📋 PASSO 2: Limpeza adicional (opcional)..."
echo ""
echo "Escolha uma opção:"
echo "1. Apenas parou o container (padrão)"
echo "2. Remover container + imagem (mas manter dados)"
echo "3. Limpar TUDO (container + imagem + volumes)"
echo ""

read -p "Escolha (1-3): " choice

case $choice in
    2)
        echo "Removendo imagem..."
        docker rmi stock-lstm-api:latest || true
        echo -e "${GREEN}✅ Imagem removida${NC}"
        ;;
    3)
        echo -e "${RED}⚠️  CUIDADO: Isto removerá TUDO${NC}"
        read -p "Tem certeza? (s/n): " confirm
        if [ "$confirm" = "s" ]; then
            docker-compose down -v
            docker rmi stock-lstm-api:latest || true
            echo -e "${GREEN}✅ Limpeza completa realizada${NC}"
        fi
        ;;
    *)
        echo -e "${GREEN}✅ Container parado (imagem mantida)${NC}"
        ;;
esac

echo ""

# ==================== STEP 3: Verificar status ====================
echo "📋 PASSO 3: Status final..."

if docker ps | grep -q "stock-lstm-api"; then
    echo -e "${RED}❌ Container ainda está rodando${NC}"
else
    echo -e "${GREEN}✅ Container parado${NC}"
fi

echo ""
echo "=========================================================================="
echo -e "${GREEN}✅ Operação concluída${NC}"
echo "=========================================================================="
echo ""
echo "Para reiniciar:"
echo "  bash deploy.sh"
echo ""
