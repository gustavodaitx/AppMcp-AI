import os
import sys
import json
import logging
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adicionar o diretório raiz para permitir importações locais de fallback
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.append(root_dir)

class SheetsService:
    def __init__(self):
        # Determina o executável do Python ativo (do venv)
        self.python_exe = sys.executable
        # Caminho absoluto do script do servidor MCP
        self.server_script = os.path.join(root_dir, "mcp_server", "server.py")
        
        logger.info(f"SheetsService configurado com Python: {self.python_exe} e Script: {self.server_script}")

    async def get_tasks(self) -> list:
        """
        Chama a ferramenta read_sheet do MCP Server utilizando transporte stdio.
        Se falhar por qualquer motivo, faz o fallback direto para o módulo sheets_tool.
        """
        server_params = StdioServerParameters(
            command=self.python_exe,
            args=[self.server_script],
            env=os.environ.copy()
        )
        
        logger.info("Iniciando conexão com o MCP Server via stdio...")
        try:
            # Conecta ao servidor MCP subprocesso
            async with stdio_client(server_params) as (read_channel, write_channel):
                async with ClientSession(read_channel, write_channel) as session:
                    # Inicializar a sessão do cliente MCP
                    logger.info("Inicializando sessão com MCP Server...")
                    await session.initialize()
                    
                    # Chamar a ferramenta 'read_sheet' exposta pelo servidor
                    logger.info("Chamando a ferramenta read_sheet do MCP Server...")
                    result = await session.call_tool("read_sheet")
                    
                    # Tratar a resposta da ferramenta
                    if result and result.content:
                        json_str = result.content[0].text
                        data = json.loads(json_str)
                        if isinstance(data, dict) and "error" in data:
                            logger.error(f"Erro retornado pelo MCP Server: {data['error']}")
                            raise ValueError(data["error"])
                        return data
                    else:
                        raise ValueError("MCP Server retornou conteúdo vazio")
                        
        except Exception as e:
            logger.error(f"Falha na comunicação com o MCP Server: {e}. Executando fallback direto...")
            # Fallback de segurança: importar e chamar diretamente para evitar que a aplicação quebre
            try:
                from mcp_server.sheets_tool import fetch_sheets_data
                return fetch_sheets_data()
            except Exception as fe:
                logger.critical(f"Falha crítica ao executar fallback direto: {fe}")
                return []

# Para testes rápidos
if __name__ == "__main__":
    service = SheetsService()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        tasks = loop.run_until_complete(service.get_tasks())
        print(f"Sucesso! Encontradas {len(tasks)} tarefas.")
        if tasks:
            print(tasks[0])
    finally:
        loop.close()
