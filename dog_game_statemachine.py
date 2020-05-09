
from __future__ import annotations

import typing
import logging

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # https://www.stefaanlippens.net/circular-imports-type-hints-python.html
    import dog_game
    import dog_game_state

import dog_constants

class NewGameStateException(BaseException):
    def __init__(self, state):
        self.state = state

class GameStatemachineBase:
    def __init__(self, gameState: dog_game_state.GameState):
        self._gameState = gameState

    @property
    def game(self):
        return self._gameState.game

    def event(self, json: dog_game.JsonWrapper) -> typing.Optional[str]:
        raise NotImplementedError()

    def handleGenericEvent(self, json: dog_game.JsonWrapper) -> typing.Optional[str]:
        '''
        Events which always are valid.
        return True if event was handled
        '''
        if json.isEvent('newGame'):
            json.addMessage('Neues Spiel')
            raise NewGameStateException(GameStateExchangeCards(self._gameState))

        if json.isEvent('setName'):
            playerIndex = json.getInt('player')
            playerName = json.getStr('name')
            self._gameState.setName(playerIndex, playerName)
            json.addMessage(f'Heisst neu "{playerName}"')
            return True

        if json.isEvent('rotateBoard'):
            playerIndex = json.getInt('player')
            logging.warning(f'Player {playerIndex} rotated.')
            json.addMessage('Spielbrett drehen')
            return True

        if json.isEvent('browserConnected'):
            playerIndex = json.getInt('player')
            logging.warning(f'****************************************** {playerIndex} verbunden.')
            # json.addMessage('Verbunden')
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

    def buttonPlayEnabled(self, playerState: dog_game_state.PlayerState):
        return False

    def buttonChangeEnabled(self, playerState: dog_game_state.PlayerState):
        return False

class GameStateInit(GameStatemachineBase):
    def event(self, json: dog_game.JsonWrapper) -> typing.Optional[str]:
        if self.handleGenericEvent(json):
            return
        return self.unexpectedEvent(json)

    def appendState(self, json: dict) -> None:
        pass

    def getAssistance(self):
        return f'Spiel starten!'

class GameStateExchangeCards(GameStatemachineBase):
    def __init__(self, gameState: dog_game_state.GameState):
        super().__init__(gameState)
        self._gameState.serveCards(dog_constants.INITIAL_CARDS_TO_BE_SERVED)

    @property
    def playersRequireToChangeText(self):
        return ', '.join(sorted([player.name for player in self._gameState.playersRequireToChange]))

    def event(self, json: dog_game.JsonWrapper) -> typing.Optional[str]:
        # dict(player=0, event='changeCard', card=1))
        if self.handleGenericEvent(json):
            return
        if json.isEvent('changeCard'):
            playerIndex = json.getInt('player')
            cardIndex = json.getInt('card')
            json.addMessage('Tauschen')
            err = self._gameState.cardToBeChanged(playerIndex, cardIndex)
            if self._gameState.changeCards():
                raise NewGameStateException(GameStatePlay(self._gameState))
            return err
        return self.unexpectedEvent(json)

    def appendState(self, json: dict) -> None:
        return

    def buttonChangeEnabled(self, playerState: dog_game_state.PlayerState):
        return playerState.requireToChange

    def getAssistance(self):
        return f'{self.playersRequireToChangeText}: Bitte eine Karte tauschen!'

class GameStatePlay(GameStatemachineBase):
    def __init__(self, gameState: dog_game_state.GameState):
        super().__init__(gameState)
        self._count_cards_served = dog_constants.INITIAL_CARDS_TO_BE_SERVED
        self._playerToPlayIndex = dog_constants.dogRandom.randint(0, self._gameState.game.player_count-1)

    def event(self, json: dog_game.JsonWrapper) -> typing.Optional[str]:
        if self.handleGenericEvent(json):
            return

    def appendState(self, json: dict) -> None:
        return

    def getAssistance(self):
        return f'{self._gameState.getPlayer(self._playerToPlayIndex).name} bitte Karte ausspielen!'

