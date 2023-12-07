import random

class Card:
    def __init__(self, suit, val):
        self.suit = suit
        self.val = val

    def __repr__(self):
        suits_to_uni = {'h': "\u2764", 'c': "\u2663", 's': '\u2660', 'd': '\u2666'}
        return f'{self.val} of {suits_to_uni[self.suit]}'


class Deck(Card):
    def __init__(self, joker):
        self.joker = joker
        self.suits = ['c', 'd', 'h', 's']
        self.vals = ['A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K']
        self.deck = []

        for suit in self.suits:
            for val in self.vals:
                self.deck.append(Card(suit, val))
        
        if self.joker:
            self.deck.append('w')
    
    def draw_Card(self):
        if len(self.deck) == 0:
            self.deck = Deck(self.joker).deck
        spot = random.randint(0, len(self.deck)-1)
        drawn_card = self.deck[spot]
        self.deck.remove(drawn_card)
        return drawn_card
    
    def shuffle(self):
        random.shuffle(self.deck)
    
    def __len__(self):
        return len(self.deck)

    def __repr__(self):
        return str(self.deck)

if __name__ == '__main__':
    main_deck = Deck(False)
    print(main_deck)

    for i in range(1000):
        card_drawn = main_deck.draw_Card()
        print(card_drawn)
        print('\n')
        print(main_deck.deck)