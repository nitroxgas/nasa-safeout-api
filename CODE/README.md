# NASA SafeOut API

Backend service em Python que fornece dados ambientais da NASA Earthdata e outras fontes através de uma API REST.

## 🌍 Funcionalidades

- **Precipitação**: Previsão horária via GPM IMERG
- **Qualidade do Ar**: Dados de satélite (TROPOMI) e estações terrestres (OpenAQ)
- **Clima**: Temperatura, umidade e vento via MERRA-2
- **Índice UV**: Dados do TROPOMI/Sentinel-5P
- **Focos de Incêndio**: Detecção via NASA FIRMS

## 🚀 Quick Start

### Pré-requisitos

- Python 3.9 ou superior
- Conta NASA Earthdata (https://urs.earthdata.nasa.gov/)
- NASA FIRMS API Key (https://firms.modaps.eosdis.nasa.gov/api/)

### Instalação

1. Clone o repositório e navegue até a pasta CODE:
```bash
cd CODE
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Configure as variáveis de ambiente:
```bash
# Copie o arquivo de exemplo
copy .env.example .env

# Edite o arquivo .env com suas credenciais
```

6. Configure o earthaccess (primeira vez):
```python
python -c "import earthaccess; earthaccess.login(persist=True)"
```

### Executar a API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em: http://localhost:8000

Documentação interativa (Swagger): http://localhost:8000/docs

## 📡 Uso da API

### Exemplo de Requisição

```bash
curl -X POST "http://localhost:8000/api/v1/environmental-data" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": -27.5954,
    "longitude": -48.5480,
    "radius_meters": 5000
  }'
```

### Exemplo de Resposta

```json
{
  "location": {
    "latitude": -27.5954,
    "longitude": -48.5480,
    "radius_meters": 5000
  },
  "timestamp": "2025-10-04T21:47:09Z",
  "data": {
    "precipitation": {...},
    "air_quality": {...},
    "weather": {...},
    "uv_index": {...},
    "fire_history": {...}
  }
}
```

## 📚 Documentação

- [Plano de Desenvolvimento](../SPECS/development_plan.md)
- [Documentação da API](../SPECS/api_documentation.md)
- [Especificação Original](../SPECS/specification.md)

## 🏗️ Estrutura do Projeto

```
CODE/
├── app/
│   ├── main.py              # Entry point
│   ├── config.py            # Configurações
│   ├── models/              # Modelos Pydantic
│   ├── services/            # Integração com fontes de dados
│   ├── routers/             # Endpoints da API
│   └── utils/               # Utilitários
├── tests/                   # Testes
├── requirements.txt         # Dependências
├── .env.example            # Exemplo de variáveis de ambiente
└── README.md               # Este arquivo
```

## 🔧 Tecnologias

- **FastAPI**: Framework web moderno e rápido
- **earthaccess**: Biblioteca para acessar dados NASA Earthdata
- **xarray**: Processamento de dados científicos multidimensionais
- **httpx**: Cliente HTTP assíncrono
- **pydantic**: Validação de dados

## 🌐 Fontes de Dados

| Fonte | Tipo | Provedor | Atualização |
|-------|------|----------|-------------|
| GPM IMERG | Precipitação | NASA | 30 minutos |
| TROPOMI | Qualidade do Ar | ESA/NASA | Diária |
| OpenAQ | Qualidade do Ar (solo) | OpenAQ | Horária |
| MERRA-2 | Clima | NASA | Horária |
| FIRMS | Focos de Incêndio | NASA | Tempo real |

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Com cobertura
pytest --cov=app tests/

# Testes específicos
pytest tests/test_api.py
```

## 📝 Desenvolvimento

### Formatação de Código
```bash
black app/
```

### Linting
```bash
flake8 app/
```

### Type Checking
```bash
mypy app/
```

## 🐛 Troubleshooting

### Erro de Autenticação NASA Earthdata
```bash
# Reconfigurar credenciais
python -c "import earthaccess; earthaccess.login(persist=True)"
```

### Dados não disponíveis
- Verifique se a localização está dentro da cobertura dos satélites
- Alguns dados têm latência de horas a dias
- Verifique os logs para detalhes

### Performance lenta
- Dados são cacheados por padrão
- Primeira requisição pode ser mais lenta
- Ajuste `CACHE_EXPIRY_HOURS` no `.env`

## 📄 Licença

Este projeto é fornecido como está para fins educacionais e de pesquisa.

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📧 Contato

Para questões ou suporte, abra uma issue no repositório.

## 🙏 Agradecimentos

- NASA Earthdata por fornecer acesso aos dados
- OpenAQ pela plataforma de qualidade do ar
- Comunidade open source pelas excelentes bibliotecas
