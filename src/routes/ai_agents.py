from flask import Blueprint, request, jsonify
import json
import time
import random

ai_agents_bp = Blueprint('ai_agents', __name__)

# Available AI agents
AVAILABLE_AGENTS = {
    'gpt-4o': {'name': 'GPT-4o', 'provider': 'OpenAI', 'status': 'active'},
    'chatgpt-4-turbo': {'name': 'ChatGPT 4 Turbo', 'provider': 'OpenAI', 'status': 'active'},
    'gemini-2-flash': {'name': 'Gemini 2.0 Flash', 'provider': 'Google', 'status': 'active'},
    'meta-llama-3-3': {'name': 'Meta Llama 3.3', 'provider': 'Meta', 'status': 'active'},
    'deepseek-r1': {'name': 'DeepSeek R1', 'provider': 'DeepSeek', 'status': 'active'},
    'wizardlm-2': {'name': 'WizardLM 2', 'provider': 'Microsoft', 'status': 'active'},
    'mixtral-8x22b': {'name': 'Mixtral 8x22B', 'provider': 'Mistral', 'status': 'active'},
    'neural-chat': {'name': 'Neural Chat', 'provider': 'Intel', 'status': 'active'},
    'gemini-pro-1-5': {'name': 'Gemini Pro 1.5', 'provider': 'Google', 'status': 'active'},
    'yi-large': {'name': 'Yi Large', 'provider': '01.AI', 'status': 'active'},
    'nous-hermes-3': {'name': 'Nous Hermes 3', 'provider': 'NousResearch', 'status': 'active'},
    'dolphin-mixtral': {'name': 'Dolphin Mixtral', 'provider': 'Cognitive Computations', 'status': 'active'},
    'perplexity-pro': {'name': 'Perplexity Pro', 'provider': 'Perplexity', 'status': 'active'},
    'command-r-plus': {'name': 'Command R+', 'provider': 'Cohere', 'status': 'active'},
    'qwen-2-5-72b': {'name': 'Qwen 2.5 72B', 'provider': 'Alibaba', 'status': 'active'},
    'openhermes-2-5': {'name': 'OpenHermes 2.5', 'provider': 'Teknium', 'status': 'active'},
    'mistral-large': {'name': 'Mistral Large', 'provider': 'Mistral', 'status': 'active'},
    'llama-3-3-70b': {'name': 'Llama 3.3 70B', 'provider': 'Meta', 'status': 'active'},
    'starling-7b': {'name': 'Starling 7B', 'provider': 'Berkeley', 'status': 'active'},
    'claude-3-5-sonnet': {'name': 'Claude 3.5 Sonnet', 'provider': 'Anthropic', 'status': 'active'}
}

# Session storage (in production, use Redis or database)
sessions = {}

@ai_agents_bp.route('/agents', methods=['GET'])
def get_agents():
    """Get list of available AI agents"""
    return jsonify({
        'success': True,
        'agents': AVAILABLE_AGENTS
    })

@ai_agents_bp.route('/session/start', methods=['POST'])
def start_session():
    """Start a new AI conversation session"""
    data = request.get_json()
    
    session_id = f"session_{int(time.time())}_{random.randint(1000, 9999)}"
    
    sessions[session_id] = {
        'id': session_id,
        'mode': data.get('mode', 'manual-relay'),
        'agent_a': data.get('agent_a'),
        'agent_b': data.get('agent_b'),
        'conversation_style': data.get('conversation_style'),
        'initial_prompt': data.get('initial_prompt'),
        'rounds': data.get('rounds', 5),
        'messages': [],
        'status': 'active',
        'created_at': time.time(),
        'current_round': 0
    }
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'session': sessions[session_id]
    })

@ai_agents_bp.route('/session/<session_id>/message', methods=['POST'])
def send_message():
    """Send a message in the conversation"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    if session_id not in sessions:
        return jsonify({'success': False, 'error': 'Session not found'}), 404
    
    session = sessions[session_id]
    
    message = {
        'id': len(session['messages']) + 1,
        'agent': data.get('agent'),
        'content': data.get('content'),
        'timestamp': time.time(),
        'round': session['current_round']
    }
    
    session['messages'].append(message)
    
    return jsonify({
        'success': True,
        'message': message,
        'session': session
    })

@ai_agents_bp.route('/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session details"""
    if session_id not in sessions:
        return jsonify({'success': False, 'error': 'Session not found'}), 404
    
    return jsonify({
        'success': True,
        'session': sessions[session_id]
    })

@ai_agents_bp.route('/session/<session_id>/stop', methods=['POST'])
def stop_session(session_id):
    """Stop a session"""
    if session_id not in sessions:
        return jsonify({'success': False, 'error': 'Session not found'}), 404
    
    sessions[session_id]['status'] = 'stopped'
    
    return jsonify({
        'success': True,
        'session': sessions[session_id]
    })

@ai_agents_bp.route('/simulator/start', methods=['POST'])
def start_human_simulator():
    """Start human simulator mode"""
    data = request.get_json()
    
    session_id = f"simulator_{int(time.time())}_{random.randint(1000, 9999)}"
    
    sessions[session_id] = {
        'id': session_id,
        'mode': 'human-simulator',
        'strategy_mode': data.get('strategy_mode', 'balanced'),
        'collaboration_mode': data.get('collaboration_mode', 'auto-detect'),
        'rounds': data.get('rounds', 5),
        'instructions': data.get('instructions', ''),
        'messages': [],
        'status': 'active',
        'created_at': time.time(),
        'current_round': 0,
        'clone_stats': {
            'phrases_learned': 0,
            'sessions_completed': 0,
            'patterns_recognized': 0,
            'confidence': 0
        }
    }
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'session': sessions[session_id]
    })

@ai_agents_bp.route('/simulator/<session_id>/progress', methods=['GET'])
def get_simulator_progress(session_id):
    """Get human simulator progress"""
    if session_id not in sessions:
        return jsonify({'success': False, 'error': 'Session not found'}), 404
    
    session = sessions[session_id]
    
    # Simulate progress updates
    if session['mode'] == 'human-simulator':
        session['clone_stats']['phrases_learned'] = min(session['current_round'] * 15, 500)
        session['clone_stats']['patterns_recognized'] = min(session['current_round'] * 8, 200)
        session['clone_stats']['confidence'] = min(session['current_round'] * 10, 100)
    
    return jsonify({
        'success': True,
        'progress': session['clone_stats']
    })

@ai_agents_bp.route('/export/<session_id>/<format>', methods=['GET'])
def export_session(session_id, format):
    """Export session in various formats"""
    if session_id not in sessions:
        return jsonify({'success': False, 'error': 'Session not found'}), 404
    
    session = sessions[session_id]
    
    if format == 'json':
        return jsonify({
            'success': True,
            'data': session,
            'filename': f'session_{session_id}.json'
        })
    elif format == 'txt':
        content = f"UnityLab Session Export\n"
        content += f"Session ID: {session_id}\n"
        content += f"Mode: {session['mode']}\n"
        content += f"Created: {time.ctime(session['created_at'])}\n\n"
        
        for msg in session['messages']:
            content += f"[Round {msg['round']}] {msg['agent']}: {msg['content']}\n\n"
        
        return jsonify({
            'success': True,
            'data': content,
            'filename': f'session_{session_id}.txt'
        })
    
    return jsonify({'success': False, 'error': 'Unsupported format'}), 400

@ai_agents_bp.route('/status', methods=['GET'])
def get_system_status():
    """Get system status"""
    return jsonify({
        'success': True,
        'status': {
            'system': 'online',
            'active_sessions': len([s for s in sessions.values() if s['status'] == 'active']),
            'total_sessions': len(sessions),
            'available_agents': len(AVAILABLE_AGENTS),
            'uptime': time.time()
        }
    })

