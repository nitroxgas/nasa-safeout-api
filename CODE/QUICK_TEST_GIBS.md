# 🚀 Teste Rápido - NASA GIBS

**Tempo estimado:** 5 minutos

---

## 1️⃣ Instalar Dependência

```bash
cd CODE
pip install OWSLib==0.29.3
```

---

## 2️⃣ Testar Serviço GIBS Diretamente

Crie um arquivo `test_gibs.py`:

```python
from app.services.gibs import GIBSService

# Inicializar serviço
gibs = GIBSService()

# Testar conexão
print("✅ Conectado ao GIBS WMS")

# Obter dados ambientais para New York
data = gibs.get_environmental_data(
    latitude=40.7128,
    longitude=-74.0060,
    radius_km=5.0
)

print(f"\n📊 Dados obtidos:")
print(f"   Fonte: {data['source']}")
print(f"   Data: {data['date']}")
print(f"   Camadas disponíveis: {len(data['imagery'])}")

print(f"\n🖼️ URLs de imagens geradas:")
for key, img_data in data['imagery'].items():
    print(f"\n   {key}:")
    print(f"   - Camada: {img_data['layer']}")
    print(f"   - URL: {img_data['url'][:80]}...")
    print(f"   - Descrição: {img_data['description']}")

print("\n✅ Teste concluído com sucesso!")
```

Execute:
```bash
python test_gibs.py
```

**Resultado esperado:**
```
✅ Conectado ao GIBS WMS

📊 Dados obtidos:
   Fonte: NASA GIBS
   Data: 2025-10-05
   Camadas disponíveis: 9

🖼️ URLs de imagens geradas:

   true_color:
   - Camada: MODIS_Terra_CorrectedReflectance_TrueColor
   - URL: https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?SERVICE=WMS&...
   - Descrição: True color satellite imagery

   aerosol:
   - Camada: MODIS_Combined_Value_Added_AOD
   - URL: https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?SERVICE=WMS&...
   - Descrição: Aerosol Optical Depth (air quality indicator)

   ... (mais 7 camadas)

✅ Teste concluído com sucesso!
```

---

## 3️⃣ Testar via API

```bash
# Iniciar servidor
uvicorn app.main:app --reload
```

Em outro terminal:

```bash
curl -X POST http://localhost:8000/api/v1/environmental-data \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 40.7128,
    "longitude": -74.0060,
    "radius_meters": 5000
  }' | python -m json.tool
```

**Procure por:**
```json
{
  "data": {
    "satellite_imagery": {
      "source": "NASA GIBS",
      "imagery": {
        "true_color": {
          "url": "https://gibs.earthdata.nasa.gov/..."
        }
      }
    }
  }
}
```

---

## 4️⃣ Visualizar Imagem no Navegador

1. Copie uma das URLs retornadas
2. Cole no navegador
3. Você verá a imagem de satélite!

Exemplo de URL:
```
https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=MODIS_Terra_CorrectedReflectance_TrueColor&STYLES=&SRS=EPSG:4326&BBOX=-74.051,40.668,-74.006,40.758&WIDTH=512&HEIGHT=512&FORMAT=image/png&TIME=2025-10-05&TRANSPARENT=TRUE
```

---

## 5️⃣ Testar Diferentes Localizações

### São Paulo, Brasil
```python
data = gibs.get_environmental_data(-23.5505, -46.6333, 10.0)
```

### Los Angeles, EUA
```python
data = gibs.get_environmental_data(34.0522, -118.2437, 10.0)
```

### Londres, UK
```python
data = gibs.get_environmental_data(51.5074, -0.1278, 10.0)
```

### Tóquio, Japão
```python
data = gibs.get_environmental_data(35.6762, 139.6503, 10.0)
```

---

## 6️⃣ Testar Camadas Específicas

### Imagem de Incêndios
```python
fire_imagery = gibs.get_fire_imagery(
    latitude=34.0522,  # Los Angeles
    longitude=-118.2437,
    radius_km=100,
    days_back=7
)

print(f"Imagens de incêndio: {len(fire_imagery)} dias")
for img in fire_imagery[:3]:
    print(f"  {img['date']}: {img['url'][:80]}...")
```

### Imagem de Precipitação
```python
precip_imagery = gibs.get_precipitation_imagery(
    latitude=40.7128,  # New York
    longitude=-74.0060,
    radius_km=50,
    hours_back=24
)

print(f"Imagens de precipitação: {len(precip_imagery)} horas")
for img in precip_imagery[:3]:
    print(f"  {img['time']}: {img['url'][:80]}...")
```

---

## 7️⃣ Baixar e Salvar Imagem

```python
import requests
from PIL import Image
from io import BytesIO

# Obter URL
data = gibs.get_environmental_data(40.7128, -74.0060, 5.0)
url = data['imagery']['true_color']['url']

# Baixar imagem
response = requests.get(url)
img = Image.open(BytesIO(response.content))

# Salvar
img.save('satellite_image.png')
print("✅ Imagem salva como satellite_image.png")

# Mostrar
img.show()
```

---

## ✅ Checklist de Teste

- [ ] OWSLib instalado
- [ ] Serviço GIBS conecta com sucesso
- [ ] URLs são geradas corretamente
- [ ] Imagens são visualizadas no navegador
- [ ] API retorna campo `satellite_imagery`
- [ ] Diferentes localizações funcionam
- [ ] Camadas específicas funcionam
- [ ] Download de imagens funciona

---

## 🐛 Troubleshooting

### Erro: "No module named 'owslib'"
```bash
pip install OWSLib==0.29.3
```

### Erro: "Connection timeout"
- Verifique sua conexão com a internet
- GIBS pode estar temporariamente indisponível
- Tente novamente em alguns minutos

### URLs não carregam imagens
- Verifique se a URL está completa
- Algumas camadas podem não ter dados para todas as datas
- Tente uma data diferente

### Imagem aparece em branco
- Normal para algumas regiões/datas
- Tente aumentar o `radius_km`
- Tente uma camada diferente (ex: true_color)

---

## 📊 Resultado Esperado

Após todos os testes, você deve ter:

✅ **Serviço GIBS funcionando**
✅ **9 tipos de imagens disponíveis**
✅ **URLs geradas corretamente**
✅ **Imagens visualizadas no navegador**
✅ **API retornando dados GIBS**
✅ **Download de imagens funcionando**

---

**Tempo total:** ~5 minutos  
**Dificuldade:** Fácil  
**Resultado:** URLs de imagens de satélite em tempo real! 🛰️
