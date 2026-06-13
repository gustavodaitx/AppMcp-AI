import os
import sys
import json
import logging
from mcp.server.fastmcp import FastMCP

# Configurar logs no stderr para não interferir na comunicação JSON-RPC via stdio
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

# Adicionar o diretório atual ao sys.path para que o import funcione em qualquer contexto de execução
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from sheets_tool import fetch_sheets_data
except ImportError:
    # Caso seja executado a partir do diretório raiz
    from mcp_server.sheets_tool import fetch_sheets_data

# Inicializar o servidor FastMCP
mcp = FastMCP("Google-Sheets-Reminder-Server")

@mcp.tool()
def read_sheet(sheet_id: str = None) -> str:
    """
    Lê os dados da planilha configurada do Google Sheets.
    
    Retorna uma string JSON contendo uma lista de objetos com chaves:
    - proprietario: Nome do proprietário
    - etapa: Etapa atual do processo
    - data_solicitacao: Data em que a etapa foi solicitada
    - data_prevista: Data prevista para a entrega da etapa
    - entrega_etapa: Data da entrega final da etapa (ou vazio caso pendente)
    """
    logger.info("Ferramenta read_sheet chamada via MCP")
    try:
        data = fetch_sheets_data(sheet_id)
        return json.dumps(data, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erro ao ler a planilha: {e}")
        return json.dumps({"error": f"Falha ao processar os dados: {str(e)}"}, ensure_ascii=False)

if __name__ == "__main__":
    # Executar o servidor no modo stdio
    logger.info("Iniciando MCP Server no transporte stdio...")
    mcp.run(transport="stdio")
