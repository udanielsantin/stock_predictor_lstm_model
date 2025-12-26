# 🚀 Deploy no EC2 com Docker

## Visão Geral

Deploy da aplicação Stock LSTM Predictor em uma instância EC2 da AWS usando Docker e Docker Compose.

**Arquitetura:**
- FastAPI rodando em container Docker
- Logs salvos APENAS no S3 (`vapor-stock-predictor-logs`)
---

## Pré-requisitos

### 1. EC2 Instance
- **AMI:** Ubuntu 24.04 LTS (ou similar)
- **Instance Type:** t3.medium (recomendado) ou t3.small
- **Storage:** 20-30 GB EBS
- **Security Group:** Portas abertas
  - 22 (SSH)
  - 8000 (API)
  - 443 (HTTPS, opcional)

### 2. AWS Credentials
- Access Key ID
- Secret Access Key
- Bucket S3: `vapor-stock-predictor-logs` (já criado)

### 3. Softwares na EC2
- Docker
- Docker Compose
- Git

---

## Instalação no EC2

### Passo 1: Conectar na instância EC2

```bash
ssh -i seu-key.pem ubuntu@seu-ec2-ip
```

### Passo 2: Atualizar o sistema

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Passo 3: Instalar Docker

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adicionar usuário ao grupo docker
sudo usermod -aG docker ubuntu

# Relogar para aplicar mudanças
newgrp docker
exit  # Desconectar e reconectar
```

### Passo 4: Instalar Docker Compose

```bash
# Verificar versão mais recente em https://github.com/docker/compose/releases
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalação
docker-compose --version
```

### Passo 5: Instalar Git

```bash
sudo apt-get install -y git
```

### Passo 6: Clonar o repositório

```bash
cd /home/ubuntu
git clone https://github.com/seu-usuario/stock_predictor_lstm_model.git
cd stock_predictor_lstm_model
```

---

## Configuração do Deploy

### Passo 1: Criar arquivo .env

Crie um arquivo `.env` na raiz do projeto com suas credenciais AWS:

```bash
cat > .env << EOF
AWS_ACCESS_KEY_ID=sua-access-key-aqui
AWS_SECRET_ACCESS_KEY=sua-secret-key-aqui
AWS_REGION=us-east-1
S3_BUCKET_NAME=vapor-stock-predictor-logs
S3_LOG_PREFIX=logs/
EOF
```

**⚠️ IMPORTANTE:** Não commit este arquivo no git! Já está no `.gitignore`.

### Passo 2: Verificar permissões

```bash
# O arquivo .env deve ter permissões restritas
chmod 600 .env

# Verificar que está no .gitignore
grep ".env" .gitignore
```

### Passo 3: Testar conexão com S3

```bash
# Instalar AWS CLI (opcional, mas útil)
sudo apt-get install -y awscli

# Testar conexão
export AWS_ACCESS_KEY_ID=$(grep AWS_ACCESS_KEY_ID .env | cut -d '=' -f2)
export AWS_SECRET_ACCESS_KEY=$(grep AWS_SECRET_ACCESS_KEY .env | cut -d '=' -f2)

aws s3 ls s3://vapor-stock-predictor-logs/ --region us-east-1
```

---

## Build e Deploy com Docker

### Passo 1: Build da imagem Docker

```bash
# Build com as variáveis do .env
docker-compose build

# Verificar se build foi bem-sucedido
docker images | grep stock-lstm
```

### Passo 2: Iniciar o container

```bash
# Com docker-compose (recomendado)
docker-compose up -d

# Ou manualmente
docker run -d \
  --name stock-lstm-api \
  --env-file .env \
  -p 8000:8000 \
  stock-lstm-api:latest
```

### Passo 3: Verificar se está rodando

```bash
# Ver status do container
docker ps

# Ver logs
docker-compose logs -f api

# Ou
docker logs -f stock-lstm-api
```

### Passo 4: Testar a API

```bash
# Health check
curl http://localhost:8000/health

# Deve retornar:
# {"status":"ok","model_loaded":true,"scaler_loaded":true}
```

---

## Testando a Aplicação

### Teste 1: Fazer uma previsão

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "ABEV3",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }'
```

Verifique nos logs se o arquivo foi salvo no S3:

```bash
aws s3 ls s3://vapor-stock-predictor-logs/logs/ --recursive
```

### Teste 2: Consultar logs via API

```bash
# Logs recentes
curl http://localhost:8000/api/logs/recent?limit=5

# Estatísticas
curl http://localhost:8000/api/logs/stats
```

### Teste 3: Acessar dashboard

```bash
# Via navegador
curl http://seu-ec2-ip:8000/dashboard

# Ou abra no navegador:
# http://seu-ec2-ip:8000/dashboard
```

---

## Gerenciamento do Container

### Parar o container

```bash
docker-compose down

# Ou
docker stop stock-lstm-api
```

### Reiniciar o container

```bash
docker-compose restart

# Ou
docker restart stock-lstm-api
```

### Ver logs em tempo real

```bash
docker-compose logs -f api

# Últimas 100 linhas
docker-compose logs --tail=100 api
```

### Remover tudo (cuidado!)

```bash
docker-compose down -v
docker rmi stock-lstm-api:latest
```

---

## Configuração de Auto-restart

O `docker-compose.yml` já está configurado com `restart: unless-stopped`, o que significa que:

- ✅ Container reinicia automaticamente se falhar
- ✅ Container continua rodando após reboot da EC2
- ❌ Só para manualmente ou se houver erro

Para verificar:

```bash
docker inspect stock-lstm-api | grep -A 5 "RestartPolicy"
```

---

## Monitoramento

### Verificar uso de recursos

```bash
docker stats stock-lstm-api

# Saída:
# CONTAINER          CPU %   MEM USAGE / LIMIT
# stock-lstm-api     2.5%    450MB / 1GB
```

### Logs de erro

```bash
# Ver apenas erros
docker-compose logs api | grep -i error

# Ver as últimas 50 linhas
docker-compose logs --tail=50 api
```

### Verificar saúde do container

```bash
docker inspect stock-lstm-api | grep -A 5 "Health"
```

---

## Atualizar a Aplicação

Se fez mudanças no código:

```bash
# Pull das mudanças
git pull origin main

# Rebuild da imagem
docker-compose build

# Reiniciar
docker-compose up -d

# Verificar logs
docker-compose logs -f api
```

---

## Troubleshooting

### ❌ "docker: command not found"

```bash
# Docker não foi instalado ou não está no PATH
sudo apt-get install -y docker.io
sudo usermod -aG docker ubuntu
newgrp docker
```

### ❌ "S3_BUCKET_NAME environment variable is required"

```bash
# O arquivo .env não está sendo lido
cat .env  # Verifique se as variáveis estão corretas
docker-compose down
docker-compose up -d  # Rebuilde com o .env
```

### ❌ "Connection refused on 127.0.0.1:8000"

```bash
# A API não iniciou corretamente
docker-compose logs api  # Veja os erros

# Reinicie o container
docker-compose restart api
```

### ❌ "NoSuchBucket: The specified bucket does not exist"

```bash
# Verifique se o bucket existe
aws s3 ls | grep vapor-stock-predictor-logs

# Verifique o nome no .env
grep S3_BUCKET_NAME .env
```

### ❌ "Unable to locate credentials"

```bash
# As credenciais AWS não estão configuradas
# Verifique o arquivo .env
cat .env

# Redefina as variáveis
docker-compose down
# Edite o .env
docker-compose up -d
```

---

## Backup de Logs

Os logs estão no S3, então não precisa se preocupar com espaço em disco. Mas para backup:

```bash
# Fazer download de todos os logs do S3
aws s3 sync s3://vapor-stock-predictor-logs/logs/ ./backup-logs/ --region us-east-1

# Fazer upload de backup para S3 (glacier, por exemplo)
aws s3 sync ./backup-logs/ s3://seu-bucket-backup/logs/ --storage-class GLACIER
```

---

## Segurança

### Proteger o arquivo .env

```bash
# Definir permissões corretas
chmod 600 .env

# Verificar que não é acessível
ls -la .env
# Deve mostrar: -rw------- 1 ubuntu ubuntu
```

### Limitar acesso à API

Se precisar de autenticação:

```bash
# Adicione variáveis de environment
API_KEY=sua-chave-secreta-aqui

# E atualize o code para validar
```

### Usar Security Groups

No AWS Console:
- Restringir SSH ao seu IP
- Liberar porta 8000 apenas para IPs confiáveis
- Restringir HTTPS (porto 443) se usar

---

## Checklist Final

- [ ] EC2 criada e rodando
- [ ] Docker e Docker Compose instalados
- [ ] Repositório clonado
- [ ] `.env` configurado com credenciais AWS
- [ ] S3 bucket criado (`vapor-stock-predictor-logs`)
- [ ] Docker build bem-sucedido
- [ ] Container rodando (`docker ps`)
- [ ] Health check passa (`curl http://localhost:8000/health`)
- [ ] Previsão funciona (teste via API)
- [ ] Logs aparecem no S3
- [ ] Dashboard acessível
- [ ] Auto-restart configurado

---

## Próximos Passos

1. ✅ Deploy no EC2 concluído
2. ⏭️ Configurar domínio (opcional)
3. ⏭️ Adicionar HTTPS/SSL (Let's Encrypt)
4. ⏭️ Configurar CI/CD com GitHub Actions (se precisar)
5. ⏭️ Monitorar com CloudWatch

