
import logging
import typing


import dog_cards
import dog_constants
import dog_game_state
import dog_game_statemachine

logging.basicConfig(level=logging.DEBUG)


INITIAL_NAME = ('Asterix', 'Obelix', 'Trubadix', 'Idefix')


class GameState:
    def __init__(self, game: 'Game'):
        self.game = game
        self.reset()
        self.__game_dirty = False
        self.__board_dirty = False

    @property
    def dgc(self) -> dog_constants.DogGameConstants:
        return self.game.dgc

    def reset(self) -> None:
        self.list_player_names = list(self.dgc.PLAYER_NAMES_DEFAULTS)
        self.__game_dirty = True
        self.__board_dirty = True

    def boardDirty(self):
        self.__game_dirty = True
        self.__board_dirty = True

    def gameDirty(self):
        self.__game_dirty = True

    def event(self, json: str) -> typing.Optional[str]:
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
