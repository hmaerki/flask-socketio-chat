from __future__ import annotations
import typing
import logging

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # https://www.stefaanlippens.net/circular-imports-type-hints-python.html
    import dog_game

import dog_constants
import dog_game_statemachine

import dog_cards

class PlayerState:
    def __init__(self, player: dog_game.Player):
        self.__player = player
        self.__name = player.initialName
        self.__cards = ()
        self.__cardToBeChangedIndex = None

    def __repr__(self) -> str:
        return f'{type(self).__name__} {self.__player.colorID}({self.__name})'

    @property
    def game(self) -> dog_game.Game:
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

        for card_index in range(dog_constants.COUNT_PLAYER_CARDS):
            enabled = self.__enableCardAtIndex(card_index, statemachineState.buttonPlayEnabled(self))
            json.append({
                'html_id': f'button#player{self.__player.index}_playCard[name="{card_index}"]',
                    'attr_set': { 'disabled': not enabled }
            })

        json.append({
            'html_id': f'#player{self.__player.index}_textfield_name',
                'attr_set': { 'value': self.name }
        })

class GameState:
    def __init__(self, game: dog_game.Game):
        self.__game = game
        self.__statemachine = dog_game_statemachine.GameStateInit(self)
        self.__player_state = [PlayerState(player) for player in self.__game.players]
        self.__cardStack = dog_cards.Cards()
        self.__cardStack.shuffle(dog_constants.dogRandom.shuffle)

    @property
    def game(self) -> dog_game.Game:
        return self.__game
    
    @property
    def playersRequireToChange(self):
        return [player for player in self.__player_state if player.requireToChange]

    def getPlayer(self, index: int) -> 'PlayerState':
        return self.__player_state[index]

    def serveCards(self, count_cards: int) -> None:
        for playerState in self.__player_state:
            playerState.serveCards(self.__cardStack.pop_cards(count_cards))

    def event(self, json: dog_game.JsonWrapper) -> typing.Optional[str]:
        try:
            return self.__statemachine.event(json)
        except dog_game_statemachine.NewGameStateException as ex:
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
