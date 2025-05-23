import pytest
import sys
import os
from unittest.mock import patch

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from core.deck import Deck
from core.card import Card


class TestDeck:
    """Test cases for the Deck class."""
    
    def test_deck_initialization(self):
        """Test that a deck is properly initialized."""
        deck = Deck()
        
        # Should have 52 cards
        assert len(deck) == 52
        assert len(deck.cards) == 52
        
        # Should contain all combinations of ranks and suits
        expected_cards = []
        for suit in Card.SUITS:
            for rank in Card.RANKS:
                expected_cards.append(Card(rank, suit))
        
        # Check that all expected cards are present
        for expected_card in expected_cards:
            found = False
            for deck_card in deck.cards:
                if deck_card.rank == expected_card.rank and deck_card.suit == expected_card.suit:
                    found = True
                    break
            assert found, f"Card {expected_card.rank}{expected_card.suit} not found in deck"
    
    def test_deck_reset(self):
        """Test that deck reset works properly."""
        deck = Deck()
        
        # Deal some cards
        deck.deal(5)
        assert len(deck) == 47
        
        # Reset the deck
        deck.reset()
        assert len(deck) == 52
        
        # Should contain all cards again
        ranks_found = set()
        suits_found = set()
        for card in deck.cards:
            ranks_found.add(card.rank)
            suits_found.add(card.suit)
        
        assert ranks_found == set(Card.RANKS)
        assert suits_found == set(Card.SUITS)
    
    def test_deck_shuffle(self):
        """Test that deck shuffle changes card order."""
        deck1 = Deck()
        deck2 = Deck()
        
        # Get initial order
        initial_order = [repr(card) for card in deck1.cards]
        
        # Shuffle one deck
        deck1.shuffle()
        shuffled_order = [repr(card) for card in deck1.cards]
        
        # Orders should be different (with very high probability)
        # Note: There's a tiny chance they could be the same, but it's negligible
        assert shuffled_order != initial_order
        
        # Both decks should still have the same cards, just in different order
        assert sorted(shuffled_order) == sorted([repr(card) for card in deck2.cards])
    
    @patch('random.shuffle')
    def test_deck_shuffle_calls_random_shuffle(self, mock_shuffle):
        """Test that shuffle method calls random.shuffle."""
        deck = Deck()
        deck.shuffle()
        
        # Verify that random.shuffle was called once with the deck's cards
        mock_shuffle.assert_called_once_with(deck.cards)
    
    def test_deal_single_card(self):
        """Test dealing a single card."""
        deck = Deck()
        initial_length = len(deck)
        
        # Deal one card (default)
        cards = deck.deal()
        
        assert len(cards) == 1
        assert isinstance(cards[0], Card)
        assert len(deck) == initial_length - 1
        
        # The dealt card should no longer be in the deck
        assert cards[0] not in deck.cards
    
    def test_deal_multiple_cards(self):
        """Test dealing multiple cards."""
        deck = Deck()
        initial_length = len(deck)
        num_to_deal = 5
        
        cards = deck.deal(num_to_deal)
        
        assert len(cards) == num_to_deal
        assert len(deck) == initial_length - num_to_deal
        
        # All dealt cards should be Card instances
        for card in cards:
            assert isinstance(card, Card)
        
        # No dealt cards should remain in the deck
        for card in cards:
            assert card not in deck.cards
        
        # All dealt cards should be unique
        assert len(set(repr(card) for card in cards)) == num_to_deal
    
    def test_deal_all_cards(self):
        """Test dealing all cards from the deck."""
        deck = Deck()
        
        cards = deck.deal(52)
        
        assert len(cards) == 52
        assert len(deck) == 0
        assert deck.cards == []
    
    def test_deal_too_many_cards(self):
        """Test that dealing more cards than available raises ValueError."""
        deck = Deck()
        
        # Try to deal more cards than in the deck
        with pytest.raises(ValueError, match="Cannot deal 53 cards. Only 52 cards left in the deck."):
            deck.deal(53)
        
        # Deal some cards first, then try to deal too many
        deck.deal(10)
        with pytest.raises(ValueError, match="Cannot deal 50 cards. Only 42 cards left in the deck."):
            deck.deal(50)
    
    def test_deal_zero_cards(self):
        """Test dealing zero cards."""
        deck = Deck()
        initial_length = len(deck)
        
        cards = deck.deal(0)
        
        assert len(cards) == 0
        assert len(deck) == initial_length
    
    def test_deal_negative_cards(self):
        """Test dealing negative number of cards."""
        deck = Deck()
        
        # The current implementation doesn't validate negative numbers
        # range(-1) produces an empty range, so it should return an empty list
        cards = deck.deal(-1)
        
        assert len(cards) == 0
        assert len(deck) == 52  # Deck should be unchanged
    
    def test_deck_length_operator(self):
        """Test the __len__ operator."""
        deck = Deck()
        
        assert len(deck) == 52
        
        deck.deal(1)
        assert len(deck) == 51
        
        deck.deal(10)
        assert len(deck) == 41
        
        deck.reset()
        assert len(deck) == 52
    
    def test_deck_string_representation(self):
        """Test the __str__ method."""
        deck = Deck()
        
        str_repr = str(deck)
        assert "52 cards remaining" in str_repr
        
        deck.deal(5)
        str_repr = str(deck)
        assert "47 cards remaining" in str_repr
        
        deck.deal(47)
        str_repr = str(deck)
        assert "0 cards remaining" in str_repr
    
    def test_deck_order_after_reset(self):
        """Test that deck has consistent order after reset."""
        deck1 = Deck()
        deck2 = Deck()
        
        # Both decks should have the same initial order
        order1 = [repr(card) for card in deck1.cards]
        order2 = [repr(card) for card in deck2.cards]
        assert order1 == order2
        
        # After dealing and resetting, order should be the same
        deck1.deal(10)
        deck1.reset()
        order1_after_reset = [repr(card) for card in deck1.cards]
        assert order1_after_reset == order2
    
    def test_deck_contains_no_duplicates(self):
        """Test that deck contains no duplicate cards."""
        deck = Deck()
        
        card_representations = [repr(card) for card in deck.cards]
        unique_cards = set(card_representations)
        
        # Should have 52 unique cards
        assert len(unique_cards) == 52
        assert len(card_representations) == 52
    
    def test_deck_contains_all_suits_and_ranks(self):
        """Test that deck contains all suits and ranks."""
        deck = Deck()
        
        ranks_in_deck = set()
        suits_in_deck = set()
        
        for card in deck.cards:
            ranks_in_deck.add(card.rank)
            suits_in_deck.add(card.suit)
        
        assert ranks_in_deck == set(Card.RANKS)
        assert suits_in_deck == set(Card.SUITS)
        
        # Each rank should appear exactly 4 times (once per suit)
        rank_counts = {}
        for card in deck.cards:
            rank_counts[card.rank] = rank_counts.get(card.rank, 0) + 1
        
        for rank in Card.RANKS:
            assert rank_counts[rank] == 4
        
        # Each suit should appear exactly 13 times (once per rank)
        suit_counts = {}
        for card in deck.cards:
            suit_counts[card.suit] = suit_counts.get(card.suit, 0) + 1
        
        for suit in Card.SUITS:
            assert suit_counts[suit] == 13
    
    def test_deal_from_top_of_deck(self):
        """Test that cards are dealt from the top (beginning) of the deck."""
        deck = Deck()
        
        # Get the first few cards
        expected_first_card = deck.cards[0]
        expected_second_card = deck.cards[1]
        
        # Deal one card
        dealt_cards = deck.deal(1)
        assert dealt_cards[0].rank == expected_first_card.rank
        assert dealt_cards[0].suit == expected_first_card.suit
        
        # Deal another card
        dealt_cards = deck.deal(1)
        assert dealt_cards[0].rank == expected_second_card.rank
        assert dealt_cards[0].suit == expected_second_card.suit
    
    def test_multiple_deck_independence(self):
        """Test that multiple deck instances are independent."""
        deck1 = Deck()
        deck2 = Deck()
        
        # Deal from one deck
        deck1.deal(5)
        
        # Other deck should be unaffected
        assert len(deck1) == 47
        assert len(deck2) == 52
        
        # Shuffle one deck
        deck1.shuffle()
        
        # Other deck should maintain original order
        original_order = []
        for suit in Card.SUITS:
            for rank in Card.RANKS:
                original_order.append(f"{rank}{suit}")
        
        deck2_order = [repr(card) for card in deck2.cards]
        assert deck2_order == original_order
    
    @pytest.mark.parametrize("num_cards", [1, 5, 10, 26, 51, 52])
    def test_deal_various_amounts(self, num_cards):
        """Test dealing various amounts of cards."""
        deck = Deck()
        initial_length = len(deck)
        
        cards = deck.deal(num_cards)
        
        assert len(cards) == num_cards
        assert len(deck) == initial_length - num_cards
        
        # All cards should be unique
        card_reprs = [repr(card) for card in cards]
        assert len(set(card_reprs)) == num_cards
