from colorama import Fore, Style

class Card:
    """Class representing a standard playing card."""
    
    # Replace Unicode symbols with simple letters
    SUITS = ['h', 'd', 'c', 's']  # hearts, diamonds, clubs, spades
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    # Mapping for display purposes
    SUIT_DISPLAY = {
        'h': '♥',
        'd': '♦',
        'c': '♣',
        's': '♠'
    }
    
    def __init__(self, rank, suit):
        """Initialize a card with a rank and suit.
        
        Args:
            rank (str): The rank of the card, e.g., '2', 'J', 'A'
            suit (str): The suit of the card, either letter (s, h, d, c) or Unicode symbol
        """
        if rank not in self.RANKS:
            raise ValueError(f"Invalid rank: {rank}")
            
        # Convert Unicode symbols to simple letters if needed
        if suit in self.SUIT_DISPLAY.values():
            for letter, symbol in self.SUIT_DISPLAY.items():
                if symbol == suit:
                    suit = letter
                    break
                    
        if suit not in self.SUITS:
            raise ValueError(f"Invalid suit: {suit}")
        
        self.rank = rank
        self.suit = suit
        self.rank_value = self.RANKS.index(rank)
    
    def __repr__(self):
        return f"{self.rank}{self.suit}"
    
    def __str__(self):
        # For colored display in terminal, still use Unicode symbols but store as letters
        symbol = self.SUIT_DISPLAY[self.suit]
        color = Fore.RED if self.suit in ['h', 'd'] else Fore.WHITE
        return f"{color}{self.rank}{symbol}{Style.RESET_ALL}"
    
    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit
    
    def __hash__(self):
        return hash((self.rank, self.suit)) 