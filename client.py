import random
import json
from perso import Personage, ShadowBlade, Bitbreaker, Ripperdoc
import sys
import os
import socket
import pickle
import argparse
import requests
import time
import logging


# Set up argument parser
parser = argparse.ArgumentParser()
parser.add_argument('--player', type=int, required=True, help='Player number (1 or 2)')
args = parser.parse_args()

# cree une liste de personage disponible
all_characters = [
    ShadowBlade(),
    Bitbreaker(),
    Ripperdoc()
]

SERVER_HOST = 'localhost'  # Change this to your server's IP
SERVER_PORT = 5555

logging.basicConfig(
    filename='game.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class GameClient:
    def __init__(self, player_number):
        self.player_number = player_number
        self.guild = []
        self.opponent_guild = []
        self.last_action_time = 0
        self.last_sync_time = 0
        self.sync_interval = 0.5  # Sync every 500ms
        self.SERVER_HOST = f"http://{SERVER_HOST}:{SERVER_PORT}"

    def send(self, data):
        try:
            headers = {'Content-Type': 'application/json'}
            
            # Add player number and proper action type
            if isinstance(data, dict):
                data['player_number'] = self.player_number
                if data.get('action') == 'perform_action':
                    # Add action type based on character class
                    actor = self.guild[data.get('actor_idx', 0)]
                    data['action_type'] = 'heal' if isinstance(actor, Ripperdoc) else 'attack'

            endpoint = {
                'get_state': 'get_state',
                'submit_team': 'join_game',
                'perform_action': 'make_move'
            }.get(data.get('action'), 'join_game')

            logging.info(f"Sending request to {endpoint}: {data}")
            response = requests.post(
                f'{self.SERVER_HOST}/{endpoint}',
                json=data,
                headers=headers,
                timeout=5
            )

            # Log response for debugging
            logging.info(f"Server response ({response.status_code}): {response.text}")

            if response.status_code != 200:
                logging.error(f"Server error: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "message": f"Server error: {response.text}",
                    "current_turn": self.player_number
                }

            return response.json()

        except requests.exceptions.RequestException as e:
            logging.error(f"Connection error: {e}")
            return {
                "status": "error",
                "message": f"Connection failed: {str(e)}",
                "current_turn": self.player_number
            }

    def send_with_retry(self, data, max_retries=3, retry_delay=1):
        for attempt in range(max_retries):
            try:
                return self.send(data)
            except requests.exceptions.ConnectionError:
                if attempt < max_retries - 1:
                    print(f"Connection lost. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    print("Failed to reconnect after multiple attempts")
                    raise

    def sync_game_state(self):
        current_time = time.time()
        if current_time - self.last_sync_time >= self.sync_interval:
            response = self.send({"action": "get_state"})
            if response.get("status") == "success":
                self.update_game_state(response)
            self.last_sync_time = current_time

def online_game():
    # Initialize le client client avec le nombre de joueurs des args
    game_client = GameClient(args.player)

    # Character selection phase
    print("Personnages disponibles :")
    for idx, char in enumerate(all_characters):
        print(f"{idx + 1}: {char.name} ({char.__class__.__name__}, HP: {char.health}, Attaque: {char.degat}, Esquive: {char.esquive})")
    
    print(f"############\n#  Player {args.player} Team  #\n############")
    while len(game_client.guild) < 5:
        try:
            choice = int(input(f"Sélectionnez le personnage {len(game_client.guild) + 1} par numéro : ")) - 1
            if 0 <= choice < len(all_characters):
                original_char = all_characters[choice]
                if isinstance(original_char, ShadowBlade):
                    new_char = ShadowBlade()
                elif isinstance(original_char, Bitbreaker):
                    new_char = Bitbreaker()
                elif isinstance(original_char, Ripperdoc):
                    new_char = Ripperdoc()
                
                name = input(f"Donnez un nom à votre {original_char.__class__.__name__} : ")
                new_char.name = name
                game_client.guild.append(new_char)
            else:
                print("Sélection invalide. Réessayez.")
        except ValueError:
            print("Veuillez entrer un nombre valide.")

    print("Submitting team and waiting for opponent...")
    max_wait_time = 60  # 60 seconds timeout
    start_time = time.time()
    
    while True:
        response = game_client.send({
            "action": "submit_team",
            "team": [{
                'name': char.name,
                'health': char.health,
                'degat': char.degat,
                'esquive': char.esquive,
                'is_alive': char.is_alive,
                'class': char.__class__.__name__
            } for char in game_client.guild]
        })
        
        if response.get("status") == "ready":
            print("Opponent found! Game starting...")
            # Update opponent team data
            opponent_data = response.get("opponent_team", [])
            game_client.opponent_guild = []
            for char_data in opponent_data:
                char_class = char_data.get("class", "")
                if char_class == "ShadowBlade":
                    char = ShadowBlade()
                elif char_class == "Bitbreaker":
                    char = Bitbreaker()
                elif char_class == "Ripperdoc":
                    char = Ripperdoc()
                char.name = char_data.get("name", "Unknown")
                char.health = char_data.get("health", 100)
                char.is_alive = char_data.get("is_alive", True)
                game_client.opponent_guild.append(char)
            break
            
        elif response.get("status") == "waiting":
            if time.time() - start_time > max_wait_time:
                print("\nTimeout waiting for opponent. Returning to menu...")
                return
            print(f"\rWaiting for opponent... {int(max_wait_time - (time.time() - start_time))}s", end='', flush=True)
            time.sleep(2)  # Poll every 2 seconds
            
        else:
            print(f"\nError: {response.get('message', 'Unknown error')}")
            return

    # Game loop
    while True:
        try:
            state = game_client.send({"action": "get_state"})
            if state.get("game_over"):
                print("\n" + "="*50)
                print(state.get("winner_message", "Game Over!"))
                print("="*50)
                input("\nPress Enter to return to menu...")
                break
                
            current_turn = state.get("current_turn", 1)
            
            # Clear screen and show game state
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"\nTurn: Player {current_turn}")
            
            if current_turn != game_client.player_number:
                print("\nWaiting for opponent's turn...")
                time.sleep(1)
                continue
                
            # Show team status
            print("\nYour team:")
            for idx, char in enumerate(game_client.guild):
                status = "DEAD" if not char.is_alive else f"HP: {char.health}"
                print(f"{idx + 1}: {char.name} ({status})")
            
            try:
                actor_idx = int(input("\nChoisit une personnage a agir (0 pour retourner au menu): ")) - 1
                
                if actor_idx == -1:
                    confirm = input("Voulez-vous vraiment quitter la partie ? (o/n): ")
                    if confirm.lower() == 'o':
                        return  # Return to menu
                    continue  # Stay in game if not confirmed

                if 0 <= actor_idx < len(game_client.guild):
                    actor = game_client.guild[actor_idx]
                    if not actor.is_alive:
                        print(f"{actor.name} il est mort.")
                        continue
                
                    if isinstance(actor, (Ripperdoc )):
                        print("\nchoisisser un allie:")
                        for idx, char in enumerate(game_client.guild):
                            etat = "MORT" if not char.is_alive else f"HP: {char.health}"
                            print(f"{idx + 1}: {char.name} ({etat})")

                        try:
                            target_idx = int(input("choisisser un ennemi: ")) - 1
                            if 0 <= target_idx < len(game_client.guild):
                                action_data = {
                                    "action": "perform_action",
                                    "actor_idx": actor_idx,
                                    "target_idx": target_idx
                                }
                                response = game_client.send(action_data)
                                if response.get("status") == "success":
                                    # Print the action message with formatting
                                    action_message = response.get("action_message")
                                    if action_message:
                                        print("\n" + "="*50)
                                        print(action_message)
                                        print("="*50)
# Mise à jour de l'état du jeu actuel
                                player_team_data = response.get("player_team", [])
                                for idx, char_data in enumerate(player_team_data):
                                    game_client.guild[idx].health = char_data.get("health")
                                    game_client.guild[idx].is_alive = char_data.get("is_alive")
                                
                                opponent_team_data = response.get("opponent_team", [])
                                for idx, char_data in enumerate(opponent_team_data):
                                    game_client.opponent_guild[idx].health = char_data.get("health")
                                    game_client.opponent_guild[idx].is_alive = char_data.get("is_alive")
                                
                                # After action is performed, add a pause
                                if response.get("status") == "success":
                                    action_message = response.get("action_message")
                                    if action_message:
                                        print("\n" + "="*50)
                                        print(action_message)
                                        print("="*50)
                                        time.sleep(1)  # Add pause after action
                                    
                                    # Update stats
                                    actor = game_client.guild[actor_idx]
                                    target = game_client.opponent_guild[target_idx]
                                    
                                else:
                                    print(f"Action failed: {response.get('message', 'erreur inconnue')}")
                            else:
                                print("Cible Invalide")
                        except ValueError:
                            print("Veuiller enter un nombre valide")
                    else:
                    
                        print("\nchoisisser un ennemi:")
                        for idx, char in enumerate(game_client.opponent_guild):
                            etat = "MORT" if not char.is_alive else f"HP: {char.health}"
                            print(f"{idx + 1}: {char.name} ({etat})")

                        try:
                            target_idx = int(input("choisisser un ennemi: ")) - 1
                            if 0 <= target_idx < len(game_client.opponent_guild):
                                action_data = {
                                    "action": "perform_action",
                                    "actor_idx": actor_idx,
                                    "target_idx": target_idx
                                }
                                response = game_client.send(action_data)
                                if response.get("status") == "success":
                                    # Print the action message with formatting
                                    action_message = response.get("action_message")
                                    if action_message:
                                        print("\n" + "="*50)
                                        print(action_message)
                                        print("="*50)
                                        
                                
                                
                                # Mise à jour de l'état du jeu actuel
                                player_team_data = response.get("player_team", [])
                                for idx, char_data in enumerate(player_team_data):
                                    game_client.guild[idx].health = char_data.get("health")
                                    game_client.guild[idx].is_alive = char_data.get("is_alive")
                                
                                opponent_team_data = response.get("opponent_team", [])
                                for idx, char_data in enumerate(opponent_team_data):
                                    game_client.opponent_guild[idx].health = char_data.get("health")
                                    game_client.opponent_guild[idx].is_alive = char_data.get("is_alive")
                                
                                # After action is performed, add a pause
                                if response.get("status") == "success":
                                    action_message = response.get("action_message")
                                    if action_message:
                                        print("\n" + "="*50)
                                        print(action_message)
                                        print("="*50)
                                        time.sleep(1)  # Add pause after action
                                    
                                    # Update stats
                                    actor = game_client.guild[actor_idx]
                                    target = game_client.opponent_guild[target_idx]
                                else:
                                    print(f"Action failed: {response.get('message', 'erreur inconnue')}")
                            else:
                                print("Cible Invalide")
                        except ValueError:
                            print("Veuiller enter un nombre valide")
                else:
                    print("personnage selectinner invalide")
            except ValueError:
                print("Veuillez entrer un nombre valide.")
                time.sleep(1)  # Add pause after error
                continue

        except Exception as e:
            print(f"Error during game state update: {e}")
            time.sleep(1)  # Add pause after error
            continue

def afficher_titre():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("#############################")
    print("#          WayZero          #")
    print("#          Colapse          #")
    print("#############################\n")

def quitter_jeu():
    print("Merci d'avoir joué à WayZero : COLLAPSE !")
    sys.exit(0)
def afficher_menu():
    while True:
        afficher_titre()
        print("1. en ligne")
        print("2. hors ligne")
        print("3. Continuer la partien hors ligne")
        print("4. Quit\n")

        choix = input("Select an option: ")

        if choix == '1':
            online_game()
        elif choix == '2':
            pass
        elif choix == '3':
            pass
        elif choix == '4':
            quitter_jeu()
        else:
            print("\nInvalid choice. Try again.\n")

# Keep the rest of your existing code (offline functions, etc.)
# but add the online_game() option to the menu

if __name__ == "__main__":
    afficher_menu()
