#!/bin/bash

##########################################################################
# Script de Setup - Instalar Docker e Docker Compose no EC2
# Execute com: bash setup-docker.sh
##########################################################################

set -e

echo ""
echo "=========================================================================="
echo "🔧 Setup Docker - Stock LSTM Predictor"
echo "=========================================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ==================== STEP 1: Verificar OS ====================
echo "📋 PASSO 1: Verificando sistema operacional..."

if ! grep -q "Ubuntu" /etc/os-release; then
    echo -e "${YELLOW}⚠️  Este script foi testado apenas em Ubuntu${NC}"
    read -p "Continuar mesmo assim? (s/n): " continue
    if [ "$continue" != "s" ]; then
        exit 1
    fi
fi

echo -e "${GREEN}✅ Sistema verificado${NC}"
echo ""

# ==================== STEP 2: Atualizar sistema ====================
echo "📋 PASSO 2: Atualizando sistema..."

sudo apt-get update
sudo apt-get upgrade -y

echo -e "${GREEN}✅ Sistema atualizado${NC}"
echo ""

# ==================== STEP 3: Instalar Docker ====================
echo "📋 PASSO 3: Instalando Docker..."

if command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker já está instalado${NC}"
    docker --version
else
    echo "   Baixando Docker installer..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    
    echo "   Executando installer..."
    sudo sh get-docker.sh
    
    # Limpar
    rm get-docker.sh
    
    echo -e "${GREEN}✅ Docker instalado${NC}"
    docker --version
fi

echo ""

# ==================== STEP 4: Configurar Docker ====================
echo "📋 PASSO 4: Configurando Docker..."

echo "   Adicionando usuário ao grupo docker..."
sudo usermod -aG docker ubuntu

echo "   Iniciando daemon do Docker..."
sudo systemctl start docker
sudo systemctl enable docker

echo -e "${GREEN}✅ Docker configurado${NC}"
echo ""

# ==================== STEP 5: Instalar Docker Compose ====================
echo "📋 PASSO 5: Instalando Docker Compose..."

if command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker Compose já está instalado${NC}"
    docker-compose --version
else
    echo "   Descobrindo versão mais recente..."
    
    VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d'"' -f4)
    
    echo "   Versão: $VERSION"
    echo "   Baixando..."
    
    sudo curl -L "https://github.com/docker/compose/releases/download/${VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    
    sudo chmod +x /usr/local/bin/docker-compose
    
    echo -e "${GREEN}✅ Docker Compose instalado${NC}"
    docker-compose --version
fi

echo ""

# ==================== STEP 6: Instalar Git ====================
echo "📋 PASSO 6: Instalando Git..."

if command -v git &> /dev/null; then
    echo -e "${YELLOW}⚠️  Git já está instalado${NC}"
    git --version
else
    sudo apt-get install -y git
    echo -e "${GREEN}✅ Git instalado${NC}"
    git --version
fi

echo ""

# ==================== STEP 7: Instalar AWS CLI (opcional) ====================
echo "📋 PASSO 7: Instalando AWS CLI (opcional)..."

read -p "Deseja instalar AWS CLI? (s/n): " install_awscli

if [ "$install_awscli" = "s" ]; then
    if command -v aws &> /dev/null; then
        echo -e "${YELLOW}⚠️  AWS CLI já está instalado${NC}"
        aws --version
    else
        echo "   Instalando..."
        sudo apt-get install -y awscli
        echo -e "${GREEN}✅ AWS CLI instalado${NC}"
        aws --version
    fi
fi

echo ""

# ==================== STEP 8: Reload do shell ====================
echo "📋 PASSO 8: Finalizando..."

echo -e "${YELLOW}⚠️  Você precisa fazer logout e login novamente${NC}"
echo "   para o grupo 'docker' ser aplicado"
echo ""
echo "Execute:"
echo "  exit"
echo ""
echo "Depois reconecte:"
echo "  ssh -i seu-key.pem ubuntu@seu-ec2-ip"
echo ""

# ==================== Resumo ====================
echo "=========================================================================="
echo -e "${GREEN}✅ SETUP CONCLUÍDO${NC}"
echo "=========================================================================="
echo ""
echo "Programas instalados:"
echo -e "${GREEN}✅${NC} Docker"
echo -e "${GREEN}✅${NC} Docker Compose"
echo -e "${GREEN}✅${NC} Git"
if [ "$install_awscli" = "s" ]; then
    echo -e "${GREEN}✅${NC} AWS CLI"
fi
echo ""
echo "Próximos passos:"
echo "1. Faça logout:"
echo "   exit"
echo ""
echo "2. Reconecte na EC2:"
echo "   ssh -i seu-key.pem ubuntu@seu-ec2-ip"
echo ""
echo "3. Clone o repositório:"
echo "   git clone https://github.com/seu-usuario/stock_predictor_lstm_model.git"
echo "   cd stock_predictor_lstm_model"
echo ""
echo "4. Execute o deploy:"
echo "   bash deploy.sh"
echo ""
echo "=========================================================================="
echo ""
