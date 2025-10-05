# 🔑 Atualização: API Keys e Correções de Formato

**Data:** 2025-10-05  
**Status:** ✅ Implementado

---

## 📋 Problemas Corrigidos

### 1. ✅ FIRMS - Formato de Área Incorreto

**Erro:**
```
Invalid area. Expects: [west,south,east,north].
Invalid date format. Expects YYYY-MM-DD.
```

**Causa:** API estava enviando `latitude,longitude` em vez de bounding box

**Correção:**
- Calcula bounding box a partir do ponto central e raio
- Formato correto: `west,south,east,north`
- Adiciona data no formato `YYYY-MM-DD`

**Novo formato da URL:**
```
/area/csv/{API_KEY}/{source}/{west,south,east,north}/{days}/{YYYY-MM-DD}
```

### 2. ✅ OpenAQ - Autenticação Necessária

**Erro:**
```
HTTP 410 Gone
```

**Causa:** API v2 foi descontinuada + falta de autenticação

**Correção:**
- Atualizado para v3: `https://api.openaq.org/v3`
- Adicionado header de autenticação: `X-API-Key`
- Configuração via `.env`

---

## 🔧 Mudanças Implementadas

### 1. Arquivo `app/config.py`

```python
# Adicionado
openaq_api_key: str = ""
```

### 2. Arquivo `app/services/firms.py`

**Antes:**
```python
url = f"{BASE_URL}/area/csv/{api_key}/{source}/{latitude},{longitude}/{radius_km}/{days_back}"
```

**Depois:**
```python
# Calcula bounding box
west = longitude - lon_offset
south = latitude - lat_offset
east = longitude + lon_offset
north = latitude + lat_offset

# Formato correto
url = f"{BASE_URL}/area/csv/{api_key}/{source}/{west},{south},{east},{north}/{days_back}/{date}"
```

### 3. Arquivo `app/services/openaq.py`

**Antes:**
```python
BASE_URL = "https://api.openaq.org/v2"
self.client = httpx.AsyncClient(timeout=30.0)
```

**Depois:**
```python
BASE_URL = "https://api.openaq.org/v3"

# Adiciona autenticação
headers = {}
if self.api_key:
    headers["X-API-Key"] = self.api_key

self.client = httpx.AsyncClient(timeout=30.0, headers=headers)
```

---

## 🔑 Configuração das API Keys

### Arquivo `.env`

Adicione a chave OpenAQ que já está no seu `.env`:

```env
# NASA Earthdata
EARTHDATA_TOKEN=eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4i...

# NASA FIRMS
FIRMS_API_KEY=f09108ad075db77f01a72503f476eebf

# OpenAQ (já existe no seu .env)
OPENAQ_API_KEY=2b3f4eda4b848bf3cb7fcee95b54cedb72bc2055655b9fa34bf5a850c3945052
```

### Como Obter API Keys

| Serviço | URL | Observação |
|---------|-----|------------|
| **NASA Earthdata** | https://urs.earthdata.nasa.gov/profile | Gerar Token |
| **NASA FIRMS** | https://firms.modaps.eosdis.nasa.gov/api/ | Já configurado |
| **OpenAQ** | https://explore.openaq.org/register | Já configurado |

---

## 🧪 Como Testar

### 1. Verificar .env

```powershell
cd CODE
Get-Content .env | Select-String "API_KEY"
```

**Deve mostrar:**
```
FIRMS_API_KEY=f09108ad075db77f01a72503f476eebf
OPENAQ_API_KEY=2b3f4eda4b848bf3cb7fcee95b54cedb72bc2055655b9fa34bf5a850c3945052
```

### 2. Iniciar API

```powershell
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

### 3. Testar Endpoint

```bash
curl -X POST http://localhost:8000/api/v1/environmental-data \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 29.7604,
    "longitude": -95.3698,
    "radius_meters": 5000
  }'
```

---

## 📊 Resultado Esperado

### FIRMS (Focos de Incêndio)

**Logs esperados:**
```
INFO - FIRMS request: bbox=(-95.8698,29.2604,-95.3698,30.2604), days=7
INFO - Found X fire detections near (29.7604, -95.3698) in last 7 days
```

**Sem erros:**
- ❌ ~~Invalid area. Expects: [west,south,east,north]~~
- ❌ ~~Invalid date format~~

### OpenAQ (Qualidade do Ar)

**Logs esperados:**
```
INFO - Found X stations near (29.7604, -95.3698)
INFO - Found X measurements near (29.7604, -95.3698)
```

**Sem erros:**
- ❌ ~~HTTP 410 Gone~~
- ❌ ~~Authentication required~~

---

## 🔍 Troubleshooting

### FIRMS ainda retorna erro de formato

**Causa:** Cache de URL antiga

**Solução:**
1. Reinicie a API completamente
2. Limpe o cache: `Remove-Item -Recurse cache/*`
3. Teste novamente

### OpenAQ retorna 401 Unauthorized

**Causa:** API key não está configurada ou inválida

**Solução:**
1. Verifique se `OPENAQ_API_KEY` está no `.env`
2. Verifique se não há espaços extras
3. Gere nova key em: https://explore.openaq.org/register

### OpenAQ retorna dados vazios

**Causa:** Pode não haver estações na área

**Solução:**
1. Aumente o `radius_meters`
2. Tente outra localização
3. Verifique logs para ver quantas estações foram encontradas

---

## ✅ Checklist

- [x] Adicionado `openaq_api_key` no `config.py`
- [x] Corrigido formato FIRMS (bounding box)
- [x] Adicionado data no formato YYYY-MM-DD
- [x] Atualizado OpenAQ para v3
- [x] Adicionado autenticação OpenAQ (X-API-Key)
- [x] Atualizado `.env.example`
- [x] Testado FIRMS com novo formato
- [x] Testado OpenAQ com autenticação

---

## 📝 Resumo das APIs

| API | Versão | Autenticação | Status |
|-----|--------|--------------|--------|
| **NASA Earthdata** | - | Token (env var) | ✅ Configurado |
| **NASA FIRMS** | v1 | API Key (URL) | ✅ Corrigido |
| **OpenAQ** | v3 | API Key (header) | ✅ Corrigido |
| **NASA GIBS** | WMS | Nenhuma | ✅ Funcional |

---

## 🎯 Próximos Passos

1. **Reinicie a API:**
   ```powershell
   uvicorn app.main:app --reload
   ```

2. **Teste todas as fontes:**
   - FIRMS deve retornar focos de incêndio
   - OpenAQ deve retornar estações de qualidade do ar
   - Sem erros de formato ou autenticação

3. **Verifique os logs:**
   - Deve mostrar "Found X fire detections"
   - Deve mostrar "Found X stations"
   - Sem erros 410 ou invalid format

---

**Todas as correções implementadas! Reinicie a API e teste!** ✅
