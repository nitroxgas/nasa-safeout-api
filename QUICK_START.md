# 🚀 Quick Start - NASA SafeOut API

**Status:** ✅ 100% Funcional | **Última atualização:** 2025-10-05

---

## ⚡ Início Rápido (3 minutos)

### 1. Inicie a API

```bash
cd CODE
uvicorn app.main:app --reload
```

### 2. Acesse a Interface de Testes

Abra no navegador: **http://localhost:8000/test**

### 3. Teste com um Clique!

1. Clique em qualquer cidade (ex: **📍 New York, NY**)
2. Clique em **🌍 Teste Completo**
3. Veja os dados ambientais em tempo real!

---

## 🌍 Cidades Disponíveis

### 🇧🇷 Brasil
- Florianópolis, SC
- São Paulo, SP
- Rio de Janeiro, RJ
- Brasília, DF

### 🇺🇸 Estados Unidos
- New York, NY
- Los Angeles, CA
- Chicago, IL
- Houston, TX
- Phoenix, AZ
- San Francisco, CA
- Seattle, WA
- Miami, FL

---

## 📊 O Que a API Retorna

Para cada localização, você recebe:

✅ **Precipitação** (GPM IMERG)
- Taxa de chuva em mm/h
- Dados em tempo real

✅ **Qualidade do Ar - Satélite** (TROPOMI)
- Índice de aerosol
- NO2 troposférico
- Classificação de qualidade

✅ **Qualidade do Ar - Solo** (OpenAQ)
- PM2.5, PM10, NO2, O3
- Estações próximas
- AQI (Air Quality Index)

✅ **Clima** (MERRA-2)
- Temperatura (°C)
- Vento (velocidade e direção)
- Umidade (%)
- Pressão atmosférica

✅ **Índice UV**
- Valor do índice UV
- Categoria (low, moderate, high, etc.)
- Nível de risco

✅ **Focos de Incêndio** (NASA FIRMS)
- Detecções dos últimos 7 dias
- Distância dos focos
- Confiança da detecção

---

## 🧪 Testes Automatizados

### Teste Completo
```bash
cd CODE
python test_complete_api.py
```

### Teste de Autenticação
```bash
cd CODE
python test_earthdata_auth.py
```

### Testes pytest
```bash
cd CODE
pytest
```

---

## 📡 Uso via API (curl)

### Exemplo: Nova York

```bash
curl -X POST http://localhost:8000/api/v1/environmental-data \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 40.7128,
    "longitude": -74.0060,
    "radius_meters": 5000
  }'
```

### Exemplo: São Paulo

```bash
curl -X POST http://localhost:8000/api/v1/environmental-data \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": -23.5505,
    "longitude": -46.6333,
    "radius_meters": 5000
  }'
```

---

## 🐍 Uso via Python

```python
import requests

# Dados de Los Angeles
response = requests.post(
    "http://localhost:8000/api/v1/environmental-data",
    json={
        "latitude": 34.0522,
        "longitude": -118.2437,
        "radius_meters": 5000
    }
)

data = response.json()
print(f"Temperatura: {data['data']['weather']['temperature_celsius']}°C")
print(f"Qualidade do ar: {data['data']['air_quality']['satellite']['quality_flag']}")
```

---

## 📚 Documentação Completa

### Documentos Disponíveis

1. **`README.md`** - Visão geral do projeto
2. **`IMPLEMENTATION_SUMMARY.md`** - Resumo da implementação
3. **`CODE/IMPLEMENTATION_GUIDE.md`** - Guia técnico detalhado
4. **`CODE/TOKEN_AUTH_UPDATE.md`** - Guia de autenticação
5. **`FINAL_UPDATES.md`** - Últimas atualizações
6. **`QUICK_START.md`** - Este arquivo

### Documentação Online

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🔧 Configuração (Opcional)

Se precisar alterar configurações, edite o arquivo `.env`:

```env
# Autenticação NASA (token recomendado)
EARTHDATA_TOKEN=seu_token_aqui

# API FIRMS
FIRMS_API_KEY=sua_chave_aqui

# Configurações da API
API_PORT=8000
LOG_LEVEL=INFO
```

---

## ⚠️ Troubleshooting Rápido

### API não inicia?
```bash
# Verifique se está no diretório correto
cd CODE

# Ative o ambiente virtual (se necessário)
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Instale dependências
pip install -r requirements.txt
```

### Dados NASA não retornam?
- **Normal!** Primeira requisição pode levar 30-60 segundos
- Downloads de granules são grandes (50-500 MB)
- Verifique se o token está configurado no `.env`

### Sem dados para uma cidade?
- Nem todas as regiões têm dados disponíveis
- Tente aumentar o `radius_meters`
- Algumas fontes podem não ter cobertura na área

---

## 🎯 Casos de Uso

### 1. Monitoramento de Qualidade do Ar
```
Teste: Los Angeles, CA
Por quê: Alta poluição urbana
Dados: PM2.5, NO2, Aerosol Index
```

### 2. Análise de Precipitação
```
Teste: Miami, FL
Por quê: Clima tropical, chuvas frequentes
Dados: Taxa de precipitação IMERG
```

### 3. Monitoramento de Incêndios
```
Teste: Phoenix, AZ
Por quê: Região com histórico de incêndios
Dados: Focos de calor FIRMS
```

### 4. Análise Climática
```
Teste: Chicago, IL
Por quê: Clima continental variado
Dados: Temperatura, vento, umidade
```

---

## 📊 Performance Esperada

| Fonte | Primeira Requisição | Requisições Seguintes |
|-------|---------------------|----------------------|
| OpenAQ | 1-2 segundos | 1-2 segundos |
| NASA FIRMS | 2-3 segundos | 2-3 segundos |
| TROPOMI | 30-60 segundos | 5-10 segundos |
| GPM IMERG | 30-60 segundos | 5-10 segundos |
| MERRA-2 | 30-60 segundos | 5-10 segundos |

**Dica:** Cache local acelera requisições subsequentes!

---

## 🎉 Pronto para Usar!

A API está **100% funcional** e pronta para:

✅ Desenvolvimento e testes  
✅ Demonstrações  
✅ Integração com aplicações  
✅ Análise de dados ambientais  
✅ Pesquisa e educação  

---

## 📞 Suporte

**Documentação:** Veja os arquivos na pasta raiz e `CODE/`  
**Testes:** Execute `pytest` ou `python test_complete_api.py`  
**Logs:** Verifique o console para mensagens detalhadas  

---

**Desenvolvido com** ❤️ **usando dados da NASA e outras fontes abertas**

**Status:** 🟢 PRODUCTION READY | **Versão:** 1.0.0
