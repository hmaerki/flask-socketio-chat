import pathlib
import xml.sax
import xml.sax.xmlreader
import xml.sax.saxutils
import dog_constants

# A dog game contains 2 cards of black spade, but 6 cards of joker
LIST_NUMBER_CARDS = ('2', '6')

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).parent
DIRECTORY_CARDS_ORI = DIRECTORY_OF_THIS_FILE / 'static' / 'boardori' / 'cards'

class CardsPatcher(xml.sax.saxutils.XMLFilterBase):
    def __init__(self, dbc: dog_constants.DogBoardConstants):
        parent = xml.sax.make_parser()
        super().__init__(parent)
        self.__dbc = dbc

    def startElement(self, name, attrs):
        if name == 'svg':
            card_width = self.__dbc.CARD_SIZE.real
            card_height = self.__dbc.CARD_SIZE.imag
            attrs = {key:value for key, value in attrs.items()}
            attrs['height'] = str(card_height)
            attrs['width'] = str(card_width)
            attrs['x'] = str(card_width/2)
            attrs['y'] = str(card_height/2)

        super().startElement(name, attrs)

    @classmethod
    def __convert_cards_for_board(cls, dbc: dog_constants.DogBoardConstants):
        directory_cards_new = DIRECTORY_OF_THIS_FILE / dbc.BOARD_DIRECTORY_RELATIVE / 'cards'
        for number_cards in LIST_NUMBER_CARDS:
            directory_new = directory_cards_new.joinpath(number_cards)
            if not directory_new.exists():
                directory_new.mkdir(parents=True)

            for filenameOri in DIRECTORY_CARDS_ORI.joinpath(number_cards).glob('*.svg'):
                filenameNew = directory_new.joinpath(filenameOri.name)
                # print(f'*** {filenameOri} -> {filenameNew}')

                reader = CardsPatcher(dbc)
                with open(filenameNew, 'w', encoding='utf-8') as f:
                    handler = xml.sax.saxutils.XMLGenerator(f, encoding='utf-8')
                    reader.setContentHandler(handler)
                    reader.parse(str(filenameOri))

    @classmethod
    def convert_cards(cls):
        for dbc in dog_constants.LIST_DOG_BOARD_CONSTANTS:
            cls.__convert_cards_for_board(dbc)

if __name__ == '__main__':
    CardsPatcher.convert_cards()
