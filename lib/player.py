"""Player class module."""
import copy
import string


class Player:
    """Player class.

    Can be either a human player or a computer player.

    :attr Game game: ghost game object to which the player belongs
    :attr int id: player ID
    :attr str player_type: type of player ('human' or 'computer')
    :attr str name: player name
    :attr int current_strikes: number of strikes against the player
    :attr bool is_eliminated: player is eliminated
    """

    def __init__(self, game, player_type='human', name=None):
        """Initialize a Player object.

        :param Game game: ghost game object to which the new player
            will belong
        :param str player_type: (optional) type of player; must be
            'human' or 'computer'; defaults to 'human'
        :param str name: (optional) player name; defaults to None, and
            assigns a generic name based on player ID
        """
        self.game = game

        # assign ID based on number of players in game thus far
        self.id = game.player_count
        game.player_count += 1

        if player_type not in ('human', 'computer'):
            invalid_player_type_err_msg = (
                f"Player.player_type must be either 'human' or "
                f"'computer'; found player_type: '{player_type}'"
            )
            raise ValueError(invalid_player_type_err_msg)
        self.player_type = player_type

        # create generic name based on ID if no name is given
        if name is None:
            self.name = f'{player_type.upper()} {self.id + 1}'
        else:
            self.name = name

        # set initial player status attributes
        self.current_strikes = 0
        self.is_eliminated = False

    def __repr__(self):
        """Represent player as string.

        :return: string representation of player object
        :rtype: str
        """
        return f"Player <{self.id}, '{self.name}'>"

    @staticmethod
    def init_players_from_configs(game, player_configs):
        """Initialize the list of players from a list of player configs.

        :param Game game: ghost game object to use to create the players
        :param list[dict[str,str]] player_configs: list of player
            configuration dictionaries
        :return: list of players
        :rtype: list[Player]
        """
        players = []
        for player_config in player_configs:
            player_config = copy.deepcopy(player_config)

            player_config['game'] = game

            player_type = player_config['player_type']
            if player_type is None:
                player_type = 'human'
            del player_config['player_type']

            if player_type == 'human':
                player = HumanPlayer(**player_config)
            elif player_type == 'computer':
                player = ComputerPlayer(**player_config)
            players.append(player)

        return players

    def take_turn(self):
        """Take a turn of the game.

        Game turns can either be playing a letter, challenging the
        previous player, or forfeiting the round.

        WARNING: Not implemented in abstract Player class.

        :raises: NotImplementedError
        """
        take_turn_implementation_err_msg = (
            "Player.take_turn() is not implemented because Player is an "
            "abstract class. Use HumanPlayer or ComputerPlayer objects "
            "instead to call the take_turn() method."
        )
        raise NotImplementedError(take_turn_implementation_err_msg)

    def respond_to_challenge(self):
        """Respond to another player's challenge with the intended word.

        WARNING: Not implemented in abstract Player class.

        :return: word intended by player's last letter
        :rtype: str
        :raises: NotImplementedError
        """
        respond_implementation_err_msg = (
            "Player.respond_to_challenge() is not implemented because "
            "Player is an abstract class. Use HumanPlayer or "
            "ComputerPlayer objects instead to call the "
            "respond_to_challenge() method."
        )
        raise NotImplementedError(respond_implementation_err_msg)

    def lose_round(self):
        """Lose the round.

        Resets the game's current word fragment back to an empty string,
        and adds to the player's current strike count.
        """
        self.game.reset_current_word_fragment()

        self.current_strikes += 1

        player_ghost_word = self.game.ghost_word[:self.current_strikes]
        lost_round_msg = (
            f"{self.name} has lost the round; they gain one letter, "
            f"and they now have '{player_ghost_word}'"
        )
        print(lost_round_msg)

        if self.current_strikes == self.game.num_strikes_allowed:
            self.game.eliminate_player(self)

    def play_letter(self, letter):
        """Play a letter and add to the game's current word fragment.

        :param str letter: single letter of the alphabet to play
        """
        if len(letter) != 1:
            raise ValueError(f"{letter} is not a letter")
        if letter not in list(string.ascii_lowercase):
            raise ValueError(f"Invalid letter: {letter}")

        self.game.current_word_fragment += letter
        print(f"{self.name} played the letter '{letter}'")
        print(
            f"The current word fragment is "
            f"'{self.game.current_word_fragment}'"
        )

    def challenge_previous_player_as_complete(self):
        """Challenge the previous player with completing a word."""
        previous_player = self.game.get_previous_player()

        challenge_msg = (
            f"{self.name} is challenging {previous_player.name}, who "
            f"played the letter '{self.game.current_word_fragment[-1]}' "
            f"creating the word fragment "
            f"'{self.game.current_word_fragment}', for having "
            f"accidentally completed a valid word"
        )
        print(challenge_msg)

        # if the previous player spelled a word and is challenged the
        # previous player loses the round, otherwise the current player
        # loses the round
        current_word_fragment = self.game.current_word_fragment
        if self.game.is_valid_word(current_word_fragment):
            prev_player_valid_word_msg = (
                f"The word fragment {current_word_fragment} is a valid "
                f"word, therefore {previous_player.name} loses the round"
            )
            print(prev_player_valid_word_msg)
            previous_player.lose_round()
        else:
            prev_player_invalid_word_msg = (
                f"The word fragment {current_word_fragment} is not a "
                f"valid word, therefore {self.name} loses the round"
            )
            print(prev_player_invalid_word_msg)
            self.lose_round()

    def challenge_previous_player_as_impossible(self):
        """Challenge the previous player's letter as impossible.

        A letter is impossible if there are no valid words that can be
        completed using the new word fragment.
        """
        previous_player = self.game.get_previous_player()

        challenge_msg = (
            f"{self.name} is challenging {previous_player.name}, who "
            f"played the letter '{self.game.current_word_fragment[-1]}' "
            f"creating the word fragment "
            f"'{self.game.current_word_fragment}', for having created "
            f"a word fragment that is impossible to complete"
        )
        print(challenge_msg)

        # if the previous player's intended word is valid, the current
        # player loses the round; otherwise, the previous player loses
        # the round
        prev_player_intended_word = previous_player.respond_to_challenge()
        if self.game.is_valid_intended_word(prev_player_intended_word):
            prev_player_valid_intended_word_msg = (
                f"{previous_player.name}'s intended word, "
                f"'{prev_player_intended_word}', is a valid word, "
                f"therefore {self.name} loses the round"
            )
            print(prev_player_valid_intended_word_msg)
            self.lose_round()
        else:
            prev_player_invalid_intended_word_msg = (
                f"{previous_player.name}'s intended word, "
                f"'{prev_player_intended_word}', is NOT a valid word, "
                f"therefore {previous_player.name} loses the round"
            )
            print(prev_player_invalid_intended_word_msg)
            previous_player.lose_round()

    def forfeit_round(self):
        """Forfeit the round.

        This move should only be taken if the player cannot think of any
        valid words, or if the only valid words left will complete a
        word for the player.
        """
        print(f"{self.name} is stumped and is forfeiting the round")
        self.lose_round()


class HumanPlayer(Player):
    """HumanPlayer class.

    The strategy for a human player is determined by user input.

    :attr Game game: ghost game object to which the player belongs
    :attr int id: player ID
    :attr str player_type: type of player; set to 'human'
    :attr str name: player name
    :attr int current_strikes: number of strikes against the player
    :attr bool is_eliminated: player is eliminated
    """

    def __init__(self, game, name=None):
        """Initialize a HumanPlayer object.

        :param Game game: ghost game object to which the new player
            will belong
        :param str name: (optional) player name; defaults to None, and
            assigns a generic name based on player ID
        """
        super().__init__(game, 'human', name)

    def take_turn(self):
        """Take a turn of the game.

        Game turns can either be playing a letter, challenging the
        previous player, or forfeiting the round.
        """
        turn_type = input("TURN TYPE:\t")

        if turn_type == 'play':
            letter_to_play = input("LETTER:\t").lower()
            if len(letter_to_play) != 1:
                print(f"{letter_to_play} is not a letter")
                self.take_turn()
            elif letter_to_play not in list(string.ascii_lowercase):
                print(f"Invalid letter: {letter_to_play}")
                self.take_turn()
            else:
                self.play_letter(letter_to_play)

        elif turn_type == 'challenge':
            if self.game.current_word_fragment == '':
                print("Cannot challenge on first turn of round")
                self.take_turn()
            else:
                self.challenge_previous_player()

        elif turn_type == 'forfeit':
            self.forfeit_round()

        else:
            print("Turn type must be 'play', 'challenge', or 'forfeit'")
            self.take_turn()

    def respond_to_challenge(self):
        """Respond to another player's challenge with the intended word.

        :return: word intended by player's last letter
        :rtype: str
        """
        intended_word = input(f"{self.name}'s INTENDED WORD:\t")
        return intended_word


class ComputerPlayer(Player):
    """ComputerPlayer class.

    The strategy for a computer player is determined by an algorithm. The
    computer player makes moves automatically, and does not require
    user input.

    :attr Game game: ghost game object to which the player belongs
    :attr int id: player ID
    :attr str player_type: type of player; set to 'computer'
    :attr str name: player name
    :attr int current_strikes: number of strikes against the player
    :attr bool is_eliminated: player is eliminated
    """

    def __init__(self, game, name=None):
        """Initialize a ComputerPlayer object.

        :param Game game: ghost game object to which the new player
            will belong
        :param str name: (optional) player name; defaults to None, and
            assigns a generic name based on player ID
        """
        raise NotImplementedError("Not yet implemented")
        # super().__init__(game, 'computer', name)

    def take_turn(self):
        """Take a turn of the game.

        Game turns can either be playing a letter, challenging the
        previous player, or forfeiting the round.
        """
        raise NotImplementedError("Not yet implemented")

    def respond_to_challenge(self):
        """Respond to another player's challenge with the intended word.

        :return: word intended by player's last letter
        :rtype: str
        """
        raise NotImplementedError("Not yet implemented")
