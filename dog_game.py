
import math
import typing
import logging

import dog_cards
import dog_constants
import dog_patch_cards

logging.basicConfig(level=logging.DEBUG)

dog_patch_cards.CardsPatcher.convert_cards()

INITIAL_NAME = ('Asterix', 'Obelix', 'Trubadix', 'Idefix')

class PlayersCard:
    def __init__(self, gameState: 'GameState', id: int, angle: int, x_initial: int, y_initial: int, card: dog_cards.Card):
        self.__gameState = gameState
        self.__id = id
        self.__layer = 0
        self.__angle = angle
        self.__x = x_initial
        self.__y = y_initial
        self.__x_initial = x_initial
        self.__y_initial = y_initial
        self.__card = card

    def move(self, x:int, y:int):
        self.__x = x
        self.__y = y

    def setCard(self, card: dog_cards.Card):
        self.__card = card

    @property
    def jsonMove(self):
        return (int(self.__angle), int(self.__x), int(self.__y))

    @property
    def jsonAll(self):
        return (int(self.__angle), int(self.__x), int(self.__y), self.__card.filebase, self.__card.descriptionI18N)

class GameState:
    def __init__(self, game: 'Game', room: str):
        self.cards = dog_cards.Cards()
        self.game = game
        self.room = room
        self.reset()
        self.__game_dirty = False
        self.__board_dirty = False

    @property
    def dgc(self) -> dog_constants.DogGameConstants:
        return self.game.dgc

    @property
    def dbc(self) -> dog_constants.DogGameConstants:
        return self.game.dbc

    # @property
    # def card_urls(self) -> list:
    #     return [f'/static/{self.dbc.BOARD_ID}/cards/{card.filename}' for card in self.__cards.all]

    @property
    def card_filebases(self) -> list:
        # {% for card in game.gameState.cards.all %}{{card.filebase}};{% endfor %}
        return ';'.join([card.filebase for card in self.cards.all])

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
                    id = playerIndex*self.dgc.PLAYER_COUNT + cardIndex
                    cardCenterRotated = math.e**(complex(0, playerAngle)) * cardCenter
                    x_initial = cardCenterRotated.real
                    y_initial = cardCenterRotated.imag
                    card = self.cards.pop_card()
                    yield PlayersCard(gameState=self, id=id, angle=angleDeg, x_initial=x_initial, y_initial=y_initial, card=card)

        self.__list_cards = list(generator())

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

        json['cards'] = [card.jsonAll for card in self.__list_cards]

    def moveCard(self, id:int, x:int, y:int) -> dict:
        card = self.__list_cards[id]
        card.move(x=x, y=y)
        return {'card': (id, card.jsonMove)}

    def appendStateBoard(self, json: dict) -> None:
        self.__board_dirty = False

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
    def __init__(self, players: int, room: str):
        def getDgc(playerCount):
            for dgc in dog_constants.LIST_DOG_GAME_CONSTANTS:
                if dgc.PLAYER_COUNT == playerCount:
                    return dgc
            return dog_constants.DOG_GAME_CONSTANTS_2
        self.dgc = getDgc(players)
        self.gameState = GameState(self, room)
        self.gameState.boardDirty()

    def event(self, json: str) -> typing.Optional[str]:
        return self.gameState.event(json)

    def appendState(self, json: dict) -> None:
        self.gameState.appendState(json)

    def moveCard(self, id:int, x:int, y:int) -> dict:
        return self.gameState.moveCard(id=id, x=x, y=y)

    def getAssistance(self):
        return self.gameState.getAssistance()

    def getPlayer(self, index: int) -> 'PlayerState':
        return self.gameState.getPlayer(index)
    
    def setMarble(self, dictPosition: dict) -> None:
        self.gameState.setMarble(dictPosition)

    @property
    def dbc(self) -> dog_constants.DogBoardConstants:
        return self.dgc.dbc

    @property
    def room(self) -> str:
        return self.gameState.room

    # @property
    # def card_urls_as_javascript(self) -> str:
    #     l = [f"'{url}'" for url in self.__gameState.card_urls]
    #     return f'[{",".join(l)}]'

    # @property
    # def template_params(self):
    #     # playerIndexNext = (playerIndex+1)%game.player_count
    #     playerIndex = 2
    #     playerIndexNext = 42
    #     rotateUrl = 'xy' # f'{flask.request.url_root}{playerIndexNext}'
    #     params = dict(
    #         game = self,
    #         playerCount = self.dgc.PLAYER_COUNT,
    #         playerIndex = playerIndex,
    #         rotateUrl = rotateUrl
    #     )
    #     return params


if __name__ == '__main__':
  import doctest
  failures, tests = doctest.testmod()
  print('SUCCESS' if failures == 0 else f'{failures} FAILURES')
