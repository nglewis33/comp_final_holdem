import pytest
import sys
import os
from unittest.mock import patch

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from core.evaluator import HandEvaluator
from core.card import Card


class TestHandEvaluator:
    """Test class for HandEvaluator."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.evaluator = HandEvaluator()
    
    def test_hand_rankings_order(self):
        """Test that hand rankings are in correct order."""
        expected_order = [
            "Royal Flush", "Straight Flush", "Four of a Kind", "Full House",
            "Flush", "Straight", "Three of a Kind", "Two Pair", "One Pair", "High Card"
        ]
        assert self.evaluator.HAND_RANKINGS == expected_order
    
    def test_royal_flush_spades(self):
        """Test royal flush in spades."""
        hole_cards = [Card('A', '♠'), Card('K', '♠')]
        community_cards = [Card('Q', '♠'), Card('J', '♠'), Card('10', '♠'), Card('2', '♥'), Card('3', '♣')]
        
        result = self.evaluator.evaluate_hand(hole_cards, community_cards)
        
        assert result[1] == "Royal Flush"
        assert result[0] == 0  # Royal flush has rank index 0
        assert len(result[2]) == 5  # best_hand should have 5 cards
        # All cards should be spades and royal ranks
        royal_ranks = {'A', 'K', 'Q', 'J', '10'}
        for card in result[2]:
            assert card.suit == 's'  # Internal representation is 's'
            assert card.rank in royal_ranks
    
    def test_royal_flush_hearts(self):
        """Test royal flush in hearts."""
        hole_cards = [Card('A', '♥'), Card('K', '♥')]
        community_cards = [Card('Q', '♥'), Card('J', '♥'), Card('10', '♥'), Card('2', '♠'), Card('3', '♣')]
        
        result = self.evaluator.evaluate_hand(hole_cards, community_cards)
        
        assert result[1] == "Royal Flush"
        assert result[0] == 0
        assert len(result[2]) == 5
        # All cards should be hearts and royal ranks
        royal_ranks = {'A', 'K', 'Q', 'J', '10'}
        for card in result[2]:
            assert card.suit == 'h'  # Internal representation is 'h'
            assert card.rank in royal_ranks
    
    def test_straight_flush(self):
        """Test straight flush (not royal)."""
        hole_cards = [Card('9', '♠'), Card('8', '♠')]
        community_cards = [Card('7', '♠'), Card('6', '♠'), Card('5', '♠'), Card('A', '♥'), Card('2', '♣')]
        
        result = self.evaluator.evaluate_hand(hole_cards, community_cards)
        
        assert result[1] == "Straight Flush"
        assert result[0] == 1  # Straight flush has rank index 1
        assert len(result[2]) == 5
        # All cards should be spades
        for card in result[2]:
            assert card.suit == 's'  # Internal representation is 's'
    
    def test_four_of_a_kind(self):
        """Test four of a kind."""
        hole_cards = [Card('A', '♠'), Card('A', '♥')]
        community_cards = [Card('A', '♣'), Card('A', '♦'), Card('K', '♠'), Card('Q', '♥'), Card('J', '♣')]
        
        result = self.evaluator.evaluate_hand(hole_cards, community_cards)
        
        assert result[1] == "Four of a Kind"
        assert result[0] == 2  # Four of a kind has rank index 2
        assert len(result[2]) == 5
        # Should have 4 Aces
        aces = [card for card in result[2] if card.rank == 'A']
        assert len(aces) == 4
    
    def test_full_house(self):
        """Test full house."""
        hole_cards = [Card('A', '♠'), Card('A', '♥')]
        community_cards = [Card('A', '♣'), Card('K', '♦'), Card('K', '♠'), Card('Q', '♥'), Card('J', '♣')]
        
        result = self.evaluator.evaluate_hand(hole_cards, community_cards)
        
        assert result[1] == "Full House"
        assert result[0] == 3  # Full house has rank index 3
        assert len(result[2]) == 5
        # Should have 3 Aces and 2 Kings
        aces = [card for card in result[2] if card.rank == 'A']
        kings = [card for card in result[2] if card.rank == 'K']
        assert len(aces) == 3
        assert len(kings) == 2
    
    def test_flush(self):
        """Test flush."""
        hole_cards = [Card('A', '♠'), Card('K', '♠')]
        community_cards = [Card('Q', '♠'), Card('J', '♠'), Card('9', '♠'), Card('8', '♥'), Card('7', '♣')]
        
        result = self.evaluator.evaluate_hand(hole_cards, community_cards)
        
        assert result[1] == "Flush"
        assert result[0] == 4  # Flush has rank index 4
        assert len(result[2]) == 5
        # All cards should be spades
        for card in result[2]:
            assert card.suit == 's'  # Internal representation is 's'
    
    def test_straight(self):
        """Test straight."""
        hole_cards = [Card('A', '♠'), Card('K', '♥')]
        community_cards = [Card('Q', '♣'), Card('J', '♦'), Card('10', '♠'), Card('9', '♥'), Card('8', '♣')]
        
        result = self.evaluator.evaluate_hand(hole_cards, community_cards)
        
        assert result[1] == "Straight"
        assert result[0] == 5  # Straight has rank index 5
        assert len(result[2]) == 5
        # Should be A-K-Q-J-10 straight
        ranks = sorted([card.rank_value for card in result[2]], reverse=True)
        expected_ranks = [12, 11, 10, 9, 8]  # A, K, Q, J, 10
        assert ranks == expected_ranks
    
    def test_straight_ace_low(self):
        """Test ace-low straight (A-2-3-4-5)."""
        hole_cards = [Card('A', '♠'), Card('2', '♥')]
        community_cards = [Card('3', '♣'), Card('4', '♦'), Card('5', '♠'), Card('K', '♥'), Card('Q', '♣')]
        
        result = self.evaluator.evaluate_hand(hole_cards, community_cards)
        
        assert result[1] == "Straight"
        assert result[0] == 5  # Straight has rank index 5
        assert len(result[2]) == 5
    
    def test_three_of_a_kind(self):
        """Test three of a kind."""
        hole_cards = [Card('A', '♠'), Card('A', '♥')]
        community_cards = [Card('A', '♣'), Card('K', '♦'), Card('Q', '♠'), Card('7', '♥'), Card('3', '♣')]
        
        result = self.evaluator.evaluate_hand(hole_cards, community_cards)
        
        assert result[1] == "Three of a Kind"
        assert result[0] == 6  # Three of a kind has rank index 6
        assert len(result[2]) == 5
        # Should have 3 Aces
        aces = [card for card in result[2] if card.rank == 'A']
        assert len(aces) == 3
    
    def test_two_pair(self):
        """Test two pair."""
        hole_cards = [Card('A', '♠'), Card('A', '♥')]
        community_cards = [Card('K', '♣'), Card('K', '♦'), Card('Q', '♠'), Card('7', '♥'), Card('3', '♣')]
        
        result = self.evaluator.evaluate_hand(hole_cards, community_cards)
        
        assert result[1] == "Two Pair"
        assert result[0] == 7  # Two pair has rank index 7
        assert len(result[2]) == 5
        # Should have 2 Aces and 2 Kings
        aces = [card for card in result[2] if card.rank == 'A']
        kings = [card for card in result[2] if card.rank == 'K']
        assert len(aces) == 2
        assert len(kings) == 2
    
    def test_one_pair(self):
        """Test one pair."""
        hole_cards = [Card('A', '♠'), Card('A', '♥')]
        community_cards = [Card('K', '♣'), Card('Q', '♦'), Card('J', '♠'), Card('9', '♥'), Card('7', '♣')]
        
        result = self.evaluator.evaluate_hand(hole_cards, community_cards)
        
        assert result[1] == "One Pair"
        assert result[0] == 8  # One pair has rank index 8
        assert len(result[2]) == 5
        # Should have 2 Aces
        aces = [card for card in result[2] if card.rank == 'A']
        assert len(aces) == 2
    
    def test_high_card(self):
        """Test high card."""
        hole_cards = [Card('A', '♠'), Card('K', '♥')]
        community_cards = [Card('Q', '♣'), Card('J', '♦'), Card('9', '♠'), Card('7', '♥'), Card('5', '♣')]
        
        result = self.evaluator.evaluate_hand(hole_cards, community_cards)
        
        assert result[1] == "High Card"
        assert result[0] == 9  # High card has rank index 9
        assert len(result[2]) == 5
        # Highest card should be Ace
        highest_card = max(result[2], key=lambda c: c.rank_value)
        assert highest_card.rank == 'A'
    
    def test_evaluate_with_seven_cards(self):
        """Test evaluation with exactly 7 cards (2 hole + 5 community)."""
        hole_cards = [Card('A', '♠'), Card('K', '♥')]
        community_cards = [Card('Q', '♣'), Card('J', '♦'), Card('10', '♠'), Card('9', '♥'), Card('8', '♣')]
        
        result = self.evaluator.evaluate_hand(hole_cards, community_cards)
        
        # Should find the best 5-card hand
        assert len(result[2]) == 5
        assert result[1] == "Straight"  # A-K-Q-J-10 straight
    
    def test_evaluate_with_fewer_than_five_cards(self):
        """Test evaluation with fewer than 5 total cards."""
        hole_cards = [Card('A', '♠'), Card('K', '♥')]
        community_cards = [Card('Q', '♣')]  # Only 3 total cards
        
        result = self.evaluator.evaluate_hand(hole_cards, community_cards)
        
        # Should still return a result with available cards
        assert len(result[2]) == 3
        assert result[1] == "High Card"
    
    def test_tiebreaker_same_hand_type(self):
        """Test tiebreaker logic for same hand types."""
        # Two pairs with different high pairs
        hole_cards1 = [Card('A', '♠'), Card('A', '♥')]
        community_cards = [Card('K', '♣'), Card('K', '♦'), Card('Q', '♠'), Card('7', '♥'), Card('3', '♣')]
        
        hole_cards2 = [Card('J', '♠'), Card('J', '♥')]
        # Same community cards
        
        result1 = self.evaluator.evaluate_hand(hole_cards1, community_cards)
        result2 = self.evaluator.evaluate_hand(hole_cards2, community_cards)
        
        # Both should be two pair, but result1 should have higher tiebreaker
        assert result1[1] == "Two Pair"
        assert result2[1] == "Two Pair"
        assert result1[3] > result2[3]  # Higher tiebreaker for A-A vs J-J
    
    def test_flush_with_more_than_five_suited_cards(self):
        """Test flush when more than 5 cards of same suit are available."""
        hole_cards = [Card('A', '♠'), Card('K', '♠')]
        community_cards = [Card('Q', '♠'), Card('J', '♠'), Card('10', '♠'), Card('9', '♠'), Card('8', '♠')]
        
        result = self.evaluator.evaluate_hand(hole_cards, community_cards)
        
        # Should be straight flush (or royal flush)
        assert result[1] in ["Straight Flush", "Royal Flush"]
        assert len(result[2]) == 5
        # All cards should be spades
        for card in result[2]:
            assert card.suit == 's'  # Internal representation is 's'
    
    def test_empty_hole_cards(self):
        """Test evaluation with empty hole cards."""
        hole_cards = []
        community_cards = [Card('A', '♠'), Card('K', '♥'), Card('Q', '♣'), Card('J', '♦'), Card('10', '♠')]
        
        result = self.evaluator.evaluate_hand(hole_cards, community_cards)
        
        # Should still evaluate the community cards
        assert len(result[2]) == 5
        assert result[1] == "Straight"
    
    def test_empty_community_cards(self):
        """Test evaluation with empty community cards."""
        hole_cards = [Card('A', '♠'), Card('K', '♥')]
        community_cards = []
        
        result = self.evaluator.evaluate_hand(hole_cards, community_cards)
        
        # Should evaluate just the hole cards
        assert len(result[2]) == 2
        assert result[1] == "High Card"
    
    def test_duplicate_cards_handling(self):
        """Test that duplicate cards are handled properly."""
        hole_cards = [Card('A', '♠'), Card('K', '♥')]
        community_cards = [Card('Q', '♣'), Card('J', '♦'), Card('10', '♠'), Card('9', '♥'), Card('8', '♣')]
        
        result = self.evaluator.evaluate_hand(hole_cards, community_cards)
        
        # Should find the best hand without issues
        assert len(result[2]) == 5
        assert result[1] == "Straight"
    
    @pytest.mark.parametrize("suit", ['♠', '♥', '♦', '♣'])
    def test_royal_flush_all_suits(self, suit):
        """Test royal flush in all suits."""
        hole_cards = [Card('A', suit), Card('K', suit)]
        community_cards = [Card('Q', suit), Card('J', suit), Card('10', suit), Card('2', '♥'), Card('3', '♣')]
        
        result = self.evaluator.evaluate_hand(hole_cards, community_cards)
        
        assert result[1] == "Royal Flush"
        assert result[0] == 0
        assert len(result[2]) == 5
        # All cards should be of the same suit (convert to internal representation)
        suit_map = {'♠': 's', '♥': 'h', '♦': 'd', '♣': 'c'}
        expected_suit = suit_map[suit]
        for card in result[2]:
            assert card.suit == expected_suit
    
    @pytest.mark.parametrize("rank", ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2'])
    def test_four_of_a_kind_all_ranks(self, rank):
        """Test four of a kind with all possible ranks."""
        hole_cards = [Card(rank, '♠'), Card(rank, '♥')]
        community_cards = [Card(rank, '♣'), Card(rank, '♦'), Card('A', '♠'), Card('K', '♥'), Card('Q', '♣')]
        
        result = self.evaluator.evaluate_hand(hole_cards, community_cards)
        
        assert result[1] == "Four of a Kind"
        assert result[0] == 2  # Four of a kind has rank index 2
        assert len(result[2]) == 5
        # Should have 4 cards of the specified rank
        matching_cards = [card for card in result[2] if card.rank == rank]
        assert len(matching_cards) == 4
    
    def test_result_structure(self):
        """Test that the result has the expected structure."""
        hole_cards = [Card('A', '♠'), Card('K', '♥')]
        community_cards = [Card('Q', '♣'), Card('J', '♦'), Card('10', '♠'), Card('9', '♥'), Card('8', '♣')]
        
        result = self.evaluator.evaluate_hand(hole_cards, community_cards)
        
        # Check tuple structure: (rank_idx, name, cards, tiebreakers)
        assert isinstance(result, tuple)
        assert len(result) == 4
        assert isinstance(result[0], int)  # rank index
        assert isinstance(result[1], str)  # hand name
        assert isinstance(result[2], list)  # best hand cards
        assert isinstance(result[3], list)  # tiebreakers
        
        # Check that hand name is valid
        assert result[1] in self.evaluator.HAND_RANKINGS
        
        # Check that rank index matches hand name
        assert self.evaluator.HAND_RANKINGS[result[0]] == result[1]
    
    def test_tiebreaker_consistency(self):
        """Test that tiebreaker values are consistent."""
        # Same hand should produce same tiebreaker
        hole_cards = [Card('A', '♠'), Card('K', '♥')]
        community_cards = [Card('Q', '♣'), Card('J', '♦'), Card('10', '♠'), Card('9', '♥'), Card('8', '♣')]
        
        result1 = self.evaluator.evaluate_hand(hole_cards, community_cards)
        result2 = self.evaluator.evaluate_hand(hole_cards, community_cards)
        
        assert result1[3] == result2[3]  # Tiebreakers should be identical
