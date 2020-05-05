
import random as r
import logging
import typing

import dog_cards

logging.basicConfig(level=logging.DEBUG)

INITIAL_CARDS_TO_BE_SERVED = 6
COUNT_PLAYER_CARDS = 6
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
        self.__state = GameState(self)

    def event(self, json: JsonWrapper) -> typing.Optional[str]:
        try:
            return self.__state.event(JsonWrapper(json))
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

    @property
    def requireToChange(self) -> bool:
        return self.__cardToBeChangedIndex is None

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

    def __getCardAtIndex(self, card_index:int):
        '''Returns card or "None"'''
        if card_index >= len(self.__cards):
            return None
        return self.__cards[card_index]

    def __enableCardAtIndex(self, card_index:int, enabled:bool):
        '''Returns "False" if no card, else "enabled"'''
        card = self.__getCardAtIndex(card_index)
        if card is None:
            return False
        return enabled

    def appendState(self, json: list, statemachineState: 'GameStatemachineBase'):
        # changeCard-buttons: Enable or disable all
        enabled = statemachineState.buttonChangeEnabled(self)
        json.append({
            'html_id': f'button#player{self.__player.index}_changeCard',
                'attr_set': { 'disabled': not enabled }
        })

        for card_index in range(COUNT_PLAYER_CARDS):
            enabled = self.__enableCardAtIndex(card_index, statemachineState.buttonPlayEnabled(self))
            json.append({
                'html_id': f'button#player{self.__player.index}_playCard[name="{card_index}"]',
                    'attr_set': { 'disabled': not enabled }
            })

        json.append({
            'html_id': f'#player{self.__player.index}_textfield_name',
                'attr_set': { 'value': self.name }
        })

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
    
    @property
    def playersRequireToChange(self):
        return [player for player in self.__player_state if player.requireToChange]

    def getPlayer(self, index: int) -> 'PlayerState':
        return self.__player_state[index]

    def serveCards(self, count_cards: int) -> None:
        for playerState in self.__player_state:
            playerState.serveCards(self.__cardStack.pop_cards(count_cards))

    def event(self, json: JsonWrapper) -> typing.Optional[str]:
        try:
            return self.__statemachine.event(json)
        except NewGameState as ex:
            self.__statemachine = ex.state
            return f'New State "{type(self.__statemachine).__name__}"'

    def appendState(self, json: dict) -> None:
        rc = self.__statemachine.appendState(json)
        for playerState in self.__player_state:
            playerState.appendState(json, self.__statemachine)
        return rc

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

class GameStatemachineBase:
    def __init__(self, gameState: GameState):
        self._gameState = gameState

    @property
    def game(self):
        return self._gameState.game

    def event(self, json: JsonWrapper) -> typing.Optional[str]:
        raise NotImplementedError()

    def handleGenericEvent(self, json: JsonWrapper) -> typing.Optional[str]:
        '''
        Events which always are valid.
        return True if event was handled
        '''
        if json.isEvent('newGame'):
            raise NewGameState(GameStateExchangeCards(self._gameState))

        if json.isEvent('setName'):
            playerIndex = json.getInt('player')
            playerName = json.getStr('name')
            self._gameState.setName(playerIndex, playerName)
            return True

        if json.isEvent('rotateBoard'):
            playerIndex = json.getInt('player')
            logging.warning(f'Player {playerIndex} rotated.')
            return True

        if json.isEvent('browserConnected'):
            playerIndex = json.getInt('player')
            logging.warning(f'Player {playerIndex} rotated.')
            return True

        return False

    def unexpectedEvent(self, json: dict) -> None:
        err = f'{type(self).__name__}: Unexpected event:{repr(json)}'
        logging.warning(err)
        return err

    def appendState(self, json: dict) -> None:
        raise NotImplementedError()

    def getAssistance(self) -> str:
        raise NotImplementedError()

    def buttonPlayEnabled(self, playerState: PlayerState):
        return False

    def buttonChangeEnabled(self, playerState: PlayerState):
        return False

class GameStateInit(GameStatemachineBase):
    def event(self, json: JsonWrapper) -> typing.Optional[str]:
        if self.handleGenericEvent(json):
            return
        return self.unexpectedEvent(json)

    def appendState(self, json: dict) -> None:
        pass

    def getAssistance(self):
        return f'Spiel starten!'

class GameStateExchangeCards(GameStatemachineBase):
    def __init__(self, gameState: GameState):
        super().__init__(gameState)
        self._gameState.serveCards(INITIAL_CARDS_TO_BE_SERVED)

    @property
    def playersRequireToChangeText(self):
        return ', '.join(sorted([player.name for player in self._gameState.playersRequireToChange]))

    def event(self, json: JsonWrapper) -> typing.Optional[str]:
        # dict(player=0, event='changeCard', card=1))
        if self.handleGenericEvent(json):
            return
        if json.isEvent('changeCard'):
            playerIndex = json.getInt('player')
            cardIndex = json.getInt('card')
            err = self._gameState.cardToBeChanged(playerIndex, cardIndex)
            if self._gameState.changeCards():
                raise NewGameState(GameStatePlay(self._gameState))
            return err
        return self.unexpectedEvent(json)

    def appendState(self, json: dict) -> None:
        return

    def buttonChangeEnabled(self, playerState: PlayerState):
        return playerState.requireToChange

    def getAssistance(self):
        return f'{self.playersRequireToChangeText}: Bitte eine Karte tauschen!'

class GameStatePlay(GameStatemachineBase):
    def __init__(self, gameState: GameState):
        super().__init__(gameState)
        self._count_cards_served = INITIAL_CARDS_TO_BE_SERVED
        self._playerToPlayIndex = dogRandom.randint(0, self._gameState.game.player_count-1)

    def event(self, json: JsonWrapper) -> typing.Optional[str]:
        if self.handleGenericEvent(json):
            return

    def appendState(self, json: dict) -> None:
        return

    def getAssistance(self):
        return f'{self._gameState.getPlayer(self._playerToPlayIndex).name} bitte Karte ausspielen!'

def test_game():
    '''
    >>> dogRandom.seed(0, mockMode=True)
    >>> game = Game()
    >>> json_command = []
    >>> game.appendState(json_command)
    >>> json_command
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
# TODO: Throw exception
