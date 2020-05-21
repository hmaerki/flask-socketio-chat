import pathlib
import xml.etree.ElementTree
import dog_constants

# A dog game contains 2 cards of black spade, but 6 cards of joker
LIST_NUMBER_CARDS = ('2', '6')

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).parent
DIRECTORY_CARDS_ORI = DIRECTORY_OF_THIS_FILE / 'static' / 'boardori' / 'cards'

class CardsPatcher:
    def __init__(self, dbc: dog_constants.DogBoardConstants):
        self.__dbc = dbc

    def __convert_svg(self, tree):
        card_width = self.__dbc.CARD_SIZE.real
        card_height = self.__dbc.CARD_SIZE.imag
        xml_declaration = tree.find(".")
        xml_declaration.attrib['height'] = str(card_height)
        xml_declaration.attrib['width'] = str(card_width)
        xml_declaration.attrib['x'] = str(card_width/2)
        xml_declaration.attrib['y'] = str(card_height/2)

    def __convert_cards_for_board(self):
        directory_cards_new = DIRECTORY_OF_THIS_FILE / self.__dbc.BOARD_DIRECTORY_RELATIVE / 'cards'
        for number_cards in LIST_NUMBER_CARDS:
            directory_new = directory_cards_new.joinpath(number_cards)
            if not directory_new.exists():
                directory_new.mkdir(parents=True)

            for filenameOri in DIRECTORY_CARDS_ORI.joinpath(number_cards).glob('*.svg'):
                filenameNew = directory_new.joinpath(filenameOri.name)
                print(f'*** {filenameOri} -> {filenameNew}')

                tree = xml.etree.ElementTree.parse(filenameOri)
                self.__convert_svg(tree)
                xml.etree.ElementTree.register_namespace('', 'http://www.w3.org/2000/svg')
                tree.write(filenameNew, encoding='utf-8', xml_declaration=True)

    @classmethod
    def convert_cards(cls):
        for dbc in dog_constants.LIST_DOG_BOARD_CONSTANTS:
            cp = CardsPatcher(dbc)
            cp.__convert_cards_for_board()

if __name__ == '__main__':
    CardsPatcher.convert_cards()
