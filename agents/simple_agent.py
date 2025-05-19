import random
from .base_agent import BaseAgent
from texas_holdem.evaluator import HandEvaluator

class SimpleAgent(BaseAgent):
    """A simple rule-based poker agent."""
    
    def __init__(self, name, aggression=0.5):
        """Initialize the agent.
        
        Args:
            name (str): The name of the agent
            aggression (float): The aggression factor (0-1)
        """
        super().__init__(name)
        self.aggression = max(0, min(1, aggression))  # Ensure value is between 0 and 1
    
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
        # Simple heuristic: evaluate our hand strength
        if game_state['phase'] == 'preflop':
            hand_strength = self._evaluate_preflop_hand(player.hole_cards)
        else:
            hand_strength = self._evaluate_hand_strength(player.hole_cards, game_state['community_cards'])
        
        # Modify hand strength by our aggression factor
        adjusted_strength = hand_strength * (1 + (self.aggression - 0.5))
        
        # Calculate pot odds for calling
        to_call = game_state['current_bet'] - player.current_bet
        pot_odds = to_call / (game_state['pot'] + to_call) if to_call > 0 else 0
        
        # Decide action based on hand strength and pot odds
        if 'check' in valid_actions:
            # We can check - decide whether to check or raise
            if adjusted_strength > 0.7 and 'raise' in valid_actions:
                # Strong hand, raise
                raise_amount = int(player.stack * adjusted_strength * 0.3)
                raise_amount = max(game_state['min_raise'], raise_amount)
                return 'raise', raise_amount
            elif adjusted_strength > 0.4 and random.random() < self.aggression and 'raise' in valid_actions:
                # Semi-bluff raise
                raise_amount = int(game_state['min_raise'] * (1 + self.aggression))
                return 'raise', raise_amount
            else:
                # Check
                return 'check', 0
        
        elif 'call' in valid_actions:
            # We need to call or fold/raise
            if adjusted_strength > pot_odds * 1.5:
                # Call if hand strength justifies the pot odds
                if adjusted_strength > 0.8 and 'raise' in valid_actions:
                    # Very strong hand, raise
                    raise_amount = int(player.stack * adjusted_strength * 0.4)
                    raise_amount = max(game_state['min_raise'], raise_amount)
                    return 'raise', raise_amount
                else:
                    # Decent hand, call
                    return 'call', to_call
            else:
                # Fold with weak hands unless we want to bluff
                if random.random() < self.aggression * 0.3 and 'raise' in valid_actions:
                    # Bluff raise
                    raise_amount = int(game_state['min_raise'] * 1.5)
                    return 'raise', raise_amount
                else:
                    # Fold
                    return 'fold', 0
        
        # If we can't check or call, fold (shouldn't happen, but just in case)
        return 'fold', 0
    
    def _evaluate_preflop_hand(self, hole_cards):
        """Evaluate the strength of a preflop hand.
        
        Args:
            hole_cards (list): List of 2 Card objects
            
        Returns:
            float: Hand strength value between 0 and 1
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
    
    def _evaluate_hand_strength(self, hole_cards, community_cards):
        """Evaluate the strength of a hand given the community cards.
        
        Args:
            hole_cards (list): List of 2 Card objects
            community_cards (list): List of community Card objects
            
        Returns:
            float: Hand strength value between 0 and 1
        """
        if not community_cards:
            return self._evaluate_preflop_hand(hole_cards)
        
        # Evaluate current hand
        rank_idx, _, _ = HandEvaluator.evaluate_hand(hole_cards, community_cards)
        
        # Map rank index to a strength value (0 is best, 9 is worst)
        # Invert and normalize to 0-1 scale
        base_strength = (9 - rank_idx) / 9.0
        
        # Adjust based on betting round
        if len(community_cards) == 3:  # Flop
            return base_strength * 0.8  # Still lots of uncertainty
        elif len(community_cards) == 4:  # Turn
            return base_strength * 0.9  # More certainty
        else:  # River
            return base_strength  # Full certainty
        
    def __str__(self):
        return f"{self.name} Agent (Aggression: {self.aggression:.2f})" 