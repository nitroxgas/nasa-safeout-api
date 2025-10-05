# Guia de Configuração - NASA SafeOut API

## Pré-requisitos

### 1. Python
- Python 3.9 ou superior
- pip (gerenciador de pacotes Python)

### 2. Conta NASA Earthdata
1. Acesse https://urs.earthdata.nasa.gov/
2. Clique em "Register" para criar uma conta
3. Preencha o formulário de registro
4. Confirme seu email
5. Anote seu username e password

### 3. NASA FIRMS API Key
1. Acesse https://firms.modaps.eosdis.nasa.gov/api/
2. Clique em "Request API Key"
3. Preencha o formulário
4. Você receberá a chave por email
5. Anote sua API key

## Instalação Passo a Passo

### Passo 1: Preparar o Ambiente

```powershell
# Navegue até a pasta CODE
cd D:\NASASafeOutData\CODE

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Se houver erro de execução de scripts, execute:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Passo 2: Instalar Dependências

```powershell
# Atualize pip
python -m pip install --upgrade pip

# Instale as dependências
pip install -r requirements.txt
```

### Passo 3: Configurar Variáveis de Ambiente

```powershell
# Copie o arquivo de exemplo
copy .env.example .env

# Edite o arquivo .env com um editor de texto
notepad .env
```

Preencha as seguintes variáveis no arquivo `.env`:

```env
# NASA Earthdata Credentials
EARTHDATA_USERNAME=seu_username_aqui
EARTHDATA_PASSWORD=sua_senha_aqui

# NASA FIRMS API Key
FIRMS_API_KEY=sua_chave_api_aqui

# Outras configurações podem manter os valores padrão
```

### Passo 4: Configurar earthaccess

O earthaccess precisa ser configurado na primeira vez:

```powershell
# Execute o Python interativo
python

# No prompt do Python, execute:
>>> import earthaccess
>>> earthaccess.login(persist=True)
```

Você será solicitado a inserir suas credenciais NASA Earthdata. Elas serão salvas de forma segura.

Digite `exit()` para sair do Python.

### Passo 5: Criar Diretório de Cache

```powershell
# Crie o diretório de cache
New-Item -ItemType Directory -Path "cache" -Force
```

### Passo 6: Testar a Instalação

```powershell
# Execute os testes
pytest

# Ou execute um teste específico
pytest tests/test_api.py -v
```

### Passo 7: Executar a API

```powershell
# Método 1: Usando uvicorn diretamente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Método 2: Usando o script Python
python -m app.main
```

A API estará disponível em:
- **API**: http://localhost:8000
- **Documentação Interativa (Swagger)**: http://localhost:8000/docs
- **Documentação Alternativa (ReDoc)**: http://localhost:8000/redoc

## Verificação da Instalação

### 1. Verificar Health Check

Abra um navegador e acesse:
```
http://localhost:8000/health
```

Você deve ver:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-04T21:47:09Z",
  "version": "1.0.0"
}
```

### 2. Verificar Informações da API

Acesse:
```
http://localhost:8000/api/v1/info
```

### 3. Testar Endpoint Principal

Use o Swagger UI em http://localhost:8000/docs ou execute:

```powershell
# Usando curl (se disponível)
curl -X POST "http://localhost:8000/api/v1/environmental-data" `
  -H "Content-Type: application/json" `
  -d '{\"latitude\": -27.5954, \"longitude\": -48.5480, \"radius_meters\": 5000}'

# Ou usando Invoke-RestMethod (PowerShell)
$body = @{
    latitude = -27.5954
    longitude = -48.5480
    radius_meters = 5000
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/environmental-data" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"
```

## Solução de Problemas

### Erro: "earthaccess library not installed"

```powershell
pip install earthaccess
```

### Erro: "Not authenticated with NASA Earthdata"

Reconfigure as credenciais:
```powershell
python -c "import earthaccess; earthaccess.login(persist=True)"
```

### Erro: "FIRMS API key not configured"

Verifique se a variável `FIRMS_API_KEY` está configurada no arquivo `.env`.

### Erro: "ModuleNotFoundError"

Certifique-se de que o ambiente virtual está ativado e as dependências estão instaladas:
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Porta 8000 já em uso

Altere a porta no arquivo `.env`:
```env
API_PORT=8001
```

Ou especifique ao executar:
```powershell
uvicorn app.main:app --reload --port 8001
```

### Erro de Permissão no PowerShell

Se você receber erro ao executar scripts:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Estrutura de Arquivos Após Instalação

```
CODE/
├── venv/                    # Ambiente virtual (criado)
├── cache/                   # Cache de dados (criado)
├── app/                     # Código da aplicação
├── tests/                   # Testes
├── .env                     # Configurações (criado)
├── requirements.txt         # Dependências
└── README.md               # Documentação
```

## Próximos Passos

1. **Testar Integração com Earthdata**
   - Execute testes de download de dados
   - Verifique logs para erros

2. **Explorar a Documentação**
   - Acesse http://localhost:8000/docs
   - Teste diferentes endpoints
   - Veja exemplos de requisições

3. **Desenvolver Funcionalidades**
   - Implemente integração com fontes de dados
   - Adicione processamento de dados
   - Crie testes adicionais

4. **Otimizar Performance**
   - Configure cache adequadamente
   - Ajuste timeouts
   - Monitore uso de recursos

## Recursos Adicionais

- [Documentação earthaccess](https://earthaccess.readthedocs.io/)
- [Documentação FastAPI](https://fastapi.tiangolo.com/)
- [NASA Earthdata](https://earthdata.nasa.gov/)
- [OpenAQ API](https://docs.openaq.org/)
- [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/)

## Suporte

Para problemas ou dúvidas:
1. Verifique os logs da aplicação
2. Consulte a documentação
3. Verifique as issues conhecidas
4. Abra uma nova issue se necessário
