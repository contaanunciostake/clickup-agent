# 🚀 Guia Completo de Deploy no Render.com

## 📋 Pré-requisitos

- ✅ Conta no GitHub
- ✅ Conta no Render.com (gratuita)
- ✅ Arquivos do ClickUp Agent (já inclusos)

## 🎯 Passo a Passo Completo

### **PASSO 1: Preparar Repositório GitHub**

1. **Crie um novo repositório no GitHub:**
   - Vá para [github.com](https://github.com)
   - Clique em "New repository"
   - Nome: `clickup-agent`
   - Visibilidade: Público ou Privado
   - Clique em "Create repository"

2. **Faça upload dos arquivos:**
   - Baixe todos os arquivos desta pasta
   - No GitHub, clique em "uploading an existing file"
   - Arraste todos os arquivos para o GitHub
   - Commit: "Initial commit: ClickUp Agent v2.1.0"

### **PASSO 2: Deploy no Render.com**

1. **Acesse o Render.com:**
   - Vá para [render.com](https://render.com)
   - Faça login ou crie uma conta gratuita

2. **Conecte o GitHub:**
   - No Dashboard, clique em "New Web Service"
   - Selecione "Build and deploy from a Git repository"
   - Clique em "Connect GitHub"
   - Autorize o Render a acessar seus repositórios

3. **Selecione o Repositório:**
   - Encontre o repositório `clickup-agent`
   - Clique em "Connect"

4. **Configuração Automática:**
   - **Name:** `clickup-agent` (ou nome de sua escolha)
   - **Region:** `Oregon (US West)` (recomendado)
   - **Branch:** `main`
   - **Root Directory:** (deixe em branco)
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT app:app`

5. **Plano de Serviço:**
   - **Free:** Para testes (pode hibernar após 15min)
   - **Starter ($7/mês):** Para produção 24/7
   - Selecione conforme sua necessidade

6. **Deploy:**
   - Clique em "Create Web Service"
   - Aguarde o deploy (2-5 minutos)

### **PASSO 3: Verificar Deploy**

1. **URL do Serviço:**
   - Após o deploy, você receberá uma URL como:
   - `https://clickup-agent-xxxx.onrender.com`

2. **Teste de Funcionamento:**
   - Acesse: `https://sua-url.onrender.com/health`
   - Deve retornar: `{"status": "healthy"}`

3. **Teste Completo:**
   - Acesse: `https://sua-url.onrender.com/test`
   - Deve criar uma tarefa teste no ClickUp

### **PASSO 4: Configurar ChatGPT**

1. **Abra seu GPT personalizado**
2. **Vá em Configure → Actions**
3. **Edite o schema OpenAPI:**

```yaml
openapi: 3.1.0
info:
  title: ClickUp Demand Creator
  description: Creates demands in ClickUp
  version: v2.1.0
servers:
  - url: https://SUA-URL-AQUI.onrender.com
paths:
  /webhook/demand:
    post:
      description: Send demand data to ClickUp
      operationId: createDemand
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                empresa:
                  type: string
                  description: Company name
                tarefa:
                  type: string
                  description: Task title
                tipo:
                  type: string
                  description: Task type
                equipe:
                  type: string
                  description: Team responsible
                hora:
                  type: string
                  description: Estimated hours
                data_hora_entrega:
                  type: integer
                  description: Unix timestamp for delivery
                responsavel:
                  type: string
                  description: Responsible person
              required:
                - empresa
                - tarefa
                - tipo
                - equipe
                - hora
      responses:
        '200':
          description: Demand created successfully
```

4. **Salve a configuração**

### **PASSO 5: Teste Final**

1. **No ChatGPT, digite:**
   > "Criar tarefa de teste para empresa TesteCorp, Victor responsável, prazo 1 semana"

2. **Verifique no ClickUp:**
   - Nova lista "TesteCorp" criada
   - Tarefa com Victor como responsável
   - Checklist e subtarefas adicionadas

## ✅ Configurações Já Incluídas

**Suas credenciais do ClickUp já estão configuradas:**
- ✅ API Token: pk_200493732_TQSTRPR2GOD0GTNOFEWIRVCHR127ZIBY
- ✅ Workspace ID: 90131539337
- ✅ Space ID: 90136445296
- ✅ Folder ID: 90138204864

**Responsáveis já configurados:**
- ✅ Victor: 200493732
- ✅ Angelo: 206512589
- ✅ Giorgia: 99908367
- ✅ Kelly: 200544020

## 🔧 Solução de Problemas

### **Deploy Falhou:**
- Verifique se todos os arquivos estão no repositório
- Confirme que `requirements.txt` está na raiz
- Veja os logs na aba "Logs" do Render

### **Erro 500:**
- Acesse `/health` para verificar status
- Verifique logs no painel do Render
- Confirme se as variáveis de ambiente estão corretas

### **ChatGPT não conecta:**
- Verifique se a URL no schema está correta
- Teste a URL diretamente no navegador
- Confirme que o serviço está online

### **Tarefas não aparecem no ClickUp:**
- Verifique se o token de API está correto
- Confirme os IDs do Workspace/Space/Folder
- Teste o endpoint `/test` diretamente

## 📊 Monitoramento

**No painel do Render.com:**
- **Logs:** Visualize logs em tempo real
- **Metrics:** CPU, memória, requests
- **Settings:** Altere configurações
- **Environment:** Gerencie variáveis

**Endpoints de monitoramento:**
- `/health` - Status do sistema
- `/config` - Configurações atuais
- `/responsaveis` - Lista de responsáveis

## 💰 Custos

**Plano Free:**
- ✅ 750 horas/mês gratuitas
- ⚠️ Hiberna após 15min de inatividade
- ✅ Ideal para testes

**Plano Starter ($7/mês):**
- ✅ Sempre online (24/7)
- ✅ Sem hibernação
- ✅ Ideal para produção

## 🎉 Pronto!

**Seu sistema ClickUp Agent está funcionando 24/7!**

- 🚀 Deploy completo em menos de 10 minutos
- 🔄 Atualizações automáticas via Git
- 📊 Monitoramento em tempo real
- 🛡️ Configuração de produção
- 💾 Backup automático

**Agora você pode criar demandas no ClickUp diretamente pelo ChatGPT!**

