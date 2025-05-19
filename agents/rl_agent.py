import random
import numpy as np
from .base_agent import BaseAgent
from texas_holdem.evaluator import HandEvaluator

class RLAgent(BaseAgent):
    """A reinforcement learning agent for poker using the Bellman equation."""
    
    def __init__(self, name, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.2):
        """Initialize the RL agent.
        
        Args:
            name (str): The name of the agent
            learning_rate (float): Learning rate for Q-learning
            discount_factor (float): Discount factor for future rewards
            exploration_rate (float): Epsilon for exploration vs. exploitation
        """
        super().__init__(name)
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        
        # Q-values: state-action value function
        # Format: {state_key: {action: value}}
        self.q_values = {}
        
        # Cache of recently observed states and actions
        self.state_history = []
        self.action_history = []
        self.reward_history = []
    
    def decide_action(self, game_state, valid_actions, player):
        """Decide on an action based on the current game state using the Q-learning algorithm.
        
        Args:
            game_state (dict): The current state of the game
            valid_actions (list): List of valid actions for the player
            player (Player): The player object controlled by this agent
            
        Returns:
            tuple: (action, amount)
                action (str): The action to take (e.g., 'fold', 'check', 'call', 'raise')
                amount (int, optional): The amount to bet if action is 'raise'
        """
        # Convert the game state to a simplified state representation
        state_key = self._get_state_key(game_state, player)
        
        # Initialize Q-values for this state if not seen before
        if state_key not in self.q_values:
            self.q_values[state_key] = {action: 0.0 for action in ['fold', 'check', 'call', 'raise']}
        
        # Ensure Q-values only exist for valid actions
        q_values = {action: self.q_values[state_key].get(action, 0.0) for action in valid_actions}
        
        # Epsilon-greedy action selection
        if random.random() < self.exploration_rate:
            # Explore: choose a random action
            action = random.choice(valid_actions)
        else:
            # Exploit: choose the best action according to Q-values
            if q_values:
                action = max(q_values, key=q_values.get)
            else:
                # Fallback if no valid actions have Q-values
                action = random.choice(valid_actions)
        
        # Determine bet amount if action is 'raise'
        amount = 0
        if action == 'raise':
            # Use Q-value to determine raise amount
            # Normalize to range [0, 1]
            q_val = q_values.get(action, 0.0)
            normalized_q = max(0, min(1, (q_val + 1) / 2))  # Convert from [-1, 1] to [0, 1]
            
            # Calculate raise between min_raise and all-in based on Q-value
            min_raise = game_state['min_raise']
            max_raise = player.stack
            
            # Use the Q-value to scale between min and max raise
            amount = int(min_raise + normalized_q * (max_raise - min_raise))
            amount = max(min_raise, min(amount, max_raise))
        
        # Store the state and action for learning
        self.state_history.append(state_key)
        self.action_history.append((action, amount))
        
        return action, amount
    
    def update_q_values(self, reward):
        """Update Q-values based on the observed reward using the Bellman equation.
        
        Args:
            reward (float): The reward received after taking the action
        """
        if not self.state_history:
            return
        
        # Store the reward
        self.reward_history.append(reward)
        
        # If we have enough history, update Q-values
        if len(self.state_history) >= 2:
            # Get the most recent state and action
            state = self.state_history[-2]
            action, _ = self.action_history[-2]
            next_state = self.state_history[-1]
            
            # Initialize if needed
            if state not in self.q_values:
                self.q_values[state] = {a: 0.0 for a in ['fold', 'check', 'call', 'raise']}
            if next_state not in self.q_values:
                self.q_values[next_state] = {a: 0.0 for a in ['fold', 'check', 'call', 'raise']}
            
            # Get the maximum Q-value for the next state
            max_next_q = max(self.q_values[next_state].values()) if self.q_values[next_state] else 0
            
            # Bellman equation: Q(s,a) = Q(s,a) + α * [r + γ * max(Q(s',a')) - Q(s,a)]
            current_q = self.q_values[state].get(action, 0.0)
            new_q = current_q + self.learning_rate * (
                reward + self.discount_factor * max_next_q - current_q
            )
            
            # Update the Q-value
            self.q_values[state][action] = new_q
    
    def reset_episode(self):
        """Reset the agent's state for a new episode."""
        self.state_history = []
        self.action_history = []
        self.reward_history = []
    
    def _get_state_key(self, game_state, player):
        """Create a simplified state representation for Q-learning.
        
        Args:
            game_state (dict): The current game state
            player (Player): The player object
            
        Returns:
            str: A string key representing the simplified state
        """
        # Extract relevant features from the game state
        # These features should balance between being informative and maintaining a manageable state space
        
        # 1. Hand strength
        if game_state['community_cards']:
            rank_idx, _, _ = HandEvaluator.evaluate_hand(player.hole_cards, game_state['community_cards'])
            hand_strength = (9 - rank_idx) / 9.0  # Normalize to [0, 1]
        else:
            # Preflop hand evaluation
            hand_strength = self._evaluate_preflop(player.hole_cards)
        
        # 2. Game phase
        phase = game_state['phase']
        
        # 3. Pot odds
        to_call = game_state['current_bet'] - player.current_bet
        pot_odds = min(1.0, to_call / (game_state['pot'] + to_call)) if to_call > 0 else 0.0
        
        # 4. Stack-to-pot ratio
        spr = min(5.0, player.stack / max(1, game_state['pot'])) / 5.0  # Normalize to [0, 1]
        
        # 5. Position (simplified)
        num_players = len(game_state['players'])
        position = ((game_state['current_idx'] - game_state['dealer_idx']) % num_players) / num_players
        
        # Discretize continuous values to limit state space
        hand_str_bin = int(hand_strength * 5)  # 0-4
        pot_odds_bin = int(pot_odds * 5)       # 0-4
        spr_bin = int(spr * 5)                 # 0-4
        position_bin = int(position * 3)       # 0-2
        
        # Create a state key
        return f"{phase}_{hand_str_bin}_{pot_odds_bin}_{spr_bin}_{position_bin}"
    
    def _evaluate_preflop(self, hole_cards):
        """Evaluate preflop hand strength.
        
        Args:
            hole_cards (list): List of 2 Card objects
            
        Returns:
            float: Hand strength value between 0 and 1
        """
        # Simple preflop evaluation
        rank_values = [card.rank_value for card in hole_cards]
        
        # Check for pocket pair
        if hole_cards[0].rank == hole_cards[1].rank:
            # Scale based on rank (higher pairs are better)
            return 0.5 + (hole_cards[0].rank_value / 24.0)
        
        # High card value
        high_card = max(rank_values) / 12.0
        
        # Suited bonus
        suited_bonus = 0.1 if hole_cards[0].suit == hole_cards[1].suit else 0
        
        # Connectivity bonus (closer ranks are better)
        gap = abs(rank_values[0] - rank_values[1])
        gap_penalty = max(0, 0.1 - 0.02 * gap)
        
        # Combine factors
        return min(0.9, 0.2 + high_card * 0.3 + suited_bonus + gap_penalty)
    
    def save_model(self, filepath):
        """Save the Q-values to a file.
        
        Args:
            filepath (str): Path to save the model
        """
        np.save(filepath, self.q_values)
        
    def load_model(self, filepath):
        """Load the Q-values from a file.
        
        Args:
            filepath (str): Path to load the model from
        """
        try:
            self.q_values = np.load(filepath, allow_pickle=True).item()
        except (FileNotFoundError, IOError):
            print(f"Could not load model from {filepath}")
    
    def __str__(self):
        return f"{self.name} RL Agent (LR={self.learning_rate}, DF={self.discount_factor}, ε={self.exploration_rate})" 