# Documentação da API - NASA SafeOut

## Visão Geral

API REST para consulta de dados ambientais baseados em localização geográfica, integrando múltiplas fontes de dados da NASA e outras organizações.

## Base URL

```
http://localhost:8000/api/v1
```

## Autenticação

A API não requer autenticação do usuário final, mas o servidor precisa de credenciais NASA Earthdata configuradas.

## Endpoints

### 1. Obter Dados Ambientais

Retorna dados ambientais agregados para uma localização específica.

**Endpoint:** `POST /environmental-data`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "latitude": -27.5954,
  "longitude": -48.5480,
  "radius_meters": 5000
}
```

**Parâmetros:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| latitude | float | Sim | Latitude em graus decimais (-90 a 90) |
| longitude | float | Sim | Longitude em graus decimais (-180 a 180) |
| radius_meters | integer | Sim | Raio de busca em metros (100 a 50000) |

**Response (200 OK):**
```json
{
  "location": {
    "latitude": -27.5954,
    "longitude": -48.5480,
    "radius_meters": 5000
  },
  "timestamp": "2025-10-04T21:47:09Z",
  "data": {
    "precipitation": {
      "source": "GPM_3IMERGHHE",
      "last_update": "2025-10-04T20:00:00Z",
      "forecast_hours": [
        {
          "hour": 1,
          "rate_mm_h": 2.5,
          "confidence": "high"
        },
        {
          "hour": 2,
          "rate_mm_h": 3.1,
          "confidence": "high"
        }
      ],
      "daily_accumulation_mm": 45.2
    },
    "air_quality": {
      "satellite": {
        "source": "TROPOMI/Sentinel-5P",
        "last_update": "2025-10-04T12:00:00Z",
        "aerosol_index": 1.2,
        "no2_mol_m2": 0.00015,
        "quality_flag": "good"
      },
      "ground_stations": {
        "source": "OpenAQ",
        "last_update": "2025-10-04T21:30:00Z",
        "stations_count": 3,
        "stations": [
          {
            "location": "Florianópolis Centro",
            "distance_km": 2.3,
            "measurements": {
              "pm25": {
                "value": 15.2,
                "unit": "µg/m³",
                "aqi": "good"
              },
              "pm10": {
                "value": 25.3,
                "unit": "µg/m³",
                "aqi": "good"
              },
              "no2": {
                "value": 12.1,
                "unit": "µg/m³",
                "aqi": "good"
              }
            },
            "last_update": "2025-10-04T21:00:00Z"
          }
        ],
        "average": {
          "pm25": 14.8,
          "pm10": 24.1,
          "no2": 11.5,
          "overall_aqi": "good"
        }
      }
    },
    "weather": {
      "source": "MERRA-2",
      "last_update": "2025-10-04T21:00:00Z",
      "temperature_celsius": 22.5,
      "temperature_fahrenheit": 72.5,
      "humidity_percent": 75.0,
      "wind": {
        "speed_m_s": 3.2,
        "speed_km_h": 11.5,
        "direction_degrees": 180,
        "direction_cardinal": "S"
      },
      "pressure_hpa": 1013.2
    },
    "uv_index": {
      "source": "TROPOMI",
      "last_update": "2025-10-04T12:00:00Z",
      "value": 7.5,
      "category": "high",
      "recommendation": "Proteção necessária. Use protetor solar e evite exposição prolongada."
    },
    "fire_history": {
      "source": "NASA FIRMS",
      "period_days": 7,
      "last_update": "2025-10-04T21:00:00Z",
      "active_fires_count": 2,
      "fires": [
        {
          "latitude": -27.60,
          "longitude": -48.55,
          "distance_km": 1.2,
          "brightness_kelvin": 320.5,
          "confidence": "high",
          "confidence_percent": 85,
          "date": "2025-10-04T18:30:00Z",
          "satellite": "VIIRS"
        },
        {
          "latitude": -27.58,
          "longitude": -48.52,
          "distance_km": 3.8,
          "brightness_kelvin": 315.2,
          "confidence": "medium",
          "confidence_percent": 65,
          "date": "2025-10-03T14:20:00Z",
          "satellite": "MODIS"
        }
      ]
    }
  },
  "metadata": {
    "processing_time_ms": 1250,
    "data_sources_queried": 5,
    "data_sources_successful": 5,
    "warnings": []
  }
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Invalid coordinates: latitude must be between -90 and 90"
}
```

**Response (500 Internal Server Error):**
```json
{
  "detail": "Error fetching data from NASA Earthdata",
  "error_code": "EARTHDATA_ERROR",
  "timestamp": "2025-10-04T21:47:09Z"
}
```

**Response (503 Service Unavailable):**
```json
{
  "detail": "One or more data sources are temporarily unavailable",
  "available_data": {
    "precipitation": true,
    "air_quality": false,
    "weather": true,
    "uv_index": true,
    "fire_history": false
  },
  "timestamp": "2025-10-04T21:47:09Z"
}
```

### 2. Health Check

Verifica o status da API e das fontes de dados.

**Endpoint:** `GET /health`

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-04T21:47:09Z",
  "services": {
    "api": "up",
    "earthdata": "up",
    "openaq": "up",
    "firms": "up"
  },
  "version": "1.0.0"
}
```

### 3. Informações da API

Retorna informações sobre a API e suas capacidades.

**Endpoint:** `GET /info`

**Response (200 OK):**
```json
{
  "name": "NASA SafeOut API",
  "version": "1.0.0",
  "description": "API para consulta de dados ambientais da NASA e outras fontes",
  "data_sources": [
    {
      "name": "GPM IMERG",
      "type": "precipitation",
      "provider": "NASA",
      "update_frequency": "30 minutes"
    },
    {
      "name": "TROPOMI/Sentinel-5P",
      "type": "air_quality",
      "provider": "ESA/NASA",
      "update_frequency": "daily"
    },
    {
      "name": "OpenAQ",
      "type": "air_quality_ground",
      "provider": "OpenAQ",
      "update_frequency": "hourly"
    },
    {
      "name": "MERRA-2",
      "type": "weather",
      "provider": "NASA",
      "update_frequency": "hourly"
    },
    {
      "name": "NASA FIRMS",
      "type": "fire_detection",
      "provider": "NASA",
      "update_frequency": "near real-time"
    }
  ],
  "limits": {
    "max_radius_meters": 50000,
    "min_radius_meters": 100,
    "rate_limit": "100 requests per minute"
  }
}
```

## Códigos de Status HTTP

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 400 | Requisição inválida (parâmetros incorretos) |
| 429 | Muitas requisições (rate limit excedido) |
| 500 | Erro interno do servidor |
| 503 | Serviço temporariamente indisponível |

## Categorias de Qualidade do Ar (AQI)

| Categoria | Faixa PM2.5 (µg/m³) | Descrição |
|-----------|---------------------|-----------|
| good | 0-12 | Boa |
| moderate | 12-35.4 | Moderada |
| unhealthy_sensitive | 35.5-55.4 | Insalubre para grupos sensíveis |
| unhealthy | 55.5-150.4 | Insalubre |
| very_unhealthy | 150.5-250.4 | Muito insalubre |
| hazardous | 250.5+ | Perigosa |

## Categorias de Índice UV

| Categoria | Faixa | Recomendação |
|-----------|-------|--------------|
| low | 0-2 | Baixo risco. Proteção mínima necessária. |
| moderate | 3-5 | Risco moderado. Use protetor solar. |
| high | 6-7 | Alto risco. Proteção necessária. |
| very_high | 8-10 | Risco muito alto. Proteção extra necessária. |
| extreme | 11+ | Risco extremo. Evite exposição ao sol. |

## Exemplos de Uso

### Python (requests)
```python
import requests

url = "http://localhost:8000/api/v1/environmental-data"
payload = {
    "latitude": -27.5954,
    "longitude": -48.5480,
    "radius_meters": 5000
}

response = requests.post(url, json=payload)
data = response.json()
print(f"Temperatura: {data['data']['weather']['temperature_celsius']}°C")
```

### JavaScript (fetch)
```javascript
const url = "http://localhost:8000/api/v1/environmental-data";
const payload = {
  latitude: -27.5954,
  longitude: -48.5480,
  radius_meters: 5000
};

fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(payload)
})
  .then(response => response.json())
  .then(data => {
    console.log(`Temperatura: ${data.data.weather.temperature_celsius}°C`);
  });
```

### cURL
```bash
curl -X POST "http://localhost:8000/api/v1/environmental-data" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": -27.5954,
    "longitude": -48.5480,
    "radius_meters": 5000
  }'
```

## Notas Importantes

1. **Latência de Dados**: Dados de satélite podem ter latência de horas a dias dependendo da fonte.

2. **Disponibilidade**: Nem todos os dados estarão disponíveis para todas as localizações e horários.

3. **Precisão**: A precisão varia por fonte de dados e condições atmosféricas.

4. **Cache**: Dados são cacheados por períodos apropriados para otimizar performance.

5. **Rate Limiting**: Implementado para proteger a API e as fontes de dados upstream.

## Suporte

Para questões ou problemas, consulte a documentação completa ou abra uma issue no repositório do projeto.
