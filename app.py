"""Main game module."""
from lib.game import Game


def play():
    """Play the game."""
    print("---- Game Setup ----")
    player_configs = []
    num_players = int(input("HOW MANY PLAYERS?\t"))
    for player_num in range(1, num_players + 1):
        player_config = {}
        print(f"\nPLAYER {player_num}:")

        player_type = input("PLAYER TYPE (default to 'human'):\t")
        if player_type == '':
            player_config['player_type'] = None
        elif player_type not in ('human', 'computer'):
            invalid_player_type_err_msg = (
                f"player_type must be either 'human' or 'computer'; found "
                f"player_type: '{player_type}'"
            )
            raise ValueError(invalid_player_type_err_msg)
        else:
            player_config['player_type'] = player_type

        player_name = input("PLAYER NAME (default to generic name):\t")
        if player_name == '':
            player_config['name'] = None
        else:
            player_config['name'] = player_name

        player_configs.append(player_config)

    while True:
        print("\n\n===========================")
        print("-*- STARTING A NEW GAME -*-")
        print("===========================\n")

        game = Game(player_configs)
        game.start()

        new_game_confirmation = input("Start a new game? (y/n):\t")
        if new_game_confirmation != 'y':
            print("Thanks for playing!")
            break


if __name__ == '__main__':
    play()
