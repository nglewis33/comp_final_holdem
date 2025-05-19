import random
from .base_agent import BaseAgent
from core.evaluator import HandEvaluator

class ProbabilityAgent(BaseAgent):
    """A poker agent that uses basic heuristics to make decisions."""
    
    def __init__(self, name, aggression=0.5, risk_tolerance=0.5, bluff_frequency=0.1, sim_count=1000):
        """Initialize the agent.
        
        Args:
            name (str): The name of the agent
            aggression (float): The aggression factor (0-1) - how aggressively to bet when ahead
            risk_tolerance (float): The risk tolerance (0-1) - willingness to call with marginal hands
            bluff_frequency (float): The frequency of bluffing (0-1)
            sim_count (int): Number of Monte Carlo simulations to run (not used anymore)
        """
        super().__init__(name)
        self.aggression = max(0, min(1, aggression))
        self.risk_tolerance = max(0, min(1, risk_tolerance))
        self.bluff_frequency = max(0, min(1, bluff_frequency))
        
        # Cache for hand strengths to avoid recalculating
        self.hand_strength_cache = {}
    
    def decide_action(self, game_state, valid_actions, player):
        """Decide on an action based on the current game state.
        
        Args:
            game_state (dict): The current state of the game
            valid_actions (list): List of valid actions for the player
            player (Player): The player object controlled by this agent
            
        Returns:
            tuple: (action, amount)
                action (str): The action to take (e.g., 'fold', 'check', 'call', 'raise')
                amount (int, optional): The amount to bet if action is 'raise'
        """
        # Calculate hand strength
        hand_strength = self._get_hand_strength(player.hole_cards, game_state['community_cards'])
        
        # Calculate pot odds for calling
        to_call = game_state['current_bet'] - player.current_bet
        pot_odds = to_call / (game_state['pot'] + to_call) if to_call > 0 else 0
        
        # Calculate pot size relative to stack
        pot_to_stack_ratio = game_state['pot'] / player.stack if player.stack > 0 else float('inf')
        
        # Calculate position advantage (later position is better)
        position = ((game_state['current_idx'] - game_state['dealer_idx']) % len(game_state['players'])) / len(game_state['players'])
        position_advantage = position * 0.1  # Up to 10% boost for position
        
        # Adjust hand strength based on position and aggression
        adjusted_strength = hand_strength * (1 + position_advantage)
        
        # Decide action based on hand strength, pot odds, and agent characteristics
        if 'check' in valid_actions:
            # We can check - decide whether to check or raise
            if adjusted_strength > 0.6:  # Strong hand
                # Bet sizing based on hand strength and aggression
                bet_size = self._calculate_bet_size(adjusted_strength, game_state, player)
                
                if 'raise' in valid_actions and random.random() < self.aggression:
                    return 'raise', bet_size
                else:
                    return 'check', 0
            elif random.random() < self.bluff_frequency:  # Bluff occasionally
                if 'raise' in valid_actions:
                    bluff_size = self._calculate_bluff_size(game_state, player)
                    return 'raise', bluff_size
                else:
                    return 'check', 0
            else:
                return 'check', 0
        
        elif 'call' in valid_actions:
            # We need to call or fold/raise
            pot_odds_threshold = 1.0 - (adjusted_strength + self.risk_tolerance * 0.2)
            
            if adjusted_strength > pot_odds:  # +EV call
                if adjusted_strength > 0.7 and 'raise' in valid_actions:  # Very strong hand
                    bet_size = self._calculate_bet_size(adjusted_strength, game_state, player)
                    return 'raise', bet_size
                else:
                    return 'call', to_call
            elif random.random() < self.bluff_frequency * 2 and 'raise' in valid_actions:  # Bluff
                bluff_size = self._calculate_bluff_size(game_state, player)
                return 'raise', bluff_size
            elif random.random() < self.risk_tolerance and pot_to_stack_ratio > 0.3:  # Call with marginal hands
                return 'call', to_call
            else:
                return 'fold', 0
        
        # If we can't check or call, fold
        return 'fold', 0
    
    def _get_hand_strength(self, hole_cards, community_cards):
        """Get the relative strength of the current hand.
        
        Args:
            hole_cards (list): List of 2 Card objects
            community_cards (list): List of community cards
            
        Returns:
            float: Hand strength (0-1)
        """
        # Create a cache key
        cache_key = (
            tuple((card.rank, card.suit) for card in hole_cards),
            tuple((card.rank, card.suit) for card in community_cards)
        )
        
        # Check if we've already calculated this
        if cache_key in self.hand_strength_cache:
            return self.hand_strength_cache[cache_key]
        
        # If we're preflop, use preflop evaluation
        if not community_cards:
            strength = self._evaluate_preflop(hole_cards)
            self.hand_strength_cache[cache_key] = strength
            return strength
        
        # Evaluate hand strength based on hand ranking
        rank_idx, _, _, _ = HandEvaluator.evaluate_hand(hole_cards, community_cards)
        
        # Map rank index to a strength value (0-9, lower is better)
        # Invert and normalize to 0-1 scale
        base_strength = (9 - rank_idx) / 9.0
        
        # Adjust strength based on stage of the hand (more cards = more certainty)
        if len(community_cards) == 3:  # Flop
            strength = base_strength * 0.8  # Still lots of uncertainty
        elif len(community_cards) == 4:  # Turn
            strength = base_strength * 0.9  # More certainty
        else:  # River
            strength = base_strength  # Full certainty
        
        # Store in cache for future use
        self.hand_strength_cache[cache_key] = strength
        
        return strength
    
    def _evaluate_preflop(self, hole_cards):
        """Evaluate the strength of preflop hole cards.
        
        Args:
            hole_cards (list): List of 2 Card objects
            
        Returns:
            float: Hand strength (0-1)
        """
        # Check for pocket pair
        if hole_cards[0].rank == hole_cards[1].rank:
            rank_value = hole_cards[0].rank_value / 12.0  # 12 is the max rank_value (A)
            # Higher pairs are stronger
            return 0.6 + rank_value * 0.4
        
        # Check for suited cards
        suited = hole_cards[0].suit == hole_cards[1].suit
        
        # Get rank values (0-12)
        ranks = [card.rank_value for card in hole_cards]
        high_card = max(ranks)
        low_card = min(ranks)
        
        # Normalize rank values to 0-1 scale
        high_card_norm = high_card / 12.0
        gap = high_card - low_card
        
        # Calculate base strength
        if suited:
            # Suited cards get a bonus
            strength = 0.3 + high_card_norm * 0.3
        else:
            strength = 0.2 + high_card_norm * 0.25
        
        # Connectors (small gap) are better
        if gap <= 2:
            strength += 0.15
        elif gap <= 4:
            strength += 0.05
        
        return min(strength, 0.9)  # Cap at 0.9 for non-pairs
    
    def _calculate_bet_size(self, hand_strength, game_state, player):
        """Calculate bet size based on hand strength and game state.
        
        Args:
            hand_strength (float): Hand strength (0-1)
            game_state (dict): The current game state
            player (Player): The player object
            
        Returns:
            int: Bet size
        """
        # Base sizing on pot and hand strength
        min_raise = game_state['min_raise']
        pot_size = game_state['pot']
        to_call = game_state['current_bet'] - player.current_bet
        
        # Calculate base bet size as a percentage of the pot
        # Higher strength = larger bet
        pot_percentage = min(1.0, hand_strength * 2 * self.aggression)
        base_bet = int(pot_size * pot_percentage)
        
        # Ensure bet is at least the minimum raise
        bet_size = max(min_raise, base_bet)
        
        # Cap bet at player's stack
        return min(bet_size, player.stack)
    
    def _calculate_bluff_size(self, game_state, player):
        """Calculate bluff size based on game state.
        
        Args:
            game_state (dict): The current game state
            player (Player): The player object
            
        Returns:
            int: Bluff size
        """
        min_raise = game_state['min_raise']
        pot_size = game_state['pot']
        
        # Smaller bluffs are more likely to get called
        # Larger bluffs have more fold equity
        # Balance based on aggression
        if self.aggression > 0.7:  # Very aggressive
            bluff_percentage = 0.75  # 3/4 pot bet
        elif self.aggression > 0.4:  # Moderately aggressive
            bluff_percentage = 0.5   # 1/2 pot bet
        else:  # Conservative
            bluff_percentage = 0.33  # 1/3 pot bet
        
        bluff_size = int(pot_size * bluff_percentage)
        
        # Ensure bluff is at least the minimum raise
        bluff_size = max(min_raise, bluff_size)
        
        # Cap bluff at player's stack
        return min(bluff_size, player.stack)
    
    def __str__(self):
        return f"{self.name} Probability Agent (Aggression: {self.aggression:.2f}, Risk: {self.risk_tolerance:.2f})" 