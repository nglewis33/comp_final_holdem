from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Abstract base class for poker agents."""
    
    def __init__(self, name):
        """Initialize the agent.
        
        Args:
            name (str): The name of the agent
        """
        self.name = name
    
    @abstractmethod
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
        pass
    
    def __str__(self):
        return f"{self.name} Agent" 