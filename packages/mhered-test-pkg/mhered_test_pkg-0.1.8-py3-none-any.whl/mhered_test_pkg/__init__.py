"""A simple Rock Paper Scissors game"""

__version__ = "0.1.8"

import random
import sys


def move_msg(move):
    """Return msg with choice name"""

    move_msgs = {
        "r": "ROCK",
        "p": "PAPER",
        "s": "SCISSORS",
    }
    return move_msgs[move]


def player_play():
    """Return Player move"""

    # input loop
    while True:
        print("Enter your move: (r)ock (p)aper (s)cissors or (q)uit")
        player_move = input()
        if player_move == "q":
            print("Bye!")
            sys.exit()  # Quit the program.
        elif player_move in ["r", "p", "s"]:
            return player_move
        print("Type one of r, p, s, or q.")


def computer_play():
    """Return Computer move"""

    computer_moves = ["r", "p", "s"]
    return computer_moves[random.randint(0, 2)]


def compare_moves(player_move, computer_move):
    """Compare Player and Computer moves and return outcome"""

    print(move_msg(player_move) + " vs " + move_msg(computer_move))

    player_wins = [
        (player_move == "r" and computer_move == "s"),
        (player_move == "p" and computer_move == "r"),
        (player_move == "s" and computer_move == "p"),
    ]

    if player_move == computer_move:
        outcome = "tie"
    elif any(player_wins):
        outcome = "win"
    else:
        outcome = "lose"
    return outcome


def rock_paper_scissors():
    """Main game loop"""

    print("ROCK, PAPER, SCISSORS")

    # Init variables to keep track of the number of wins, losses, and ties.
    wins = 0
    losses = 0
    ties = 0

    # Main game loop
    while True:
        print(f"{wins} Wins, {losses} Losses, {ties} Ties")

        # Player plays
        player_move = player_play()

        # Computer plays
        computer_move = computer_play()

        # assess result
        outcome = compare_moves(player_move, computer_move)
        if outcome == "win":
            print("You win!")
            wins = wins + 1
        elif outcome == "lose":
            print("You lose!")
            losses = losses + 1
        else:  # outcome == "tie":
            print("It is a tie!")
            ties = ties + 1


if __name__ == "__main__":
    rock_paper_scissors()
