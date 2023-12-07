from deck import *
from collections import OrderedDict
c_to_v = {
    'A': (1, 11),
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    6: 6,
    7: 7,
    8: 8,
    9: 9,
    10: 10,
    'J': 10,
    'Q': 10,
    'K': 10
} #card to value

class Hand:
    def __init__(self):
        self.cards = []
        self.value = [0]
        self.bust = False
        self.stand = False

    def update(self, card):
        self.cards.append(card)
        if card.val == 'A':
            new_vals = set()
            for i in range(len(self.value)):
                new_vals.update([self.value[i] + 1, self.value[i] + 11])
            new_vals = list(new_vals)
            new_vals.sort()
            new_vals = new_vals[:2]
            for x in new_vals[:]:
                if x > 21:
                    new_vals.remove(x)
            self.value = new_vals
            if not self.value: # if it's empty then every value in new_vals was > 21
                self.bust = True
        else:
            self.value = [x + c_to_v[card.val] for x in self.value if x + c_to_v[card.val] < 22]
            if not self.value:
                self.bust = True

        return self.cards, self.value
    
class Player:
    def __init__(self, name, bankroll, dealer = False):
        self.name = name
        self.cards = []
        self.value = [0]
        self.bankroll = bankroll
        self.wager = 0
        self.dealer = dealer
        self.bust = False
        self.stand = False
        self.blackjack = False

        '''if self.dealer == True:
            self.bankroll = None
            self.wager = None'''
    
    def update(self, card):
        self.cards.append(card)
        if card.val == 'A':
            new_vals = set()
            for i in range(len(self.value)):
                new_vals.update([self.value[i] + 1, self.value[i] + 11])
            new_vals = list(new_vals)
            new_vals.sort()
            new_vals = new_vals[:2]
            for x in new_vals[:]:
                if x > 21:
                    new_vals.remove(x)
            self.value = new_vals
            if not self.value:
                self.bust = True
        else:
            self.value = [x + c_to_v[card.val] for x in self.value if x + c_to_v[card.val] < 22]
            if not self.value:
                self.bust = True

        
        return self.name, self.cards, self.value
        
    def reset(self):
        self.cards = []
        self.value = [0]
        self.wager = 0
        self.blackjack = False
        self.bust = False
        self.stand = False
    
    def __repr__(self):
        return self.name

class Blackjack(Deck):
    '''
    Begins a game of blackjack // 
    Draw_Card(self) randomly draws a card from self.deck and removes it //
    Alternatively, one can use shuffle(self) to shuffle self.deck and then use self.deck.pop //
    '''
    def __init__(self, test = False):
        self.game_over = False
        self.players = list()
        self.deck = Deck(False)

        if test == True:
            Henry = Player('Henry', 100, dealer = False)
            Ryan = Player('Ryan', 100, dealer = False)
            self.players.append(Henry)
            self.players.append(Ryan)
        else:
            add_players = True
            i = 1
            while add_players:
                cur_player = input('Enter player ' + str(i) + ' name: ')
                if cur_player in [player.name for player in self.players]:
                    raise Exception("Player already in play!")
                cur_money = float(input('Enter ' + cur_player + ' bankroll: '))

                player_obj = Player(cur_player, cur_money)
                self.players.append(player_obj)

                i += 1
                add_players = bool(input('Type anything to add another player (leave blank to begin game): '))
        Dealer = Player('Dealer', 0, True)
        self.players.append(Dealer)

    def deal_Hand(self, test):
        '''
        Takes wagers and deals initial 2 cards.
        Returns wagers.
        '''
        wagers = OrderedDict()

        if test == True:
            for player in self.players[:-1]:
                player.wager = 1
                wagers[player.name] = 1
                '''player.update(Card('c', 'A'))
                player.update(Card('s', 'J'))
            
            self.players[-1].update(Card('c', 6))
            self.players[-1].update(Card('s', 4))
            return'''
        else:
            for player in self.players[:-1]:
                while True: # Exits out of while loop when player makes a valid wager
                    cur_wager = float(input('Enter ' + player.name + '`s wager: '))
                    if player.bankroll - cur_wager < 0:
                        print('Error you are broke. Make valid wager.')
                        continue
                    break

                player.wager = cur_wager
                wagers[player] = cur_wager
        

        for i in range(2):
            for player in self.players:
                drawn_card = self.deck.draw_Card()
                player.update(drawn_card)
                
        for player in self.players:
            player.bankroll -= player.wager # Not sure whether this should go before or after cards are dealt
            if 21 in player.value:
                player.blackjack = True
            
        
        dealer = self.players[-1]

        game_description = [(player.name, player.cards, player.value) for player in self.players[:-1]]
        game_description.append((dealer.name, [dealer.cards[0]], [c_to_v[dealer.cards[0].val]]))
        
        print(game_description)

        if c_to_v[dealer.cards[0].val] == 10 and dealer.cards[1].val == 'A': # If dealer's upcard is 10
            for player in self.players[:-1]: # everyone but the dealer
                if not player.blackjack:
                    player.bankroll -= player.wager
            return self.end_game()
            

        if dealer.cards[0].val == 'A':
            insurance_dic = self.offer_insurance(self.players[:-1])

            if c_to_v[dealer.cards[1].val] == 10:
                for player in self.players[:-1]:
                    if insurance_dic[player] == True:
                        player.bankroll += (3*player.wager)/2
                return self.end_game()  

        for player in self.players[:-1]:
            if player.blackjack == True:
                player.bankroll += (5/2)*player.wager
                player.reset()
                player.stand = True

        return wagers

    def offer_insurance(self, players):
        insurance_dic = {}
        for player in players:
            decision = bool(input(str(player) + ", accept insurance for $" + str(player.wager/2) + "? (leave blank to reject) "))
            insurance_dic[player] = decision
            if decision == True:
                player.bankroll -= player.wager/2 
        return insurance_dic
    
    def end_game(self):
        self.game_over = True
        for player in self.players:
            player.reset()
            self.deck = Deck(False)
    
    def second_phase(self):

        dealer = self.players[-1]


        for player in self.players[:-1]:
            if player.stand == False:
                first_hit = True
            
                action = True
                while action:
                    print("Action on " + str(player) + ".")
                    print("Player " + str(player.value) + " " + str(player.cards) + "\nvs\nDealer " + str([c_to_v[dealer.cards[0].val]]) + " " + str([dealer.cards[0]]))
                    if first_hit == True:
                        action = input("Hit (h) / Double (type dd) / Stand (leave blank)? ")
                    else:
                        action = input("Hit (any key) / Stand (leave blank)? ")

                    first_hit = False
                    if action == 'dd':
                        if player.bankroll > player.wager:
                            player.bankroll -= player.wager
                            player.wager += player.wager
                            drawn_card = self.deck.draw_Card()
                            player.update(drawn_card)
                            print("Player " + str(player.value) + " " + str(player.cards) + "\nvs\nDealer " + str([c_to_v[dealer.cards[0].val]]) + " " + str([dealer.cards[0]]))
                            action = False

                    if action:
                        drawn_card = self.deck.draw_Card()
                        player.update(drawn_card)
                        if player.bust == True:
                            print("Player " + str(player.value) + " " + str(player.cards) + "\nvs\nDealer " + str([c_to_v[dealer.cards[0].val]]) + " " + str([dealer.cards[0]]))
                            print("Player bust.")
                            action = False
        print(dealer.value, 'this is dealer.value line 221')
            
        
        while not dealer.bust and dealer.stand == False:
            if max(dealer.value) >= 18 or dealer.value[0] > 16:
                dealer.stand = True
                break
            if max(dealer.value) < 18 or dealer.value[0] <= 16:
                drawn_card = self.deck.draw_Card()
                dealer.update(drawn_card)
                if dealer.bust:
                    break

        
        for player in self.players[:-1]:
            if player.bust:
                continue
            if player.bust == False and dealer.bust == True:
                player.bankroll += 2*player.wager
            elif max(player.value) > max(dealer.value):
                player.bankroll += 2*player.wager
            elif max(player.value) == max(dealer.value):
                player.bankroll += player.wager

        print([(player.name, player.cards, player.value) for player in self.players])        
            
        return [(player.name, player.cards, player.value) for player in self.players]

                        
            
            


if __name__ == '__main__':
    game = Blackjack(True)
    wagers = game.deal_Hand(True) # deals the initial 2 cards per player. Returns wagers.
    if not game.game_over:
            print(game.second_phase())

    for player in game.players:
        print(player.bankroll)
    
    


    


    
    


    


    
        

    





