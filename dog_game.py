
import logging
import typing


import dog_cards
import dog_constants
import dog_game_state
import dog_game_statemachine

logging.basicConfig(level=logging.DEBUG)


INITIAL_NAME = ('Asterix', 'Obelix', 'Trubadix', 'Idefix')


class GameState:
    def __init__(self, game: 'Game', dgc: dog_constants.DogGameConstants):
        self.dgc = dgc
        self.list_player_names = list(dgc.PLAYER_NAMES_DEFAULTS)
        # self.dict_id = {}
        # for playerIndex, name in enumerate(dgc.PLAYER_NAMES_DEFAULTS):
        #     self.dict_id[game.html.playerIndexToId(playerIndex)] = name

    def event(self, json: str) -> typing.Optional[str]:
        if json['event'] == 'newName':
            idx = json['idx']
            name = json['name']
            self.list_player_names[idx] = name

    def appendState(self, json: dict) -> None:
        json['playerNames'] = self.list_player_names

class Game:
    def __init__(self, dgc: dog_constants.DogGameConstants):
        self.setPlayerCount(2)

    def setPlayerCount(self, playerCount=2):
        def getDgc():
            for dgc in dog_constants.LIST_DOG_GAME_CONSTANTS:
                if dgc.PLAYER_COUNT == playerCount:
                    return dgc
            return dog_constants.DOG_GAME_CONSTANTS_2
        self.dgc = getDgc()
        self.__gameState = GameState(self, self.dgc)

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
