import random
from .card import Card

class Deck:
    """Class representing a standard 52-card deck."""
    
    def __init__(self):
        """Initialize a new, ordered deck of cards."""
        self.cards = []
        self.reset()
    
    def reset(self):
        """Reset the deck to its initial state (ordered, unshuffled)."""
        self.cards = []
        for suit in Card.SUITS:
            for rank in Card.RANKS:
                self.cards.append(Card(rank, suit))
    
    def shuffle(self):
        """Shuffle the deck of cards."""
        random.shuffle(self.cards)
    
    def deal(self, num_cards=1):
        """Deal a specified number of cards from the top of the deck.
        
        Args:
            num_cards (int): Number of cards to deal
            
        Returns:
            list: List of Card objects that were dealt
        """
        if num_cards > len(self.cards):
            raise ValueError(f"Cannot deal {num_cards} cards. Only {len(self.cards)} cards left in the deck.")
        
        dealt_cards = []
        for _ in range(num_cards):
            dealt_cards.append(self.cards.pop(0))
        
        return dealt_cards
    
    def __len__(self):
        return len(self.cards)
    
    def __str__(self):
        return f"Deck with {len(self.cards)} cards remaining" 