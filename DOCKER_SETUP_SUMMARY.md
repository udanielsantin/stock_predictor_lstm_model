# 📦 Docker Setup - Resumo Executivo

## O que foi configurado

### 1. **Dockerfile** (`api/Dockerfile`)
- ✅ Baseado em Python 3.11-slim
- ✅ Instala dependências (boto3, matplotlib, etc.)
- ✅ Copia modelos e source code
- ✅ **NÃO cria mais pasta local de logs** (usa S3)
- ✅ Health check integrado
- ✅ Rodando na porta 8000

### 2. **Docker Compose** (`docker-compose.yml`)
- ✅ Serviço API configurado
- ✅ Variáveis de ambiente para S3
- ✅ Volumes read-only para modelos e código
- ✅ **SEM volume local para logs** (tudo no S3)
- ✅ Auto-restart configurado
- ✅ Health check

### 3. **.dockerignore** (`.dockerignore`)
- ✅ Excluir Git, venv, notebooks, etc.
- ✅ Imagem final otimizada (~800MB)
- ✅ Sem dados desnecessários

### 4. **Scripts de Deploy**

#### `setup-docker.sh`
Instala Docker, Docker Compose e Git:
```bash
bash setup-docker.sh
```

#### `deploy.sh`
Deploy completo com validações:
```bash
bash deploy.sh
```

#### `stop.sh`
Para o container com limpeza opcional:
```bash
bash stop.sh
```

### 5. **Documentação**

| Arquivo | Propósito |
|---------|-----------|
| `DOCKER_EC2_DEPLOY.md` | Guia completo e detalhado |
| `QUICK_START_EC2.md` | Resumo em 5 minutos |
| `.env.example` | Template de variáveis |

---

## Fluxo de Deploy no EC2

```
┌─────────────────────────────────────────────┐
│ 1. SSH para EC2                             │
│    ssh -i key.pem ubuntu@ip                 │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│ 2. Setup Docker (primeira vez)               │
│    bash setup-docker.sh                     │
│    (saída e reconectar)                     │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│ 3. Clone repositório                        │
│    git clone <repo>                         │
│    cd stock_predictor_lstm_model            │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│ 4. Configurar .env                          │
│    cat > .env << EOF                        │
│    AWS_ACCESS_KEY_ID=...                    │
│    AWS_SECRET_ACCESS_KEY=...                │
│    ...                                       │
│    EOF                                       │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│ 5. Deploy com Docker                        │
│    bash deploy.sh                           │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│ 6. Testar API                               │
│    curl http://localhost:8000/health        │
│    curl -X POST http://localhost:8000/api   │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│ ✅ API rodando no S3                        │
│    Logs salvos em S3                        │
│    Dashboard funcional                      │
└─────────────────────────────────────────────┘
```

---

## Arquivos Modificados

```
stock_predictor_lstm_model/
├── api/
│   ├── Dockerfile              ✅ ATUALIZADO (sem pasta logs/)
│   └── log_utils.py            ✅ S3-only
├── docker-compose.yml          ✅ ATUALIZADO (com S3 vars)
├── .dockerignore                ✅ ATUALIZADO
├── .env.example                ✅ NOVO (template)
├── setup-docker.sh             ✅ NOVO
├── deploy.sh                   ✅ NOVO
├── stop.sh                     ✅ NOVO
├── DOCKER_EC2_DEPLOY.md        ✅ NOVO (guia detalhado)
├── QUICK_START_EC2.md          ✅ NOVO (resumo rápido)
└── DOCKER_SETUP_SUMMARY.md     ✅ NOVO (este arquivo)
```

---

## Variáveis de Ambiente

Essas variáveis devem estar no `.env`:

```env
# Obrigatórias
AWS_ACCESS_KEY_ID=sua-chave
AWS_SECRET_ACCESS_KEY=sua-senha
S3_BUCKET_NAME=vapor-stock-predictor-logs

# Opcionais (têm defaults)
AWS_REGION=us-east-1          # (padrão: us-east-1)
S3_LOG_PREFIX=logs/           # (padrão: logs/)
```

---

## Checklist Final

### Antes do Deploy

- [ ] EC2 criada (Ubuntu 24.04, t3.medium)
- [ ] Security Group aberto (porta 22, 8000)
- [ ] Bucket S3 criado (`vapor-stock-predictor-logs`)
- [ ] Credenciais AWS em mãos

### Primeiro Deploy

- [ ] SSH conectado à EC2
- [ ] Correr `bash setup-docker.sh`
- [ ] Logout e reconectar
- [ ] Clonar repositório
- [ ] Criar `.env` com credenciais
- [ ] Correr `bash deploy.sh`
- [ ] Validar que subiu (curl health check)

### Testes

- [ ] Health check: `curl http://localhost:8000/health`
- [ ] Fazer previsão (curl POST)
- [ ] Logs aparecem no S3
- [ ] Dashboard acessível
- [ ] Stats funcionam

### Produção

- [ ] Container rodando
- [ ] Auto-restart ativado
- [ ] Logs em S3
- [ ] Monitorar com CloudWatch (opcional)
- [ ] Documentar IP público

---

## Tamanho da Imagem

```
REPOSITORY          SIZE
stock-lstm-api      ~850MB (slim Python + deps)
```

Comparação:
- Python:3.11-slim: ~150MB
- Dependências: ~700MB
- Seu código: minimal

---

## Storage no EC2

- **Root volume:** 20GB (suficiente)
  - OS: ~5GB
  - Docker images: ~1GB
  - Containers: minimal
  - Resto: livre

---

## Segurança

### ✅ Implementado

- [ ] `.env` não é commitado (.gitignore)
- [ ] Permissões do `.env` (chmod 600)
- [ ] Credenciais não em logs Docker
- [ ] Container rodando como usuário ubuntu
- [ ] Volumes read-only para código/modelos

### ⏭️ Recomendações Futuras

- [ ] Usar IAM Roles em vez de credenciais diretas
- [ ] Adicionar HTTPS/SSL
- [ ] Autenticação na API
- [ ] Limitar acesso por IP

---

## Troubleshooting Rápido

| Erro | Solução |
|------|---------|
| "docker: command not found" | `bash setup-docker.sh` |
| "Permission denied" | `sudo usermod -aG docker $USER` |
| ".env not found" | `cat > .env << EOF ... EOF` |
| "S3_BUCKET_NAME is required" | Verifique `.env` |
| "Container won't start" | `docker-compose logs api` |

---

## Próximos Passos

1. ✅ Setup Docker concluído
2. ⏭️ Deploy no EC2
3. ⏭️ Monitorar em produção
4. ⏭️ Configurar alertas CloudWatch
5. ⏭️ Setup CI/CD (opcional)

---

## Documentação Adicional

- [DOCKER_EC2_DEPLOY.md](DOCKER_EC2_DEPLOY.md) - Guia completo
- [QUICK_START_EC2.md](QUICK_START_EC2.md) - 5 minutos
- [S3_SETUP.md](S3_SETUP.md) - Configuração S3
- [TEST_S3_LOCAL.md](TEST_S3_LOCAL.md) - Testes locais

---

**Status:** ✅ Pronto para Deploy

Data: 2025-12-26
