import random
import json
from perso import Personage, ShadowBlade, Bitbreaker, Ripperdoc
import sys
import os
filename = "guilds.json"

# Création du fichier JSON initial s'il n'existe pas
def create_initial_json():
    if not os.path.exists(filename):
        initial_data = {
            "guild1": [],
            "guild2": []
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=4, ensure_ascii=False)
        print(f"Fichier {filename} créé avec succès.")

# Appel de la fonction au démarrage
create_initial_json()
def save_guilds_to_json(guild1, guild2, filename):
    guilds_data = {
        "guild1": [],
        "guild2": []
    }
    
    for character in guild1:
        character_data = {
            "name": character.name,
            "health": character.health,
            "degat": character.degat,
            "esquive": character.esquive,
            "is_alive": character.is_alive,
            "class": character.__class__.__name__
        }
        guilds_data["guild1"].append(character_data)
    
    for character in guild2:
        character_data = {
            "name": character.name,
            "health": character.health,
            "degat": character.degat, 
            "esquive": character.esquive,
            "is_alive": character.is_alive,
            "class": character.__class__.__name__
        }
        guilds_data["guild2"].append(character_data)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(guilds_data, f, indent=4, ensure_ascii=False)

def load_guilds_from_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        guilds_data = json.load(f)
    
    guild1 = []
    guild2 = []
    
    for char_data in guilds_data["guild1"]:
        if char_data["class"] == "ShadowBlade":
            new_char = ShadowBlade()
        elif char_data["class"] == "Bitbreaker":
            new_char = Bitbreaker()
        elif char_data["class"] == "Ripperdoc":
            new_char = Ripperdoc()
            
        new_char.name = char_data["name"]
        new_char.health = char_data["health"]
        new_char.degat = char_data["degat"]
        new_char.esquive = char_data["esquive"]
        new_char.is_alive = char_data["is_alive"]
        
        guild1.append(new_char)
    
    for char_data in guilds_data["guild2"]:
        if char_data["class"] == "ShadowBlade":
            new_char = ShadowBlade()
        elif char_data["class"] == "Bitbreaker":
            new_char = Bitbreaker()
        elif char_data["class"] == "Ripperdoc":
            new_char = Ripperdoc()
            
        new_char.name = char_data["name"]
        new_char.health = char_data["health"]
        new_char.degat = char_data["degat"]
        new_char.esquive = char_data["esquive"]
        new_char.is_alive = char_data["is_alive"]
        
        guild2.append(new_char)
    
    return guild1, guild2


# Création des personnages prédéfinis (une seule instance de chaque)
shadow_blade = ShadowBlade()
bitbreaker = Bitbreaker()
ripperdoc = Ripperdoc()

all_characters = [shadow_blade, bitbreaker, ripperdoc]

def jeux():
    # Sélection des personnages pour la guilde du joueur
    print("Personnages disponibles :")
    for idx, char in enumerate(all_characters):
        print(f"{idx + 1}: {char.name} ({char.__class__.__name__}, HP: {char.health}, Attaque: {char.degat}, Esquive: {char.esquive})")

    selected_indices = []
    guild1 = []
    print(f"############\n#  equipe1  #\n############")
    while len(selected_indices) < 5:  # Changed to 5 characters
        try:
            choice = int(input(f"Sélectionnez le personnage {len(selected_indices) + 1} par numéro : ")) - 1
            if 0 <= choice < len(all_characters):
                original_char = all_characters[choice]
                # Create a new instance of the same class
                if isinstance(original_char, ShadowBlade):
                    new_char = ShadowBlade()
                elif isinstance(original_char, Bitbreaker):
                    new_char = Bitbreaker()
                elif isinstance(original_char, Ripperdoc):
                    new_char = Ripperdoc()
                
                name = input(f"Donnez un nom à votre {original_char.__class__.__name__} : ")
                new_char.name = name  # Set the name for the new instance
                selected_indices.append(choice)
                guild1.append(new_char)
            else:
                print("Sélection invalide. Réessayez.")
        except ValueError:
            print("Veuillez entrer un nombre valide.")

    selected_indices = []
    guild2 = []
    print(f"############\n#  eqipe2  #\n############")
    while len(selected_indices) < 5:  # Changed to 5 characters
        try:
            choice = int(input(f"Sélectionnez le personnage {len(selected_indices) + 1} par numéro : ")) - 1
            if 0 <= choice < len(all_characters):
                original_char = all_characters[choice]
                # Create a new instance of the same class
                if isinstance(original_char, ShadowBlade):
                    new_char = ShadowBlade()
                elif isinstance(original_char, Bitbreaker):
                    new_char = Bitbreaker()
                elif isinstance(original_char, Ripperdoc):
                    new_char = Ripperdoc()
                
                name = input(f"Donnez un nom à votre {original_char.__class__.__name__} : ")
                new_char.name = name
                selected_indices.append(choice)
                guild2.append(new_char)
            else:
                print("Sélection invalide. Réessayez.")
        except ValueError:
            print("Veuillez entrer un nombre valide.")
    offline(guild1, guild2)

    # Rest of the game loop remains the same
def offline(guild1, guild2):
    while True:
        print("\n--- Menu d'action ---")
        print("Votre guilde :")
        for idx, char in enumerate(guild1):
            etat = "MORT" if char.is_alive == False else f"HP: {char.health}"
            print(f"{idx + 1}: {char.name} ({etat})")
        print("0: Quitter")

        try:
            actor_idx = int(input("Choisissez un personnage pour agir : ")) - 1
            if actor_idx == -1:
                print("Fin du jeu.")
                break
            if 0 <= actor_idx < len(guild1):
                actor = guild1[actor_idx]
                if actor.is_alive == False:
                    print(f"{actor.name} est mort et ne peut plus agir.")
                    guild1.remove(actor)
                    continue
                print(f"\n{actor.name} sélectionné.")
                if isinstance(actor, (ShadowBlade, Bitbreaker)):
                    target_guild = guild2
                    print("Cibles ennemies :")
                else:
                    target_guild = guild1
                    print("Cibles alliées :")
                for idx, char in enumerate(target_guild):
                    etat = "MORT" if char.is_alive == False else f"HP: {char.health}"
                    print(f"{idx + 1}: {char.name} ({etat})")
                target_idx = int(input("Numéro de la cible : ")) - 1
                if 0 <= target_idx < len(target_guild):
                    target = target_guild[target_idx]
                    if target.is_alive == False:
                        print(f"{target.name} est déjà mort.")
                        continue
                    actor.action(target)
                    guild1 = [c for c in guild1 if c.is_alive == True]
                    guild2 = [c for c in guild2 if c.is_alive == True]
                    if not guild1:
                        print("Tous vos personnages sont morts. GAME OVER !")
                        break
                    if not guild2:
                        print("Tous les ennemis sont morts. VICTOIRE !")
                        break
        finally:
            # Sauvegarde des guildes dans le fichier JSON
            save_guilds_to_json(guild1, guild2, filename)
            print("Les guildes ont été sauvegardées dans le fichier JSON.")

def continuer_partie():
    try:
        guild1, guild2 = load_guilds_from_json(filename)
        print("Partie chargée avec succès!")
        offline(guild1, guild2)
    except FileNotFoundError:
        print("Aucune sauvegarde trouvée.")
        return False
    except Exception as e:
        print(f"Erreur lors du chargement : {e}")
        return False

def afficher_menu():
    while True:
        afficher_titre()
        print("1. Nouvelle partie")
        print("2. Continuer partie")  
        print("3. Quitter\n")

        choix = input("Sélectionne une option: ")

        if choix == '1':
            jeux()
        elif choix == '2':
            continuer_partie()
        elif choix == '3':
            quitter_jeu()
        else:
            print("\nChoix invalide. Réessaie.\n")

def afficher_titre():
    print("=" * 40)
    print("        WayZero : COLLAPSE")
    print("=" * 40)

def quitter_jeu():
    print("\nMerci d'avoir joué à WayZero : COLLAPSE !")
    sys.exit()

def afficher_menu():
    while True:
        afficher_titre()
        print("1. Lancer le jeu")
        print("2. Quitter\n")

        choix = input("Sélectionne une option: ")

        if choix == '1':
            jeux()
        elif choix == '2':
            quitter_jeu()
        else:
            print("\nChoix invalide. Réessaie.\n")


# Lancer le menu
if __name__ == "__main__":

    afficher_menu()