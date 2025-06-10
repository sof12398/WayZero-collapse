from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import json
from perso import Personage, ShadowBlade, Bitbreaker, Ripperdoc
import random
app = Flask(__name__)
CORS(app)
from queue import Queue
import threading
import time
import signal
from threading import Lock
import logging

logging.basicConfig(level=logging.INFO)

game_lock = Lock()

def auto_turn_switch():
    TURN_TIMEOUT = 60  # 60 seconds per turn
    
    while True:
        time.sleep(1)
        if current_game['game_started'] and not check_game_over():
            current_time = time.time()
            time_in_turn = current_time - current_game['last_action_time']
            
            if time_in_turn >= TURN_TIMEOUT:
                # Switch turn if player is inactive
                current_game['current_turn'] = 3 - current_game['current_turn']
                current_game['last_action_time'] = current_time

# Start the auto turn switch thread
threading.Thread(target=auto_turn_switch, daemon=True).start()
current_game = {
    'guild1': [],
    'guild2': [],
    'current_turn': 1,
    'last_action': None,
    'game_started': False,
    'player1_ready': False,
    'player2_ready': False,
    'last_action_time': time.time()
}

# Add game state queues for each player
current_game.update({
    'player1_queue': Queue(),
    'player2_queue': Queue(),
    'game_loop_active': False
})

def game_loop():
    while current_game['game_loop_active']:
        current_player = current_game['current_turn']
        opponent = 3 - current_player
        
        # Wait for current player's action
        try:
            action = current_game[f'player{current_player}_queue'].get(timeout=0.5)
            if action.get('type') == 'move':
                actor_idx = action.get('actor_idx')
                target_idx = action.get('target_idx')
                
                attacker = current_game[f'guild{current_player}'][actor_idx]
                defender = current_game[f'guild{opponent}'][target_idx]
                
                # Perform action
                attacker.action(defender)
                
                # Update game state
                game_state = {
                    'status': 'success',
                    'current_turn': current_game['current_turn'],
                    'player_team': serialize_team(current_game[f'guild{current_player}']),
                    'opponent_team': serialize_team(current_game[f'guild{opponent}']),
                    'game_over': check_game_over(),
                    'winner_message': get_winner_message() if check_game_over() else None
                }
                
                # Send update to both players
                current_game[f'player{current_player}_queue'].put(game_state)
                current_game[f'player{opponent}_queue'].put(game_state)
                
                # Switch turns
                current_game['current_turn'] = opponent
                
        except:
            continue

@app.route('/get_state', methods=['POST'])
def get_state():
    try:
        data = request.json
        player_number = data.get('player_number')
        
        if not player_number:
            return jsonify({'status': 'error', 'message': 'Player number required'}), 400
            
        return jsonify({
            'status': 'success',
            'current_turn': current_game['current_turn'],
            'player_team': serialize_team(current_game[f'guild{player_number}']),
            'opponent_team': serialize_team(current_game[f'guild{3-player_number}']),
            'game_over': check_game_over(),
            'winner_message': get_winner_message() if check_game_over() else None
        })
    except Exception as e:
        print(f"Error in get_state: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/join_game', methods=['POST'])
def join_game():
    with game_lock:
        try:
            data = request.json
            player_number = data.get('player_number')
            team = data.get('team')

            if not team and player_number == 2:
                # Player 2 checking status
                if not current_game['player1_ready']:
                    return jsonify({
                        'status': 'error',
                        'message': 'Waiting for player 1 to join'
                    }), 400
                elif current_game['player2_ready']:
                    return jsonify({
                        'status': 'ready',
                        'opponent_team': serialize_team(current_game['guild1']),
                        'current_turn': current_game['current_turn']
                    })
                else:
                    return jsonify({
                        'status': 'waiting',
                        'message': 'Waiting for player 1 to join'
                    })

            # Handle player 1
            if player_number == 1:
                current_game['guild1'] = deserialize_team(team)
                current_game['player1_ready'] = True
                
                if current_game['player2_ready']:
                    return jsonify({
                        'status': 'ready',
                        'opponent_team': serialize_team(current_game['guild2']),
                        'current_turn': current_game['current_turn']
                    })
                    
                return jsonify({
                    'status': 'waiting',
                    'message': 'Waiting for player 2...'
                })

            # Handle player 2
            elif player_number == 2:
                if not current_game['player1_ready']:
                    return jsonify({
                        'status': 'error',
                        'message': 'Waiting for player 1 to join'
                    }), 400

                current_game['guild2'] = deserialize_team(team)
                current_game['player2_ready'] = True
                current_game['game_started'] = True
                current_game['current_turn'] = 1  # Always start with player 1

                return jsonify({
                    'status': 'ready',
                    'opponent_team': serialize_team(current_game['guild1']),
                    'current_turn': current_game['current_turn']
                })

        except Exception as e:
            logging.error(f"Join game error: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'Server error: {str(e)}'
            }), 500

@app.route('/make_move', methods=['POST'])
def make_move():
    with game_lock:
        try:
            data = request.json
            logging.info(f"Received move request: {data}")

            # Validate request data
            player = data.get('player_number')
            actor_idx = data.get('actor_idx')
            target_idx = data.get('target_idx')
            action_type = data.get('action_type', 'attack')

            # Validate all required fields
            if any(x is None for x in [player, actor_idx, target_idx]):
                return jsonify({
                    'status': 'error',
                    'message': 'Missing required fields'
                }), 400

            # Validate indices
            try:
                actor_idx = int(actor_idx)
                target_idx = int(target_idx)
            except (TypeError, ValueError):
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid index values'
                }), 400

            # Verify it's the player's turn
            if player != current_game['current_turn']:
                return jsonify({
                    'status': 'error',
                    'message': f"Not your turn. Current turn: Player {current_game['current_turn']}"
                }), 400

            # Get attacker and validate
            if actor_idx >= len(current_game[f'guild{player}']):
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid actor index'
                }), 400

            attacker = current_game[f'guild{player}'][actor_idx]
            if not attacker.is_alive:
                return jsonify({
                    'status': 'error',
                    'message': 'Dead characters cannot act'
                }), 400

            # Get defender based on action type
            if action_type == 'heal':
                if target_idx >= len(current_game[f'guild{player}']):
                    return jsonify({
                        'status': 'error',
                        'message': 'Invalid heal target'
                    }), 400
                defender = current_game[f'guild{player}'][target_idx]
            else:
                opponent = 3 - player
                if target_idx >= len(current_game[f'guild{opponent}']):
                    return jsonify({
                        'status': 'error',
                        'message': 'Invalid attack target'
                    }), 400
                defender = current_game[f'guild{opponent}'][target_idx]

            # Perform action
            action_message = attacker.action(defender)
            
            # Switch turns
            current_game['current_turn'] = 3 - player
            current_game['last_action_time'] = time.time()

            # Prepare response
            response_data = {
                'status': 'success',
                'player_team': serialize_team(current_game[f'guild{player}']),
                'opponent_team': serialize_team(current_game[f'guild{3-player}']),
                'current_turn': current_game['current_turn'],
                'action_message': action_message,
                'game_over': check_game_over(),
                'winner_message': get_winner_message() if check_game_over() else None
            }
            
            logging.info(f"Action completed successfully: {response_data}")
            return jsonify(response_data)

        except Exception as e:
            logging.error(f"Server error in make_move: {str(e)}", exc_info=True)
            return jsonify({
                'status': 'error',
                'message': f'Server error: {str(e)}'
            }), 500

def serialize_team(team):
    return [{
        'name': char.name,
        'health': char.health,
        'is_alive': char.is_alive,
        'class': char.__class__.__name__
    } for char in team]

def deserialize_team(team_data):
    team = []
    for char_data in team_data:
        if char_data['class'] == 'ShadowBlade':
            char = ShadowBlade()
        elif char_data['class'] == 'Bitbreaker':
            char = Bitbreaker()
        elif char_data['class'] == 'Ripperdoc':
            char = Ripperdoc()
        else:
            continue
        char.name = char_data['name']
        char.health = char_data.get('health', char.health)
        char.is_alive = char_data.get('is_alive', True)
        team.append(char)
    return team

def check_game_over():
    if not current_game['game_started']:
        return False
    team1_alive = any(char.is_alive for char in current_game['guild1'])
    team2_alive = any(char.is_alive for char in current_game['guild2'])
    return not (team1_alive and team2_alive)

def get_winner_message():
    if not check_game_over():
        return None
    team1_alive = any(char.is_alive for char in current_game['guild1'])
    team2_alive = any(char.is_alive for char in current_game['guild2'])
    if team1_alive:
        return "Player 1 wins!"
    elif team2_alive:
        return "Player 2 wins!"
    return "Game ended in a draw!"

if __name__ == '__main__':
    try:
        # Start the game loop in a separate thread
        game_loop_thread = threading.Thread(target=game_loop, daemon=True)
        game_loop_thread.start()
        
        # Start the auto turn switch thread
        turn_switch_thread = threading.Thread(target=auto_turn_switch, daemon=True)
        turn_switch_thread.start()
        
        # Set up signal handlers for graceful shutdown
        def signal_handler(sig, frame):
            print("\nShutting down server...")
            current_game['game_loop_active'] = False
            # Give threads time to clean up
            time.sleep(1)
            exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Start the Flask server
        print("Starting server on http://localhost:5555")
        app.run(host='0.0.0.0', port=5555, debug=False, threaded=True)
        
    except Exception as e:
        print(f"Server startup error: {str(e)}")