import os
import sys
import logging
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adicionar diretório raiz ao path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from services.sheets_service import SheetsService
from services.ai_service import AIService

# Carregar variáveis do .env
load_dotenv()

app = FastAPI(
    title="Assistente de Lembretes com IA e MCP",
    description="Aplicação FastAPI integrada ao Google Sheets e Gemini via MCP"
)

# Inicializar serviços
sheets_service = SheetsService()
ai_service = AIService()

# Criar diretórios templates e static se não existirem
os.makedirs(os.path.join(root_dir, "templates"), exist_ok=True)
os.makedirs(os.path.join(root_dir, "static"), exist_ok=True)

# Montar diretório de arquivos estáticos
app.mount("/static", StaticFiles(directory=os.path.join(root_dir, "static")), name="static")

# Configurar templates
templates = Jinja2Templates(directory=os.path.join(root_dir, "templates"))


class QuestionRequest(BaseModel):
    question: str


def parse_date(date_str: str) -> datetime:
    """Converte strings de datas de formatos variados de maneira segura."""
    if not date_str:
        return None
    date_str = date_str.strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d/%m/%y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def is_task_completed(task: dict) -> bool:
    """Verifica se a tarefa foi concluída."""
    etapa = task.get("etapa", "").lower()
    entrega = task.get("entrega_etapa", "").strip()
    return "finalizado" in etapa or len(entrega) > 0


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Renderiza a interface principal HTML."""
    return templates.TemplateResponse(request, "index.html", {})


@app.get("/api/tasks")
async def get_tasks():
    """Retorna os dados limpos da planilha."""
    try:
        tasks = await sheets_service.get_tasks()
        return JSONResponse(content=tasks)
    except Exception as e:
        logger.error(f"Erro ao obter tarefas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")


@app.get("/api/reminders")
async def get_reminders():
    """Retorna a lista de tarefas e o resumo estatístico de atrasos/prazos."""
    try:
        tasks = await sheets_service.get_tasks()
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        three_days_later = today + timedelta(days=3)
        
        delayed_tasks = []
        upcoming_tasks = []
        
        for task in tasks:
            # Ignorar tarefas já concluídas
            if is_task_completed(task):
                continue
                
            prev_date_str = task.get("data_prevista", "")
            prev_date = parse_date(prev_date_str)
            
            if not prev_date:
                continue
                
            if prev_date < today:
                delayed_tasks.append(task)
            elif today <= prev_date <= three_days_later:
                upcoming_tasks.append(task)
                
        summary = {
            "total": len(tasks),
            "delayed": len(delayed_tasks),
            "upcoming": len(upcoming_tasks)
        }
        
        return JSONResponse(content={
            "tasks": tasks,
            "summary": summary,
            "delayed_tasks": delayed_tasks,
            "upcoming_tasks": upcoming_tasks
        })
    except Exception as e:
        logger.error(f"Erro ao calcular lembretes: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter lembretes: {str(e)}")


@app.post("/api/ask")
async def ask_ai(request: QuestionRequest):
    """Recebe uma pergunta do usuário e responde usando Gemini e o contexto da planilha."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="A pergunta não pode estar vazia.")
        
    try:
        # Obter dados mais recentes da planilha
        tasks = await sheets_service.get_tasks()
        
        # Enviar pergunta para o serviço de IA
        answer = await ai_service.ask_question(request.question, tasks)
        
        return JSONResponse(content={"answer": answer})
    except Exception as e:
        logger.error(f"Erro ao consultar a IA: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar consulta da IA: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    # Ler configurações do .env com fallbacks
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    
    logger.info(f"Iniciando servidor FastAPI em http://{host}:{port}")
    uvicorn.run("app:app", host=host, port=port, reload=True)
