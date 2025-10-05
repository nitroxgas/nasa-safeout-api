# Guia de Deploy - NASA SafeOut API

## 🚀 Opções de Deploy Gratuito

### Comparação de Plataformas

| Plataforma | Custo | RAM | Uptime | Cartão? | Dificuldade |
|------------|-------|-----|--------|---------|-------------|
| **Render** | Grátis | 512MB | Dorme após 15min | ❌ Não | ⭐ Fácil |
| **Railway** | $5/mês grátis | 512MB | 24/7 | ⚠️ Sim | ⭐ Fácil |
| **Fly.io** | Grátis | 256MB | 24/7 | ⚠️ Sim | ⭐⭐ Médio |
| **Heroku** | $5-7/mês | 512MB | 24/7 | ✅ Sim | ⭐ Fácil |

---

## 🏆 Opção 1: Render (Recomendado)

### Pré-requisitos
- Conta no GitHub com o repositório publicado
- Credenciais NASA Earthdata
- NASA FIRMS API Key

### Passo a Passo

#### 1. Criar Conta no Render
1. Acesse https://render.com
2. Clique em "Get Started for Free"
3. Conecte com sua conta GitHub

#### 2. Criar Web Service
1. No dashboard, clique em "New +"
2. Selecione "Web Service"
3. Conecte seu repositório `nasa-safeout-api`
4. Clique em "Connect"

#### 3. Configurar o Service

**Configurações Básicas:**
- **Name:** `nasa-safeout-api`
- **Region:** Oregon (US West)
- **Branch:** `main`
- **Root Directory:** (deixe vazio)
- **Runtime:** Python 3
- **Build Command:**
  ```bash
  cd CODE && pip install -r requirements.txt
  ```
- **Start Command:**
  ```bash
  cd CODE && uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

**Plan:**
- Selecione "Free"

#### 4. Configurar Environment Variables

Clique em "Advanced" e adicione:

```
EARTHDATA_USERNAME=seu_username_nasa
EARTHDATA_PASSWORD=sua_senha_nasa
FIRMS_API_KEY=sua_chave_firms
API_HOST=0.0.0.0
LOG_LEVEL=INFO
CACHE_DIR=/tmp/cache
```

#### 5. Deploy
1. Clique em "Create Web Service"
2. Aguarde o build (5-10 minutos)
3. Sua API estará disponível em: `https://nasa-safeout-api.onrender.com`

#### 6. Testar

```bash
curl https://nasa-safeout-api.onrender.com/health
```

### ⚠️ Importante sobre Render Free

- **Sleep Mode:** A API "dorme" após 15 minutos de inatividade
- **Cold Start:** Primeira requisição após dormir demora ~30 segundos
- **Solução:** Use um serviço de ping (UptimeRobot) para manter ativa

---

## 🚂 Opção 2: Railway

### Passo a Passo

#### 1. Criar Conta
1. Acesse https://railway.app
2. Faça login com GitHub
3. Adicione cartão de crédito (não será cobrado no plano free)

#### 2. Deploy
1. Clique em "New Project"
2. Selecione "Deploy from GitHub repo"
3. Escolha `nasa-safeout-api`
4. Railway detectará automaticamente Python

#### 3. Configurar
1. Vá em "Variables"
2. Adicione as mesmas variáveis do Render
3. Em "Settings", configure:
   - **Start Command:** `cd CODE && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### 4. Deploy Automático
- Railway fará deploy automaticamente
- URL será gerada automaticamente

---

## ✈️ Opção 3: Fly.io

### Pré-requisitos
- Instalar Fly CLI: https://fly.io/docs/hands-on/install-flyctl/

### Passo a Passo

#### 1. Instalar CLI

**Windows (PowerShell):**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

**Linux/Mac:**
```bash
curl -L https://fly.io/install.sh | sh
```

#### 2. Login
```bash
flyctl auth login
```

#### 3. Criar fly.toml

Crie o arquivo `fly.toml` na raiz:

```toml
app = "nasa-safeout-api"
primary_region = "gru"  # São Paulo

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8080"
  API_HOST = "0.0.0.0"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

#### 4. Deploy
```bash
cd D:\NASASafeOutData
flyctl launch
flyctl secrets set EARTHDATA_USERNAME=seu_username
flyctl secrets set EARTHDATA_PASSWORD=sua_senha
flyctl secrets set FIRMS_API_KEY=sua_chave
flyctl deploy
```

---

## 🔧 Configurações Adicionais

### 1. Manter API Ativa (Render)

Use **UptimeRobot** (gratuito):
1. Acesse https://uptimerobot.com
2. Crie um monitor HTTP(s)
3. URL: `https://sua-api.onrender.com/health`
4. Intervalo: 5 minutos

### 2. Configurar CORS para Frontend

Se você for criar um frontend, edite `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://seu-frontend.com"],  # Seu domínio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Logs e Monitoramento

**Render:**
- Logs em tempo real no dashboard
- Acesse: Dashboard → Service → Logs

**Railway:**
- Logs em tempo real no dashboard
- Acesse: Project → Deployments → Logs

---

## 📊 Comparação de Performance

### Render Free
- ✅ Bom para testes e demos
- ⚠️ Cold start de ~30s
- ⚠️ 512MB RAM (suficiente para a API)

### Railway Free
- ✅ Melhor performance
- ✅ Sem cold start
- ✅ $5/mês de crédito (renova mensalmente)

### Fly.io Free
- ✅ Ótima performance
- ✅ Região Brasil (São Paulo)
- ⚠️ Configuração mais técnica

---

## 🎯 Recomendação por Caso de Uso

### Para Testes Rápidos
→ **Render** (mais simples, sem cartão)

### Para Desenvolvimento Contínuo
→ **Railway** (melhor performance, sem sleep)

### Para Produção Leve
→ **Fly.io** (melhor latência no Brasil)

### Para Produção Séria
→ **AWS/GCP/Azure** (pago, mas robusto)

---

## 🐛 Troubleshooting

### Erro: "Application failed to start"
- Verifique o Start Command
- Confirme que `requirements.txt` está correto
- Veja os logs para detalhes

### Erro: "Port already in use"
- Use `$PORT` no comando uvicorn
- Render/Railway injetam a porta automaticamente

### API muito lenta
- Normal no primeiro acesso (cold start)
- Configure UptimeRobot para manter ativa

### Erro de autenticação NASA
- Verifique se as variáveis de ambiente estão corretas
- Teste localmente primeiro

---

## 📝 Checklist de Deploy

- [ ] Código no GitHub
- [ ] `.env` NÃO commitado (use .gitignore)
- [ ] Credenciais NASA Earthdata válidas
- [ ] FIRMS API Key obtida
- [ ] Plataforma escolhida
- [ ] Variáveis de ambiente configuradas
- [ ] Build bem-sucedido
- [ ] Health check funcionando
- [ ] Endpoint principal testado
- [ ] Documentação acessível (/docs)

---

## 🔗 Links Úteis

- **Render:** https://render.com
- **Railway:** https://railway.app
- **Fly.io:** https://fly.io
- **UptimeRobot:** https://uptimerobot.com
- **Documentação FastAPI Deploy:** https://fastapi.tiangolo.com/deployment/

---

## 💡 Dicas Finais

1. **Comece com Render** - É o mais simples para começar
2. **Use UptimeRobot** - Para evitar cold starts
3. **Monitore os logs** - Especialmente nas primeiras horas
4. **Teste localmente primeiro** - Garanta que tudo funciona antes do deploy
5. **Documente sua URL** - Atualize o README com a URL da API em produção

Boa sorte com o deploy! 🚀
