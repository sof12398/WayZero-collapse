import random
class Personage:
    def __init__(self, name, health, degat1, degat2, esquive):
        self.name = name
        self.health = health
        self.vie_max = health
        self.degat = random.randint(degat1, degat2)
        self.esquive = esquive
        self.skip_turn = False  
        self.is_alive = True
    def action():
        pass
    
    def take_damage(self, degat, attacker=None):
        if random.randint(0, 100) > self.esquive:
            print(f"{self.name} esquive l'attaque!")
            return
        else:
            self.health -= max(0, degat)
            if self.health <= 0:
                self.health = 0
                self.is_alive = False
                print(f"{self.name} est mort.")
            if attacker:
                print(f"{attacker.name} attaque {self.name} et inflige {degat} dégâts. Il reste {self.health} HP à {self.name}.")
            else:
                if self.health == 0:
                    print(f"{self.name} subit {degat} dégâts et meurt.")
                else:
                    print(f"{self.name} subit {degat} dégâts. Il reste {self.health} HP.")

class ShadowBlade(Personage):
    def __init__(self):
        super().__init__("Shadow Blade", 75, 35, 38, 75)
    def action(self, target):
        print(f"{self.name} utilise son action contre {target.name} !")
        target.take_damage(self.degat, attacker=self)

class Bitbreaker(Personage):
    def __init__(self):
        super().__init__("Bitbreaker", 100, 15, 20, 40)
        
    def action(self, target):
        choice = input(f"Choisir action pour {self.name}:\n1: Désactivation (50% chance)\nChoix: ")
        if choice == "1":
            if random.randint(0, 100) < 50:
                print(f"{self.name} désactive {target.name} ! {target.name} passe son prochain tour.")
                target.skip_turn = True
            else:
                print(f"{self.name} rate sa tentative de désactivation!")
        else:
            print("Action invalide, tour passé!")

class Ripperdoc(Personage):
    def __init__(self):
        super().__init__("Ripperdoc", 85, 0, 0, 50)

    def action(self, ally): 
        heal_amount = random.randint(20, 30) / 100  # You can change the heal value as you want
        vie_add = ally.health * heal_amount
        ally.health += vie_add
        print(f"{self.name} soigne {ally.name} et lui rend {vie_add} HP. {ally.name} a maintenant {ally.health} HP.")
        if ally.health > ally.vie_max:
            ally.health = ally.vie_max
            print(f"{ally.name} est à sa vie max !")
        else:
            print(f"{ally.name} a maintenant {ally.health} HP.")