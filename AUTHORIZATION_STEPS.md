# 🔐 Passos para Autorizar NASA Earthdata

**AÇÃO NECESSÁRIA:** Autorize a aplicação NASA GESDISC para acessar dados

---

## ⚡ Passo a Passo (5 minutos)

### 1️⃣ Execute o Diagnóstico

```bash
cd CODE
python diagnose_earthdata.py
```

**Resultado esperado:** Erro na busca de dados indicando necessidade de autorização

---

### 2️⃣ Acesse Seu Perfil NASA Earthdata

🔗 **Link:** https://urs.earthdata.nasa.gov/profile

**Login:**
- Username: `safeoutdoor`
- Password: (sua senha)

---

### 3️⃣ Autorize a Aplicação

1. No menu lateral, clique em **"Applications"**
2. Clique em **"Authorized Apps"**
3. Procure por: **"NASA GESDISC DATA ARCHIVE"**
4. Clique em **"Approve"** ou **"Authorize"**

**Importante:** Esta aplicação dá acesso a:
- ✅ GPM IMERG (precipitação)
- ✅ MERRA-2 (clima)

---

### 4️⃣ Teste Novamente

```bash
cd CODE
python diagnose_earthdata.py
```

**Resultado esperado:** ✅ Sucesso na busca de dados!

---

### 5️⃣ Reinicie a API

```bash
cd CODE
uvicorn app.main:app --reload
```

Acesse: http://localhost:8000/test

---

## 📊 O Que Vai Funcionar

### ✅ Após Autorização

- **GPM IMERG** - Precipitação em tempo real
- **MERRA-2** - Temperatura, vento, umidade
- **OpenAQ** - Qualidade do ar (estações)
- **NASA FIRMS** - Focos de incêndio

**Total:** 4/6 fontes funcionais (67%)

### ⚠️ Ainda Indisponíveis

- **TROPOMI** - Requer acesso ESA/Copernicus (não é NASA)
- **UV Index** - Depende do TROPOMI

---

## 🔍 Troubleshooting

### Não encontro "NASA GESDISC DATA ARCHIVE"

**Solução:**
1. Tente buscar apenas por "GESDISC"
2. Ou procure por "GES DISC"
3. Pode aparecer como "GES DISC Data Archive"

### Já autorizei mas ainda não funciona

**Soluções:**
1. Aguarde 1-2 minutos (propagação)
2. Execute `python diagnose_earthdata.py` novamente
3. Reinicie a API
4. Limpe o cache: `rm -rf cache/` (ou delete a pasta cache)

### Erro de autenticação

**Verifique:**
1. Token no `.env` está correto
2. Token não expirou (validade ~60 dias)
3. Conta está ativa em https://urs.earthdata.nasa.gov/

---

## 📝 Checklist

- [ ] Executei `python diagnose_earthdata.py`
- [ ] Acessei https://urs.earthdata.nasa.gov/profile
- [ ] Autorizei "NASA GESDISC DATA ARCHIVE"
- [ ] Executei diagnóstico novamente (sucesso!)
- [ ] Reiniciei a API
- [ ] Testei em http://localhost:8000/test

---

## 🎯 Resultado Final Esperado

```json
{
  "data": {
    "precipitation": {
      "source": "GPM IMERG",
      "precipitation_rate_mm_hr": 2.5
    },
    "weather": {
      "source": "MERRA-2",
      "temperature_celsius": 22.5,
      "wind": { "speed_kmh": 15.2 }
    },
    "air_quality": {
      "ground_stations": {
        "source": "OpenAQ",
        "stations_count": 3
      },
      "satellite": null
    },
    "fire_history": {
      "source": "NASA FIRMS",
      "active_fires_count": 0
    }
  },
  "metadata": {
    "data_sources_successful": 4,
    "warnings": [
      "TROPOMI data unavailable (requires ESA/Copernicus access)",
      "UV index unavailable (depends on TROPOMI)"
    ]
  }
}
```

---

**Após seguir estes passos, 4 das 6 fontes de dados estarão funcionais!** ✅
