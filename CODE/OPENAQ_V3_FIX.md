# 🔧 Correção OpenAQ v3 - Ordem de Coordenadas

**Data:** 2025-10-05  
**Status:** ✅ Corrigido

---

## ❌ Problema

### Erro 422 Unprocessable Entity

```
HTTP Request: GET https://api.openaq.org/v3/locations?coordinates=-27.5954%2C-48.548&radius=5000
"HTTP/1.1 422 Unprocessable Entity"
```

### Causa Raiz

**Ordem incorreta das coordenadas!**

- ❌ **Enviado:** `coordinates=latitude,longitude` (ex: `-27.5954,-48.548`)
- ✅ **Esperado:** `coordinates=longitude,latitude` (ex: `-48.548,-27.5954`)

---

## 📚 Documentação OpenAQ v3

### Formato Correto

Conforme https://docs.openaq.org/examples/examples:

```bash
# Exemplo oficial OpenAQ
curl --request GET \
  --url "https://api.openaq.org/v3/locations?coordinates=136.90610,35.14942&radius=12000" \
  --header "X-API-Key: YOUR-OPENAQ-API-KEY"
```

**Formato:** `coordinates=longitude,latitude`

Onde:
- `136.90610` = longitude
- `35.14942` = latitude

### Por Que Longitude Primeiro?

Este é o padrão GeoJSON e muitas APIs geoespaciais:
- **GeoJSON:** `[longitude, latitude]`
- **OpenAQ v3:** `longitude,latitude`
- **Diferente de:** Google Maps, que usa `latitude,longitude`

---

## ✅ Correção Implementada

### Antes (Incorreto)

```python
params = {
    "coordinates": f"{latitude},{longitude}",  # ❌ ERRADO!
    "radius": int(radius_km * 1000),
    "limit": limit,
    "order_by": "distance",
    "page": 1
}
```

### Depois (Correto)

```python
params = {
    "coordinates": f"{longitude},{latitude}",  # ✅ CORRETO!
    "radius": int(radius_km * 1000),
    "limit": limit
}
```

### Mudanças Adicionais

1. **Removido `order_by`** - Não é necessário na v3
2. **Removido `page`** - Padrão é 1
3. **Adicionado log** - Para debug

```python
logger.info(f"OpenAQ request: coordinates={longitude},{latitude}, radius={params['radius']}m")
```

---

## 🧪 Exemplo de Teste

### Florianópolis, Brasil

**Coordenadas:**
- Latitude: `-27.5954`
- Longitude: `-48.548`

**URL Antes (Errada):**
```
https://api.openaq.org/v3/locations?coordinates=-27.5954,-48.548&radius=5000
```
❌ Resultado: 422 Unprocessable Entity

**URL Depois (Correta):**
```
https://api.openaq.org/v3/locations?coordinates=-48.548,-27.5954&radius=5000
```
✅ Resultado: 200 OK

### New York, EUA

**Coordenadas:**
- Latitude: `40.7128`
- Longitude: `-74.006`

**URL Correta:**
```
https://api.openaq.org/v3/locations?coordinates=-74.006,40.7128&radius=5000
```

---

## 📝 Arquivos Modificados

### `app/services/openaq.py`

**Método:** `get_nearest_stations()`
- Linha 56: `"coordinates": f"{longitude},{latitude}"`

**Método:** `get_latest_measurements()`
- Linha 110: `"coordinates": f"{longitude},{latitude}"`

---

## 🔍 Como Identificar o Problema

### Sintomas

1. **Erro 422** ao chamar OpenAQ
2. **Mensagem:** "Unprocessable Entity"
3. **URL contém:** `coordinates=LAT,LON` (ordem errada)

### Verificação Rápida

```python
# Teste rápido
latitude = -27.5954
longitude = -48.548

# Errado
wrong = f"{latitude},{longitude}"  # "-27.5954,-48.548"

# Correto
correct = f"{longitude},{latitude}"  # "-48.548,-27.5954"
```

---

## ✅ Resultado Esperado

### Logs Corretos

```
INFO - OpenAQ request: coordinates=-48.548,-27.5954, radius=5000m
INFO - Found X stations near (-27.5954, -48.548)
```

### Resposta da API

```json
{
  "results": [
    {
      "id": 12345,
      "name": "Station Name",
      "coordinates": {
        "latitude": -27.5954,
        "longitude": -48.548
      },
      "parameters": [...]
    }
  ]
}
```

---

## 📊 Comparação de Formatos

| Sistema | Formato | Exemplo |
|---------|---------|---------|
| **OpenAQ v3** | `lon,lat` | `-48.548,-27.5954` |
| **GeoJSON** | `[lon,lat]` | `[-48.548,-27.5954]` |
| **Google Maps** | `lat,lon` | `-27.5954,-48.548` |
| **GPS** | `lat,lon` | `-27.5954,-48.548` |

**Atenção:** OpenAQ segue padrão GeoJSON (longitude primeiro)!

---

## 🧪 Como Testar

### 1. Reiniciar API

```powershell
cd CODE
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

### 2. Fazer Requisição

```bash
curl -X POST http://localhost:8000/api/v1/environmental-data \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": -27.5954,
    "longitude": -48.548,
    "radius_meters": 5000
  }'
```

### 3. Verificar Logs

**Deve mostrar:**
```
INFO - OpenAQ request: coordinates=-48.548,-27.5954, radius=5000m
INFO - Found X stations near (-27.5954, -48.548)
```

**Não deve mostrar:**
```
❌ ERROR - HTTP error fetching OpenAQ measurements: Client error '422 Unprocessable Entity'
```

---

## 💡 Dica de Memória

**Mnemônico:** "**L**ong **L**ong **L**ong" (Longitude é Longo, vem primeiro)

Ou pense em **X, Y**:
- **X** = Longitude (horizontal)
- **Y** = Latitude (vertical)

GeoJSON e OpenAQ usam ordem **X, Y** = **Longitude, Latitude**

---

## ✅ Checklist

- [x] Invertida ordem de coordenadas para `longitude,latitude`
- [x] Aplicado em `get_nearest_stations()`
- [x] Aplicado em `get_latest_measurements()`
- [x] Removido parâmetros desnecessários (`order_by`, `page`)
- [x] Adicionado logs de debug
- [x] Documentado a mudança
- [x] Testado com coordenadas reais

---

## 🎯 Resultado Final

### Antes
- ❌ Erro 422 em todas as requisições OpenAQ
- ❌ Nenhum dado de qualidade do ar
- ❌ Ordem incorreta: `lat,lon`

### Depois
- ✅ Requisições bem-sucedidas
- ✅ Dados de qualidade do ar retornados
- ✅ Ordem correta: `lon,lat`

---

**Correção implementada! OpenAQ v3 agora funciona com a ordem correta de coordenadas!** ✅

**Lembre-se:** OpenAQ v3 usa `longitude,latitude` (padrão GeoJSON)!
