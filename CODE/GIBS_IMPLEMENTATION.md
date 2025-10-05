# 🛰️ NASA GIBS Implementation

**Data:** 2025-10-05  
**Status:** ✅ Implementado e Funcional

---

## 📋 O Que é GIBS?

**GIBS (Global Imagery Browse Services)** é um serviço da NASA que fornece acesso rápido a imagens de satélite e visualizações de dados ambientais.

### Características
- ✅ **Sem autenticação necessária** (serviço público)
- ✅ **Acesso via WMS/WMTS** (padrões OGC)
- ✅ **1000+ camadas de dados** disponíveis
- ✅ **Dados em tempo quase real** (latência de horas)
- ✅ **Cobertura global**

---

## 🎯 Camadas Implementadas

A API agora fornece URLs para as seguintes camadas GIBS:

| Camada | Descrição | Atualização |
|--------|-----------|-------------|
| **True Color** | Imagem de satélite em cores reais | Diária |
| **Aerosol** | Índice de aerosol (qualidade do ar) | Diária |
| **Cloud Top Temp** | Temperatura do topo das nuvens | Diária |
| **Precipitation** | Taxa de precipitação | 30 minutos |
| **Land Surface Temp (Day)** | Temperatura da superfície (dia) | Diária |
| **Land Surface Temp (Night)** | Temperatura da superfície (noite) | Diária |
| **Fires** | Anomalias térmicas e incêndios | Diária |
| **Snow Cover** | Cobertura de neve | Diária |
| **Vegetation (NDVI)** | Índice de vegetação | 8 dias |

---

## 🏗️ Arquitetura

### Arquivos Criados

1. **`app/services/gibs.py`** - Serviço GIBS completo
   - Conexão com WMS
   - Geração de URLs de imagens
   - Métodos especializados para diferentes tipos de dados

2. **Integração no `data_processor.py`**
   - Método `get_gibs_imagery()`
   - Chamado automaticamente no endpoint principal

3. **Schema atualizado** (`models/schemas.py`)
   - Campo `satellite_imagery` adicionado a `EnvironmentalData`

---

## 📊 Exemplo de Resposta

### Endpoint: POST /api/v1/environmental-data

```json
{
  "data": {
    "satellite_imagery": {
      "source": "NASA GIBS",
      "date": "2025-10-05",
      "location": {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "bbox": [-74.0510, 40.6678, -74.0060, 40.7578]
      },
      "imagery": {
        "true_color": {
          "layer": "MODIS_Terra_CorrectedReflectance_TrueColor",
          "url": "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?...",
          "description": "True color satellite imagery"
        },
        "aerosol": {
          "layer": "MODIS_Combined_Value_Added_AOD",
          "url": "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?...",
          "description": "Aerosol Optical Depth (air quality indicator)"
        },
        "precipitation": {
          "layer": "GPM_3IMERGHH_Precipitation_Rate",
          "url": "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?...",
          "description": "Precipitation rate"
        },
        "fires": {
          "layer": "MODIS_Terra_Thermal_Anomalies_All",
          "url": "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?...",
          "description": "Thermal anomalies and fires"
        }
        // ... mais camadas
      },
      "timestamp": "2025-10-05T14:30:00Z"
    }
  }
}
```

---

## 🔧 Como Usar as URLs

### 1. Visualizar no Navegador

Simplesmente abra a URL no navegador para ver a imagem:

```
https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=MODIS_Terra_CorrectedReflectance_TrueColor&...
```

### 2. Usar em Aplicação Web

```html
<img src="[URL_DA_IMAGEM]" alt="Satellite Imagery" />
```

### 3. Usar com Leaflet/OpenLayers

```javascript
// Leaflet
L.tileLayer.wms("https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi", {
    layers: 'MODIS_Terra_CorrectedReflectance_TrueColor',
    format: 'image/png',
    transparent: true
}).addTo(map);
```

### 4. Processar com Python

```python
import requests
from PIL import Image
from io import BytesIO

# Baixar imagem
response = requests.get(url)
img = Image.open(BytesIO(response.content))
img.show()
```

---

## 🎨 Casos de Uso

### 1. Monitoramento de Incêndios

```python
# Obter imagens de incêndio dos últimos 7 dias
fire_imagery = gibs_service.get_fire_imagery(
    latitude=34.0522,  # Los Angeles
    longitude=-118.2437,
    radius_km=100,
    days_back=7
)
```

### 2. Análise de Precipitação

```python
# Obter imagens de precipitação das últimas 24 horas
precip_imagery = gibs_service.get_precipitation_imagery(
    latitude=40.7128,  # New York
    longitude=-74.0060,
    radius_km=50,
    hours_back=24
)
```

### 3. Visualização de Qualidade do Ar

```python
# Obter dados ambientais completos com imagens
env_data = gibs_service.get_environmental_data(
    latitude=-23.5505,  # São Paulo
    longitude=-46.6333,
    radius_km=25
)
```

---

## 📈 Vantagens do GIBS

### vs. Earthdata (earthaccess)

| Aspecto | GIBS | Earthdata |
|---------|------|-----------|
| **Autenticação** | ❌ Não requer | ✅ Requer |
| **Velocidade** | ⚡ Muito rápido (< 1s) | 🐌 Lento (30-60s) |
| **Formato** | 🖼️ Imagens PNG/JPEG | 📊 NetCDF/HDF5 |
| **Uso** | 👁️ Visualização | 🔢 Análise numérica |
| **Tamanho** | 📦 Pequeno (KB) | 📦 Grande (MB) |
| **Processamento** | ✅ Pronto para uso | ⚙️ Requer processamento |

### Quando Usar Cada Um

**Use GIBS quando:**
- ✅ Precisa de visualização rápida
- ✅ Quer mostrar imagens para usuários
- ✅ Não precisa de valores numéricos exatos
- ✅ Quer evitar autenticação

**Use Earthdata quando:**
- ✅ Precisa de valores numéricos precisos
- ✅ Vai fazer análise científica
- ✅ Precisa de dados brutos
- ✅ Quer processar dados localmente

---

## 🔍 Camadas Disponíveis

### Qualidade do Ar
- `MODIS_Combined_Value_Added_AOD` - Aerosol Optical Depth
- `AIRS_L2_Carbon_Monoxide_500hPa_Volume_Mixing_Ratio_Day` - CO
- `OMI_Aerosol_Index` - Índice de Aerosol

### Clima
- `MODIS_Terra_Land_Surface_Temp_Day` - Temperatura superfície (dia)
- `MODIS_Terra_Land_Surface_Temp_Night` - Temperatura superfície (noite)
- `AIRS_L2_Surface_Air_Temperature_Day` - Temperatura do ar

### Precipitação
- `GPM_3IMERGHH_Precipitation_Rate` - Taxa de precipitação
- `GPM_3IMERGHH_Snow_Rate` - Taxa de neve

### Incêndios
- `MODIS_Terra_Thermal_Anomalies_All` - Anomalias térmicas (Terra)
- `MODIS_Aqua_Thermal_Anomalies_All` - Anomalias térmicas (Aqua)
- `VIIRS_SNPP_Thermal_Anomalies_375m_All` - VIIRS (alta resolução)

### Vegetação
- `MODIS_Terra_NDVI_8Day` - Índice de vegetação
- `MODIS_Terra_EVI_8Day` - Índice de vegetação melhorado

### Neve e Gelo
- `MODIS_Terra_Snow_Cover` - Cobertura de neve
- `MODIS_Terra_Sea_Ice` - Gelo marinho

---

## 🚀 Performance

### Tempos de Resposta

| Operação | Tempo |
|----------|-------|
| Gerar URL | < 1ms |
| Download imagem (512x512) | 100-500ms |
| Download imagem (1024x1024) | 200-1000ms |
| Múltiplas camadas | 1-3 segundos |

### Otimizações

1. **URLs são geradas, não baixadas**
   - Cliente pode baixar sob demanda
   - Reduz carga no servidor
   - Mais rápido para usuário final

2. **Cache do navegador**
   - Imagens podem ser cacheadas
   - Reduz requisições repetidas

3. **Tamanho configurável**
   - Ajuste width/height conforme necessário
   - Menor = mais rápido

---

## 📝 Dependências

### Adicionadas ao requirements.txt

```
OWSLib==0.29.3  # Cliente WMS/WMTS
```

### Bibliotecas Usadas

- `owslib.wms.WebMapService` - Conexão WMS
- `requests` - HTTP requests (já instalado)

---

## ✅ Checklist de Implementação

- [x] Criar serviço GIBS (`gibs.py`)
- [x] Integrar no DataProcessor
- [x] Adicionar ao endpoint da API
- [x] Atualizar schema (satellite_imagery)
- [x] Adicionar OWSLib ao requirements.txt
- [x] Documentar implementação
- [x] Testar funcionalidade

---

## 🧪 Como Testar

### 1. Instalar Dependências

```bash
cd CODE
pip install OWSLib==0.29.3
```

### 2. Testar Diretamente

```python
from app.services.gibs import GIBSService

gibs = GIBSService()
data = gibs.get_environmental_data(40.7128, -74.0060, 5.0)
print(data)
```

### 3. Testar via API

```bash
curl -X POST http://localhost:8000/api/v1/environmental-data \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 40.7128,
    "longitude": -74.0060,
    "radius_meters": 5000
  }'
```

Verifique o campo `satellite_imagery` na resposta!

---

## 🎯 Próximos Passos (Opcional)

### Melhorias Futuras

1. [ ] **Cache de URLs**
   - Armazenar URLs geradas
   - Evitar regeneração

2. [ ] **Download de imagens**
   - Opção para baixar e servir imagens
   - Processar imagens localmente

3. [ ] **Análise de pixels**
   - Extrair valores de pixels específicos
   - Converter cores em valores numéricos

4. [ ] **Animações**
   - Gerar GIFs de séries temporais
   - Visualizar mudanças ao longo do tempo

5. [ ] **Mais camadas**
   - Adicionar camadas específicas por região
   - Camadas sazonais

---

**GIBS está implementado e funcional! URLs de imagens de satélite agora disponíveis na API!** 🛰️✨
