# Projeto: Assistente de Lembretes com IA + MCP + Google Sheets

## Objetivo

Criar uma aplicação simples, funcional e demonstrável utilizando:

* Python
* MCP (Model Context Protocol)
* Google Sheets como fonte de dados
* IA integrada (Claude, OpenAI ou modelo gratuito compatível)
* Interface Web HTML simples
* Ferramentas gratuitas e Open Source sempre que possível

A aplicação deve demonstrar claramente o uso de MCP para conectar uma ferramenta externa (Google Sheets) a um sistema com IA.

---

# Requisitos Funcionais

A aplicação deve ler uma planilha do Google Sheets contendo os campos:

* Nome do Proprietário
* Etapa
* Data da Solicitação
* Data Prevista da Entrega Etapa
* Entrega da Etapa

Ao acessar a aplicação web, exibir uma tabela contendo:

| Nome do Proprietário | Etapa | Data da Solicitação | Data Prevista da Entrega Etapa | Entrega da Etapa |
| -------------------- | ----- | ------------------- | ------------------------------ | ---------------- |

---

# Funcionalidade de Lembretes

A aplicação deve identificar automaticamente:

### Entregas Atrasadas

Quando:

Data Prevista < Data Atual

Exibir destaque visual em vermelho.

---

### Entregas Próximas

Quando:

Data Prevista <= Hoje + 3 dias

Exibir destaque visual em amarelo.

---

### Resumo Automático

Exibir no topo:

* Total de registros
* Total de entregas atrasadas
* Total de entregas próximas do vencimento

---

# Funcionalidade de IA

Adicionar um campo de pergunta:

Exemplos:

* Quais entregas estão atrasadas?
* Quais etapas pertencem ao João?
* O que vence esta semana?
* Liste apenas entregas concluídas.

A IA deverá responder usando os dados da planilha.

Não utilizar banco de dados.

Os dados devem ser carregados diretamente do Google Sheets.

---

# Uso obrigatório de MCP

Implementar um MCP Server responsável por acessar a planilha.

Arquitetura:

Usuário
↓
Interface HTML
↓
FastAPI
↓
IA
↓
MCP Client
↓
MCP Server
↓
Google Sheets

O MCP Server deve disponibilizar uma ferramenta chamada:

read_sheet

Responsável por retornar os dados da planilha.

---

# Tecnologias

Utilizar:

## Backend

* Python 3.11+
* FastAPI
* Uvicorn

## Frontend

* HTML
* CSS simples
* JavaScript Vanilla

Sem React.

Sem frameworks pesados.

---

# Ferramentas Gratuitas

Utilizar apenas soluções gratuitas:

### Google Sheets

Leitura via API do Google ou gspread.

### MCP

Implementar MCP Server usando SDK oficial.

### IA

Preferencialmente:

* OpenRouter (modelo gratuito)
  ou
* Gemini Free
  ou
* Claude se configurado pelo usuário

Toda integração deve ficar desacoplada em uma camada:

services/ai_service.py

---

# Estrutura Esperada

Gerar a estrutura:

project/

├── app.py

├── requirements.txt

├── .env.example

├── README.md

├── mcp_server/

│ ├── server.py

│ └── sheets_tool.py

├── services/

│ ├── sheets_service.py

│ └── ai_service.py

├── templates/

│ └── index.html

├── static/

│ ├── style.css

│ └── app.js

└── models/

---

# Interface Web

Criar uma página simples.

Layout:

---

Assistente de Entregas

Resumo:

Total: X

Atrasadas: Y

Próximas: Z

---

[Tabela]

---

Pergunte à IA:

[ campo texto ]

[ botão Perguntar ]

Resposta:

...

---

Visual limpo.

Sem dependências externas.

---

# API

Criar endpoints:

GET /

Página principal

GET /api/tasks

Retorna os dados da planilha

GET /api/reminders

Retorna atrasadas e próximas

POST /api/ask

Recebe pergunta do usuário e responde usando IA

---

# Integração Google Sheets

Utilizar a planilha:

https://docs.google.com/spreadsheets/d/1uSzbNC1gZQ8MYhzM4vjUUDknvCtxSzQvva2l6AzE4ec

Implementar leitura configurável por:

GOOGLE_SHEET_ID

no arquivo .env

---

# Passo a Passo Obrigatório

Gerar:

1. Estrutura completa do projeto
2. requirements.txt
3. Arquivo .env.example
4. MCP Server completo
5. Integração Google Sheets
6. Serviço de IA
7. Backend FastAPI
8. Interface HTML
9. CSS
10. JavaScript
11. Instruções de execução
12. Como testar
13. Como validar o MCP
14. Como trocar o modelo de IA
15. Como publicar gratuitamente

---

# Publicação Gratuita

Explicar como publicar em:

* Render
  ou
* Railway
  ou
* Fly.io

---

# Qualidade do Código

Requisitos:

* Código comentado
* Organização por módulos
* Tratamento de erros
* Logs básicos
* Código pronto para execução

Gerar todos os arquivos completos.

Não usar pseudocódigo.

Entregar código funcional e executável.
