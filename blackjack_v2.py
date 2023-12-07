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
    def __init__(self, wager = 0):
        self.cards = []
        self.value = [0]
        self.wager = wager
        self.bust = False
        self.stand = False
        self.first_hit = True
    
    def split(self):
        hand_2 = Hand(self.wager)

        hand_2.update(self.cards[1])

        temp = self.cards[0]

        self.cards = []
        self.value = [0]
        self.update(temp)

        return self, hand_2

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

    def __len__(self):
        return len(self.cards)

    def __repr__(self):
        return str(self.cards) + " " + str(self.value)
    
class Player:
    def __init__(self, name, bankroll, dealer = False):
        self.name = name
        self.hands = []
        self.bankroll = bankroll
        self.dealer = dealer
        self.blackjack = False
        
    def reset(self):
        self.hands = []
        self.blackjack = False
    
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
        self.game_over = False

        if test == True:
            for player in self.players[:-1]:

                hand_ = Hand(1) # create a hand object
                player.hands.append(hand_)

                '''player.hands[0].update(Card('h', 9))
                player.hands[0].update(Card('d', 9))
            hand_ = Hand()
            self.players[-1].hands.append(hand_)
            self.players[-1].hands[0].update(Card('c', 6))
            self.players[-1].hands[0].update(Card('s', 4))'''

        else:
            for player in self.players[:-1]:
                while True: # Exits out of while loop when player makes a valid wager
                    cur_wager = float(input('Enter ' + player.name + '`s wager: '))
                    if player.bankroll - cur_wager < 0:
                        print('Error you are broke. Make valid wager.')
                        continue
                    break
                
                hand_ = Hand(cur_wager) # create hand object
                player.hands.append(hand_)
        
        self.players[-1].hands.append(Hand()) # add a hand to dealer

        
    
        for i in range(2):
            for player in self.players:
                drawn_card = self.deck.draw_Card()
                player.hands[0].update(drawn_card)
                
        for player in self.players:
            player.bankroll -= player.hands[0].wager # Not sure whether this should go before or after cards are dealt
            if 21 in player.hands[0].value:
                player.blackjack = True
        
        
        dealer = self.players[-1]

        game_description = [(player.name, player.hands) for player in self.players[:-1]]
        game_description.append((dealer.name, [dealer.hands]))
        
        print(game_description, '\n')

        if c_to_v[dealer.hands[0].cards[0].val] == 10 and dealer.hands[0].cards[1].val == 'A': # If dealer's upcard is 10
            for player in self.players[:-1]: # everyone but the dealer
                if player.blackjack:
                    player.bankroll += player.hands[0].wager
            return self.end_game()
            

        if dealer.hands[0].cards[0].val == 'A':
            insurance_dic = self.offer_insurance(self.players[:-1])

            if c_to_v[dealer.hands[0].cards[1].val] == 10:
                for player in self.players[:-1]:
                    if insurance_dic[player] == True:
                        player.bankroll += (3*player.hands[0].wager)/2
                return self.end_game()  

        for player in self.players[:-1]:
            if player.blackjack == True:
                player.bankroll += (5/2)*player.hands[0].wager
                player.hands[0].stand = True

        return

    def offer_insurance(self, players):
        insurance_dic = {}
        for player in players:
            decision = bool(input(str(player) + ", accept insurance for $" + str(player.hands[0].wager/2) + "? (leave blank to reject) "))
            insurance_dic[player] = decision
            if decision == True:
                player.bankroll -= player.hands[0].wager/2 
        return insurance_dic
    
    def end_game(self):
        self.game_over = True
        for player in self.players:
            player.reset()
        self.deck = Deck(False)        
    
    def second_phase(self):

        dealer = self.players[-1]

        for player in [player for player in self.players[:-1] if player.hands[0].stand == False]: # all players (not dealer) who didn't get blackjack

            queue = player.hands[:]

            while queue:
                hand = queue[0]

                if len(hand) < 2:
                    drawn_card = self.deck.draw_Card()
                    hand.update(drawn_card)
                
                print("Action on " + str(player) +  ".")
                print("Player " + str(hand.value) + " " + str(hand.cards) + "\nvs\nDealer " + str([c_to_v[dealer.hands[0].cards[0].val]]) + " " + str([dealer.hands[0].cards[0]]))

                if hand.first_hit == True and player.bankroll >= hand.wager:
                    if hand.cards[0].val == hand.cards[1].val: # option to split or double
                        action = input("Hit (h) / Double (dd) / Split (ss) / Stand (leave blank) ")

                        if action == 'ss':
                            hand, hand_2 = hand.split()

                            player.bankroll -= hand.wager

                            player.hands.append(hand_2)

                            queue.pop(0)

                            queue.insert(0, hand)
                            queue.insert(1, hand_2)

                            continue

                        # else get out of here resumes at line 248

                                
                    else: # option to double
                        action = input("Hit (h) / Double (type dd) / Stand (leave blank)? ")

                else:
                    action = input("Hit (any key) / Stand (leave blank)? ")


                if action == 'dd' and hand.first_hit == True:
                        player.bankroll -= hand.wager
                        hand.wager += hand.wager
                        drawn_card = self.deck.draw_Card()
                        hand.update(drawn_card)
                        print("Player " + str(hand.value) + " " + str(hand.cards) + "\nvs\nDealer " + str([c_to_v[dealer.hands[0].cards[0].val]]) + " " + str([dealer.hands[0].cards[0]]))
                        queue.pop(0)
                        hand.first_hit = False
                        hand.stand == True
                        continue

                if action:
                    drawn_card = self.deck.draw_Card()
                    hand.update(drawn_card)
                    hand.first_hit = False
                    if hand.bust == True:
                        print("Player " + str(hand.value) + " " + str(hand.cards) + "\nvs\nDealer " + str([c_to_v[dealer.hands[0].cards[0].val]]) + " " + str([dealer.hands[0].cards[0]]))
                        print("Player bust.")
                        queue.pop(0)
                else:
                    queue.pop(0)
                    
        while not dealer.hands[0].bust and dealer.hands[0].stand == False:
            if max(dealer.hands[0].value) >= 18 or dealer.hands[0].value[0] > 16:
                dealer.hands[0].stand = True
                break
            if max(dealer.hands[0].value) < 18 or dealer.hands[0].value[0] <= 16:
                drawn_card = self.deck.draw_Card()
                dealer.hands[0].update(drawn_card)
                if dealer.hands[0].bust:
                    break


        dealer_val = dealer.hands[0].value
        
        for player in self.players[:-1]:
            if player.blackjack == True:
                continue
            for hand in player.hands:
                if hand.bust:
                    continue
                if hand.bust == False and dealer.hands[0].bust == True:
                    player.bankroll += 2*hand.wager
                elif max(hand.value) > max(dealer_val):
                    player.bankroll += 2*hand.wager
                elif max(hand.value) == max(dealer_val):
                    player.bankroll += hand.wager
            
        return [(player.name, player.hands) for player in self.players]

                        
            
            


if __name__ == '__main__':
    game = Blackjack(True)
    wagers = game.deal_Hand(True) # deals the initial 2 cards per player. Returns wagers.
    if not game.game_over:
            print(game.second_phase())

    for player in game.players:
        print(player, player.bankroll)