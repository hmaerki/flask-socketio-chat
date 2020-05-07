
import logging
import typing


import dog_cards
import dog_constants
import dog_game_state
import dog_game_statemachine

logging.basicConfig(level=logging.DEBUG)


COLORS_ID = ('red', 'green', 'blue', 'yellow')
COLORS_GERMAN = ('Rot', 'Grün', 'Blau', 'Gelb')
INITIAL_NAME = ('Asterix', 'Obelix', 'Trubadix', 'Idefix')

class JsonWrapper:
    def __init__(self, json:dict):
        self.__json = json

    def isEvent(self, eventName: str):
        return self.__json.get('event', None) == eventName

    def getStr(self, tag, mandatory=True):
        text = self.__json.get(tag, None)
        if text is None:
            if mandatory:
                raise Exception(f'"{tag}" mssing in: {self.__json}')
        return text

    def getInt(self, tag, mandatory=True):
        text = self.getStr(tag=tag, mandatory=mandatory)
        try:
            return int(text)
        except ValueError:
            raise Exception(f'Expected a integer but got "{tag}" in: {self.__json}')

    def __repr__(self):
        return repr(self.__json)

class Player:
    def __init__(self, game: 'Game', index: int):
        self.__index = index
        self.__game = game

    @property
    def game(self) -> 'Game':
        return self.__game

    @property
    def index(self) -> int:
        return self.__index

    @property
    def initialName(self) -> str:
        return INITIAL_NAME[self.__index]

    @property
    def colorID(self) -> str:
        return COLORS_ID[self.__index]

    @property
    def colorI18N(self) -> str:
        return COLORS_GERMAN[self.__index]

    def disableButtonPlay(self, json: dict, enable=True):
        pass

    def disableButtonChange(self, json, enable=True):
        pass

class Game:
    def __init__(self, player_count=2):
        self.player_count = player_count
        self.players = [Player(self, index) for index in range(player_count)]
        self.__state = dog_game_state.GameState(self)

    def event(self, json: JsonWrapper) -> typing.Optional[str]:
        try:
            return self.__state.event(JsonWrapper(json))
        except dog_game_statemachine.NewGameStateException as ex:
            self.__state = ex.state

    def appendState(self, json: dict) -> None:
        return self.__state.appendState(json)

    def getAssistance(self):
        return self.__state.getAssistance()

    def getPlayer(self, index: int) -> 'PlayerState':
        return self.__state.getPlayer(index)

def test_game():
    '''
    >>> dog_constants.dogRandom.seed(0, mockMode=True)
    >>> game = Game()
    >>> json_command = []
    >>> game.appendState(json_command)
    >>> x = json_command
    >>> game.getAssistance()
    'Spiel starten!'
    >>> game.event(dict(player=0, event='newGame'))
    'New State "GameStateExchangeCards"'
    >>> game.getPlayer(0).cardsText
    'red changeIndex=None cards=2,3,4,5,6,7'
    >>> game.getPlayer(1).cardsText
    'green changeIndex=None cards=10,8,9,ace,jack,queen'
    >>> game.getAssistance()
    'Asterix, Obelix: Bitte eine Karte tauschen!'
    >>> game.event(dict(player=1, event='setName', name='Karlotto'))
    >>> game.event(dict(player=0, event='changeCard', card=1))
    >>> game.getAssistance()
    'Karlotto: Bitte eine Karte tauschen!'
    >>> game.event(dict(player=0, event='changeCard', card=2))
    'PlayerState red(Asterix): Expected __cardToBeChangedIndex to be "None" but got "1"'
    >>> dog_constants.dogRandom.seed(0, mockMode=True) # Force the seed for the next player
    >>> game.event(dict(player=1, event='changeCard', card=5))
    'New State "GameStatePlay"'
    >>> game.getAssistance()
    'Asterix bitte Karte ausspielen!'
    >>> game.getPlayer(0).cardsText
    'red changeIndex=1 cards=2,queen,4,5,6,7'
    >>> game.getPlayer(1).cardsText
    'green changeIndex=5 cards=10,8,9,ace,jack,3'
    '''
import doctest
doctest.testmod()
# TODO: Throw exception
