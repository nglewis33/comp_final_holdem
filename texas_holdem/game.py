import time
from colorama import Fore, Style
from .deck import Deck
from .evaluator import HandEvaluator

class TexasHoldemGame:
    """Main class for a Texas Hold'em poker game."""
    
    # Game phases
    PHASE_PREFLOP = 'preflop'
    PHASE_FLOP = 'flop'
    PHASE_TURN = 'turn'
    PHASE_RIVER = 'river'
    PHASE_SHOWDOWN = 'showdown'
    
    def __init__(self, players, small_blind, big_blind, ante=0):
        """Initialize a new Texas Hold'em game.
        
        Args:
            players (list): List of Player objects
            small_blind (int): Small blind amount
            big_blind (int): Big blind amount
            ante (int, optional): Ante amount
        """
        self.players = players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.ante = ante
        self.deck = Deck()
        self.community_cards = []
        self.dealer_idx = 0
        self.current_phase = None
        self.pots = []  # List of pots (main pot and side pots)
        self.current_bet = 0
        self.min_raise = big_blind  # Minimum raise is initially the big blind
        self.last_raiser_idx = -1
        
    def play_hand(self):
        """Play a single hand of Texas Hold'em."""
        # Reset the game state
        self._reset_game_state()
        
        # Deal hole cards to players
        self._deal_hole_cards()
        
        # Play each phase of the hand
        self._betting_round(self.PHASE_PREFLOP)
        
        # Check if hand is over (all but one player folded)
        if self._count_active_players() <= 1:
            self._resolve_winners()
            return
        
        self._deal_community_cards(self.PHASE_FLOP)
        self._betting_round(self.PHASE_FLOP)
        
        if self._count_active_players() <= 1:
            self._resolve_winners()
            return
        
        self._deal_community_cards(self.PHASE_TURN)
        self._betting_round(self.PHASE_TURN)
        
        if self._count_active_players() <= 1:
            self._resolve_winners()
            return
        
        self._deal_community_cards(self.PHASE_RIVER)
        self._betting_round(self.PHASE_RIVER)
        
        # Showdown
        self._resolve_winners()
        
        # Move the dealer button
        self.dealer_idx = (self.dealer_idx + 1) % len(self.players)
    
    def _reset_game_state(self):
        """Reset the game state for a new hand."""
        # Reset deck and community cards
        self.deck = Deck()
        self.deck.shuffle()
        self.community_cards = []
        
        # Reset player states
        for player in self.players:
            player.reset_for_new_hand()
        
        # Initialize pot
        self.pots = [{"amount": 0, "eligible_players": self.players.copy()}]
        self.current_bet = 0
        self.min_raise = self.big_blind
        self.current_phase = None
        self.last_raiser_idx = -1
        
        # Post blinds and antes
        self._post_blinds_and_antes()
    
    def _post_blinds_and_antes(self):
        """Post blinds and antes."""
        # Collect antes if any
        if self.ante > 0:
            print(f"\n{Fore.YELLOW}Collecting antes (${self.ante}){Style.RESET_ALL}")
            for player in self.players:
                amount = player.place_bet(self.ante)
                self.pots[0]["amount"] += amount
        
        # Small blind
        sb_idx = (self.dealer_idx + 1) % len(self.players)
        sb_player = self.players[sb_idx]
        print(f"\n{Fore.YELLOW}{sb_player.name} posts small blind (${self.small_blind}){Style.RESET_ALL}")
        amount = sb_player.place_bet(self.small_blind)
        self.pots[0]["amount"] += amount
        
        # Big blind
        bb_idx = (self.dealer_idx + 2) % len(self.players)
        bb_player = self.players[bb_idx]
        print(f"{Fore.YELLOW}{bb_player.name} posts big blind (${self.big_blind}){Style.RESET_ALL}")
        amount = bb_player.place_bet(self.big_blind)
        self.pots[0]["amount"] += amount
        
        # Set current bet to big blind
        self.current_bet = self.big_blind
    
    def _deal_hole_cards(self):
        """Deal 2 hole cards to each player."""
        print(f"\n{Fore.CYAN}Dealing hole cards...{Style.RESET_ALL}")
        for player in self.players:
            cards = self.deck.deal(2)
            player.receive_cards(cards)
    
    def _deal_community_cards(self, phase):
        """Deal community cards based on the current phase.
        
        Args:
            phase (str): The current game phase
        """
        self.current_phase = phase
        
        if phase == self.PHASE_FLOP:
            # Deal 3 cards for the flop
            print(f"\n{Fore.CYAN}Dealing the flop...{Style.RESET_ALL}")
            flop_cards = self.deck.deal(3)
            self.community_cards.extend(flop_cards)
        elif phase == self.PHASE_TURN:
            # Deal 1 card for the turn
            print(f"\n{Fore.CYAN}Dealing the turn...{Style.RESET_ALL}")
            turn_card = self.deck.deal(1)
            self.community_cards.extend(turn_card)
        elif phase == self.PHASE_RIVER:
            # Deal 1 card for the river
            print(f"\n{Fore.CYAN}Dealing the river...{Style.RESET_ALL}")
            river_card = self.deck.deal(1)
            self.community_cards.extend(river_card)
        
        # Display community cards
        print(f"Community cards: {' '.join(str(card) for card in self.community_cards)}")
    
    def _betting_round(self, phase):
        """Conduct a betting round.
        
        Args:
            phase (str): The current game phase
        """
        self.current_phase = phase
        print(f"\n{Fore.GREEN}=== {phase.upper()} BETTING ROUND ==={Style.RESET_ALL}")
        
        # Reset current bet for new rounds (except preflop)
        if phase != self.PHASE_PREFLOP:
            self.current_bet = 0
            for player in self.players:
                player.current_bet = 0
        
        # Determine starting position
        if phase == self.PHASE_PREFLOP:
            current_idx = (self.dealer_idx + 3) % len(self.players)  # UTG position
        else:
            current_idx = (self.dealer_idx + 1) % len(self.players)  # SB position
        
        # Find the first active player
        while (self.players[current_idx].is_folded or 
               self.players[current_idx].is_all_in or 
               self.players[current_idx].stack == 0):
            current_idx = (current_idx + 1) % len(self.players)
            # If we've gone full circle, end the betting round
            if current_idx == self.dealer_idx:
                return
        
        # Set the first player to act
        initial_idx = current_idx
        last_aggressor_idx = -1
        
        # Keep track of who has acted
        num_active_players = self._count_active_players()
        players_acted = 0
        all_players_acted = False
        
        # Main betting loop
        while True:
            current_player = self.players[current_idx]
            
            # Skip folded, all-in, or broke players
            if (current_player.is_folded or 
                current_player.is_all_in or 
                current_player.stack == 0):
                current_idx = (current_idx + 1) % len(self.players)
                continue
            
            # Determine valid actions
            valid_actions = ['fold']
            to_call = self.current_bet - current_player.current_bet
            
            if to_call == 0:
                valid_actions.append('check')
            else:
                valid_actions.append('call')
            
            # Can only raise if player has enough chips
            if current_player.stack > to_call + self.min_raise:
                valid_actions.append('raise')
            
            # Create the game state dictionary
            game_state = {
                'phase': phase,
                'community_cards': self.community_cards,
                'pot': self.pots[0]["amount"],
                'current_bet': self.current_bet,
                'min_raise': self.min_raise,
                'players': self.players,
                'dealer_idx': self.dealer_idx,
                'current_idx': current_idx
            }
            
            # Display current player and pot
            print(f"\n{Fore.CYAN}Current pot: ${self.pots[0]['amount']}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}{current_player.name}'s turn to act{Style.RESET_ALL}")
            
            # Get action from the player
            action, amount = current_player.get_action(game_state, valid_actions)
            
            # Process the action
            if action == 'fold':
                print(f"{current_player.name} folds")
                current_player.fold()
                players_acted += 1
            
            elif action == 'check':
                print(f"{current_player.name} checks")
                players_acted += 1
            
            elif action == 'call':
                amount = self.current_bet - current_player.current_bet
                actual_bet = current_player.place_bet(amount)
                self.pots[0]["amount"] += actual_bet
                print(f"{current_player.name} calls ${actual_bet}")
                players_acted += 1
            
            elif action == 'raise':
                to_call = self.current_bet - current_player.current_bet
                raise_amount = amount
                actual_bet = current_player.place_bet(to_call + raise_amount)
                self.pots[0]["amount"] += actual_bet
                self.current_bet = current_player.current_bet
                self.min_raise = raise_amount
                last_aggressor_idx = current_idx
                
                # Reset players_acted since we have a new aggressor
                players_acted = 1
                all_players_acted = False
                
                print(f"{current_player.name} raises to ${self.current_bet}")
            
            # Check if we're done with the betting round
            active_players = self._count_active_players()
            
            # If only one player left, end the round
            if active_players == 1:
                break
            
            # If all active players have acted
            if players_acted >= active_players:
                if all_players_acted or last_aggressor_idx == -1:
                    break
                all_players_acted = True
            
            # Move to the next player
            current_idx = (current_idx + 1) % len(self.players)
    
    def _count_active_players(self):
        """Count the number of active (not folded) players.
        
        Returns:
            int: Number of active players
        """
        return sum(1 for player in self.players if not player.is_folded)
    
    def _resolve_winners(self):
        """Determine the winner(s) of the hand and award the pot."""
        active_players = [p for p in self.players if not p.is_folded]
        
        # If only one player remains, they win
        if len(active_players) == 1:
            winner = active_players[0]
            print(f"\n{Fore.GREEN}=== HAND COMPLETE ==={Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{winner.name} wins ${self.pots[0]['amount']}{Style.RESET_ALL}")
            winner.add_to_stack(self.pots[0]["amount"])
            return
        
        # Otherwise, we need a showdown
        print(f"\n{Fore.GREEN}=== SHOWDOWN ==={Style.RESET_ALL}")
        
        # Show all hole cards
        for player in active_players:
            print(f"{player.name}'s hole cards: {' '.join(str(card) for card in player.hole_cards)}")
        
        # Evaluate each player's hand
        player_hands = []
        for player in active_players:
            rank_idx, hand_name, best_hand = HandEvaluator.evaluate_hand(player.hole_cards, self.community_cards)
            player_hands.append((player, rank_idx, hand_name, best_hand))
        
        # Sort by hand rank (lower index is better)
        player_hands.sort(key=lambda x: x[1])
        
        # Determine winners (there can be ties)
        winners = [player_hands[0][0]]
        best_rank = player_hands[0][1]
        for player, rank, _, _ in player_hands[1:]:
            if rank == best_rank:
                winners.append(player)
            else:
                break
        
        # Distribute the pot
        pot_amount = self.pots[0]["amount"]
        each_share = pot_amount // len(winners)
        remainder = pot_amount % len(winners)  # Any remainder goes to the first winner
        
        print(f"\n{player_hands[0][0].name} has {player_hands[0][2]} ")
        
        for i, winner in enumerate(winners):
            if i == 0:
                winner.add_to_stack(each_share + remainder)
                print(f"{Fore.YELLOW}{winner.name} wins ${each_share + remainder} with {player_hands[0][2]}{Style.RESET_ALL}")
            else:
                winner.add_to_stack(each_share)
                print(f"{Fore.YELLOW}{winner.name} wins ${each_share} with {player_hands[0][2]}{Style.RESET_ALL}")
    
    def display_game_status(self):
        """Display the current game status."""
        print(f"\n{Fore.GREEN}=== GAME STATUS ==={Style.RESET_ALL}")
        
        # Display dealer position
        dealer_name = self.players[self.dealer_idx].name
        print(f"Dealer: {dealer_name}")
        
        # Display players and their chip stacks
        print("Players:")
        for i, player in enumerate(self.players):
            status = ""
            if player.is_folded:
                status = "(folded)"
            elif player.is_all_in:
                status = "(all-in)"
            
            if i == self.dealer_idx:
                print(f"  {player} {status} [D]")
            else:
                print(f"  {player} {status}")
        
        # Display pot
        print(f"Current pot: ${self.pots[0]['amount']}")
        
        # Display community cards if any
        if self.community_cards:
            print(f"Community cards: {' '.join(str(card) for card in self.community_cards)}") 