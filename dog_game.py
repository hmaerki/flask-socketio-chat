
import math
import typing
import logging

import dog_cards
import dog_constants

logging.basicConfig(level=logging.DEBUG)


INITIAL_NAME = ('Asterix', 'Obelix', 'Trubadix', 'Idefix')

class Card:
    def __init__(self, id: int, angle: int, x_initial: int, y_initial: int):
        self.__id = id
        self.__layer = 0
        self.__face_index = 22
        self.__angle = angle
        self.__x = x_initial
        self.__y = y_initial
        self.__x_initial = x_initial
        self.__y_initial = y_initial

    def move(self, x:int, y:int):
        self.__x = x
        self.__y = y

    @property
    def json(self):
        return (int(self.__angle), int(self.__x), int(self.__y))

class GameState:
    def __init__(self, game: 'Game'):
        self.game = game
        self.reset()
        self.__game_dirty = False
        self.__board_dirty = False

    @property
    def dgc(self) -> dog_constants.DogGameConstants:
        return self.game.dgc

    @property
    def dbc(self) -> dog_constants.DogGameConstants:
        return self.game.dbc

    def reset(self) -> None:
        self.__game_dirty = True
        self.__board_dirty = True
        self.list_player_names = list(self.dgc.PLAYER_NAMES_DEFAULTS)
        self.__initializeCards()

    def __initializeCards(self):
        def generator():
            for playerIndex in range(self.dgc.PLAYER_COUNT):
                angleDeg = 360.0 * playerIndex / self.dgc.PLAYER_COUNT
                playerAngle = 2 * math.pi * playerIndex / self.dgc.PLAYER_COUNT
                for cardIndex, cardCenter in enumerate(self.dbc.LIST_CARD_CENTER):
                    id = playerIndex* self.dgc.PLAYER_COUNT + cardIndex
                    cardCenterRotated = math.e**(complex(0, playerAngle)) * cardCenter
                    x_initial = cardCenterRotated.real
                    y_initial = cardCenterRotated.imag
                    yield Card(id=id, angle=angleDeg, x_initial=x_initial, y_initial=y_initial)

        self.__list_cards = list(generator())
        print(f'self.__list_cards: {len(self.__list_cards)}')

    def boardDirty(self):
        self.__game_dirty = True
        self.__board_dirty = True

    def gameDirty(self):
        self.__game_dirty = True

    def event(self, json: str) -> typing.Optional[str]:
        if json['event'] == 'browserConnected':
            self.gameDirty()
            return

        if json['event'] == 'newName':
            idx = json['idx']
            name = json['name']
            self.list_player_names[idx] = name
            self.gameDirty()

        if json['event'] == 'buttonPressed':
            label = json['label']
            method = f'button_{label.upper()}'
            f = getattr(self, method)
            assert f is not None
            f()

    def appendState(self, json: dict) -> None:
        if self.__board_dirty:
            self.appendStateBoard(json)
            self.appendStateGame(json)
            return

        if self.__game_dirty:
            self.appendStateGame(json)
            return

    def appendStateGame(self, json: dict) -> None:
        self.__game_dirty = False
        json['playerNames'] = self.list_player_names

        json['cards'] = [card.json for card in self.__list_cards]

    def moveCard(self, id:int, x:int, y:int) -> dict:
        card = self.__list_cards[id]
        card.move(x=x, y=y)
        return {'card': (id, card.json)}

    def appendStateBoard(self, json: dict) -> None:
        self.__board_dirty = False
    
    def button_G2(self):
        print('button_G2')
        self.game.setPlayerCount(2)

    def button_G4(self):
        print('button_G4')
        self.game.setPlayerCount(4)

    def button_G6(self):
        print('button_G6')
        self.game.setPlayerCount(6)

    def button_R(self):
        print('button_R')

    def button_2(self):
        print('button_2')

    def button_3(self):
        print('button_3')

    def button_4(self):
        print('button_4')

    def button_5(self):
        print('button_5')

    def button_6(self):
        print('button_6')

class Game:
    def __init__(self):
        self.dgc = dog_constants.DOG_GAME_CONSTANTS_4
        self.__gameState = GameState(self)
        self.__gameState.boardDirty()

    def setPlayerCount(self, playerCount):
        def getDgc():
            for dgc in dog_constants.LIST_DOG_GAME_CONSTANTS:
                if dgc.PLAYER_COUNT == playerCount:
                    return dgc
            return dog_constants.DOG_GAME_CONSTANTS_2

        self.dgc = getDgc()
        self.__gameState.boardDirty()

    def event(self, json: str) -> typing.Optional[str]:
        return self.__gameState.event(json)

    def appendState(self, json: dict) -> None:
        self.__gameState.appendState(json)

    def moveCard(self, id:int, x:int, y:int) -> dict:
        return self.__gameState.moveCard(id=id, x=x, y=y)

    def getAssistance(self):
        return self.__gameState.getAssistance()

    def getPlayer(self, index: int) -> 'PlayerState':
        return self.__gameState.getPlayer(index)
    
    def setMarble(self, dictPosition: dict) -> None:
        self.__gameState.setMarble(dictPosition)

    @property
    def dbc(self) -> dog_constants.DogBoardConstants:
        return self.dgc.dbc

    @property
    def template_params(self):
        # playerIndexNext = (playerIndex+1)%game.player_count
        playerIndex = 2
        playerIndexNext = 42
        rotateUrl = 'xy' # f'{flask.request.url_root}{playerIndexNext}'
        params = dict(
            game = self,
            playerCount = self.dgc.PLAYER_COUNT,
            playerIndex = playerIndex,
            rotateUrl = rotateUrl
        )
        return params


if __name__ == '__main__':
  import doctest
  failures, tests = doctest.testmod()
  print('SUCCESS' if failures == 0 else f'{failures} FAILURES')
