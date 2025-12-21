#!/bin/bash

# Stock LSTM Predictor - FastAPI Launcher
# Script para iniciar a API FastAPI

set -e

echo "📈 Stock LSTM Predictor - FastAPI"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment não encontrado. Criando...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
else
    source venv/bin/activate
fi

echo -e "${GREEN}✅ Ambiente ativado${NC}"
echo ""

# Check if models exist
if [ ! -f "models/stock_lstm.pt" ] || [ ! -f "models/scaler.joblib" ]; then
    echo -e "${YELLOW}⚠️  Modelos não encontrados em models/${NC}"
    echo "   Copie os arquivos do notebook para continuar:"
    echo "   - models/stock_lstm.pt"
    echo "   - models/scaler.joblib"
    exit 1
fi

echo -e "${GREEN}✅ Modelos encontrados${NC}"
echo ""

# Options
echo "Escolha uma opção:"
echo "1) Desenvolvimento (com reload automático)"
echo "2) Produção (4 workers)"
echo "3) Docker"
echo ""
read -p "Opção (1-3): " option

case $option in
    1)
        echo ""
        echo -e "${BLUE}🚀 Iniciando FastAPI em modo desenvolvimento...${NC}"
        echo "   URL: http://localhost:8000"
        echo "   Docs: http://localhost:8000/docs"
        echo ""
        cd api
        uvicorn app:app --reload --host 0.0.0.0 --port 8000
        ;;
    2)
        echo ""
        echo -e "${BLUE}🚀 Iniciando FastAPI em modo produção...${NC}"
        echo "   URL: http://localhost:8000"
        echo "   Workers: 4"
        echo ""
        cd api
        uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
        ;;
    3)
        echo ""
        echo -e "${BLUE}🐳 Iniciando com Docker Compose...${NC}"
        docker-compose up --build
        ;;
    *)
        echo -e "${YELLOW}Opção inválida!${NC}"
        exit 1
        ;;
esac
