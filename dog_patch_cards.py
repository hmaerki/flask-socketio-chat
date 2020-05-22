import pathlib
import xml.sax
import xml.sax.xmlreader
import xml.sax.saxutils
import dog_constants

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).parent
DIRECTORY_CARDS_ORI = DIRECTORY_OF_THIS_FILE / 'static' / 'boardori' / 'cards'

class CardsPatcher(xml.sax.saxutils.XMLFilterBase):
    def __init__(self, dbc: dog_constants.DogBoardConstants):
        parent = xml.sax.make_parser()
        super().__init__(parent)
        self.__dbc = dbc
        self.__rect = None

    def startElement(self, name, attrs):
        if name == 'svg':
            card_width = self.__dbc.CARD_SIZE.real
            card_height = self.__dbc.CARD_SIZE.imag
            attrs = {key:value for key, value in attrs.items()}
            attrs['height'] = f'{card_height}'
            attrs['width'] = f'{card_width}'
            attrs['x'] = f'{-card_width/2}'
            attrs['y'] = f'{-card_height/2}'

        if name == 'rect':
            self.__rect = {key:value for key, value in attrs.items()}
            self.__rect['stroke'] = 'blue'
            self.__rect['stroke-width'] = '0'
            super().startElement(name, self.__rect)
            return

        super().startElement(name, attrs)

    def endElement(self, name):
        if name == 'svg':
            assert self.__rect is not None
            self.__rect['fill'] = 'lightgray'
            self.__rect['opacity'] = '0.0'
            self.__rect['id'] = 'mask'
            super().startElement('rect', self.__rect)
            super().endElement('rect')

        super().endElement(name)

    @classmethod
    def __convert_cards_for_board(cls, dbc: dog_constants.DogBoardConstants):
        directory_new = DIRECTORY_OF_THIS_FILE / dbc.BOARD_DIRECTORY_RELATIVE / 'cards'
        if not directory_new.exists():
            directory_new.mkdir(parents=True)

        for filenameOri in DIRECTORY_CARDS_ORI.glob('*.svg'):
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
