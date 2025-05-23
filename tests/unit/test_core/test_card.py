import pytest
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from core.card import Card


class TestCard:
    """Test cases for the Card class."""
    
    def test_card_initialization_valid_inputs(self):
        """Test that cards can be initialized with valid inputs."""
        # Test all valid ranks
        for rank in Card.RANKS:
            for suit in Card.SUITS:
                card = Card(rank, suit)
                assert card.rank == rank
                assert card.suit == suit
                assert card.rank_value == Card.RANKS.index(rank)
    
    def test_card_initialization_with_unicode_suits(self):
        """Test that cards can be initialized with Unicode suit symbols."""
        card_heart = Card('A', '♥')
        assert card_heart.suit == 'h'
        
        card_diamond = Card('K', '♦')
        assert card_diamond.suit == 'd'
        
        card_club = Card('Q', '♣')
        assert card_club.suit == 'c'
        
        card_spade = Card('J', '♠')
        assert card_spade.suit == 's'
    
    def test_card_initialization_invalid_rank(self):
        """Test that invalid ranks raise ValueError."""
        with pytest.raises(ValueError, match="Invalid rank"):
            Card('X', 'h')
        
        with pytest.raises(ValueError, match="Invalid rank"):
            Card('1', 's')
        
        with pytest.raises(ValueError, match="Invalid rank"):
            Card('11', 'd')
    
    def test_card_initialization_invalid_suit(self):
        """Test that invalid suits raise ValueError."""
        with pytest.raises(ValueError, match="Invalid suit"):
            Card('A', 'x')
        
        with pytest.raises(ValueError, match="Invalid suit"):
            Card('K', 'hearts')
        
        with pytest.raises(ValueError, match="Invalid suit"):
            Card('Q', '1')
    
    def test_rank_values(self):
        """Test that rank values are correctly assigned."""
        assert Card('2', 'h').rank_value == 0
        assert Card('3', 's').rank_value == 1
        assert Card('10', 'd').rank_value == 8
        assert Card('J', 'c').rank_value == 9
        assert Card('Q', 'h').rank_value == 10
        assert Card('K', 's').rank_value == 11
        assert Card('A', 'd').rank_value == 12
    
    def test_card_repr(self):
        """Test the __repr__ method."""
        card = Card('A', 's')
        assert repr(card) == 'As'
        
        card = Card('10', 'h')
        assert repr(card) == '10h'
    
    def test_card_str(self):
        """Test the __str__ method returns colored output."""
        card_red = Card('A', 'h')
        str_output = str(card_red)
        # Should contain the rank and Unicode symbol
        assert 'A' in str_output
        assert '♥' in str_output
        
        card_black = Card('K', 's')
        str_output = str(card_black)
        assert 'K' in str_output
        assert '♠' in str_output
    
    def test_card_equality(self):
        """Test card equality comparison."""
        card1 = Card('A', 's')
        card2 = Card('A', 's')
        card3 = Card('A', 'h')
        card4 = Card('K', 's')
        
        # Same rank and suit should be equal
        assert card1 == card2
        
        # Different suit should not be equal
        assert card1 != card3
        
        # Different rank should not be equal
        assert card1 != card4
        
        # Card should not equal non-Card object
        assert card1 != "As"
        assert card1 != None
        assert card1 != 42
    
    def test_card_hash(self):
        """Test that cards can be hashed and used in sets/dicts."""
        card1 = Card('A', 's')
        card2 = Card('A', 's')
        card3 = Card('K', 's')
        
        # Equal cards should have same hash
        assert hash(card1) == hash(card2)
        
        # Cards can be used in sets
        card_set = {card1, card2, card3}
        assert len(card_set) == 2  # card1 and card2 are the same
        
        # Cards can be used as dictionary keys
        card_dict = {card1: 'ace of spades', card3: 'king of spades'}
        assert len(card_dict) == 2
        assert card_dict[card2] == 'ace of spades'  # card2 equals card1
    
    def test_all_suits_constant(self):
        """Test that SUITS constant contains all expected suits."""
        expected_suits = ['h', 'd', 'c', 's']
        assert Card.SUITS == expected_suits
    
    def test_all_ranks_constant(self):
        """Test that RANKS constant contains all expected ranks."""
        expected_ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        assert Card.RANKS == expected_ranks
    
    def test_suit_display_mapping(self):
        """Test that SUIT_DISPLAY mapping is correct."""
        expected_mapping = {
            'h': '♥',
            'd': '♦',
            'c': '♣',
            's': '♠'
        }
        assert Card.SUIT_DISPLAY == expected_mapping
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test lowest and highest cards
        lowest_card = Card('2', 'h')
        highest_card = Card('A', 's')
        
        assert lowest_card.rank_value == 0
        assert highest_card.rank_value == 12
        
        # Test 10 specifically (two-character rank)
        ten_card = Card('10', 'd')
        assert ten_card.rank == '10'
        assert ten_card.rank_value == 8
        assert repr(ten_card) == '10d'
    
    @pytest.mark.parametrize("rank,expected_value", [
        ('2', 0), ('3', 1), ('4', 2), ('5', 3), ('6', 4), ('7', 5),
        ('8', 6), ('9', 7), ('10', 8), ('J', 9), ('Q', 10), ('K', 11), ('A', 12)
    ])
    def test_rank_value_parametrized(self, rank, expected_value):
        """Test rank values using parametrized testing."""
        card = Card(rank, 'h')
        assert card.rank_value == expected_value
    
    @pytest.mark.parametrize("suit_letter,suit_symbol", [
        ('h', '♥'), ('d', '♦'), ('c', '♣'), ('s', '♠')
    ])
    def test_unicode_suit_conversion(self, suit_letter, suit_symbol):
        """Test Unicode suit symbol conversion using parametrized testing."""
        card = Card('A', suit_symbol)
        assert card.suit == suit_letter
