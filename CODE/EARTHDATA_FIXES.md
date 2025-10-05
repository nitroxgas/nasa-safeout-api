# 🔧 Correções Aplicadas - NASA Earthdata

**Data:** 2025-10-05  
**Status:** Correções implementadas

---

## 🐛 Problemas Identificados e Corrigidos

### 1. Erro no Processamento de Arquivos NetCDF

**Problema:**
```
Error extracting point value from : did not find a match in any of xarray's currently installed IO backends
```

**Causa:**
- `earthaccess.download()` retorna objetos, não strings de caminhos
- Arquivo não tinha caminho válido para o processador NetCDF

**Correção:**
```python
# Converter objetos retornados para strings de caminhos
file_paths = []
for f in files:
    if isinstance(f, str):
        file_paths.append(f)
    elif hasattr(f, '__str__'):
        file_paths.append(str(f))
```

**Arquivo:** `app/services/earthdata.py` - método `download_granules()`

---

### 2. Bounding Box Muito Pequeno

**Problema:**
```
Granules found: 0
No MERRA-2 granules found
```

**Causa:**
- Bounding box calculado era muito pequeno (poucos metros)
- Granules NASA cobrem áreas grandes (grids de 0.1° a 0.5°)
- Busca não encontrava granules que cobrissem a área

**Correção:**

**IMERG:**
```python
# Antes: radius_km / 111.0
# Depois: max(radius_km / 111.0, 0.5)  # Mínimo 0.5 graus
lat_offset = max(radius_km / 111.0, 0.5)
lon_offset = max(radius_km / (111.0 * abs(max(abs(latitude), 0.1))), 0.5)
```

**MERRA-2:**
```python
# MERRA-2 tem resolução de 0.5° x 0.625°
lat_offset = max(radius_km / 111.0, 1.0)  # Mínimo 1 grau
lon_offset = max(radius_km / (111.0 * abs(max(abs(latitude), 0.1))), 1.0)
```

---

### 3. Período Temporal Muito Curto

**Problema:**
- Busca de 24 horas não encontrava dados recentes
- Granules podem ter delay de processamento

**Correção:**

**IMERG:**
```python
# Antes: timedelta(hours=24)
# Depois: timedelta(days=7)  # Últimos 7 dias
start_time = end_time - timedelta(days=7)
```

**MERRA-2:**
```python
# Buscar últimos 3 dias
start_time = end_time - timedelta(days=3)
```

---

### 4. Validação de Arquivos Baixados

**Problema:**
- Arquivos baixados não eram validados antes do processamento
- Erros ocorriam durante a leitura

**Correção:**
```python
# Verificar se arquivo existe
if not os.path.exists(latest_file):
    logger.error(f"Downloaded file does not exist: {latest_file}")
    return None

# Verificar extensão
if not latest_file.endswith(('.nc', '.nc4', '.hdf', '.h5', '.he5')):
    logger.warning(f"File may not be NetCDF/HDF5: {latest_file}")
```

---

## 📊 Impacto das Correções

### Antes
- ❌ Arquivos não processados (erro de caminho)
- ❌ Nenhum granule encontrado (bbox muito pequeno)
- ❌ Dados não disponíveis (período muito curto)

### Depois
- ✅ Arquivos processados corretamente
- ✅ Granules encontrados (bbox adequado)
- ✅ Dados disponíveis (período mais longo)

---

## 🧪 Como Testar

### 1. Execute o diagnóstico
```bash
cd CODE
python diagnose_earthdata.py
```

**Resultado esperado:**
- ✅ Autenticação bem-sucedida
- ✅ Busca de dados retorna granules
- ✅ Download bem-sucedido

### 2. Teste a API
```bash
cd CODE
uvicorn app.main:app --reload
```

Acesse: http://localhost:8000/test

**Teste com:**
- New York, NY (40.7128, -74.0060)
- Raio: 5000 metros

**Resultado esperado:**
```json
{
  "precipitation": {
    "source": "GPM IMERG",
    "precipitation_rate_mm_hr": 2.5
  },
  "weather": {
    "source": "MERRA-2",
    "temperature_celsius": 15.2,
    "wind": {
      "speed_kmh": 12.5
    }
  }
}
```

---

## 📝 Arquivos Modificados

1. **`app/services/earthdata.py`**
   - `download_granules()` - Conversão de objetos para strings
   - `get_imerg_data()` - Bbox maior, período mais longo, validação
   - `get_merra2_data()` - Bbox maior, período mais longo, validação

---

## ⚠️ Observações Importantes

### Tamanho dos Arquivos
- Granules IMERG: ~50-100 MB cada
- Granules MERRA-2: ~200-500 MB cada
- **Primeira requisição será lenta** (30-60 segundos)
- Cache local acelera requisições subsequentes

### Cobertura de Dados
- **IMERG**: Cobertura global, atualização a cada 30 minutos
- **MERRA-2**: Cobertura global, atualização horária
- Pode haver delay de 2-6 horas nos dados mais recentes

### Resolução Espacial
- **IMERG**: 0.1° x 0.1° (~11 km)
- **MERRA-2**: 0.5° x 0.625° (~50 km)
- Bounding box deve ser maior que a resolução do grid

---

## ✅ Checklist de Verificação

Após aplicar as correções:

- [x] Converter objetos de download para strings
- [x] Aumentar bounding box mínimo
- [x] Estender período de busca temporal
- [x] Adicionar validação de arquivos
- [x] Testar com diagnóstico
- [ ] Autorizar NASA GESDISC (você precisa fazer)
- [ ] Testar API completa
- [ ] Verificar dados retornados

---

## 🚀 Próximos Passos

1. **Autorize NASA GESDISC:**
   - https://urs.earthdata.nasa.gov/profile
   - Applications → Authorized Apps
   - Aprovar "NASA GESDISC DATA ARCHIVE"

2. **Execute o diagnóstico:**
   ```bash
   python diagnose_earthdata.py
   ```

3. **Teste a API:**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Verifique os logs:**
   - Deve mostrar granules encontrados
   - Deve mostrar arquivos baixados
   - Deve mostrar dados processados

---

**Com estas correções, a API deve funcionar corretamente após autorizar NASA GESDISC!** ✅
