from abc import ABC, abstractmethod
from colorama import Fore, Style

class Player(ABC):
    """Abstract base class for a poker player."""
    
    def __init__(self, name, starting_stack):
        """Initialize a player with a name and starting stack.
        
        Args:
            name (str): The player's name
            starting_stack (int): The player's starting chip stack
        """
        self.name = name
        self.stack = starting_stack
        self.hole_cards = []
        self.is_folded = False
        self.is_all_in = False
        self.current_bet = 0
        
    def reset_for_new_hand(self):
        """Reset the player's state for a new hand."""
        self.hole_cards = []
        self.is_folded = False
        self.is_all_in = False
        self.current_bet = 0
    
    def receive_cards(self, cards):
        """Receive hole cards.
        
        Args:
            cards (list): List of Card objects
        """
        self.hole_cards = cards
    
    def place_bet(self, amount):
        """Place a bet of the specified amount.
        
        Args:
            amount (int): The amount to bet
            
        Returns:
            int: The actual amount bet (might be less if player doesn't have enough chips)
        """
        # Ensure player doesn't bet more than their stack
        amount = min(amount, self.stack)
        self.stack -= amount
        self.current_bet += amount
        
        # Check if player is all-in
        if self.stack == 0:
            self.is_all_in = True
            
        return amount
    
    def fold(self):
        """Fold the current hand."""
        self.is_folded = True
    
    def add_to_stack(self, amount):
        """Add chips to the player's stack.
        
        Args:
            amount (int): Amount of chips to add
        """
        self.stack += amount
    
    @abstractmethod
    def get_action(self, game_state, valid_actions):
        """Get the player's action based on the current game state.
        
        Args:
            game_state (dict): The current state of the game
            valid_actions (list): List of valid actions for the player
            
        Returns:
            tuple: (action, amount)
                action (str): The action to take (e.g., 'fold', 'check', 'call', 'raise')
                amount (int, optional): The amount to bet if action is 'raise'
        """
        pass
    
    def __str__(self):
        return f"{self.name} (${self.stack})"


class HumanPlayer(Player):
    """Class representing a human player."""
    
    def get_action(self, game_state, valid_actions):
        """Get the human player's action from console input.
        
        Args:
            game_state (dict): The current state of the game
            valid_actions (list): List of valid actions for the player
            
        Returns:
            tuple: (action, amount)
                action (str): The action to take (e.g., 'fold', 'check', 'call', 'raise')
                amount (int, optional): The amount to bet if action is 'raise'
        """
        # Display player's hole cards
        print(f"\n{Fore.CYAN}Your hole cards: {' '.join(str(card) for card in self.hole_cards)}{Style.RESET_ALL}")
        
        # Display valid actions
        print(f"\nValid actions:", end=" ")
        for action in valid_actions:
            if action == 'fold':
                print(f"{Fore.RED}fold{Style.RESET_ALL}", end=" ")
            elif action == 'check':
                print(f"{Fore.GREEN}check{Style.RESET_ALL}", end=" ")
            elif action == 'call':
                call_amount = game_state['current_bet'] - self.current_bet
                print(f"{Fore.YELLOW}call (${call_amount}){Style.RESET_ALL}", end=" ")
            elif action == 'raise':
                min_raise = game_state['current_bet'] - self.current_bet + game_state['min_raise']
                print(f"{Fore.MAGENTA}raise (min ${min_raise}){Style.RESET_ALL}", end=" ")
        print()
        
        # Get action from user
        while True:
            action_input = input(f"\nEnter your action: ").strip().lower()
            
            # Handle fold
            if action_input == 'fold' and 'fold' in valid_actions:
                return 'fold', 0
            
            # Handle check
            elif action_input == 'check' and 'check' in valid_actions:
                return 'check', 0
            
            # Handle call
            elif action_input == 'call' and 'call' in valid_actions:
                call_amount = game_state['current_bet'] - self.current_bet
                return 'call', call_amount
            
            # Handle raise
            elif action_input.startswith('raise') and 'raise' in valid_actions:
                try:
                    # Parse the raise amount
                    parts = action_input.split()
                    if len(parts) == 2:
                        amount = int(parts[1])
                        min_raise = game_state['current_bet'] - self.current_bet + game_state['min_raise']
                        max_raise = self.stack
                        
                        if amount < min_raise:
                            print(f"{Fore.RED}Minimum raise is ${min_raise}{Style.RESET_ALL}")
                            continue
                        if amount > max_raise:
                            print(f"{Fore.RED}You can't raise more than your stack (${max_raise}){Style.RESET_ALL}")
                            continue
                            
                        return 'raise', amount
                    else:
                        print(f"{Fore.RED}Please specify an amount (e.g., 'raise 100'){Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}Please enter a valid number{Style.RESET_ALL}")
            
            # Handle all-in as a special case of raise
            elif action_input == 'all-in' and 'raise' in valid_actions:
                return 'raise', self.stack
            
            else:
                print(f"{Fore.RED}Invalid action. Please choose from: {', '.join(valid_actions)}{Style.RESET_ALL}")


class AIPlayer(Player):
    """Base class for AI-controlled players."""
    
    def __init__(self, name, starting_stack, agent=None):
        """Initialize an AI player.
        
        Args:
            name (str): The player's name
            starting_stack (int): The player's starting chip stack
            agent (object, optional): The AI agent that will control this player
        """
        super().__init__(name, starting_stack)
        self.agent = agent
    
    def get_action(self, game_state, valid_actions):
        """Get the AI player's action using its agent.
        
        Args:
            game_state (dict): The current state of the game
            valid_actions (list): List of valid actions for the player
            
        Returns:
            tuple: (action, amount)
                action (str): The action to take (e.g., 'fold', 'check', 'call', 'raise')
                amount (int, optional): The amount to bet if action is 'raise'
        """
        if self.agent:
            action, amount = self.agent.decide_action(game_state, valid_actions, self)
            return action, amount
        else:
            # Default simple AI strategy if no agent is provided
            if 'check' in valid_actions:
                return 'check', 0
            elif 'call' in valid_actions:
                call_amount = game_state['current_bet'] - self.current_bet
                # Call if we have enough stack and it's less than 20% of our stack
                if call_amount <= self.stack * 0.2:
                    return 'call', call_amount
            
            return 'fold', 0 