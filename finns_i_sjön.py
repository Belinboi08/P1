import random
import subprocess
import os


# Rensar terminalen så man inte ser varnadras kort 
def clear_screen():
    subprocess.run("cls" if os.name == "nt" else "clear", shell=True)
    print("\033[3J\033[H\033[2J", end="", flush=True)


clear_screen()


values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
suits = ["Hjärter", "Ruter", "Klöver", "Spader"]


class Card:
    # Körs när ett nytt kort skapas. 
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit


class Player:
    def __init__(self, name):
        self.name = name
        self.cards = []
        self.points = 0

    def take_four_of_a_kind(self):
        for rank in values:
            # Plockar ut alla kort med samma valör.
            same = [card for card in self.cards if card.rank == rank]
            if len(same) == 4:
                # Behåller alla kort utom fyrtalet.
                # Sparar alla kort som inte har fyrtalets valör.
                remaining = []
                for card in self.cards:
                    if card.rank != rank:
                        remaining.append(card)
                self.cards = remaining
                self.points += 1
                print(f"{self.name} fick ett fyrtal i {rank}!")


class Game:
    def __init__(self, players):
        # Den yngsta spelaren ligger redan först i listan
        self.players = players
        # Gör alla 52 kort varje valör i varje färg
        self.pond = [
            Card(rank, suit)
            for rank in values
            for suit in suits
        ]
        random.shuffle(self.pond)  #Blandar korten 

    def deal(self):
        # 7 kort om de är 2 spelare annars 5 
        card_count = 7 if len(self.players) == 2 else 5

        for _ in range(card_count):
            for player in self.players:
                # pop() tar sista kortet ur sjön
                player.cards.append(self.pond.pop())

        for player in self.players:
            player.take_four_of_a_kind()

    def play(self):
        turn = 0  # Vems tur det 0 står för första spelaren
        shown_player = None  # Spelaren som senast visade sina kort

        # Kör så länge det finns kort i sjön
        while self.pond:
            player = self.players[turn]

            # Alla andra spelare som har kort kvar
            opponents = [
                other for other in self.players
                if other != player and other.cards
            ]

            # Inga egna kort dra ett kort och ge turen vidare
            if not player.cards:
                card = self.pond.pop()
                player.cards.append(card)
                print(f"{player.name} fick ett kort från sjön.")
                player.take_four_of_a_kind()
                # Nästa spelares tur  % gör att det börjar om från 0 efter sista spelaren
                turn = (turn + 1) % len(self.players)
                continue  # Börja om loopen

            # Ingen att fråga  drar ett kort och ge turen vidare
            if not opponents:
                card = self.pond.pop()
                player.cards.append(card)
                print(f"{player.name} fick ett kort från sjön.")
                player.take_four_of_a_kind()
                turn = (turn + 1) % len(self.players)
                continue

            # Ny spelare rensa skärmen så ingen ser de andras kort 
            if player != shown_player:
                if shown_player is not None:
                    input("\nTryck Enter för att lämna över till nästa spelare...")
                clear_screen()
                input(f"Nu är det {player.name}s tur. Tryck Enter när du är redo...")
                shown_player = player

            print(f"\n{player.name}s tur.")
            # Bygger en text med alla kort till exmepl "7, K, A".
            # Komma läggs bara till om texten inte är tom
            cards_text = ""
            for card in player.cards:
                if cards_text != "":
                    cards_text += ", "
                cards_text += card.rank
            print("Dina kort:", cards_text)

            # Skriver ut spelarna med nummer 1, 2, 3 
            for number, other in enumerate(opponents, start=1):
                print(f"{number}. {other.name}")

            # Frågar igen tills man skriver ett nummer som finns
            choice = input("Vem vill du fråga? Skriv numret: ")
            while not choice.isdigit() or not 1 <= int(choice) <= len(opponents):
                choice = input("Skriv ett giltigt nummer: ")

            # -1 för att listan börjar på 0
            chosen_opponent = opponents[int(choice) - 1]

            rank = input("Vilken valör frågar du efter? ").upper()
            # Man får bara fråga efter något man själv har
            while rank not in values or not any(
                card.rank == rank for card in player.cards
            ):
                rank = input("Välj en valör du har på handen: ").upper()

            asked_cards = [
                card for card in chosen_opponent.cards
                if card.rank == rank
            ]

            # Motspelaren hade kortet  ta det och kör igen
            if asked_cards:
                chosen_opponent.cards = [
                    card for card in chosen_opponent.cards
                    if card.rank != rank
                ]
                player.cards.extend(asked_cards)
                print(f"{chosen_opponent.name} hade {rank}. Du får fortsätta!")
                player.take_four_of_a_kind()
            # Motspelaren hade inte kortet dra från sjön
            else:
                print("Finns i sjön!")
                card = self.pond.pop()
                player.cards.append(card)
                print(f"Du drog {card.rank}.")

                player.take_four_of_a_kind()

                # Fick man inte det man frågade efter går turen vidare 
                if card.rank != rank:
                    turn = (turn + 1) % len(self.players)

        self.show_result()

    def show_result(self):
        print("\nSpelet är slut!")
        highest_points = max(player.points for player in self.players)

        for player in self.players:
            print(f"{player.name}: {player.points} poäng")

        # En lista, eftersom flera kan vinna.
        winners = [
            player.name for player in self.players
            if player.points == highest_points
        ]
        print("Vinnare:", ", ".join(winners))


# Frågar efter ett tal tills man skriver ett som är okej
def read_number(text, minimum):
    answer = input(text)
    while not answer.isdigit() or int(answer) < minimum:
        answer = input(f"Skriv ett tal som är minst {minimum}: ")
    return int(answer)


def start_game():
    count = read_number("Hur många spelar? Minst 2: ", 2)
    players = []

    for number in range(1, count + 1):
        name = input(f"Spelare {number}, skriv ditt namn: ").strip()
        players.append(Player(name))

    # Skriver ut alla spelare med nummer
    print()
    for number, player in enumerate(players, start=1):
        print(f"{number}. {player.name}")

    # Frågar vem som är yngst
    youngest = read_number("Vem är yngst? Skriv numret: ", 1)
    while youngest > count:
        youngest = read_number("Skriv ett nummer som finns: ", 1)

    # Flyttar runt listan så att den yngsta hamnar först
    # men resten behåller samma ordning
    index = youngest - 1
    players = players[index:] + players[:index]

    game = Game(players)
    game.deal()

    print(f"\n{game.players[0].name} är yngst och börjar.")
    game.play()


# Spelar om tills man svarar något annat än j
while True:
    start_game()
    again = input("\nVill ni spela igen? (j/n): ").lower()
    if again != "j":
        break
