"""Game class module."""
from lib.player import Player


class Game:
    """Controlling game object class.

    :attr int player_count: number of players in the game
    :attr list[Player] players: list of all players in the game
    :attr Player current_player: player whose turn it is
    :attr int min_word_length: minimum word length for a word to be
        considered valid
    :attr str ghost_word: the player strike counter word
    :attr int num_strikes_allowed: the number of strikes a player is allowed
        before they are eliminated; corresponds to the length of the ghost
        word
    :attr list[str] word_list: list of valid words in the game's dictionary
    :attr str current_word_fragment: the round's current word fragment
    :attr bool game_is_over: True if the game is over, False otherwise
    """

    word_list_filepaths = {
        'scrabble': 'data/scrabble.txt',
        'webster': 'data/webster.txt'
    }

    def __init__(self, player_configs, min_word_length=4,
                 ghost_word='GHOST', word_list_type='scrabble'):
        """Initialize a Game object.

        :param list[dict[str,str]] player_configs: list of player
            configuration dictionaries
        :param int min_word_length: (optional) minimum word length for a word
            to be considered valid; defaults to 4
        :param str ghost_word: (optional) the player strike counter word;
            defaults to 'GHOST'
        :param str word_list_type: (optional) type of word list to use;
            must be 'scrabble' or 'webster'; defaults to 'scrabble'
        """
        # set player variables
        self.player_count = 0
        self.players = Player.init_players_from_configs(
            game=self,
            player_configs=player_configs
        )
        self.current_player = None

        # set gameplay variables
        self.min_word_length = min_word_length
        self.ghost_word = ghost_word.upper()
        self.num_strikes_allowed = len(ghost_word)
        if word_list_type not in Game.word_list_filepaths.keys():
            invalid_word_list_err_msg = (
                f"Invalid Game.word_list_type: '{word_list_type}'; "
                f"Game.word_list_type must be one of the following: "
                f"{Game.word_list_filepaths.keys()}"
            )
            raise ValueError(invalid_word_list_err_msg)
        self.word_list = self.load_word_list(word_list_type)

        # set current game status variables
        self.current_word_fragment = ''
        self.game_is_over = False

    def load_word_list(self, word_list_type):
        """Load the word list from the word list file.

        :param str word_list_type: type of word list to use; must be 'scrabble'
            or 'webster'
        :return: list of allowed words in the dictionary
        :rtype: list[str]
        """
        word_list_filepath = Game.word_list_filepaths[word_list_type]
        with open(word_list_filepath, 'r') as word_list_file:
            word_list_raw = word_list_file.readlines()
        word_list = [word.strip().lower() for word in word_list_raw
                     if len(word.strip()) >= self.min_word_length]
        return word_list

    def start(self):
        """Start the game."""
        self.current_player = self.players[0]
        while not self.game_is_over:
            print(f"\n--{self.current_player.name}'s turn--")
            next_player = self.get_next_player()
            self.current_player.take_turn()
            self.check_for_game_over()
            self.current_player = next_player

    def get_next_player(self):
        """Get the next remaining player after the current player.

        :return: the player after the current player
        :rtype: Player
        """
        current_player_idx = self.players.index(self.current_player)
        if current_player_idx + 1 == self.player_count:
            next_player_idx = 0
        else:
            next_player_idx = current_player_idx + 1
        next_player = self.players[next_player_idx]
        return next_player

    def get_previous_player(self):
        """Get the previous remaining player before the current player.

        :return: the player before the current player
        :rtype: Player
        """
        current_player_idx = self.players.index(self.current_player)
        if current_player_idx == 0:
            previous_player_idx = self.player_count - 1
        else:
            previous_player_idx = current_player_idx - 1
        previous_player = self.players[previous_player_idx]
        return previous_player

    def check_for_game_over(self):
        """Check if the game is over."""
        if self.player_count == 1:
            winning_player = self.players[0]
            print(f"{winning_player.name} has won the game!\n\n")
            self.game_is_over = True

    def eliminate_player(self, player):
        """Eliminate a given player and remove them from the player list.

        :param Player player: player to eliminate
        """
        print(f"{player.name} has {self.ghost_word} and has been eliminated!")
        self.players.remove(player)
        self.player_count = len(self.players)

    def reset_current_word_fragment(self):
        """Reset the current game's word fragment back to an empty string."""
        self.current_word_fragment = ''

    def is_valid_intended_word(self, intended_word):
        """Validate the intended word.

        An intended word is valid is it starts with the current word fragment
        and is a valid word in the game's dictionary.

        :param str intended_word: word player intended to complete with their
            last played letter
        :return: True if the intended word is valid, False otherwise
        :rtype: bool
        """
        if intended_word is None:
            return False

        is_playable = intended_word.startswith(self.current_word_fragment)
        is_valid = self.is_valid_word(intended_word)
        return is_playable and is_valid

    def is_valid_word(self, word):
        """Validate that a given word is in the game's dictionary.

        :param str word: word to validate
        :return: True if the word is valid, False otherwise
        :rtype: bool
        """
        return word in self.word_list
