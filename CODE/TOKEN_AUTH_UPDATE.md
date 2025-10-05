# 🔐 Atualização: Autenticação via Token NASA Earthdata

**Data:** 2025-10-05  
**Status:** ✅ Implementado

---

## 📋 Resumo das Mudanças

O projeto foi atualizado para suportar autenticação via **EARTHDATA_TOKEN**, que é o método recomendado para produção.

### ✅ Arquivos Modificados

1. **`app/config.py`**
   - Adicionado campo `earthdata_token: str = ""`
   - Mantido suporte para username/password como fallback

2. **`app/services/earthdata.py`**
   - Prioriza autenticação via token se disponível
   - Fallback automático para username/password
   - Logging diferenciado para cada método

3. **`test_earthdata_auth.py`**
   - Detecta e usa token se disponível
   - Suporte para ambos os métodos de autenticação
   - Mensagens de erro específicas para cada método

4. **`.env.example`**
   - Documentação de ambas as opções
   - Token como opção recomendada

5. **Documentação**
   - `IMPLEMENTATION_GUIDE.md` atualizado
   - `README.md` atualizado
   - `IMPLEMENTATION_SUMMARY.md` atualizado

---

## 🔑 Como Usar

### Opção 1: Token (Recomendado)

No arquivo `.env`:
```env
EARTHDATA_TOKEN=eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4i...
```

**Vantagens:**
- ✅ Mais seguro (sem senha em texto plano)
- ✅ Pode ter permissões específicas
- ✅ Fácil de revogar
- ✅ Recomendado para produção

**Desvantagens:**
- ⚠️ Tem validade limitada (precisa renovar)
- ⚠️ Requer geração manual no portal NASA

### Opção 2: Username/Password (Fallback)

No arquivo `.env`:
```env
EARTHDATA_USERNAME=seu_username
EARTHDATA_PASSWORD=sua_senha
```

**Vantagens:**
- ✅ Não expira
- ✅ Mais simples de configurar

**Desvantagens:**
- ⚠️ Menos seguro
- ⚠️ Senha em texto plano no .env

---

## 🔄 Lógica de Autenticação

O sistema segue esta ordem:

1. **Verifica se `EARTHDATA_TOKEN` existe**
   - Se sim: usa token
   - Se não: vai para passo 2

2. **Verifica se `EARTHDATA_USERNAME` e `EARTHDATA_PASSWORD` existem**
   - Se sim: usa username/password
   - Se não: falha com mensagem de erro

3. **Tenta autenticar com earthaccess**
   - Sucesso: marca como autenticado
   - Falha: registra erro e continua sem autenticação

---

## 🧪 Como Testar

### Teste de Autenticação

```bash
cd CODE
python test_earthdata_auth.py
```

**Saída esperada com token:**
```
1. Checking environment variables...
   EARTHDATA_TOKEN: ✓ Set
   EARTHDATA_USERNAME: ✓ Set
   EARTHDATA_PASSWORD: ✓ Set

   Using Token Authentication
   Token: eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9...

3. Testing authentication with NASA Earthdata...
   Using token authentication...
   ✓ Authentication SUCCESSFUL!
   Authenticated using token
```

### Teste Completo da API

```bash
cd CODE
python test_complete_api.py
```

---

## 📝 Logs de Autenticação

O sistema agora registra qual método está sendo usado:

**Com token:**
```
INFO: Authenticating with NASA Earthdata using token
INFO: Successfully authenticated with NASA Earthdata using token
```

**Com username/password:**
```
INFO: Authenticating with NASA Earthdata using username/password
INFO: Successfully authenticated with NASA Earthdata using credentials
```

**Sem credenciais:**
```
WARNING: NASA Earthdata credentials not configured.
Set EARTHDATA_TOKEN or EARTHDATA_USERNAME and EARTHDATA_PASSWORD in .env
```

---

## 🔐 Como Obter um Token

1. **Acesse:** https://urs.earthdata.nasa.gov/
2. **Faça login** com suas credenciais
3. **Vá para:** Profile → Generate Token
4. **Copie o token** gerado
5. **Cole no `.env`:**
   ```env
   EARTHDATA_TOKEN=seu_token_aqui
   ```

---

## ⚠️ Importante

### Validade do Token

- Tokens NASA Earthdata têm **validade limitada** (geralmente 60 dias)
- Quando expirar, você verá erro de autenticação
- Solução: Gerar novo token no portal NASA

### Segurança

- ✅ **NUNCA** commite o arquivo `.env` no git
- ✅ `.env` já está no `.gitignore`
- ✅ Use `.env.example` como template
- ✅ Em produção, use variáveis de ambiente do sistema

### Compatibilidade

- ✅ Compatível com `earthaccess >= 0.8.0`
- ✅ Funciona com ambos os métodos
- ✅ Fallback automático
- ✅ Sem breaking changes

---

## 🎯 Benefícios da Atualização

1. **Segurança Melhorada**
   - Token pode ser revogado sem mudar senha
   - Não expõe senha em logs

2. **Flexibilidade**
   - Suporta ambos os métodos
   - Escolha automática do melhor método

3. **Produção-Ready**
   - Token é o método recomendado pela NASA
   - Melhor para ambientes de produção

4. **Backward Compatible**
   - Código antigo continua funcionando
   - Sem necessidade de mudanças imediatas

---

## ✅ Checklist de Migração

Se você está migrando de username/password para token:

- [ ] Obter token no portal NASA Earthdata
- [ ] Adicionar `EARTHDATA_TOKEN` no `.env`
- [ ] Testar autenticação: `python test_earthdata_auth.py`
- [ ] (Opcional) Remover username/password do `.env`
- [ ] Verificar logs para confirmar uso do token

---

## 📞 Troubleshooting

### Erro: "Authentication FAILED"

**Com token:**
1. Verifique se o token está completo (sem quebras de linha)
2. Verifique se o token não expirou
3. Gere um novo token no portal NASA

**Com username/password:**
1. Verifique se as credenciais estão corretas
2. Verifique se a conta está ativa
3. Tente fazer login no portal NASA

### Erro: "Invalid or expired token"

1. O token expirou
2. Gere um novo token: https://urs.earthdata.nasa.gov/
3. Atualize o `.env` com o novo token
4. Reinicie a aplicação

### Sistema não está usando o token

1. Verifique se `EARTHDATA_TOKEN` está no `.env`
2. Verifique se não há espaços extras
3. Reinicie a aplicação
4. Verifique os logs para confirmar

---

**Atualização implementada com sucesso!** ✅
