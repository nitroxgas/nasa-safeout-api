# ⚠️ TROPOMI/Sentinel-5P - Dados Não Disponíveis via NASA Earthdata

**Data:** 2025-10-05  
**Status:** TROPOMI e UV Index temporariamente desabilitados

---

## 🔍 Problema Identificado

Durante a implementação, descobrimos que **TROPOMI/Sentinel-5P NÃO está disponível via NASA Earthdata**.

### Por quê?

- **TROPOMI** é um instrumento do satélite **Sentinel-5P**
- **Sentinel-5P** é operado pela **ESA (Agência Espacial Europeia)**
- Os dados estão no **Copernicus Data Space**, não no NASA Earthdata
- Requer credenciais e acesso **separados** da ESA/Copernicus

---

## 📊 Impacto nas Fontes de Dados

### ❌ Desabilitadas Temporariamente

1. **TROPOMI (Qualidade do Ar - Satélite)**
   - Aerosol Index
   - NO2 troposférico
   - **Motivo:** Requer acesso ESA/Copernicus

2. **UV Index**
   - Cálculo baseado em dados TROPOMI
   - **Motivo:** Depende do TROPOMI

### ✅ Ainda Funcionais (NASA Earthdata)

1. **GPM IMERG** - Precipitação ✅
2. **MERRA-2** - Clima (temperatura, vento, umidade) ✅
3. **OpenAQ** - Qualidade do ar (estações terrestres) ✅
4. **NASA FIRMS** - Focos de incêndio ✅

**Status Atual:** 4/6 fontes funcionais (67%)

---

## 🔧 Ações Necessárias para Ativar NASA Earthdata

### Passo 1: Autorizar Aplicação NASA GESDISC

1. Acesse: https://urs.earthdata.nasa.gov/profile
2. Vá para **Applications** → **Authorized Apps**
3. Procure e aprove: **NASA GESDISC DATA ARCHIVE**
4. Isso habilita acesso a:
   - GPM IMERG (precipitação)
   - MERRA-2 (clima)

### Passo 2: Testar Acesso

```bash
cd CODE
python diagnose_earthdata.py
```

Se o teste passar, as fontes NASA estarão funcionais!

---

## 🌍 Alternativas para TROPOMI

### Opção 1: Usar Apenas Dados Terrestres (OpenAQ)

**Prós:**
- ✅ Já funcional
- ✅ Dados em tempo real
- ✅ Sem configuração adicional

**Contras:**
- ⚠️ Cobertura limitada (apenas onde há estações)
- ⚠️ Sem dados de satélite

### Opção 2: Integrar com Copernicus Data Space

**Prós:**
- ✅ Acesso a TROPOMI/Sentinel-5P
- ✅ Dados de satélite de alta qualidade

**Contras:**
- ⚠️ Requer registro separado em: https://dataspace.copernicus.eu/
- ⚠️ API diferente (não é earthaccess)
- ⚠️ Implementação adicional necessária

### Opção 3: Usar API OpenWeather UV Index

**Prós:**
- ✅ API simples
- ✅ Dados de UV em tempo real
- ✅ Fácil integração

**Contras:**
- ⚠️ Requer API key (gratuita limitada)
- ⚠️ Não é dado de satélite NASA

---

## 📝 Mudanças Implementadas

### Arquivos Modificados

1. **`app/services/earthdata.py`**
   - `get_tropomi_data()` retorna `None` com log explicativo
   - `get_uv_index_data()` retorna `None` com log explicativo

2. **`diagnose_earthdata.py`**
   - Removida menção a Copernicus Sentinel Data
   - Foco apenas em NASA GESDISC

### Comportamento Atual

Quando a API é chamada:
- ✅ GPM IMERG: Tenta buscar dados (se autorizado)
- ✅ MERRA-2: Tenta buscar dados (se autorizado)
- ⚠️ TROPOMI: Retorna `None` com log informativo
- ⚠️ UV Index: Retorna `None` com log informativo
- ✅ OpenAQ: Funciona normalmente
- ✅ FIRMS: Funciona normalmente

---

## 🚀 Próximos Passos Recomendados

### Curto Prazo (Agora)

1. **Execute o diagnóstico:**
   ```bash
   cd CODE
   python diagnose_earthdata.py
   ```

2. **Autorize NASA GESDISC** no perfil Earthdata

3. **Teste a API novamente:**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Verifique se IMERG e MERRA-2 funcionam**

### Médio Prazo (Opcional)

1. **Implementar acesso Copernicus** para TROPOMI
   - Registrar em: https://dataspace.copernicus.eu/
   - Implementar cliente Copernicus
   - Integrar na API

2. **Ou usar alternativa OpenWeather** para UV
   - Mais simples
   - Dados confiáveis
   - API bem documentada

---

## 📊 Status Esperado Após Autorização

### Com NASA GESDISC Autorizado

| Fonte | Status | Observação |
|-------|--------|------------|
| GPM IMERG | 🟢 Funcional | Precipitação |
| MERRA-2 | 🟢 Funcional | Clima |
| OpenAQ | 🟢 Funcional | Qualidade do ar (solo) |
| NASA FIRMS | 🟢 Funcional | Focos de incêndio |
| TROPOMI | 🔴 Indisponível | Requer ESA/Copernicus |
| UV Index | 🔴 Indisponível | Depende de TROPOMI |

**Fontes Funcionais:** 4/6 (67%)

### Se Implementar Copernicus

| Fonte | Status |
|-------|--------|
| Todas acima | 🟢 Funcional |
| TROPOMI | 🟢 Funcional |
| UV Index | 🟢 Funcional |

**Fontes Funcionais:** 6/6 (100%)

---

## ✅ Checklist de Resolução

- [ ] Executar `python diagnose_earthdata.py`
- [ ] Autorizar NASA GESDISC no perfil Earthdata
- [ ] Testar IMERG e MERRA-2
- [ ] Decidir sobre TROPOMI:
  - [ ] Opção A: Deixar desabilitado (usar apenas OpenAQ)
  - [ ] Opção B: Implementar Copernicus
  - [ ] Opção C: Usar OpenWeather UV como alternativa

---

## 📞 Suporte

**Documentação NASA Earthdata:**
- https://urs.earthdata.nasa.gov/documentation

**Documentação Copernicus:**
- https://documentation.dataspace.copernicus.eu/

**Script de Diagnóstico:**
```bash
python CODE/diagnose_earthdata.py
```

---

**Conclusão:** A API funcionará com 4/6 fontes após autorizar NASA GESDISC. TROPOMI requer implementação separada com Copernicus.
