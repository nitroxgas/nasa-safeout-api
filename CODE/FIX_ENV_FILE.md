# 🔧 Correção do Arquivo .env

**Problema:** O arquivo `.env` ainda contém `EARTHDATA_USERNAME` e `EARTHDATA_PASSWORD`, mas o código agora aceita apenas `EARTHDATA_TOKEN`.

**Erro:** `Extra inputs are not permitted`

---

## ⚡ Solução Rápida

### Opção 1: Editar Manualmente (Recomendado)

1. **Abra o arquivo:** `CODE/.env`
2. **Remova as linhas:**
   ```env
   EARTHDATA_USERNAME=safeoutdoor
   EARTHDATA_PASSWORD=B3Safe@there
   ```
3. **Mantenha apenas:**
   ```env
   EARTHDATA_TOKEN=eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4i...
   FIRMS_API_KEY=...
   ```
4. **Salve o arquivo**

### Opção 2: Via PowerShell

Execute no diretório `CODE`:

```powershell
# Backup do .env original
Copy-Item .env .env.backup

# Remover linhas de username/password
Get-Content .env | Where-Object { 
    $_ -notmatch "EARTHDATA_USERNAME" -and 
    $_ -notmatch "EARTHDATA_PASSWORD" 
} | Set-Content .env.temp

# Substituir arquivo
Move-Item -Force .env.temp .env

# Verificar
Get-Content .env | Select-String "EARTHDATA"
```

---

## ✅ Arquivo .env Correto

Após a correção, seu `.env` deve conter apenas:

```env
# NASA Earthdata Credentials
# Register at: https://urs.earthdata.nasa.gov/
# Generate token at: https://urs.earthdata.nasa.gov/profile
EARTHDATA_TOKEN=eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLCJzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ...

# NASA FIRMS API Key
# Get your key at: https://firms.modaps.eosdis.nasa.gov/api/
FIRMS_API_KEY=sua_chave_aqui

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=True
LOG_LEVEL=INFO

# Cache Configuration
CACHE_DIR=./cache
CACHE_EXPIRY_HOURS=6
```

**NÃO deve conter:**
- ❌ `EARTHDATA_USERNAME`
- ❌ `EARTHDATA_PASSWORD`

---

## 🧪 Como Verificar

### 1. Verificar variáveis no .env

```powershell
Get-Content .env | Select-String "EARTHDATA"
```

**Resultado esperado:**
```
EARTHDATA_TOKEN=eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4i...
```

**NÃO deve mostrar:**
- ❌ EARTHDATA_USERNAME
- ❌ EARTHDATA_PASSWORD

### 2. Testar a API

```powershell
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Iniciar API
uvicorn app.main:app --reload
```

**Resultado esperado:**
```
INFO: Started server process
INFO: Waiting for application startup.
INFO: Application startup complete.
INFO: Uvicorn running on http://127.0.0.1:8000
```

**NÃO deve mostrar:**
- ❌ ValidationError
- ❌ Extra inputs are not permitted

---

## 🔍 Troubleshooting

### Erro persiste após editar .env

**Causa:** Arquivo não foi salvo corretamente ou tem caracteres ocultos

**Solução:**
1. Feche e reabra o arquivo `.env`
2. Verifique se não há espaços extras
3. Salve com encoding UTF-8
4. Reinicie o terminal

### Erro: "EARTHDATA_TOKEN not set"

**Causa:** Token foi removido acidentalmente

**Solução:**
1. Verifique se a linha `EARTHDATA_TOKEN=...` existe
2. Verifique se o token está completo (sem quebras de linha)
3. Restaure do backup se necessário: `Copy-Item .env.backup .env`

### API não inicia

**Causa:** Ambiente virtual não está ativado

**Solução:**
```powershell
cd CODE
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

---

## ✅ Checklist

- [ ] Abri o arquivo `.env`
- [ ] Removi linha `EARTHDATA_USERNAME=...`
- [ ] Removi linha `EARTHDATA_PASSWORD=...`
- [ ] Mantive linha `EARTHDATA_TOKEN=...`
- [ ] Salvei o arquivo
- [ ] Verifiquei com `Get-Content .env | Select-String "EARTHDATA"`
- [ ] Ativei ambiente virtual
- [ ] Testei: `uvicorn app.main:app --reload`
- [ ] API iniciou sem erros

---

## 🎯 Resultado Final

Após a correção, você deve ver:

```
INFO: Started server process
2025-10-05 15:35:00 - app.services.earthdata - INFO - Authenticating with NASA Earthdata using token
2025-10-05 15:35:01 - app.services.earthdata - INFO - Successfully authenticated with NASA Earthdata using token
2025-10-05 15:35:01 - app.services.gibs - INFO - Connected to GIBS WMS
INFO: Application startup complete.
INFO: Uvicorn running on http://127.0.0.1:8000
```

**Sem erros de validação!** ✅

---

**Execute a Opção 1 (editar manualmente) agora e depois inicie a API!**
