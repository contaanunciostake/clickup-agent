#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ClickUp Agent - Sistema de Criação de Demandas (VERSÃO CORRIGIDA)
Versão: 2.1.1
Autor: Manus AI
Data: 2025-06-30

Sistema completo para criação automática de demandas no ClickUp
através de integração com ChatGPT e Make.com
"""

import os
import json
import logging
import requests
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('clickup_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Inicialização do Flask
app = Flask(__name__)
CORS(app)

# Configurações do ClickUp (já configuradas)
CLICKUP_CONFIG = {
    'api_token': 'pk_200493732_TQSTRPR2GOD0GTNOFEWIRVCHR127ZIBY',
    'workspace_id': '90131539337',
    'space_id': '90136445296',
    'folder_id': '90138204864',
    'base_url': 'https://api.clickup.com/api/v2'
}

# Mapeamento de responsáveis por nome
RESPONSAVEIS = {
    'victor': '200493732',
    'angelo': '206512589',
    'giorgia': '99908367',
    'kelly': '200544020'
}

# Templates de checklist por tipo de trabalho
CHECKLIST_TEMPLATES = {
    'desenvolvimento': [
        'Análise de requisitos',
        'Criação do wireframe/mockup',
        'Desenvolvimento do código',
        'Testes unitários',
        'Testes de integração',
        'Deploy e validação'
    ],
    'design': [
        'Briefing e pesquisa',
        'Conceituação e ideação',
        'Criação de layouts',
        'Revisão e ajustes',
        'Entrega de arquivos finais'
    ],
    'marketing': [
        'Definição de estratégia',
        'Criação de conteúdo',
        'Configuração de campanhas',
        'Monitoramento de resultados',
        'Otimização e ajustes'
    ],
    'conteudo': [
        'Pesquisa de tópicos',
        'Criação do conteúdo',
        'Revisão e edição',
        'Aprovação final',
        'Publicação'
    ],
    'default': [
        'Planejamento inicial',
        'Execução das atividades',
        'Revisão e qualidade',
        'Entrega final'
    ]
}

# Subtarefas padrão por tipo
SUBTAREFAS_TEMPLATES = {
    'desenvolvimento': [
        'Configurar ambiente de desenvolvimento',
        'Implementar funcionalidades principais',
        'Realizar testes e correções',
        'Preparar para deploy'
    ],
    'design': [
        'Pesquisar referências visuais',
        'Criar conceitos iniciais',
        'Desenvolver design final',
        'Preparar arquivos para entrega'
    ],
    'marketing': [
        'Definir público-alvo',
        'Criar materiais promocionais',
        'Configurar canais de divulgação',
        'Analisar métricas'
    ],
    'conteudo': [
        'Definir pauta e estrutura',
        'Redigir conteúdo',
        'Revisar e otimizar',
        'Formatar para publicação'
    ],
    'default': [
        'Definir escopo detalhado',
        'Executar atividades principais',
        'Revisar resultados',
        'Finalizar entrega'
    ]
}

class ClickUpAPI:
    """Classe para interação com a API do ClickUp"""
    
    def __init__(self):
        self.headers = {
            'Authorization': CLICKUP_CONFIG['api_token'],
            'Content-Type': 'application/json'
        }
        self.base_url = CLICKUP_CONFIG['base_url']
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Tuple[bool, Dict]:
        """Faz requisição para a API do ClickUp"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data, timeout=30)
            else:
                return False, {'error': f'Método {method} não suportado'}
            
            # Log da requisição para debug
            logger.info(f"Requisição {method} para {url}")
            logger.info(f"Status: {response.status_code}")
            
            if response.status_code >= 400:
                logger.error(f"Erro HTTP {response.status_code}: {response.text}")
                return False, {'error': f'HTTP {response.status_code}: {response.text}'}
            
            return True, response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout na requisição para {url}")
            return False, {'error': 'Timeout na requisição'}
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para {url}: {str(e)}")
            return False, {'error': str(e)}
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {str(e)}")
            return False, {'error': 'Resposta inválida da API'}
    
    def get_or_create_list(self, empresa: str) -> Tuple[bool, str]:
        """Obtém ou cria uma lista para a empresa"""
        # Buscar listas existentes no folder
        success, response = self._make_request('GET', f"folder/{CLICKUP_CONFIG['folder_id']}/list")
        
        if not success:
            logger.error(f"Erro ao buscar listas: {response}")
            return False, ""
        
        # Verificar se já existe uma lista para a empresa
        for lista in response.get('lists', []):
            if lista['name'].lower() == empresa.lower():
                logger.info(f"Lista encontrada para empresa {empresa}: {lista['id']}")
                return True, lista['id']
        
        # Criar nova lista para a empresa
        list_data = {
            'name': empresa,
            'content': f'Lista de tarefas para {empresa}',
            'due_date_time': False,
            'priority': None,
            'assignee': None,
            'status': 'red'
        }
        
        success, response = self._make_request('POST', f"folder/{CLICKUP_CONFIG['folder_id']}/list", list_data)
        
        if success:
            list_id = response['id']
            logger.info(f"Nova lista criada para empresa {empresa}: {list_id}")
            return True, list_id
        else:
            logger.error(f"Erro ao criar lista para empresa {empresa}: {response}")
            return False, ""
    
    def create_task(self, list_id: str, task_data: Dict) -> Tuple[bool, str]:
        """Cria uma tarefa no ClickUp com formato corrigido"""
        
        # Validar e limpar dados da tarefa
        cleaned_task_data = self._clean_task_data(task_data)
        
        logger.info(f"Criando tarefa com dados: {json.dumps(cleaned_task_data, indent=2)}")
        
        success, response = self._make_request('POST', f"list/{list_id}/task", cleaned_task_data)
        
        if success:
            task_id = response['id']
            logger.info(f"Tarefa criada com sucesso: {task_id}")
            return True, task_id
        else:
            logger.error(f"Erro ao criar tarefa: {response}")
            return False, ""
    
    def _clean_task_data(self, task_data: Dict) -> Dict:
        """Limpa e valida dados da tarefa para API do ClickUp"""
        cleaned_data = {}
        
        # Campo obrigatório: name
        if 'name' in task_data and task_data['name']:
            cleaned_data['name'] = str(task_data['name'])[:255]  # Limitar tamanho
        else:
            raise ValueError("Campo 'name' é obrigatório")
        
        # Description (opcional)
        if 'description' in task_data and task_data['description']:
            cleaned_data['description'] = str(task_data['description'])
        
        # Status (usar padrão se não especificado)
        if 'status' in task_data and task_data['status']:
            cleaned_data['status'] = str(task_data['status'])
        
        # Priority (1-4, sendo 1 = urgent, 4 = low)
        if 'priority' in task_data:
            priority = task_data['priority']
            if isinstance(priority, (int, str)) and str(priority).isdigit():
                priority_int = int(priority)
                if 1 <= priority_int <= 4:
                    cleaned_data['priority'] = priority_int
        
        # Due date (timestamp em millisegundos)
        if 'due_date' in task_data and task_data['due_date']:
            due_date = task_data['due_date']
            if isinstance(due_date, (int, float)):
                # Se for timestamp em segundos, converter para millisegundos
                if due_date < 10000000000:  # Timestamp em segundos
                    due_date = int(due_date * 1000)
                else:  # Já em millisegundos
                    due_date = int(due_date)
                cleaned_data['due_date'] = due_date
        
        # Assignees (array de inteiros)
        if 'assignees' in task_data and task_data['assignees']:
            assignees = task_data['assignees']
            if isinstance(assignees, list):
                cleaned_assignees = []
                for assignee in assignees:
                    if isinstance(assignee, (int, str)) and str(assignee).isdigit():
                        cleaned_assignees.append(int(assignee))
                if cleaned_assignees:
                    cleaned_data['assignees'] = cleaned_assignees
        
        # Tags (array de strings)
        if 'tags' in task_data and task_data['tags']:
            tags = task_data['tags']
            if isinstance(tags, list):
                cleaned_tags = [str(tag) for tag in tags if tag]
                if cleaned_tags:
                    cleaned_data['tags'] = cleaned_tags
        
        # Parent (para subtarefas)
        if 'parent' in task_data and task_data['parent']:
            cleaned_data['parent'] = str(task_data['parent'])
        
        # Remover custom_fields por enquanto (podem causar erro 400)
        # if 'custom_fields' in task_data:
        #     cleaned_data['custom_fields'] = task_data['custom_fields']
        
        return cleaned_data
    
    def create_checklist(self, task_id: str, checklist_name: str, items: List[str]) -> Tuple[bool, str]:
        """Cria um checklist na tarefa"""
        checklist_data = {
            'name': checklist_name
        }
        
        success, response = self._make_request('POST', f"task/{task_id}/checklist", checklist_data)
        
        if not success:
            logger.error(f"Erro ao criar checklist: {response}")
            return False, ""
        
        checklist_id = response['checklist']['id']
        
        # Adicionar itens ao checklist
        for item in items:
            item_data = {
                'name': item,
                'assignee': None
            }
            
            success, _ = self._make_request('POST', f"checklist/{checklist_id}/checklist_item", item_data)
            if not success:
                logger.warning(f"Erro ao adicionar item '{item}' ao checklist")
        
        logger.info(f"Checklist criado com sucesso: {checklist_id}")
        return True, checklist_id
    
    def create_subtask(self, parent_task_id: str, subtask_data: Dict) -> Tuple[bool, str]:
        """Cria uma subtarefa"""
        # Para criar subtarefa, usamos o mesmo endpoint de criar tarefa
        # mas com parent definido
        subtask_data['parent'] = parent_task_id
        
        # Obter a lista da tarefa pai
        success, parent_task = self._make_request('GET', f"task/{parent_task_id}")
        if not success:
            logger.error(f"Erro ao obter tarefa pai: {parent_task}")
            return False, ""
        
        list_id = parent_task['list']['id']
        
        success, response = self._make_request('POST', f"list/{list_id}/task", subtask_data)
        
        if success:
            subtask_id = response['id']
            logger.info(f"Subtarefa criada com sucesso: {subtask_id}")
            return True, subtask_id
        else:
            logger.error(f"Erro ao criar subtarefa: {response}")
            return False, ""

def detectar_responsavel(texto: str) -> Optional[str]:
    """Detecta responsável mencionado no texto"""
    texto_lower = texto.lower()
    
    for nome, user_id in RESPONSAVEIS.items():
        if nome in texto_lower:
            logger.info(f"Responsável detectado: {nome} (ID: {user_id})")
            return user_id
    
    return None

def processar_demanda(data: Dict[str, Any]) -> Dict[str, Any]:
    """Processa uma demanda e cria no ClickUp"""
    try:
        # Validar dados obrigatórios
        campos_obrigatorios = ['empresa', 'tarefa', 'tipo', 'equipe', 'hora']
        for campo in campos_obrigatorios:
            if campo not in data or not data[campo]:
                return {
                    'success': False,
                    'error': f'Campo obrigatório ausente: {campo}'
                }
        
        # Extrair dados
        empresa = data['empresa']
        tarefa = data['tarefa']
        tipo = data.get('tipo', 'default').lower()
        equipe = data['equipe']
        hora = data['hora']
        
        # Processar data de entrega
        data_entrega = None
        if 'data_hora_entrega' in data:
            # Timestamp Unix em segundos
            timestamp = int(data['data_hora_entrega'])
            data_entrega = timestamp * 1000  # ClickUp usa millisegundos
        elif 'data_entrega' in data:
            # Formato de data string
            try:
                dt = datetime.strptime(data['data_entrega'], '%Y-%m-%d')
                data_entrega = int(dt.timestamp() * 1000)
            except ValueError:
                logger.warning(f"Formato de data inválido: {data['data_entrega']}")
        
        # Detectar responsável
        responsavel_id = None
        if 'responsavel' in data and data['responsavel']:
            responsavel_nome = data['responsavel'].lower()
            responsavel_id = RESPONSAVEIS.get(responsavel_nome)
        
        if not responsavel_id:
            # Tentar detectar no título ou descrição
            texto_completo = f"{tarefa} {data.get('descricao', '')}"
            responsavel_id = detectar_responsavel(texto_completo)
        
        # Preparar checklist
        checklist_items = data.get('checklist', [])
        if not checklist_items:
            checklist_items = CHECKLIST_TEMPLATES.get(tipo, CHECKLIST_TEMPLATES['default'])
        
        # Preparar subtarefas
        subtarefas = data.get('subtarefas', [])
        if not subtarefas:
            subtarefas = SUBTAREFAS_TEMPLATES.get(tipo, SUBTAREFAS_TEMPLATES['default'])
        
        # Inicializar API do ClickUp
        clickup = ClickUpAPI()
        
        # Obter ou criar lista da empresa
        success, list_id = clickup.get_or_create_list(empresa)
        if not success:
            return {
                'success': False,
                'error': 'Erro ao obter/criar lista da empresa'
            }
        
        # Preparar dados da tarefa principal (formato corrigido)
        task_data = {
            'name': tarefa,
            'description': f"""**Tipo:** {tipo.title()}
**Equipe:** {equipe}
**Horas Estimadas:** {hora}h
**Empresa:** {empresa}

{data.get('descricao', '')}""".strip(),
            'priority': 3,  # Prioridade normal
            'tags': data.get('tags', [])
        }
        
        # Adicionar data de entrega se disponível
        if data_entrega:
            task_data['due_date'] = data_entrega
        
        # Adicionar responsável se detectado
        if responsavel_id:
            task_data['assignees'] = [int(responsavel_id)]
        
        # Criar tarefa principal
        success, task_id = clickup.create_task(list_id, task_data)
        if not success:
            return {
                'success': False,
                'error': 'Erro ao criar tarefa principal'
            }
        
        # Criar checklist
        checklist_id = None
        if checklist_items:
            checklist_name = f"Etapas - {tipo.title()}"
            success, checklist_id = clickup.create_checklist(task_id, checklist_name, checklist_items)
            if not success:
                logger.warning("Erro ao criar checklist")
        
        # Criar subtarefas
        subtask_ids = []
        for i, subtarefa in enumerate(subtarefas):
            subtask_data = {
                'name': subtarefa,
                'description': f'Subtarefa {i+1} da tarefa principal: {tarefa}',
                'priority': 3
            }
            
            # Herdar responsável da tarefa principal
            if responsavel_id:
                subtask_data['assignees'] = [int(responsavel_id)]
            
            # Herdar data de entrega
            if data_entrega:
                subtask_data['due_date'] = data_entrega
            
            success, subtask_id = clickup.create_subtask(task_id, subtask_data)
            if success:
                subtask_ids.append(subtask_id)
            else:
                logger.warning(f"Erro ao criar subtarefa: {subtarefa}")
        
        # Resultado final
        resultado = {
            'success': True,
            'message': 'Demanda criada com sucesso!',
            'data': {
                'task_id': task_id,
                'list_id': list_id,
                'empresa': empresa,
                'tarefa': tarefa,
                'responsavel': responsavel_id,
                'checklist_id': checklist_id,
                'subtask_ids': subtask_ids,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        }
        
        logger.info(f"Demanda processada com sucesso: {task_id}")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro ao processar demanda: {str(e)}")
        return {
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }

# Rotas da API
@app.route('/', methods=['GET'])
def home():
    """Página inicial da API"""
    return jsonify({
        'message': 'ClickUp Agent API v2.1.1 (CORRIGIDA)',
        'status': 'online',
        'endpoints': {
            '/health': 'Verificação de saúde',
            '/webhook/demand': 'Criação de demandas',
            '/responsaveis': 'Lista de responsáveis',
            '/config': 'Configuração do sistema'
        },
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Verificação de saúde do sistema"""
    return jsonify({
        'status': 'healthy',
        'version': '2.1.1',
        'clickup_configured': bool(CLICKUP_CONFIG['api_token']),
        'responsaveis_count': len(RESPONSAVEIS),
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

@app.route('/webhook/demand', methods=['POST'])
def webhook_demand():
    """Endpoint principal para receber demandas"""
    try:
        # Verificar se é JSON
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type deve ser application/json'
            }), 400
        
        # Obter dados
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados JSON inválidos'
            }), 400
        
        logger.info(f"Recebida demanda: {json.dumps(data, indent=2)}")
        
        # Processar demanda
        resultado = processar_demanda(data)
        
        # Retornar resultado
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400
            
    except Exception as e:
        logger.error(f"Erro no webhook: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@app.route('/responsaveis', methods=['GET'])
def listar_responsaveis():
    """Lista responsáveis disponíveis"""
    return jsonify({
        'responsaveis': RESPONSAVEIS,
        'count': len(RESPONSAVEIS),
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

@app.route('/config', methods=['GET', 'POST'])
def configuracao():
    """Configuração do sistema"""
    if request.method == 'GET':
        return jsonify({
            'clickup_configured': bool(CLICKUP_CONFIG['api_token']),
            'workspace_id': CLICKUP_CONFIG.get('workspace_id'),
            'space_id': CLICKUP_CONFIG.get('space_id'),
            'folder_id': CLICKUP_CONFIG.get('folder_id'),
            'responsaveis': RESPONSAVEIS,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Atualizar configurações se fornecidas
            if 'api_token' in data:
                CLICKUP_CONFIG['api_token'] = data['api_token']
            if 'workspace_id' in data:
                CLICKUP_CONFIG['workspace_id'] = data['workspace_id']
            if 'space_id' in data:
                CLICKUP_CONFIG['space_id'] = data['space_id']
            if 'folder_id' in data:
                CLICKUP_CONFIG['folder_id'] = data['folder_id']
            
            return jsonify({
                'success': True,
                'message': 'Configuração atualizada com sucesso',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Erro ao atualizar configuração: {str(e)}'
            }), 500

@app.route('/test', methods=['GET', 'POST'])
def test_system():
    """Endpoint de teste do sistema"""
    test_data = {
        'empresa': 'Teste Sistema Corrigido',
        'tarefa': 'Validar correção do erro 400',
        'tipo': 'desenvolvimento',
        'equipe': 'desenvolvimento',
        'hora': '2',
        'data_hora_entrega': int(datetime.now().timestamp()) + 86400,  # +1 dia
        'responsavel': 'victor',
        'checklist': [
            'Verificar conexão com ClickUp',
            'Validar criação de tarefa',
            'Confirmar responsável atribuído'
        ],
        'subtarefas': [
            'Testar endpoint principal',
            'Verificar logs do sistema',
            'Confirmar funcionamento'
        ],
        'tags': ['teste', 'correcao']
    }
    
    resultado = processar_demanda(test_data)
    return jsonify(resultado)

if __name__ == '__main__':
    # Configuração para produção
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Iniciando ClickUp Agent v2.1.1 (CORRIGIDA) na porta {port}")
    logger.info(f"Modo debug: {debug}")
    logger.info(f"ClickUp configurado: {bool(CLICKUP_CONFIG['api_token'])}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

