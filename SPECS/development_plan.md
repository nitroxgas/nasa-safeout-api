# Plano de Desenvolvimento - NASA SafeOut API

## Visão Geral do Projeto

Backend em Python que consome dados ambientais da NASA Earthdata e outras fontes para fornecer informações meteorológicas e de qualidade do ar baseadas em coordenadas geográficas.

## Arquitetura do Sistema

### Stack Tecnológico
- **Framework**: FastAPI (API REST moderna e assíncrona)
- **Linguagem**: Python 3.9+
- **Bibliotecas Principais**:
  - `earthaccess`: Acesso aos dados da NASA Earthdata
  - `fastapi`: Framework web
  - `uvicorn`: Servidor ASGI
  - `httpx`: Cliente HTTP assíncrono
  - `numpy`, `xarray`: Processamento de dados científicos
  - `pydantic`: Validação de dados

### Estrutura de Diretórios
```
CODE/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Entry point da API
│   ├── config.py               # Configurações e variáveis de ambiente
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Modelos Pydantic (request/response)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── earthdata.py        # Integração com earthaccess
│   │   ├── openaq.py           # Integração com OpenAQ API
│   │   ├── firms.py            # Integração com NASA FIRMS API
│   │   └── data_processor.py  # Processamento e agregação de dados
│   ├── routers/
│   │   ├── __init__.py
│   │   └── environmental.py    # Endpoints da API
│   └── utils/
│       ├── __init__.py
│       └── geo_utils.py        # Utilitários geográficos
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Fontes de Dados

### 1. Precipitação (IMERG) 💧
- **Dataset**: GPM_3IMERGHHE
- **Método**: earthaccess
- **Variáveis**: Taxa de precipitação
- **Resolução Temporal**: Horária

### 2. Qualidade do Ar 🌬
#### A. Dados de Satélite (TROPOMI/Sentinel-5P)
- **Datasets**: 
  - S5P_L2__AER_AI (Aerosol Index)
  - S5P_NRTI_L2__NO2 (Dióxido de Nitrogênio)
- **Método**: earthaccess

#### B. Dados de Solo (OpenAQ)
- **API**: https://api.openaq.org/v2/
- **Variáveis**: PM2.5, PM10, NO2, O3, SO2, CO
- **Método**: REST API

### 3. Vento, Temperatura e Umidade 🌡
- **Dataset**: M2I1NXASM (MERRA-2)
- **Método**: earthaccess
- **Variáveis**:
  - U2M, V2M: Componentes do vento a 2m
  - T2M: Temperatura a 2m
  - QV2M: Umidade específica a 2m

### 4. Índice UV e História Ambiental 🔥
#### A. Índice UV
- **Dataset**: S5P_L2__AER_AI (TROPOMI)
- **Método**: earthaccess

#### B. Focos de Incêndio
- **API**: NASA FIRMS
- **Endpoint**: https://firms.modaps.eosdis.nasa.gov/api/
- **Método**: REST API

## Endpoint da API

### POST /api/v1/environmental-data

**Request Body:**
```json
{
  "latitude": -27.5954,
  "longitude": -48.5480,
  "radius_meters": 5000
}
```

**Response:**
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
      "forecast_hours": [
        {
          "hour": 1,
          "rate_mm_h": 2.5
        }
      ]
    },
    "air_quality": {
      "satellite": {
        "source": "TROPOMI/Sentinel-5P",
        "aerosol_index": 1.2,
        "no2_mol_m2": 0.00015
      },
      "ground_stations": {
        "source": "OpenAQ",
        "stations": [
          {
            "location": "Station Name",
            "distance_km": 2.3,
            "measurements": {
              "pm25": 15.2,
              "pm10": 25.3,
              "no2": 12.1
            }
          }
        ]
      }
    },
    "weather": {
      "source": "MERRA-2",
      "temperature_celsius": 22.5,
      "humidity_percent": 75.0,
      "wind": {
        "speed_m_s": 3.2,
        "direction_degrees": 180
      }
    },
    "uv_index": {
      "source": "TROPOMI",
      "value": 7.5
    },
    "fire_history": {
      "source": "NASA FIRMS",
      "active_fires": 2,
      "fires": [
        {
          "latitude": -27.60,
          "longitude": -48.55,
          "distance_km": 1.2,
          "brightness": 320.5,
          "confidence": "high",
          "date": "2025-10-04"
        }
      ]
    }
  }
}
```

## Fases de Desenvolvimento

### Fase 1: Setup Inicial ✅
- [x] Criar estrutura de diretórios
- [ ] Configurar ambiente virtual Python
- [ ] Instalar dependências
- [ ] Configurar variáveis de ambiente
- [ ] Criar conta NASA Earthdata

### Fase 2: Estrutura Base da API
- [ ] Implementar FastAPI app básico
- [ ] Criar modelos Pydantic para request/response
- [ ] Implementar endpoint principal
- [ ] Adicionar validação de entrada

### Fase 3: Integração earthaccess
- [ ] Configurar autenticação NASA Earthdata
- [ ] Implementar busca e download de dados IMERG
- [ ] Implementar busca e download de dados MERRA-2
- [ ] Implementar busca e download de dados TROPOMI
- [ ] Processar dados em grade para coordenadas específicas

### Fase 4: Integração APIs Externas
- [ ] Implementar cliente OpenAQ
- [ ] Implementar cliente NASA FIRMS
- [ ] Adicionar tratamento de erros e timeouts

### Fase 5: Processamento de Dados
- [ ] Implementar extração de dados por coordenadas
- [ ] Implementar cálculo de área circular (raio)
- [ ] Implementar agregação de dados
- [ ] Implementar conversões de unidades

### Fase 6: Otimização e Cache
- [ ] Implementar cache de dados baixados
- [ ] Implementar processamento assíncrono
- [ ] Otimizar queries de dados

### Fase 7: Testes e Documentação
- [ ] Escrever testes unitários
- [ ] Escrever testes de integração
- [ ] Documentar API (Swagger/OpenAPI)
- [ ] Criar README completo

### Fase 8: Deploy e Monitoramento
- [ ] Configurar logging
- [ ] Adicionar health checks
- [ ] Preparar para containerização (Docker)
- [ ] Documentar processo de deploy

## Considerações Técnicas

### Autenticação NASA Earthdata
- Requer conta em https://urs.earthdata.nasa.gov/
- Credenciais armazenadas em variáveis de ambiente
- Usar `.netrc` ou credenciais diretas via earthaccess

### Performance
- Dados de satélite podem ser grandes (GB)
- Implementar cache local de arquivos
- Considerar processamento assíncrono para múltiplas fontes
- Timeout adequado para requests externos

### Tratamento de Erros
- Dados podem não estar disponíveis para todas as datas/localizações
- APIs externas podem estar indisponíveis
- Retornar dados parciais quando possível
- Logs detalhados para debugging

### Limitações
- Dados de satélite têm latência (horas a dias)
- Cobertura geográfica pode variar por dataset
- Resolução espacial varia por fonte
- Algumas APIs têm rate limits

## Próximos Passos Imediatos

1. **Configurar ambiente Python**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Criar conta NASA Earthdata**
   - Registrar em https://urs.earthdata.nasa.gov/
   - Configurar credenciais

3. **Testar earthaccess**
   - Autenticar
   - Baixar arquivo de teste de cada dataset

4. **Implementar MVP**
   - Endpoint básico funcionando
   - Uma fonte de dados integrada
   - Response JSON formatado

## Recursos e Links

- **earthaccess**: https://earthaccess.readthedocs.io/
- **FastAPI**: https://fastapi.tiangolo.com/
- **OpenAQ API**: https://docs.openaq.org/
- **NASA FIRMS**: https://firms.modaps.eosdis.nasa.gov/
- **GPM IMERG**: https://gpm.nasa.gov/data/imerg
- **MERRA-2**: https://gmao.gsfc.nasa.gov/reanalysis/MERRA-2/
- **Sentinel-5P**: https://sentinel.esa.int/web/sentinel/missions/sentinel-5p
