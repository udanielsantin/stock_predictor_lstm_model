# Deploy em EC2 + Docker

Guia completo para fazer deploy da aplicação em uma instância EC2 da AWS.

## 1. Criar Instância EC2

### Console AWS
1. EC2 → Instances → Launch Instance
2. **AMI:** Ubuntu Server 22.04 LTS
3. **Instance Type:** t3.micro (free tier) ou t3.small
4. **Key pair:** Criar ou selecionar existente
5. **Security group:**
   - SSH (22) - seu IP
   - HTTP (80) - 0.0.0.0/0
   - Custom TCP (8000) - 0.0.0.0/0 (ou só seu IP)
6. Launch

### Via CLI
```bash
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --count 1 \
  --instance-type t3.micro \
  --key-name sua-chave \
  --security-groups stock-predictor
```

## 2. Conectar à Instância

```bash
# SSH
chmod 400 sua-chave.pem
ssh -i sua-chave.pem ubuntu@IP_PUBLICO

# Opcional: Adicionar ao config SSH
cat > ~/.ssh/config << EOF
Host stock-ec2
  HostName IP_PUBLICO
  User ubuntu
  IdentityFile ~/.ssh/sua-chave.pem
EOF

ssh stock-ec2
```

## 3. Preparar Instância

```bash
# Update
sudo apt update && sudo apt upgrade -y

# Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar
docker --version
docker-compose --version

# Relogin para grupo docker
exit
ssh ubuntu@IP_PUBLICO
```

## 4. Clonar Repositório

```bash
# Clone
git clone https://github.com/seu-usuario/stock_predictor_lstm_model.git
cd stock_predictor_lstm_model

# (Opcional) Criar .env
cp api/.env.example api/.env
# Editar conforme necessário
```

## 5. Deploy com Docker

```bash
# Build (opcional, docker-compose baixa automaticamente)
docker-compose build

# Run em background
docker-compose up -d

# Verificar
docker ps
docker-compose logs -f

# Health check
curl http://localhost:8000/health
```

## 6. Acessar Aplicação

```
HTTP:  http://IP_PUBLICO:8000
HTTPS: https://seu-dominio (com SSL - próxima seção)

Endpoins:
- Home:      http://IP_PUBLICO:8000
- Dashboard: http://IP_PUBLICO:8000/dashboard
- API Docs:  http://IP_PUBLICO:8000/docs
```

## 7. (Opcional) Nginx + SSL com Let's Encrypt

### Instalar Nginx

```bash
sudo apt install -y nginx
```

### Nginx Config

```bash
# Backup
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.bak

# Editar
sudo nano /etc/nginx/sites-available/default
```

Cole:
```nginx
upstream fastapi {
    server localhost:8000;
}

server {
    listen 80 default_server;
    server_name _;

    location / {
        proxy_pass http://fastapi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Test e reload:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### SSL com Certbot

```bash
# Install
sudo apt install -y certbot python3-certbot-nginx

# Gerar certificado (mudar seu-dominio.com)
sudo certbot certonly --standalone -d seu-dominio.com

# Auto-renew (já configurado)
sudo systemctl enable certbot.timer
```

Nginx config com SSL:
```nginx
server {
    listen 80;
    server_name seu-dominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seu-dominio.com;

    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Reload:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 8. Gerenciar Aplicação

```bash
# Ver logs
docker-compose logs -f

# Parar
docker-compose stop

# Reiniciar
docker-compose restart

# Atualizar código
git pull
docker-compose down
docker-compose up -d

# Limpeza
docker-compose down -v  # Remove volumes também
docker system prune -a
```

## 9. Monitorar (Opcional)

### CloudWatch

```bash
# Instalar CloudWatch agent
sudo wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb
```

### Logs Aplicação

```bash
# Persistência
mkdir -p ./logs
docker-compose logs > ./logs/app.log

# Backup S3
aws s3 sync ./logs s3://seu-bucket/logs/
```

## 10. Elastic IP (Opcional)

Para manter IP constante:

```bash
# Console: EC2 → Elastic IPs → Allocate → Associate
# Ou via CLI
aws ec2 allocate-address --domain vpc
aws ec2 associate-address --instance-id i-xxxxx --allocation-id eipalloc-xxxxx
```

## Troubleshooting

### 500 - Erro Interno
```bash
docker-compose logs -f api
# Verificar models/stock_lstm.pt existe
docker exec stock-lstm-api ls -la /app/models/
```

### Porta 8000 em uso
```bash
sudo lsof -i :8000
sudo kill -9 PID
```

### Sem conexão com internet
```bash
# Verificar security group
# EC2 → Security groups → Verificar outbound rules
```

### Modelo não carrega
```bash
# Copiar arquivo localmente
docker exec stock-lstm-api python -c "import torch; print(torch.load('/app/models/stock_lstm.pt'))"
```

## Próximas Etapas

- [ ] Instância EC2 criada ✅
- [ ] Docker instalado e rodando ✅
- [ ] Aplicação acessível em http://IP:8000 ✅
- [ ] (Opcional) Nginx + SSL configurado
- [ ] (Opcional) Domínio customizado
- [ ] (Opcional) CloudWatch monitoring
- [ ] Backups logs em S3
- [ ] Alertas configurados

## Custos

- EC2 t3.micro: ~$0.0104/hora (~$7.50/mês free tier)
- t3.small: ~$0.0208/hora (~$15/mês)
- Nginx + SSL: Grátis
- Let's Encrypt: Grátis

**Estimativa total:** ~$10-20/mês (free tier)

---

**Aplicação pronta em produção! 🚀**
