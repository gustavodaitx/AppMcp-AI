import os
import csv
import logging
import requests
from io import StringIO
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dados simulados (Mock) baseados na planilha original caso tudo falhe
MOCK_DATA = [
    {
        "proprietario": "K KRAS - ISLA BAYA",
        "etapa": "Finalizar",
        "data_solicitacao": "28/04/2026",
        "data_prevista": "27/06/2026",
        "entrega_etapa": ""
    },
    {
        "proprietario": "Luis Fernando Silva Belloli",
        "etapa": "Finalizado",
        "data_solicitacao": "20/05/2026",
        "data_prevista": "20/05/2026",
        "entrega_etapa": "24/05/2026"
    },
    {
        "proprietario": "Solaine Trindade da Silva",
        "etapa": "Finalizado",
        "data_solicitacao": "16/03/2026",
        "data_prevista": "16/03/2026",
        "entrega_etapa": "30/03/2026"
    },
    {
        "proprietario": "Peterson de Medeiros Batista",
        "etapa": "Finalizado",
        "data_solicitacao": "28/04/2026",
        "data_prevista": "28/04/2026",
        "entrega_etapa": "16/05/2026"
    },
    {
        "proprietario": "Nexo Incorporadora Ltda",
        "etapa": "Finalizar",
        "data_solicitacao": "06/06/2026",
        "data_prevista": "06/07/2026",
        "entrega_etapa": ""
    },
    {
        "proprietario": "Frederico Goldschmidt",
        "etapa": "Finalizado",
        "data_solicitacao": "12/05/2026",
        "data_prevista": "12/05/2026",
        "entrega_etapa": "13/05/2026"
    },
    {
        "proprietario": "Felipe Matozo",
        "etapa": "Em Aprovação",
        "data_solicitacao": "04/05/2026",
        "data_prevista": "04/05/2026",
        "entrega_etapa": "06/05/2026"
    },
    {
        "proprietario": "Bruna e Marcell",
        "etapa": "Detalhar",
        "data_solicitacao": "11/06/2026",
        "data_prevista": "21/06/2026",
        "entrega_etapa": ""
    },
    {
        "proprietario": "Fabio Dias",
        "etapa": "Detalhar",
        "data_solicitacao": "11/06/2026",
        "data_prevista": "11/06/2026",
        "entrega_etapa": "11/06/2026"
    },
    {
        "proprietario": "Danilo Alba",
        "etapa": "Lançar Pontos",
        "data_solicitacao": "07/06/2026",
        "data_prevista": "07/07/2026",
        "entrega_etapa": ""
    }
]

def fetch_sheets_data(sheet_id: str = None) -> list:
    """
    Busca os dados da planilha do Google Sheets.
    Tenta ler por exportação CSV pública. Se falhar, usa os dados simulados (Mock).
    """
    load_dotenv()
    
    if not sheet_id:
        sheet_id = os.getenv("GOOGLE_SHEET_ID", "1uSzbNC1gZQ8MYhzM4vjUUDknvCtxSzQvva2l6AzE4ec")
        
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    logger.info(f"Tentando ler a planilha pública com ID: {sheet_id}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            csv_content = response.text
            f = StringIO(csv_content)
            reader = csv.reader(f)
            
            # Pula o cabeçalho
            try:
                headers_row = next(reader)
            except StopIteration:
                raise ValueError("A planilha está vazia")
                
            tasks = []
            for row in reader:
                # Filtrar linhas vazias ou de cabeçalho repetido
                if not row or len(row) < 5:
                    continue
                
                proprietario = row[0].strip()
                # Pula linhas que não tem proprietário definido ou são apenas vírgulas
                if not proprietario or proprietario.lower() == 'proprietário':
                    continue
                
                # Mapeamento seguro baseado na estrutura da planilha
                etapa = row[1].strip() if len(row) > 1 else ""
                data_sol = row[2].strip() if len(row) > 2 else ""
                
                # Entrega da Etapa está na coluna 4
                entrega_etapa = row[4].strip() if len(row) > 4 else ""
                
                # Data Prevista está na coluna 6
                data_prevista = row[6].strip() if len(row) > 6 else ""
                
                # Correção de datas e valores nulos
                if "/" not in data_sol:
                    continue
                
                # Limpeza de data prevista se for inválida (ex: 30/12/1899)
                if "1899" in data_prevista:
                    data_prevista = ""

                tasks.append({
                    "proprietario": proprietario,
                    "etapa": etapa,
                    "data_solicitacao": data_sol,
                    "data_prevista": data_prevista,
                    "entrega_etapa": entrega_etapa
                })
            
            logger.info(f"Planilha lida com sucesso. {len(tasks)} registros importados.")
            if tasks:
                return tasks
            else:
                logger.warning("Nenhum registro válido extraído do CSV. Usando fallback.")
        else:
            logger.error(f"Erro ao acessar Google Sheets: Status Code {response.status_code}. Usando fallback.")
    except Exception as e:
        logger.error(f"Exceção durante a leitura da planilha: {e}. Usando dados simulados.")
        
    logger.info("Usando dados simulados (Mock Data) como fallback.")
    return MOCK_DATA

if __name__ == "__main__":
    data = fetch_sheets_data()
    print(data)
