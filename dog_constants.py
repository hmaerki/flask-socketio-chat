import random as r

COUNT_PLAYER_CARDS = 6


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