# NASA SafeOut API 🌍

API REST em Python para consulta de dados ambientais da NASA Earthdata e outras fontes, fornecendo informações sobre precipitação, qualidade do ar, clima, índice UV e focos de incêndio baseados em localização geográfica.

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.9+
- Conta [NASA Earthdata](https://urs.earthdata.nasa.gov/)
- [NASA FIRMS API Key](https://firms.modaps.eosdis.nasa.gov/api/)

### Instalação

```bash
# Clone o repositório
git clone https://github.com/SEU_USUARIO/nasa-safeout-api.git
cd nasa-safeout-api/CODE

# Crie e ative o ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # Linux/Mac

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
copy .env.example .env
# Edite .env com suas credenciais NASA Earthdata e FIRMS API Key

# Configure o earthaccess
python -c "import earthaccess; earthaccess.login(persist=True)"
```

### Executar a API

```bash
uvicorn app.main:app --reload
```

A API estará disponível em: **http://localhost:8000**

## 📡 Como Usar a API

### 🎯 Página de Teste Interativa (Recomendado!)

Acesse a página de teste com interface gráfica:
```
http://localhost:8000/test
```

Nesta página você pode:
- ✅ Testar todos os endpoints com cliques
- ✅ Usar coordenadas pré-definidas de cidades brasileiras
- ✅ Ver respostas formatadas em tempo real
- ✅ Validar entradas automaticamente

### Documentação Interativa

Acesse a documentação Swagger UI em:
```
http://localhost:8000/docs
```

### Exemplo de Requisição

**Endpoint:** `POST /api/v1/environmental-data`

```bash
curl -X POST "http://localhost:8000/api/v1/environmental-data" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": -27.5954,
    "longitude": -48.5480,
    "radius_meters": 5000
  }'
```

**PowerShell:**
```powershell
$body = @{
    latitude = -27.5954
    longitude = -48.5480
    radius_meters = 5000
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/environmental-data" `
  -Method Post -Body $body -ContentType "application/json"
```

**Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/environmental-data",
    json={
        "latitude": -27.5954,
        "longitude": -48.5480,
        "radius_meters": 5000
    }
)
data = response.json()
print(data)
```

### Resposta

```json
{
  "location": {
    "latitude": -27.5954,
    "longitude": -48.5480,
    "radius_meters": 5000
  },
  "timestamp": "2025-10-04T22:35:00Z",
  "data": {
    "precipitation": {...},
    "air_quality": {...},
    "weather": {...},
    "uv_index": {...},
    "fire_history": {...}
  },
  "metadata": {
    "processing_time_ms": 1250,
    "data_sources_queried": 5,
    "data_sources_successful": 5
  }
}
```

## 🌐 Fontes de Dados

| Fonte | Tipo | Provedor | Atualização |
|-------|------|----------|-------------|
| **GPM IMERG** | Precipitação | NASA | 30 minutos |
| **TROPOMI/Sentinel-5P** | Qualidade do Ar (Satélite) | ESA/NASA | Diária |
| **OpenAQ** | Qualidade do Ar (Solo) | OpenAQ | Horária |
| **MERRA-2** | Clima (Temperatura, Vento, Umidade) | NASA | Horária |
| **NASA FIRMS** | Focos de Incêndio | NASA | Tempo Real |

## 📚 Documentação Completa

Toda a documentação está disponível na pasta **SPECS/**:

- **[Setup Guide](SPECS/setup_guide.md)** - Guia detalhado de instalação e configuração
- **[API Documentation](SPECS/api_documentation.md)** - Documentação completa da API
- **[Development Plan](SPECS/development_plan.md)** - Plano de desenvolvimento e arquitetura
- **[Project Summary](SPECS/project_summary.md)** - Resumo executivo do projeto

## 🏗️ Estrutura do Projeto

```
nasa-safeout-api/
├── CODE/
│   ├── app/
│   │   ├── main.py              # Entry point da API
│   │   ├── config.py            # Configurações
│   │   ├── models/              # Modelos Pydantic
│   │   ├── routers/             # Endpoints
│   │   ├── services/            # Integração com fontes de dados
│   │   └── utils/               # Utilitários
│   ├── tests/                   # Testes
│   └── requirements.txt         # Dependências
└── SPECS/                       # Documentação
```

## 🔧 Tecnologias

- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework web moderno e rápido
- **[earthaccess](https://earthaccess.readthedocs.io/)** - Acesso aos dados NASA Earthdata
- **[xarray](https://docs.xarray.dev/)** - Processamento de dados científicos
- **[httpx](https://www.python-httpx.org/)** - Cliente HTTP assíncrono
- **[Pydantic](https://docs.pydantic.dev/)** - Validação de dados

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Com cobertura
pytest --cov=app tests/

# Testes específicos
pytest tests/test_api.py -v
```

## 📋 Endpoints Disponíveis

- `GET /` - Informações básicas da API
- `GET /test` - 🎯 **Página de teste interativa**
- `GET /health` - Health check
- `GET /api/v1/info` - Informações sobre fontes de dados
- `POST /api/v1/environmental-data` - Obter dados ambientais por localização
- `GET /docs` - Documentação Swagger UI
- `GET /redoc` - Documentação ReDoc

## ⚙️ Configuração

Crie um arquivo `.env` na pasta `CODE/` com:

```env
# NASA Earthdata
EARTHDATA_USERNAME=seu_username
EARTHDATA_PASSWORD=sua_senha

# NASA FIRMS
FIRMS_API_KEY=sua_chave_api

# API (opcional)
API_PORT=8000
LOG_LEVEL=INFO
CACHE_EXPIRY_HOURS=6
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Add: Nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é fornecido como está para fins educacionais e de pesquisa.

## 🙏 Agradecimentos

- [NASA Earthdata](https://earthdata.nasa.gov/) - Acesso aos dados ambientais
- [OpenAQ](https://openaq.org/) - Dados de qualidade do ar
- [ESA Sentinel-5P](https://sentinel.esa.int/web/sentinel/missions/sentinel-5p) - Dados de satélite

## 📧 Suporte

Para questões ou problemas:
- Consulte a [documentação completa](SPECS/)
- Abra uma [issue](https://github.com/SEU_USUARIO/nasa-safeout-api/issues)

---

**Desenvolvido com** ❤️ **usando dados abertos da NASA e outras fontes**
