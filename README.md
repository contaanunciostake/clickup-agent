# ClickUp Agent v2.1.0

Sistema completo para criação automática de demandas no ClickUp através de integração com ChatGPT.

## 🚀 Funcionalidades

- ✅ **Criação automática de tarefas** no ClickUp
- ✅ **Organização por empresa** (listas automáticas)
- ✅ **Atribuição automática de responsáveis** por nome
- ✅ **Checklists dinâmicos** por tipo de trabalho
- ✅ **Subtarefas automáticas** contextualizadas
- ✅ **Suporte a timestamps Unix** para precisão de datas
- ✅ **API REST completa** com documentação
- ✅ **Logs detalhados** para monitoramento
- ✅ **Pronto para produção** no Render.com

## 📋 Pré-requisitos

- Conta no [ClickUp](https://clickup.com)
- Token de API do ClickUp
- Conta no [Render.com](https://render.com) (para deploy)
- Conta no GitHub (para versionamento)

## 🛠️ Configuração Rápida

### 1. Deploy no Render.com

1. **Faça fork/clone** deste repositório
2. **Conecte ao Render.com:**
   - Vá para [render.com](https://render.com)
   - Clique em "New Web Service"
   - Conecte seu repositório GitHub
   - Selecione este projeto

3. **Configuração automática:**
   - O arquivo `render.yaml` já está configurado
   - Suas credenciais do ClickUp já estão incluídas
   - Deploy será feito automaticamente

### 2. Configuração do ChatGPT

Após o deploy, você receberá uma URL como: `https://seu-app.onrender.com`

**Configure seu GPT personalizado:**

```yaml
openapi: 3.1.0
info:
  title: ClickUp Demand Creator
  description: Creates demands in ClickUp
  version: v2.1.0
servers:
  - url: https://SEU-APP.onrender.com
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
```

## 👥 Responsáveis Configurados

O sistema reconhece automaticamente os seguintes responsáveis:

- **Victor** → ID: 200493732
- **Angelo** → ID: 206512589
- **Giorgia** → ID: 99908367
- **Kelly** → ID: 200544020

## 🎯 Exemplo de Uso

**Comando no ChatGPT:**
> "Criar landing page para EmpresaX, Victor responsável, prazo 1 semana"

**Resultado no ClickUp:**
- ✅ Tarefa criada na lista "EmpresaX"
- ✅ Victor atribuído como responsável
- ✅ Checklist de desenvolvimento adicionado
- ✅ 4 subtarefas criadas automaticamente
- ✅ Data de entrega configurada

## 📊 Endpoints da API

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Informações da API |
| `/health` | GET | Status do sistema |
| `/webhook/demand` | POST | Criar demanda |
| `/responsaveis` | GET | Lista responsáveis |
| `/config` | GET/POST | Configurações |
| `/test` | GET/POST | Teste do sistema |

## 🔧 Configurações do ClickUp

As seguintes configurações já estão incluídas:

```
API Token: pk_200493732_TQSTRPR2GOD0GTNOFEWIRVCHR127ZIBY
Workspace ID: 90131539337
Space ID: 90136445296
Folder ID: 90138204864
```

## 📝 Formato de Dados

### Entrada (JSON)
```json
{
  "empresa": "Nome da Empresa",
  "tarefa": "Título da tarefa",
  "tipo": "desenvolvimento",
  "equipe": "desenvolvimento",
  "hora": "8",
  "data_hora_entrega": 1735689600,
  "responsavel": "victor",
  "checklist": ["Item 1", "Item 2"],
  "subtarefas": ["Subtarefa 1", "Subtarefa 2"],
  "tags": ["urgente", "cliente"]
}
```

### Saída (JSON)
```json
{
  "success": true,
  "message": "Demanda criada com sucesso!",
  "data": {
    "task_id": "86a9xxx",
    "list_id": "901315xxx",
    "empresa": "Nome da Empresa",
    "responsavel": "200493732",
    "timestamp": "2025-06-30T16:30:00Z"
  }
}
```

## 🧪 Teste Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
python app.py

# Testar endpoint
curl -X POST http://localhost:5000/test
```

## 📈 Monitoramento

- **Logs:** Disponíveis no painel do Render.com
- **Health Check:** `GET /health`
- **Status:** Monitoramento automático de uptime

## 🔒 Segurança

- ✅ Variáveis de ambiente para credenciais
- ✅ Validação de dados de entrada
- ✅ Tratamento de erros robusto
- ✅ Logs de auditoria completos

## 📞 Suporte

Sistema desenvolvido por **Manus AI** para automação de demandas no ClickUp.

**Versão:** 2.1.0  
**Data:** 30/06/2025  
**Status:** Produção

---

## 🚀 Deploy Rápido

1. **Fork este repositório**
2. **Conecte ao Render.com**
3. **Deploy automático**
4. **Configure ChatGPT**
5. **Comece a usar!**

**Sistema pronto em menos de 5 minutos!** 🎉

