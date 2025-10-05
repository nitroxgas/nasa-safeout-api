# 🔐 Atualização: Autenticação Apenas com Token

**Data:** 2025-10-05  
**Status:** ✅ Implementado

---

## 📋 Mudança Implementada

A API agora usa **APENAS token** para autenticação com NASA Earthdata.

### Antes
```env
# Opção 1: Token
EARTHDATA_TOKEN=...

# Opção 2: Username/Password
EARTHDATA_USERNAME=...
EARTHDATA_PASSWORD=...
```

### Depois
```env
# Apenas Token
EARTHDATA_TOKEN=...
```

---

## 🎯 Motivos da Mudança

### 1. Segurança
- ✅ Token pode ser revogado sem mudar senha
- ✅ Não expõe senha em logs ou arquivos
- ✅ Melhor controle de acesso

### 2. Simplicidade
- ✅ Apenas uma variável de ambiente
- ✅ Menos configuração
- ✅ Mais fácil de gerenciar

### 3. Boas Práticas
- ✅ Recomendado pela NASA
- ✅ Padrão da indústria
- ✅ Melhor para produção

---

## 📝 Arquivos Modificados

### 1. `app/config.py`
```python
# Antes
earthdata_username: str = ""
earthdata_password: str = ""
earthdata_token: str = ""

# Depois
earthdata_token: str = ""
```

### 2. `app/services/earthdata.py`
```python
# Antes
if settings.earthdata_token:
    # Use token
elif settings.earthdata_username and settings.earthdata_password:
    # Use username/password
else:
    # Error

# Depois
if settings.earthdata_token:
    # Use token
else:
    # Error
```

### 3. `test_earthdata_auth.py`
- Removida lógica de username/password
- Apenas verifica token
- Mensagens de erro simplificadas

### 4. `diagnose_earthdata.py`
- Removida lógica de username/password
- Apenas verifica token
- Instruções para gerar token

### 5. `.env.example`
```env
# Antes
EARTHDATA_TOKEN=your_token_here
EARTHDATA_USERNAME=your_username_here
EARTHDATA_PASSWORD=your_password_here

# Depois
EARTHDATA_TOKEN=your_token_here
```

### 6. `README.md`
- Atualizada seção de configuração
- Adicionadas instruções para gerar token
- Removidas referências a username/password

---

## 🔑 Como Obter um Token

### Passo a Passo

1. **Acesse:** https://urs.earthdata.nasa.gov/profile
2. **Faça login** com sua conta NASA Earthdata
3. **Clique em:** "Generate Token"
4. **Copie o token** gerado (longa string JWT)
5. **Cole no `.env`:**
   ```env
   EARTHDATA_TOKEN=eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4i...
   ```

### Validade do Token

- ⏰ **Duração:** ~60 dias
- 🔄 **Renovação:** Gere um novo token quando expirar
- ✅ **Múltiplos tokens:** Você pode ter vários tokens ativos

---

## 🧪 Como Testar

### 1. Verificar Token no .env

```bash
cd CODE
cat .env | grep EARTHDATA_TOKEN
```

Deve mostrar:
```
EARTHDATA_TOKEN=eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4i...
```

### 2. Testar Autenticação

```bash
python test_earthdata_auth.py
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

### 3. Testar API

```bash
uvicorn app.main:app --reload
```

Verifique os logs:
```
INFO - Authenticating with NASA Earthdata using token
INFO - Successfully authenticated with NASA Earthdata using token
```

---

## ⚠️ Troubleshooting

### Erro: "Token not found"

**Solução:**
1. Verifique se o arquivo `.env` existe em `CODE/`
2. Verifique se a linha `EARTHDATA_TOKEN=...` está presente
3. Não deve haver espaços antes ou depois do `=`
4. Token deve estar em uma única linha (sem quebras)

### Erro: "Authentication FAILED"

**Causas possíveis:**
1. Token expirou (validade ~60 dias)
2. Token inválido ou corrompido
3. Problemas de rede

**Solução:**
1. Gere um novo token em https://urs.earthdata.nasa.gov/profile
2. Atualize o `.env` com o novo token
3. Reinicie a API

### Erro: "Invalid or expired token"

**Solução:**
1. Token definitivamente expirou
2. Gere um novo token
3. Atualize o `.env`
4. Execute `python test_earthdata_auth.py` para confirmar

---

## 📊 Impacto da Mudança

### Código Simplificado

**Antes:**
- 2 métodos de autenticação
- Lógica de fallback
- Mais variáveis de ambiente
- Mais complexo

**Depois:**
- 1 método de autenticação
- Código mais simples
- Menos variáveis
- Mais fácil de manter

### Segurança Melhorada

**Antes:**
- Senha em texto plano no `.env`
- Risco de exposição de senha
- Difícil de revogar acesso

**Depois:**
- Apenas token no `.env`
- Token pode ser revogado facilmente
- Melhor controle de acesso

---

## ✅ Checklist de Migração

Se você tinha username/password configurado:

- [ ] Gerar token em https://urs.earthdata.nasa.gov/profile
- [ ] Adicionar `EARTHDATA_TOKEN` no `.env`
- [ ] Remover `EARTHDATA_USERNAME` do `.env` (opcional)
- [ ] Remover `EARTHDATA_PASSWORD` do `.env` (opcional)
- [ ] Testar: `python test_earthdata_auth.py`
- [ ] Reiniciar API
- [ ] Verificar logs para confirmar uso do token

---

## 📚 Documentação Atualizada

Todos os documentos foram atualizados para refletir apenas token:

1. ✅ `README.md`
2. ✅ `CODE/.env.example`
3. ✅ `CODE/test_earthdata_auth.py`
4. ✅ `CODE/diagnose_earthdata.py`
5. ✅ `CODE/app/config.py`
6. ✅ `CODE/app/services/earthdata.py`

---

## 🎯 Resultado Final

### Configuração Simplificada

```env
# Apenas 2 variáveis necessárias
EARTHDATA_TOKEN=seu_token_aqui
FIRMS_API_KEY=sua_chave_aqui
```

### Código Mais Limpo

```python
# Autenticação simplificada
if settings.earthdata_token:
    os.environ["EARTHDATA_TOKEN"] = settings.earthdata_token
    auth = earthaccess.login(strategy="environment")
```

### Melhor Segurança

- 🔐 Token revogável
- 🔐 Sem senhas em texto plano
- 🔐 Melhor auditoria de acesso

---

**Autenticação simplificada para apenas token implementada com sucesso!** ✅

**Benefícios:**
- ✅ Mais seguro
- ✅ Mais simples
- ✅ Mais fácil de manter
- ✅ Melhor para produção

**Próximo passo:** Autorize NASA GESDISC para ativar todas as fontes!
