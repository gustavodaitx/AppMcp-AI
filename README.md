# Assistente de Lembretes Inteligente (IA + MCP + Google Sheets)

Este é um projeto completo e funcional que demonstra o uso do **Model Context Protocol (MCP)** para integrar uma planilha do Google Sheets como fonte de dados em tempo real, exibindo um painel de lembretes interativo e permitindo consultas dinâmicas a um modelo de Inteligência Artificial (**Google Gemini**).

---

## 🏗️ Arquitetura do Sistema

A aplicação segue o padrão de design proposto no plano de desenvolvimento, utilizando comunicação JSON-RPC baseada em subprocessos (`stdio`) para o MCP:

```
[Usuário] ──> [Interface Web HTML/CSS/JS] ──> [FastAPI (Backend / MCP Client)]
                                                    │               │
                                                    ▼               ▼
                                            [Google Gemini]    [MCP Server]
                                                                    │
                                                                    ▼
                                                            [Google Sheets]
```

O **FastAPI** atua como o **MCP Client**, que inicia o script `mcp_server/server.py` como um subprocesso seguro e se comunica com ele utilizando a entrada e saída padrão (stdio). O **MCP Server** expõe a ferramenta `read_sheet` que lê dados brutos da planilha de forma dinâmica e os devolve para a aplicação.

---

## 🛠️ Requisitos de Instalação

### 1. Pré-requisitos
- **Windows OS**
- **Python 3.11** (Já instalado via `winget` nas etapas de desenvolvimento)
- Conexão com a Internet para a leitura remota do Google Sheets e chamadas da API do Gemini.

### 2. Configurando o Ambiente Virtual
Na pasta raiz do projeto, execute os comandos no terminal do Windows (PowerShell):

```powershell
# Criação do Ambiente Virtual (caso ainda não tenha sido criado)
python -m venv .venv

# Ativação do Ambiente Virtual
.\.venv\Scripts\Activate.ps1

# Atualização de pacotes e instalação de dependências
pip install -r requirements.txt
```

### 3. Configuração do Arquivo `.env`
Duplique o arquivo `.env.example` e renomeie-o para `.env`.
Edite os valores conforme necessário:

```ini
# ID da planilha pública compartilhada
GOOGLE_SHEET_ID=1uSzbNC1gZQ8MYhzM4vjUUDknvCtxSzQvva2l6AzE4ec

# Chave de acesso do Gemini Free (Obtenha no Google AI Studio)
GEMINI_API_KEY=sua_chave_aqui

# Host e Porta de Execução
HOST=127.0.0.1
PORT=8000
```

---

## 🚀 Como Executar o Projeto

1. Certifique-se de que o ambiente virtual está ativo (`.venv`).
2. Inicialize o servidor backend FastAPI executando o comando:

```powershell
python app.py
```

3. Abra o navegador e acesse a URL da aplicação:
   👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🔬 Como Validar e Testar o MCP Server

Você pode testar a ferramenta `read_sheet` do MCP Server de duas formas:

### 1. Teste Rápido via Script de Serviço
Execute o script do serviço cliente diretamente. Ele rodará o MCP Server em segundo plano, enviará o sinal de inicialização do protocolo e executará a ferramenta de leitura:

```powershell
python services/sheets_service.py
```
*Se a leitura funcionar, você verá o output das tarefas e uma mensagem de sucesso no terminal.*

### 2. Usando o MCP CLI Inspector (Oficial)
O SDK oficial do MCP fornece uma interface interativa (web) para inspecionar servidores MCP locais. No terminal, execute:

```powershell
mcp dev mcp_server/server.py
```
Isso abrirá uma janela do navegador com o **MCP Inspector** onde você poderá ver a ferramenta declarada `read_sheet`, executá-la manualmente e inspecionar a carga JSON transmitida.

---

## 🤖 Como Funciona a IA e Como Trocar o Modelo

### Como trocar de modelo ou chave
A lógica de IA está completamente isolada no arquivo [services/ai_service.py](file:///c:/Users/Gustavo%20Daitx/Desktop/Ulbra/8Semestre/IA/AppMcp/services/ai_service.py).
Por padrão, o serviço utiliza o modelo gratuito **`gemini-1.5-flash`** do Google.
Para utilizar outra variação do Gemini, basta alterar o nome do modelo na linha de inicialização:

```python
self.model = genai.GenerativeModel('gemini-1.5-pro') # Exemplo para usar o Gemini 1.5 Pro
```

### Fallback Inteligente (Local)
Se você **não** tiver uma chave `GEMINI_API_KEY` ou a API falhar temporariamente por limites de cota, o serviço ativará o **modo Fallback Local**. O sistema usará uma lógica de processamento de linguagem simplificada para responder de forma nativa às principais perguntas como:
- *Quais entregas estão atrasadas?*
- *Etapas pertencentes ao Luis/João?*
- *Etapas concluídas?*

---

## ☁️ Publicação Gratuita (Deploy)

Você pode publicar esta aplicação gratuitamente no **Render** ou no **Railway**. Como a arquitetura usa MCP local via stdio (onde o backend spawna o servidor MCP como subprocesso), não há necessidade de configurar dois serviços separados no deploy; o FastAPI roda tudo em um único container unificado.

### Publicação no Render (Recomendado)
1. Crie uma conta gratuita em [render.com](https://render.com).
2. Conecte o repositório Git do projeto.
3. Crie um novo **Web Service**.
4. Configure as seguintes opções na criação:
   - **Environment / Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Nas configurações do Web Service, vá na seção **Environment Variables** e adicione as chaves:
   - `GOOGLE_SHEET_ID`
   - `GEMINI_API_KEY`
6. Clique em **Deploy**. A aplicação estará online no link gerado pelo Render!
