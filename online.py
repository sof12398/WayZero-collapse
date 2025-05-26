from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import json
from perso import Personage, ShadowBlade, Bitbreaker, Ripperdoc

app = Flask(__name__)
CORS(app)

# Game state
current_game = {
    'guild1': [],
    'guild2': [],
    'current_turn': 1,
    'last_action': None,
    'game_started': False
}

@app.route('/join_game', methods=['POST'])
def join_game():
    data = request.json
    player_number = data.get('player_number')
    team = data.get('team')
    
    if player_number == 1 and not current_game['guild1']:
        current_game['guild1'] = deserialize_team(team)
        return jsonify({'status': 'waiting'})
    elif player_number == 2 and not current_game['guild2']:
        current_game['guild2'] = deserialize_team(team)
        current_game['game_started'] = True
        return jsonify({
            'status': 'ready',
            'opponent_team': serialize_team(current_game['guild1'])
        })
    return jsonify({'error': 'Invalid join request'})

@app.route('/game_state', methods=['GET'])
def get_game_state():
    player = request.args.get('player', type=int)
    if player == 1:
        return jsonify({
            'your_team': serialize_team(current_game['guild1']),
            'opponent_team': serialize_team(current_game['guild2']),
            'current_turn': current_game['current_turn']
        })
    else:
        return jsonify({
            'your_team': serialize_team(current_game['guild2']),
            'opponent_team': serialize_team(current_game['guild1']),
            'current_turn': current_game['current_turn']
        })

@app.route('/make_move', methods=['POST'])
def make_move():
    data = request.json
    player = data.get('player_number')
    actor_idx = data.get('actor_idx')
    target_idx = data.get('target_idx')
    
    if player != current_game['current_turn']:
        return jsonify({'status': 'error', 'message': 'Not your turn'})
    
    attacker = current_game[f'guild{player}'][actor_idx]
    defender = current_game[f'guild{3-player}'][target_idx]
    
    attacker.action(defender)
    
    # Update game state
    current_game['current_turn'] = 3 - current_game['current_turn']
    
    return jsonify({
        'status': 'success',
        'player_team': serialize_team(current_game[f'guild{player}']),
        'opponent_team': serialize_team(current_game[f'guild{3-player}']),
        'game_over': check_game_over(),
        'winner_message': get_winner_message() if check_game_over() else None
    })

def deserialize_team(team_data):
    team = []
    for char_data in team_data:
        if char_data['class'] == 'ShadowBlade':
            new_char = ShadowBlade()
        elif char_data['class'] == 'Bitbreaker':
            new_char = Bitbreaker()
        elif char_data['class'] == 'Ripperdoc':
            new_char = Ripperdoc()
        
        new_char.name = char_data['name']
        team.append(new_char)
    return team

def serialize_team(team):
    if team is None:
        return []
    serialized = []
    for char in team:
        char_data = {
            'name': char.name,
            'health': char.health,
            'degat': char.degat,
            'esquive': char.esquive,
            'is_alive': char.is_alive,
            'class': char.__class__.__name__
        }
        serialized.append(char_data)
    return serialized

def deserialize_team(team_data):
    if not team_data:
        return []
    team = []
    for char_data in team_data:
        if char_data['class'] == 'ShadowBlade':
            new_char = ShadowBlade()
        elif char_data['class'] == 'Bitbreaker':
            new_char = Bitbreaker()
        elif char_data['class'] == 'Ripperdoc':
            new_char = Ripperdoc()
        else:
            continue
            
        new_char.name = str(char_data['name'])
        new_char.health = float(char_data['health'])
        new_char.degat = float(char_data['degat'])
        new_char.esquive = float(char_data['esquive'])
        new_char.is_alive = bool(char_data['is_alive'])
        
        team.append(new_char)
    return team

def check_game_over():
    guild1_alive = any(char.is_alive for char in current_game['guild1'])
    guild2_alive = any(char.is_alive for char in current_game['guild2'])
    return not (guild1_alive and guild2_alive)

def get_winner_message():
    guild1_alive = any(char.is_alive for char in current_game['guild1'])
    if guild1_alive:
        return "Player 1 wins!"
    return "Player 2 wins!"

@app.route('/reset_game', methods=['POST'])
def reset_game():
    current_game['guild1'] = []
    current_game['guild2'] = []
    current_game['current_turn'] = 1
    current_game['last_action'] = None
    current_game['game_started'] = False
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555)