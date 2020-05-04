
import random as r
import logging
import typing

import dog_cards

logging.basicConfig(level=logging.DEBUG)

INITIAL_CARDS_TO_BE_SERVED = 6
COLORS_ID = ('red', 'green', 'blue', 'yellow')
COLORS_GERMAN = ('Rot', 'Grün', 'Blau', 'Gelb')
INITIAL_NAME = ('Asterix', 'Obelix', 'Trubadix', 'Idefix')

class DogRandom:
    def __init__(self):
        self.__mockMode = False
        self.__mockSeed = 0
    
    def seed(self, a, mockMode: bool) -> None:
        self.__mockMode = mockMode
        self.__mockSeed = a
    
    def shuffle(self, elements: list) -> None:
        if self.__mockMode:
            return
        r.shuffle(elements)

    def randint(self, a: int, b: int) -> int:
        if self.__mockMode:
            return a
        return r.randint(a, b)

dogRandom = DogRandom()

class Player:
    def __init__(self, game: 'Game', index: int):
        self.__index = index
        self.__game = game

    @property
    def game(self) -> 'Game':
        return self.__game

    @property
    def initialName(self) -> str:
        return INITIAL_NAME[self.__index]

    @property
    def colorID(self) -> str:
        return COLORS_ID[self.__index]

    @property
    def colorI18N(self) -> str:
        return COLORS_GERMAN[self.__index]

class Game:
    def __init__(self, player_count=2):
        self.player_count = player_count
        self.players = [Player(self, index) for index in range(player_count)]
        self.__state = GameState(self)

    def event(self, json: dict) -> typing.Optional[str]:
        try:
            return self.__state.event(json)
        except NewGameState as ex:
            self.__state = ex.state

    def appendState(self, json: dict) -> None:
        return self.__state.appendState(json)

    def getAssistance(self):
        return self.__state.getAssistance()

    def getPlayer(self, index: int) -> 'PlayerState':
        return self.__state.getPlayer(index)

class PlayerState:
    def __init__(self, player: Player):
        self.__player = player
        self.__name = player.initialName
        self.__cards = ()
        self.__cardToBeChangedIndex = None

    def __repr__(self) -> str:
        return f'{type(self).__name__} {self.__player.colorID}({self.__name})'

    @property
    def game(self) -> Game:
        return self.__player.game

    @property
    def colorI18N(self) -> str:
        return self.__player.colorI18N

    @property
    def name(self) -> str:
        return self.__name

    @property
    def cardsText(self) -> str:
        def name(card):
            if card is None:
                return None
            return card.id
        cards_text = [name(card) for card in self.__cards]
        return f'{self.__player.colorID} changeIndex={self.__cardToBeChangedIndex} cards={",".join(cards_text)}'

    def setName(self, name:str):
        self.__name = name

    def serveCards(self, cards: list) -> None:
        self.__cards = cards

    def cardToBeChanged(self, index:int) -> typing.Optional[str]:
        err = f'{self}: Expected __cardToBeChangedIndex to be "None" but got "{self.__cardToBeChangedIndex}"'
        if self.__cardToBeChangedIndex is not None:
            logging.warning(err)
            return err
        self.__cardToBeChangedIndex = index
    
    def changeCard(self, playerStateOther: 'PlayerState'):
        cardSelf = self.__cards[self.__cardToBeChangedIndex]
        cardOther = playerStateOther.__cards[playerStateOther.__cardToBeChangedIndex]

        self.__cards[self.__cardToBeChangedIndex] = cardOther
        playerStateOther.__cards[playerStateOther.__cardToBeChangedIndex] = cardSelf

    @property
    def requireToChange(self) -> bool:
        return self.__cardToBeChangedIndex is None

class NewGameState(BaseException):
    def __init__(self, state):
        self.state = state

class GameState:
    def __init__(self, game: Game):
        self.__game = game
        self.__statemachine = GameStateInit(self)
        self.__player_state = [PlayerState(player) for player in self.__game.players]
        self.__cardStack = dog_cards.Cards()
        self.__cardStack.shuffle(dogRandom.shuffle)

    @property
    def game(self) -> Game:
        return self.__game
    
    def getPlayer(self, index: int) -> 'PlayerState':
        return self.__player_state[index]

    def serveCards(self, count_cards: int) -> None:
        for playerState in self.__player_state:
            playerState.serveCards(self.__cardStack.pop_cards(count_cards))

    def event(self, json: dict) -> typing.Optional[str]:
        try:
            return self.__statemachine.event(json)
        except NewGameState as ex:
            self.__statemachine = ex.state
            return f'New State "{type(self.__statemachine).__name__}"'

    def appendState(self, json: dict) -> None:
        return self.__statemachine.appendState(json)

    def getAssistance(self):
        return self.__statemachine.getAssistance()

    def setName(self, player:int, name:str):
        return self.__player_state[player].setName(name)

    def cardToBeChanged(self, player:int, index:int):
        return self.__player_state[player].cardToBeChanged(index)

    def changeCards(self):
        if len(self.playersRequireToChange) > 0:
            return False
        player_count_half = self.__game.player_count//2
        for index_A in range(player_count_half):
            index_B = index_A + player_count_half
            self.__player_state[index_A].changeCard(self.__player_state[index_B])
        return True

    @property
    def playersRequireToChange(self):
        return [player for player in self.__player_state if player.requireToChange]

class GameStatemachineBase:
    def __init__(self, gameState: GameState):
        self._gameState = gameState

    @property
    def game(self):
        return self._gameState.game

    def event(self, json: dict) -> typing.Optional[str]:
        raise NotImplementedError()

    def unexpectedEvent(self, json: dict) -> None:
        err = f'{type(self).__name__}: Unexpected event:{repr(json)}'
        logging.warning(err)
        return err

    def appendState(self, json: dict) -> None:
        raise NotImplementedError()

    def getAssistance(self) -> str:
        raise NotImplementedError()

class GameStateInit(GameStatemachineBase):
    def event(self, json: dict) -> typing.Optional[str]:
        if json.get('event', None) == 'newGame':
            raise NewGameState(GameStateExchangeCards(self._gameState))
        return self.unexpectedEvent(json)

    def appendState(self, json: dict) -> None:
        return

    def getAssistance(self):
        return f'Spiel starten!'

class GameStateExchangeCards(GameStatemachineBase):
    def __init__(self, gameState: GameState):
        super().__init__(gameState)
        self._gameState.serveCards(INITIAL_CARDS_TO_BE_SERVED)

    @property
    def playersRequireToChangeText(self):
        return ', '.join(sorted([player.name for player in self._gameState.playersRequireToChange]))

    def event(self, json: dict) -> typing.Optional[str]:
        # dict(player=0, event='changeCard', card=1))
        if json.get('event', None) == 'changeCard':
            player = json['player']
            index = json['card']
            err = self._gameState.cardToBeChanged(player, index)
            if self._gameState.changeCards():
                raise NewGameState(GameStatePlay(self._gameState))
            return err
        if json.get('event', None) == 'setName':
            player = json['player']
            name = json['name']
            self._gameState.setName(player, name)
            return
        return self.unexpectedEvent(json)

    def appendState(self, json: dict) -> None:
        return

    def getAssistance(self):
        return f'{self.playersRequireToChangeText}: Bitte eine Karte tauschen!'

class GameStatePlay(GameStatemachineBase):
    def __init__(self, gameState: GameState):
        super().__init__(gameState)
        self._count_cards_served = INITIAL_CARDS_TO_BE_SERVED
        self._playerToPlayIndex = dogRandom.randint(0, self._gameState.game.player_count-1)

    def event(self, json: dict) -> typing.Optional[str]:
        pass

    def appendState(self, json: dict) -> None:
        return

    def getAssistance(self):
        return f'{self._gameState.getPlayer(self._playerToPlayIndex).name} bitte Karte ausspielen!'

def test_game():
    '''
    >>> dogRandom.seed(0, mockMode=True)
    >>> game = Game()
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
    >>> dogRandom.seed(0, mockMode=True) # Force the seed for the next player
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
