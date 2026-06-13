import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
import requests

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adicionar diretório raiz ao path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.append(root_dir)

class AIService:
    def __init__(self):
        load_dotenv()
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
        self.provider = None
        
        if self.gemini_key:
            try:
                genai.configure(api_key=self.gemini_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.provider = "gemini"
                logger.info("Serviço Gemini configurado e pronto para uso.")
            except Exception as e:
                logger.error(f"Erro ao inicializar o SDK do Gemini: {e}")
        elif self.openrouter_key:
            try:
                self.openrouter_model = os.getenv(
                    "OPENROUTER_MODEL",
                    "liquid/lfm-2.5-1.2b-thinking:free"
                )
                self.provider = "openrouter"
                logger.info(f"Serviço OpenRouter configurado com o modelo {self.openrouter_model}.")
            except Exception as e:
                logger.error(f"Erro ao inicializar o cliente do OpenRouter: {e}")
        
        if not self.provider:
            logger.warning("Nenhuma chave de API de IA (Gemini ou OpenRouter) configurada no .env. A IA rodará no modo Fallback Local.")

    async def ask_question(self, question: str, tasks_data: list) -> str:
        """
        Envia a pergunta do usuário junto com o contexto dos dados da planilha para a IA.
        Decide o provedor (Gemini, OpenRouter ou Fallback) com base nas variáveis de ambiente.
        """
        current_date_str = datetime.now().strftime("%d/%m/%Y")
        
        # Formatar os dados em uma tabela Markdown legível para dar contexto à IA
        context_table = "| Proprietário | Etapa | Data Solicitação | Data entrega Prevista | Entrega Etapa |\n"
        context_table += "|---|---|---|---|---|\n"
        for task in tasks_data:
            prop = task.get("proprietario", "")
            etapa = task.get("etapa", "")
            sol = task.get("data_solicitacao", "")
            prev = task.get("data_prevista", "")
            ent = task.get("entrega_etapa", "")
            context_table += f"| {prop} | {etapa} | {sol} | {prev} | {ent or 'Pendente'} |\n"

        prompt = (
            f"Você é um Assistente de Lembretes inteligente.\n"
            f"Data atual do sistema: {current_date_str}\n\n"
            f"Aqui estão os dados atuais carregados diretamente da planilha:\n"
            f"{context_table}\n\n"
            f"Pergunta do usuário: \"{question}\"\n\n"
            f"Instruções:\n"
            f"1. Responda à pergunta do usuário de forma clara, amigável e objetiva com base nos dados fornecidos acima.\n"
            f"2. Use formatação Markdown (como negrito, listas ou tabelas) para deixar a resposta legível.\n"
            f"3. Se o usuário perguntar sobre entregas atrasadas, compare a data prevista de cada item pendente com a data atual ({current_date_str}). Uma entrega está atrasada se estiver pendente (sem data em 'Entrega Etapa') e a 'Data entrega Prevista' for anterior à data atual.\n"
            f"4. Se a pergunta não puder ser respondida com as informações fornecidas, diga educadamente que não possui esses dados.\n"
        )

        if self.provider == "gemini":
            try:
                logger.info("Enviando prompt para a API do Gemini...")
                import asyncio
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.model.generate_content(prompt)
                )
                if response and response.text:
                    return response.text.strip()
                return "Desculpe, não consegui obter uma resposta válida do modelo Gemini."
            except Exception as e:
                logger.error(f"Erro durante a chamada da API do Gemini: {e}. Acionando fallback local.")
                return self._generate_local_fallback_response(question, tasks_data, current_date_str, error_msg=str(e))
                
        elif self.provider == "openrouter":
            try:
                logger.info(f"Enviando prompt para OpenRouter ({self.openrouter_model})...")
                import asyncio
                loop = asyncio.get_event_loop()
                
                def call_openrouter():
                    payload = {
                        "model": self.openrouter_model,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    }

                    headers = {
                        "Authorization": f"Bearer {self.openrouter_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:8000",
                        "X-Title": "Assistente de Lembretes MCP"
                    }
                    logger.info(f"Modelo enviado ao OpenRouter: {self.openrouter_model}")
                    response = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=60
                    )

                    response.raise_for_status()
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                
                response_text = await loop.run_in_executor(None, call_openrouter)
                if response_text:
                    return response_text.strip()
                return "Desculpe, não consegui obter uma resposta válida do modelo do OpenRouter."
            except Exception as e:
                logger.error(f"Erro durante a chamada do OpenRouter: {e}. Acionando fallback local.")
                return self._generate_local_fallback_response(question, tasks_data, current_date_str, error_msg=str(e))
        else:
            return self._generate_local_fallback_response(question, tasks_data, current_date_str)

    def _generate_local_fallback_response(self, question: str, tasks_data: list, current_date: str, error_msg: str = None) -> str:
        """
        Gera uma resposta simulada local de alta fidelidade baseada em regras simples de NLP.
        Isso assegura que a interface sempre retorne respostas úteis mesmo sem chaves de API configuradas.
        """
        q = question.lower()
        response = ""
        
        if error_msg:
            response += f"> **Nota do Sistema**: Ocorreu um erro ao chamar a API de IA ({error_msg}). Resposta gerada localmente.\n\n"
        else:
            response += "> **Nota do Sistema**: Nenhuma chave de API de IA configurada no `.env`. Resposta gerada localmente.\n\n"

        # 1. Verificar se o usuário está perguntando por um proprietário específico
        matched_owner_tasks = []
        matched_owner_name = ""
        for t in tasks_data:
            owner = t.get("proprietario", "")
            owner_lower = owner.lower()
            # Ignora palavras curtas/conectivos na comparação
            words = [w.strip() for w in owner_lower.replace("-", " ").split() if len(w.strip()) > 2]
            
            # Se o nome completo ou partes significativas dele estão na pergunta
            if owner_lower in q or (words and any(w in q for w in words)):
                matched_owner_tasks.append(t)
                matched_owner_name = owner
        
        if matched_owner_tasks:
            response += f"Encontrei as seguintes informações sobre as etapas de **{matched_owner_name}**:\n\n"
            for item in matched_owner_tasks:
                is_done = item.get("entrega_etapa") or "finalizado" in item.get("etapa", "").lower()
                status = "Concluído" if is_done else "Pendente"
                response += f"- **Etapa**: *{item['etapa']}*\n"
                response += f"  - Data da Solicitação: {item['data_solicitacao']}\n"
                response += f"  - Data Prevista de Entrega: {item['data_prevista']}\n"
                if item.get("entrega_etapa"):
                    response += f"  - Entregue em: {item['entrega_etapa']}\n"
                response += f"  - Status: **{status}**\n\n"
            return response

        # 2. Processar outras perguntas comuns baseadas em filtros
        if "atrasad" in q:
            # Encontrar tarefas atrasadas
            atrasadas = []
            today = datetime.strptime(current_date, "%d/%m/%Y")
            for t in tasks_data:
                is_done = t.get("entrega_etapa") or "finalizado" in t.get("etapa", "").lower()
                if not is_done and t.get("data_prevista"):
                    try:
                        prev_date = datetime.strptime(t["data_prevista"], "%d/%m/%Y")
                        if prev_date < today:
                            atrasadas.append(t)
                    except:
                        pass
            
            if atrasadas:
                response += f"Identifiquei **{len(atrasadas)} entregas atrasadas** na planilha:\n\n"
                for item in atrasadas:
                    response += f"- **{item['proprietario']}** (Etapa: *{item['etapa']}*): Venceu em {item['data_prevista']} (Solicitado em {item['data_solicitacao']})\n"
            else:
                response += "Não encontrei nenhuma entrega atrasada registrada."
                
        elif "vence" in q or "esta semana" in q or "vencimento" in q:
            # Listar tarefas com vencimento próximo ou no futuro
            pendentes = [t for t in tasks_data if not (t.get("entrega_etapa") or "finalizado" in t.get("etapa", "").lower())]
            if pendentes:
                response += "Aqui estão as próximas etapas pendentes e suas previsões de entrega:\n\n"
                for p in pendentes:
                    response += f"- **{p['proprietario']}** | Etapa: *{p['etapa']}* | Previsão: **{p['data_prevista']}**\n"
            else:
                response += "Não há entregas pendentes registradas."
                
        elif "concluíd" in q or "finalizad" in q:
            concluidas = [t for t in tasks_data if t.get("entrega_etapa") or t.get("etapa", "").lower() == "finalizado"]
            if concluidas:
                response += f"Atualmente temos **{len(concluidas)} entregas concluídas**:\n\n"
                for c in concluidas:
                    data_ent = c.get("entrega_etapa") or c.get("data_prevista")
                    response += f"- **{c['proprietario']}** (Etapa: *{c['etapa']}*): Concluída e entregue em {data_ent}\n"
            else:
                response += "Nenhuma entrega concluída foi localizada nos registros."
                
        else:
            # Resposta genérica listando o resumo da planilha
            total = len(tasks_data)
            concluidas = len([t for t in tasks_data if t.get("entrega_etapa") or t.get("etapa", "").lower() == "finalizado"])
            pendentes = total - concluidas
            response += (
                f"Olá! Sou o Assistente de Lembretes. Como a pergunta não se encaixa nos filtros automáticos locais, "
                f"aqui está um resumo geral da planilha:\n\n"
                f"- **Total de Registros**: {total}\n"
                f"- **Entregas Concluídas**: {concluidas}\n"
                f"- **Entregas Pendentes**: {pendentes}\n\n"
                f"Para obter respostas completas e dinâmicas, configure uma chave `GEMINI_API_KEY` ou `OPENROUTER_API_KEY` válida no arquivo `.env`!"
            )
            
        return response

if __name__ == "__main__":
    import asyncio
    # Teste rápido
    service = AIService()
    dummy_data = [{"proprietario": "Teste", "etapa": "Detalhar", "data_solicitacao": "10/06/2026", "data_prevista": "20/06/2026", "entrega_etapa": ""}]
    res = asyncio.run(service.ask_question("Quais entregas estão atrasadas?", dummy_data))
    print(res)