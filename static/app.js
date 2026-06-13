// Configurações e Elementos do DOM
const elements = {
    tasksBody: document.getElementById('tasks-body'),
    statTotal: document.getElementById('stat-total'),
    statDelayed: document.getElementById('stat-delayed'),
    statUpcoming: document.getElementById('stat-upcoming'),
    syncStatus: document.getElementById('sync-status'),
    btnRefresh: document.getElementById('btn-refresh'),
    chatForm: document.getElementById('chat-form'),
    chatInput: document.getElementById('chat-input'),
    chatMessages: document.getElementById('chat-messages'),
    btnSubmit: document.getElementById('btn-submit')
};

// ==========================================================================
// Utilitários de Datas
// ==========================================================================

function parseDate(dateStr) {
    if (!dateStr) return null;
    const parts = dateStr.trim().split('/');
    if (parts.length === 3) {
        const day = parseInt(parts[0], 10);
        const month = parseInt(parts[1], 10) - 1; // Mês começa em 0 no JS
        const year = parseInt(parts[2], 10);
        return new Date(year, month, day);
    }
    return null;
}

function formatDate(date) {
    if (!date) return '';
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
}

// ==========================================================================
// Buscas da API & Atualizações de Dados
// ==========================================================================

async function loadAppData() {
    elements.syncStatus.textContent = 'Atualizando...';
    elements.btnRefresh.disabled = true;
    
    try {
        const response = await fetch('/api/reminders');
        if (!response.ok) {
            throw new Error(`Status de erro HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        renderSummary(data.summary);
        renderTable(data.tasks, data.delayed_tasks, data.upcoming_tasks);
        
        const now = new Date();
        elements.syncStatus.innerHTML = `Sincronizado às ${now.toLocaleTimeString()}`;
    } catch (error) {
        console.error('Erro ao sincronizar dados:', error);
        elements.syncStatus.innerHTML = '<span class="text-danger">Falha na sincronização</span>';
        showToast('Não foi possível sincronizar os dados da planilha. Verifique a conexão.', 'error');
    } finally {
        elements.btnRefresh.disabled = false;
    }
}

function renderSummary(summary) {
    elements.statTotal.textContent = summary.total !== undefined ? summary.total : 0;
    elements.statDelayed.textContent = summary.delayed !== undefined ? summary.delayed : 0;
    elements.statUpcoming.textContent = summary.upcoming !== undefined ? summary.upcoming : 0;
}

function renderTable(tasks, delayedTasks, upcomingTasks) {
    elements.tasksBody.innerHTML = '';
    
    if (!tasks || tasks.length === 0) {
        elements.tasksBody.innerHTML = `
            <tr>
                <td colspan="5" class="empty-state">Nenhum registro encontrado na planilha.</td>
            </tr>
        `;
        return;
    }

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const threeDaysLater = new Date(today);
    threeDaysLater.setDate(today.getDate() + 3);

    tasks.forEach(task => {
        const tr = document.createElement('tr');
        
        // Determinar se a tarefa está concluída
        const etapa = task.etapa ? task.etapa.toLowerCase() : '';
        const entrega = task.entrega_etapa ? task.entrega_etapa.trim() : '';
        const isCompleted = etapa.includes('finalizado') || entrega.length > 0;
        
        // Se não concluída, checar datas para os alertas
        let taskClass = '';
        if (!isCompleted && task.data_prevista) {
            const prevDate = parseDate(task.data_prevista);
            if (prevDate) {
                if (prevDate < today) {
                    taskClass = 'task-delayed';
                } else if (prevDate <= threeDaysLater) {
                    taskClass = 'task-upcoming';
                }
            }
        }
        
        if (taskClass) {
            tr.className = taskClass;
        }

        // Formatação do Badge da Etapa
        let badgeClass = 'badge';
        if (isCompleted) {
            badgeClass += ' badge-success';
        } else if (etapa.includes('aprovação') || etapa.includes('detalhar')) {
            badgeClass += ' badge-pending';
        }

        tr.innerHTML = `
            <td><strong>${escapeHtml(task.proprietario || 'Sem Nome')}</strong></td>
            <td><span class="${badgeClass}">${escapeHtml(task.etapa || 'Pendente')}</span></td>
            <td>${escapeHtml(task.data_solicitacao || '-')}</td>
            <td>${escapeHtml(task.data_prevista || '-')}</td>
            <td>${task.entrega_etapa ? `<span class="badge badge-success">${escapeHtml(task.entrega_etapa)}</span>` : '<span class="text-muted">-</span>'}</td>
        `;
        
        elements.tasksBody.appendChild(tr);
    });
}

// ==========================================================================
// Módulo de Chat com a IA (Gemini)
// ==========================================================================

elements.chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const question = elements.chatInput.value.trim();
    if (!question) return;
    
    // Adicionar mensagem do usuário no chat
    addMessage(question, 'user', 'Você');
    elements.chatInput.value = '';
    elements.chatInput.disabled = true;
    elements.btnSubmit.disabled = true;
    
    // Adicionar indicador de digitação (typing indicator)
    const typingIndicator = addTypingIndicator();
    
    try {
        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: question })
        });
        
        // Remover indicador de digitação
        typingIndicator.remove();
        
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        addMessage(data.answer, 'ai', 'Assistente de IA');
    } catch (error) {
        console.error('Erro na chamada da IA:', error);
        typingIndicator.remove();
        addMessage('Desculpe, ocorreu uma falha ao enviar sua mensagem para a IA. Verifique as configurações de rede ou sua chave de API.', 'ai', 'Assistente de IA');
    } finally {
        elements.chatInput.disabled = false;
        elements.btnSubmit.disabled = false;
        elements.chatInput.focus();
    }
});

function addMessage(text, sender, senderName) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}-message`;
    
    const nameDiv = document.createElement('div');
    nameDiv.className = 'message-sender';
    nameDiv.textContent = senderName;
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.innerHTML = formatMarkdown(text);
    
    msgDiv.appendChild(nameDiv);
    msgDiv.appendChild(textDiv);
    
    elements.chatMessages.appendChild(msgDiv);
    
    // Rolar até o final
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

function addTypingIndicator() {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message ai-message';
    
    const nameDiv = document.createElement('div');
    nameDiv.className = 'message-sender';
    nameDiv.textContent = 'Assistente de IA';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.innerHTML = `
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    
    msgDiv.appendChild(nameDiv);
    msgDiv.appendChild(textDiv);
    
    elements.chatMessages.appendChild(msgDiv);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    
    return msgDiv;
}

// ==========================================================================
// Formatadores de HTML e Markdown Simples
// ==========================================================================

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function formatMarkdown(text) {
    // Negrito
    let html = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Itálico
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    html = html.replace(/_([^_]+)_/g, '<em>$1</em>');
    
    // Código inline
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Parágrafos e listas
    const lines = html.split('\n');
    let inList = false;
    let formattedLines = [];
    
    lines.forEach(line => {
        const trimmed = line.trim();
        if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
            if (!inList) {
                formattedLines.push('<ul>');
                inList = true;
            }
            formattedLines.push(`<li>${trimmed.substring(2)}</li>`);
        } else {
            if (inList) {
                formattedLines.push('</ul>');
                inList = false;
            }
            if (trimmed.length > 0) {
                formattedLines.push(`<p>${trimmed}</p>`);
            }
        }
    });
    
    if (inList) {
        formattedLines.push('</ul>');
    }
    
    return formattedLines.join('');
}

// Toast de Notificações
function showToast(message, type = 'info') {
    // Para simplificar, exibimos um alerta simples do navegador ou logamos no console.
    // Pode ser estendido para toasts personalizados se necessário.
    console.log(`[Toast ${type}]: ${message}`);
}

// ==========================================================================
// Eventos de Inicialização
// ==========================================================================

elements.btnRefresh.addEventListener('click', loadAppData);

// Carga Inicial ao abrir a página
document.addEventListener('DOMContentLoaded', () => {
    loadAppData();
});
