import random
from perso import Personage, ShadowBlade, Bitbreaker, Ripperdoc
import sys



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
    print(f"############\n#  guild1  #\n############")
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
    print(f"############\n#  guild2  #\n############")
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
            
            print("\n--- Menu d'action ---")
            print("Votre guilde :")
            for idx, char in enumerate(guild2):
                etat = "MORT" if char.is_alive == False else f"HP: {char.health}"
                print(f"{idx + 1}: {char.name} ({etat})")
            print("0: Quitter")

            actor_idx = int(input("Choisissez un personnage pour agir : ")) - 1
            if actor_idx == -1:
                print("Fin du jeu.")
                break
            if 0 <= actor_idx < len(guild2):
                actor = guild2[actor_idx]
                if actor.is_alive == False:
                    print(f"{actor.name} est mort et ne peut plus agir.")
                    guild2.remove(actor)
                    continue
            print(f"\n{actor.name} sélectionné.")
            if isinstance(actor, (ShadowBlade, Bitbreaker)):
                target_guild = guild1
                print("Cibles ennemies :")
            else:
                target_guild = guild2
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


                else:
                    print("Cible invalide.")
            else:
                print("Personnage invalide.")
        except ValueError:
            print("Veuillez entrer un nombre valide.")
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