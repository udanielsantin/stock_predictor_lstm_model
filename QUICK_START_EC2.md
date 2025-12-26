# 🚀 Quick Start - Deploy no EC2

## Resumo em 5 minutos

1. **SSH para EC2**
2. **Clone o repositório**
3. **Configure `.env` com credenciais AWS**
4. **Execute `bash deploy.sh`**
5. **Teste a API**

---

## Passo 1: SSH para EC2

```bash
ssh -i seu-key.pem ubuntu@seu-ec2-public-ip
```

---

## Passo 2: Clone o repositório

```bash
cd /home/ubuntu
git clone https://github.com/seu-usuario/stock_predictor_lstm_model.git
cd stock_predictor_lstm_model
```

---

## Passo 3: Configure o arquivo .env

```bash
cat > .env << EOF
AWS_ACCESS_KEY_ID=sua-chave-aqui
AWS_SECRET_ACCESS_KEY=sua-senha-aqui
AWS_REGION=us-east-1
S3_BUCKET_NAME=vapor-stock-predictor-logs
S3_LOG_PREFIX=logs/
EOF

# Proteger o arquivo
chmod 600 .env

# Verificar
cat .env
```

---

## Passo 4: Deploy

```bash
bash deploy.sh
```

O script vai:
- ✅ Verificar Docker, Docker Compose e Git
- ✅ Validar arquivo .env
- ✅ Parar containers anteriores
- ✅ Build da imagem Docker
- ✅ Iniciar container
- ✅ Testar saúde da API
- ✅ Testar acesso ao S3

---

## Passo 5: Teste a API

### Via curl

```bash
# Health check
curl http://localhost:8000/health

# Fazer previsão
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "ABEV3",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }'

# Ver logs recentes
curl http://localhost:8000/api/logs/recent?limit=5

# Ver estatísticas
curl http://localhost:8000/api/logs/stats
```

### Via navegador

```
http://seu-ec2-ip:8000
http://seu-ec2-ip:8000/dashboard
```

---

## Verificar logs no S3

```bash
# Ver todos os logs
aws s3 ls s3://vapor-stock-predictor-logs/logs/ --recursive

# Fazer download de um log específico
aws s3 cp s3://vapor-stock-predictor-logs/logs/2025/01/15/123045_ABEV3.json ./
cat 123045_ABEV3.json
```

---

## Comandos úteis

```bash
# Ver status do container
docker ps

# Ver logs em tempo real
docker-compose logs -f api

# Parar a aplicação
bash stop.sh

# Reiniciar
docker-compose restart api

# Ver uso de recursos
docker stats stock-lstm-api
```

---

## Troubleshooting rápido

| Problema | Solução |
|----------|---------|
| "docker: command not found" | Rodar script de instalação: `bash setup-docker.sh` |
| "S3_BUCKET_NAME is required" | Verifique `.env`: `cat .env` |
| "Connection refused on 8000" | Esperar API iniciar: `docker-compose logs api` |
| "NoSuchBucket" | Verifique se bucket existe: `aws s3 ls` |

---

## Próximos Passos

- [ ] Deploy concluído
- [ ] Testes funcionando
- [ ] Logs aparecendo no S3
- [ ] Dashboard acessível
- [ ] Documentar IP público da EC2
- [ ] Configurar domínio (opcional)

---

## Documentação completa

Para mais detalhes, veja [DOCKER_EC2_DEPLOY.md](DOCKER_EC2_DEPLOY.md)
