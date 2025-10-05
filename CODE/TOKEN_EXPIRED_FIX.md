# 🔑 Token NASA Earthdata Expirado - Como Corrigir

**Erro:** `Authentication with Earthdata Login failed: invalid_credentials`

**Causa:** O token NASA Earthdata expirou ou está inválido.

---

## ⚡ Solução Rápida

### 1. Gerar Novo Token

1. **Acesse:** https://urs.earthdata.nasa.gov/profile
2. **Faça login** com suas credenciais
3. **Clique em:** "Generate Token"
4. **Copie o token** gerado (longa string começando com `eyJ...`)

### 2. Atualizar .env

Abra o arquivo `CODE/.env` e substitua o token antigo:

```env
# Antes (token expirado)
EARTHDATA_TOKEN=eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4i...ANTIGO

# Depois (token novo)
EARTHDATA_TOKEN=eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4i...NOVO
```

### 3. Reiniciar API

```powershell
# Parar a API (Ctrl+C se estiver rodando)

# Iniciar novamente
cd CODE
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

---

## 🔍 Como Identificar Token Expirado

### Sintomas

```
Authentication with Earthdata Login failed with:
{"error":"invalid_credentials","error_description":"Invalid user credentials"}
```

ou

```
You have 2 more attempts before being locked out for 10 minutes
```

### Causas

1. **Token expirou** (validade ~60 dias)
2. **Token foi revogado** manualmente
3. **Token copiado incorretamente** (com espaços ou quebras)

---

## ✅ Verificar Token Atual

### Ver Token no .env

```powershell
cd CODE
Get-Content .env | Select-String "EARTHDATA_TOKEN"
```

### Verificar Formato

Token válido deve:
- ✅ Começar com `eyJ`
- ✅ Ter ~500-1000 caracteres
- ✅ Estar em uma única linha
- ✅ Não ter espaços no início/fim

Token inválido:
- ❌ Muito curto (< 100 caracteres)
- ❌ Tem quebras de linha
- ❌ Tem espaços extras
- ❌ Está incompleto

---

## 🔐 Boas Práticas

### 1. Renovar Token Regularmente

- Token expira em ~60 dias
- Gere novo token antes de expirar
- Mantenha backup do token atual

### 2. Não Compartilhar Token

- Token é pessoal e intransferível
- Não commitar token no Git
- Não compartilhar em mensagens

### 3. Revogar Token Comprometido

Se o token foi exposto:
1. Acesse: https://urs.earthdata.nasa.gov/profile
2. Revogue o token antigo
3. Gere um novo token
4. Atualize o `.env`

---

## 🧪 Testar Novo Token

### 1. Teste Rápido

```powershell
cd CODE
.\venv\Scripts\Activate.ps1
python test_earthdata_auth.py
```

**Resultado esperado:**
```
✅ Encontrado: EARTHDATA_TOKEN
✅ SUCESSO: Autenticação bem-sucedida com token!
✅ SUCESSO: A busca de dados retornou resultados!
```

### 2. Teste Completo

```powershell
python diagnose_earthdata.py
```

**Resultado esperado:**
```
[PASSO 1/4] Verificando credenciais...
  ✅ Encontrado: EARTHDATA_TOKEN

[PASSO 2/4] Tentando autenticar...
  ✅ SUCESSO: Autenticação bem-sucedida com token!

[PASSO 3/4] Tentando buscar um granule de teste...
  ✅ SUCESSO: A busca de dados retornou resultados!
```

---

## ⚠️ Troubleshooting

### Erro: "You have 2 more attempts before being locked out"

**Causa:** Múltiplas tentativas de autenticação com token inválido

**Solução:**
1. **PARE** de tentar autenticar
2. **AGUARDE** 10 minutos
3. **GERE** um novo token
4. **ATUALIZE** o `.env`
5. **TESTE** novamente

### Erro: "Token not found"

**Causa:** Variável `EARTHDATA_TOKEN` não está no `.env`

**Solução:**
1. Verifique se o arquivo `.env` existe em `CODE/`
2. Verifique se a linha `EARTHDATA_TOKEN=...` está presente
3. Não deve haver espaços antes do `=`

### Erro persiste após gerar novo token

**Causas possíveis:**
1. Token não foi copiado completamente
2. Token tem espaços ou quebras de linha
3. Arquivo `.env` não foi salvo
4. API não foi reiniciada

**Solução:**
1. Copie o token novamente (todo ele)
2. Cole em uma única linha no `.env`
3. Salve o arquivo (Ctrl+S)
4. Reinicie a API completamente

---

## 📝 Checklist

- [ ] Acessei https://urs.earthdata.nasa.gov/profile
- [ ] Gerei novo token
- [ ] Copiei token completo (começa com `eyJ`)
- [ ] Abri arquivo `CODE/.env`
- [ ] Substituí token antigo pelo novo
- [ ] Token está em uma única linha
- [ ] Salvei o arquivo
- [ ] Reiniciei a API
- [ ] Testei: `python test_earthdata_auth.py`
- [ ] Autenticação bem-sucedida!

---

## 🎯 Resultado Final

Após seguir os passos, você deve ver:

```
INFO - Authenticating with NASA Earthdata using token
INFO - Successfully authenticated with NASA Earthdata using token
```

**Sem mensagens de erro!** ✅

---

**Gere um novo token agora e atualize o .env!**

**Link direto:** https://urs.earthdata.nasa.gov/profile
