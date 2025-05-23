#!/usr/bin/env python3

import sys
import os
import unittest
from colorama import init, Fore, Style

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.card import Card
from core.evaluator import HandEvaluator
from core.player import AIPlayer
from core.game import TexasHoldemGame
from agents.simple_agent import SimpleAgent


class TestResult:
    """Class to store test results."""
    def __init__(self, name, passed, message=""):
        self.name = name
        self.passed = passed
        self.message = message

    def __str__(self):
        status = f"{Fore.GREEN}PASSED{Style.RESET_ALL}" if self.passed else f"{Fore.RED}FAILED{Style.RESET_ALL}"
        return f"{self.name}: {status} {self.message}"


class PokerHandTester:
    """Class to test poker hand evaluations."""

    # Lowercase suits
    SUITS = {'s': 's', 'h': 'h', 'd': 'd', 'c': 'c'}

    def __init__(self):
        """Initialize the tester."""
        init()  # Initialize colorama
        self.results = []

    def run_all_tests(self):
        """Run all tests and return results."""
        # Run specific problematic tests first with debug info
        self.debug_straight_flush()
        self.debug_two_pair()
        
        # Test all hand types against lower hands
        self.test_royal_flush_vs_straight_flush()
        self.test_straight_flush_vs_four_of_a_kind()
        self.test_four_of_a_kind_vs_full_house()
        self.test_full_house_vs_flush()
        self.test_flush_vs_straight()
        self.test_straight_vs_three_of_a_kind()
        self.test_three_of_a_kind_vs_two_pair()
        self.test_two_pair_vs_pair()
        self.test_pair_vs_high_card()

        # Test tiebreakers within same hand type
        self.test_royal_flush_tiebreaker()  # Should always tie
        self.test_straight_flush_tiebreaker()
        self.test_four_of_a_kind_tiebreaker()
        self.test_full_house_tiebreaker()
        self.test_flush_tiebreaker()
        self.test_straight_tiebreaker()
        self.test_three_of_a_kind_tiebreaker()
        self.test_two_pair_tiebreaker()
        self.test_pair_tiebreaker()
        self.test_high_card_tiebreaker()

        # Display results
        return self.results
        
    def debug_straight_flush(self):
        """Debug the straight flush test."""
        print(f"\n{Fore.CYAN}=== DEBUGGING STRAIGHT FLUSH VS FOUR OF A KIND ==={Style.RESET_ALL}")
        
        # Create test cards
        player1_hole = self.create_cards(['9 s', '8 s'])
        player2_hole = self.create_cards(['a h', 'a d'])
        community = self.create_cards(['7 s', '6 s', '5 s', 'a s', 'a c'])
        
        # Print card values
        print(f"Player 1 hole cards: {[f'{c.rank}{c.suit}({c.rank_value})' for c in player1_hole]}")
        print(f"Player 2 hole cards: {[f'{c.rank}{c.suit}({c.rank_value})' for c in player2_hole]}")
        print(f"Community cards: {[f'{c.rank}{c.suit}({c.rank_value})' for c in community]}")
        
        # Check flush
        all_cards = player1_hole + community
        flush_cards = HandEvaluator._get_flush_cards(all_cards)
        print(f"\nCheck flush for player 1: {flush_cards is not None}")
        if flush_cards:
            print(f"Flush cards: {[f'{c.rank}{c.suit}({c.rank_value})' for c in flush_cards]}")
            
            # Check straight flush
            straight_flush = HandEvaluator._get_straight_cards(flush_cards)
            print(f"Check straight flush: {straight_flush is not None}")
            if straight_flush:
                print(f"Straight flush cards: {[f'{c.rank}{c.suit}({c.rank_value})' for c in straight_flush]}")
            
            # Check if cards are consecutive
            if len(flush_cards) >= 5:
                for i in range(len(flush_cards) - 1):
                    print(f"Gap between {flush_cards[i].rank}{flush_cards[i].suit}({flush_cards[i].rank_value}) and {flush_cards[i+1].rank}{flush_cards[i+1].suit}({flush_cards[i+1].rank_value}): {flush_cards[i].rank_value - flush_cards[i+1].rank_value}")
        
        # Create a manually constructed straight flush
        print("\nCreating a manually constructed straight flush:")
        straight_flush_cards = [
            Card('9', 's'),  # rank_value 7
            Card('8', 's'),  # rank_value 6
            Card('7', 's'),  # rank_value 5
            Card('6', 's'),  # rank_value 4
            Card('5', 's')   # rank_value 3
        ]
        
        # Verify it's a straight flush
        print(f"Straight cards: {HandEvaluator._get_straight_cards(straight_flush_cards) is not None}")
        print(f"Flush cards: {HandEvaluator._get_flush_cards(straight_flush_cards) is not None}")
        
        # Evaluate full hands for both players
        hand1 = HandEvaluator.evaluate_hand(player1_hole, community)
        hand2 = HandEvaluator.evaluate_hand(player2_hole, community)
        
        print(f"\nPlayer 1's evaluated hand: {hand1[1]} with tiebreakers {hand1[3]}")
        print(f"Player 1's best hand: {', '.join([f'{c.rank}{c.suit}' for c in hand1[2]])}")
        
        print(f"Player 2's evaluated hand: {hand2[1]} with tiebreakers {hand2[3]}")  
        print(f"Player 2's best hand: {', '.join([f'{c.rank}{c.suit}' for c in hand2[2]])}")
        
        # Compare the hands
        comparison = HandEvaluator.compare_hands(hand1, hand2)
        winner = "Player 1" if comparison > 0 else "Player 2" if comparison < 0 else "Tie"
        print(f"\nWinner: {winner}")
    
    def debug_two_pair(self):
        """Debug the two pair test."""
        print(f"\n{Fore.CYAN}=== DEBUGGING TWO PAIR TIEBREAKER ==={Style.RESET_ALL}")
        
        # Create test cards
        player1_hole = self.create_cards(['a h', 'a s'])
        player2_hole = self.create_cards(['k h', 'k s'])
        community = self.create_cards(['k d', 'k c', '2 s', 'q d', 'q c', '3 d'])
        
        # Print card values
        print(f"Player 1 hole cards: {[f'{c.rank}{c.suit}({c.rank_value})' for c in player1_hole]}")
        print(f"Player 2 hole cards: {[f'{c.rank}{c.suit}({c.rank_value})' for c in player2_hole]}")
        print(f"Community cards: {[f'{c.rank}{c.suit}({c.rank_value})' for c in community]}")
        
        # Find pairs for each player
        p1_cards = player1_hole + community
        p2_cards = player2_hole + community
        
        p1_pairs = HandEvaluator._get_pairs(p1_cards)
        p2_pairs = HandEvaluator._get_pairs(p2_cards)
        
        print(f"\nPlayer 1 pairs: {[f'{c.rank}{c.suit}' for c in p1_pairs]}")
        print(f"Player 2 pairs: {[f'{c.rank}{c.suit}' for c in p2_pairs]}")
        
        # Find four of a kind for each player
        p1_four = HandEvaluator._get_n_of_a_kind(p1_cards, 4)
        p2_four = HandEvaluator._get_n_of_a_kind(p2_cards, 4)
        
        print(f"Player 1 four of a kind: {p1_four is not None}")
        if p1_four:
            print(f"  Cards: {[f'{c.rank}{c.suit}' for c in p1_four]}")
        
        print(f"Player 2 four of a kind: {p2_four is not None}")
        if p2_four:
            print(f"  Cards: {[f'{c.rank}{c.suit}' for c in p2_four]}")
        
        # Evaluate full hands for both players
        hand1 = HandEvaluator.evaluate_hand(player1_hole, community)
        hand2 = HandEvaluator.evaluate_hand(player2_hole, community)
        
        print(f"\nPlayer 1's evaluated hand: {hand1[1]} with tiebreakers {hand1[3]}")
        print(f"Player 1's best hand: {', '.join([f'{c.rank}{c.suit}' for c in hand1[2]])}")
        
        print(f"Player 2's evaluated hand: {hand2[1]} with tiebreakers {hand2[3]}")  
        print(f"Player 2's best hand: {', '.join([f'{c.rank}{c.suit}' for c in hand2[2]])}")
        
        # Compare the hands
        comparison = HandEvaluator.compare_hands(hand1, hand2)
        winner = "Player 1" if comparison > 0 else "Player 2" if comparison < 0 else "Tie"
        print(f"\nWinner: {winner}")
            
    def evaluate_and_compare(self, name, player1_hole_cards, player2_hole_cards, community_cards, expected_winner):
        """Evaluate hands and compare results.
        
        Args:
            name (str): Test name
            player1_hole_cards (list): Player 1's hole cards
            player2_hole_cards (list): Player 2's hole cards
            community_cards (list): Community cards
            expected_winner (int): Expected winner (1 for player 1, 2 for player 2, 0 for tie)
            
        Returns:
            TestResult: Test result
        """
        # Evaluate hands
        hand1 = HandEvaluator.evaluate_hand(player1_hole_cards, community_cards)
        hand2 = HandEvaluator.evaluate_hand(player2_hole_cards, community_cards)

        # Compare hands
        comparison = HandEvaluator.compare_hands(hand1, hand2)
        
        actual_winner = 0
        if comparison > 0:
            actual_winner = 1
        elif comparison < 0:
            actual_winner = 2
            
        # Generate message
        hand1_name = hand1[1]
        hand2_name = hand2[1]
        
        # Plain text representation of cards
        p1_cards = [f"{c.rank}{c.suit[0]}" for c in player1_hole_cards]
        p2_cards = [f"{c.rank}{c.suit[0]}" for c in player2_hole_cards]
        comm_cards = [f"{c.rank}{c.suit[0]}" for c in community_cards]
        
        message = f"\nPlayer 1: {hand1_name} {' '.join(p1_cards)}"
        message += f"\nPlayer 2: {hand2_name} {' '.join(p2_cards)}"
        message += f"\nCommunity: {' '.join(comm_cards)}"

        if expected_winner == actual_winner:
            if expected_winner == 0:
                message += f"\nCorrect result: It's a tie"
            else:
                message += f"\nCorrect result: Player {expected_winner} wins"
            result = TestResult(name, True, message)
        else:
            if expected_winner == 0:
                message += f"\nExpected a tie, but Player {actual_winner} won"
            else:
                message += f"\nExpected Player {expected_winner} to win, but "
                if actual_winner == 0:
                    message += "it was a tie"
                else:
                    message += f"Player {actual_winner} won"
            result = TestResult(name, False, message)
            
        self.results.append(result)
        return result

    def create_cards(self, cards_str):
        """Create a list of card objects from string representations.
        
        Args:
            cards_str (list): List of card strings in format 'rank s' for spades, 'rank h' for hearts, etc.
            
        Returns:
            list: List of Card objects
        """
        cards = []
        for card_str in cards_str:
            rank, suit_code = card_str.split()
            # Convert lowercase face card ranks to uppercase
            if rank.lower() in ['a', 'k', 'q', 'j']:
                rank = rank.upper()
            suit = self.SUITS.get(suit_code.lower(), suit_code.lower())
            cards.append(Card(rank, suit))
        return cards

    # Tests for hand type rankings
    def test_royal_flush_vs_straight_flush(self):
        name = "Royal Flush vs. Straight Flush"
        
        # Royal flush: AS KS QS JS 10S
        player1_hole = self.create_cards(['a s', 'k s'])
        
        # Straight flush: 9H 8H 7H 6H 5H
        player2_hole = self.create_cards(['9 h', '8 h'])
        
        community = self.create_cards(['q s', 'j s', '10 s', '7 h', '6 h', '5 h'])
        
        return self.evaluate_and_compare(name, player1_hole, player2_hole, community, 1)

    def test_straight_flush_vs_four_of_a_kind(self):
        name = "Straight Flush vs. Four of a Kind"
        
        # Straight flush: 9S 8S 7S 6S 5S
        player1_hole = self.create_cards(['9 s', '8 s'])
        
        # Four of a kind: AS AH AD AC KS
        player2_hole = self.create_cards(['a h', 'a d'])
        
        # Ensure player1 gets a straight flush and player2 gets four of a kind
        # Use exactly 5 community cards to avoid issues
        community = self.create_cards(['7 s', '6 s', '5 s', 'a s', 'a c'])
        
        return self.evaluate_and_compare(name, player1_hole, player2_hole, community, 1)

    def test_four_of_a_kind_vs_full_house(self):
        name = "Four of a Kind vs. Full House"
        
        # Four of a kind: AS AH AD AC KS
        player1_hole = self.create_cards(['a h', 'a d'])
        
        # Full house: KS KH KD QS QH
        player2_hole = self.create_cards(['k h', 'k d'])
        
        community = self.create_cards(['a s', 'a c', 'k s', 'q s', 'q h'])
        
        return self.evaluate_and_compare(name, player1_hole, player2_hole, community, 1)

    def test_full_house_vs_flush(self):
        name = "Full House vs. Flush"
        
        # Full house: KH KD KC QH QC (no spades for player 1)
        player1_hole = self.create_cards(['K h', 'K d'])
        
        # Flush: AS 8S 4S 3S 2S
        player2_hole = self.create_cards(['8 s', '4 s'])
        
        # Full house cards for player 1, flush cards for player 2, no common flush
        community = self.create_cards(['K c', 'Q h', 'Q c', '3 s', '2 s', 'A s'])
        
        return self.evaluate_and_compare(name, player1_hole, player2_hole, community, 1)

    def test_flush_vs_straight(self):
        name = "Flush vs. Straight"
        
        # Flush: AS KS QS JS 9S
        player1_hole = self.create_cards(['a s', 'k s'])
        
        # Straight: 10H 9D 8C 7S 6H
        player2_hole = self.create_cards(['10 h', '9 d'])
        
        community = self.create_cards(['q s', 'j s', '9 s', '8 c', '7 s', '6 h'])
        
        return self.evaluate_and_compare(name, player1_hole, player2_hole, community, 1)

    def test_straight_vs_three_of_a_kind(self):
        name = "Straight vs. Three of a Kind"
        
        # Straight: 10H 9D 8C 7S 6H
        player1_hole = self.create_cards(['10 h', '9 d'])
        
        # Three of a kind: AS AH AD KS QH
        player2_hole = self.create_cards(['a h', 'a d'])
        
        community = self.create_cards(['8 c', '7 s', '6 h', 'a s', 'k s', 'q h'])
        
        return self.evaluate_and_compare(name, player1_hole, player2_hole, community, 1)

    def test_three_of_a_kind_vs_two_pair(self):
        name = "Three of a Kind vs. Two Pair"
        
        # Three of a kind: AS AH AD KS QH
        player1_hole = self.create_cards(['a h', 'a d'])
        
        # Two pair: KS KH QS QH JD
        player2_hole = self.create_cards(['k h', 'k s'])
        
        community = self.create_cards(['a s', 'q s', 'q h', 'j d', '2 c'])
        
        return self.evaluate_and_compare(name, player1_hole, player2_hole, community, 1)

    def test_two_pair_vs_pair(self):
        name = "Two Pair vs. Pair"
        
        # Two pair: KS KH QS QH JD
        player1_hole = self.create_cards(['k h', 'k s'])
        
        # Pair: AS AH KD QC JH
        player2_hole = self.create_cards(['a h', 'a s'])
        
        community = self.create_cards(['q s', 'q h', 'j d', 'k d', '3 h'])
        
        return self.evaluate_and_compare(name, player1_hole, player2_hole, community, 1)

    def test_pair_vs_high_card(self):
        name = "Pair vs. High Card"
        
        # Pair: AS AH KD QC JH
        player1_hole = self.create_cards(['a h', 'a s'])
        
        # High card: AD KH QD JC 9H
        player2_hole = self.create_cards(['a d', 'k h'])
        
        community = self.create_cards(['k d', 'q c', 'j h', 'q d', 'j c', '9 h'])
        
        return self.evaluate_and_compare(name, player1_hole, player2_hole, community, 1)

    # Tests for tiebreakers within same hand type
    def test_royal_flush_tiebreaker(self):
        name = "Royal Flush Tiebreaker"
        
        # Royal flush: AS KS QS JS 10S
        player1_hole = self.create_cards(['a s', 'k s'])
        
        # Royal flush: AH KH QH JH 10H
        player2_hole = self.create_cards(['a h', 'k h'])
        
        community = self.create_cards(['q s', 'j s', '10 s', 'q h', 'j h', '10 h'])
        
        # Royal flushes always tie
        return self.evaluate_and_compare(name, player1_hole, player2_hole, community, 0)

    def test_straight_flush_tiebreaker(self):
        name = "Straight Flush Tiebreaker"
        
        # Higher straight flush: AH KH QH JH 10H
        player1_hole = self.create_cards(['a h', 'k h'])
        
        # Lower straight flush: 9S 8S 7S 6S 5S
        player2_hole = self.create_cards(['9 s', '8 s'])
        
        community = self.create_cards(['q h', 'j h', '10 h', '7 s', '6 s', '5 s'])
        
        return self.evaluate_and_compare(name, player1_hole, player2_hole, community, 1)

    def test_four_of_a_kind_tiebreaker(self):
        name = "Four of a Kind Tiebreaker"
        
        # Higher four of a kind: AS AH AD AC KH
        player1_hole = self.create_cards(['a h', 'a d'])
        
        # Lower four of a kind: KS KH KD KC AH
        player2_hole = self.create_cards(['k h', 'k d'])
        
        community = self.create_cards(['a s', 'a c', 'k s', 'k c', 'q h'])
        
        return self.evaluate_and_compare(name, player1_hole, player2_hole, community, 1)

    def test_full_house_tiebreaker(self):
        name = "Full House Tiebreaker"
        
        # Higher full house: AS AH AD KS KC
        player1_hole = self.create_cards(['a h', 'a d'])
        
        # Lower full house: KS KH KD AS AC
        player2_hole = self.create_cards(['k c', 'k h'])
        
        community = self.create_cards(['a s', 'k s', 'k d', 'a c', '2 c'])
        
        return self.evaluate_and_compare(name, player1_hole, player2_hole, community, 1)

    def test_flush_tiebreaker(self):
        name = "Flush Tiebreaker"
        
        # Higher flush: AS KS JS 9S 7S
        player1_hole = self.create_cards(['a s', 'k s'])
        
        # Lower flush: KH QH JH 9H 8H
        player2_hole = self.create_cards(['k h', 'q h'])
        
        community = self.create_cards(['j s', '9 s', '7 s', 'j h', '9 h', '8 h'])
        
        return self.evaluate_and_compare(name, player1_hole, player2_hole, community, 1)

    def test_straight_tiebreaker(self):
        name = "Straight Tiebreaker"
        
        # Higher straight: A K Q J 10
        player1_hole = self.create_cards(['a s', 'k h'])
        
        # Lower straight: K Q J 10 9
        player2_hole = self.create_cards(['k d', 'q c'])
        
        community = self.create_cards(['q d', 'j c', '10 s', 'j s', '10 h', '9 d'])
        
        return self.evaluate_and_compare(name, player1_hole, player2_hole, community, 1)

    def test_three_of_a_kind_tiebreaker(self):
        name = "Three of a Kind Tiebreaker"
        
        # Higher three of a kind: AS AH AD KC QH
        player1_hole = self.create_cards(['a h', 'a d'])
        
        # Lower three of a kind: KC KD KH AC QD
        player2_hole = self.create_cards(['k d', 'k h'])
        
        community = self.create_cards(['a s', 'k c', 'q h', 'a c', 'q d'])
        
        return self.evaluate_and_compare(name, player1_hole, player2_hole, community, 1)

    def test_two_pair_tiebreaker(self):
        name = "Two Pair Tiebreaker"
        
        # Higher two pair: AS AH QS QH 2C
        player1_hole = self.create_cards(['A h', 'A s'])
        
        # Lower two pair: KS KH QS QH 2C
        player2_hole = self.create_cards(['K h', 'K s'])
        
        # Use exactly 5 community cards to avoid higher hands
        community = self.create_cards(['2 s', '2 d', 'Q d', 'Q c', '3 h'])
        
        return self.evaluate_and_compare(name, player1_hole, player2_hole, community, 1)

    def test_pair_tiebreaker(self):
        name = "Pair Tiebreaker"
        
        # Higher pair: AS AH KD QC JH
        player1_hole = self.create_cards(['a h', 'a s'])
        
        # Lower pair: KS KH AD QS JD
        player2_hole = self.create_cards(['k h', 'k s'])
        
        community = self.create_cards(['k d', 'q c', 'j h', 'a d', 'q d', 'j d'])
        
        return self.evaluate_and_compare(name, player1_hole, player2_hole, community, 1)

    def test_high_card_tiebreaker(self):
        name = "High Card Tiebreaker"
        
        # Higher high card: AS KH QD JC 9H
        player1_hole = self.create_cards(['a s', 'k h'])
        
        # Lower high card: AH QS JH 10D 9C
        player2_hole = self.create_cards(['a h', 'q s'])
        
        community = self.create_cards(['q d', 'j c', '9 h', 'j h', '10 d', '9 c'])
        
        return self.evaluate_and_compare(name, player1_hole, player2_hole, community, 1)


def test_game_outcome():
    """Test a full game scenario with predetermined cards."""
    name = "Full Game Test"
    
    # Create players
    player1 = AIPlayer("Player 1", 1000, SimpleAgent("Agent1"))
    player2 = AIPlayer("Player 2", 1000, SimpleAgent("Agent2"))
    
    # Set up hole cards - using lowercase suit representation
    player1.hole_cards = [Card('A', 's'), Card('K', 's')]  # Going for royal flush
    player2.hole_cards = [Card('A', 'h'), Card('A', 'd')]  # Going for three of a kind
    
    # Set up community cards for royal flush vs. three of a kind
    community_cards = [Card('Q', 's'), Card('J', 's'), Card('10', 's'), Card('2', 'h'), Card('3', 'c')]
    
    # Evaluate hands
    hand1 = HandEvaluator.evaluate_hand(player1.hole_cards, community_cards)
    hand2 = HandEvaluator.evaluate_hand(player2.hole_cards, community_cards)
    
    # Compare hands
    comparison = HandEvaluator.compare_hands(hand1, hand2)
    
    # Generate results with plain text suit representation
    print(f"\n{Fore.CYAN}=== Full Game Test ==={Style.RESET_ALL}")
    print(f"Player 1 hole cards: {player1.hole_cards[0].rank}{player1.hole_cards[0].suit} {player1.hole_cards[1].rank}{player1.hole_cards[1].suit}")
    print(f"Player 2 hole cards: {player2.hole_cards[0].rank}{player2.hole_cards[0].suit} {player2.hole_cards[1].rank}{player2.hole_cards[1].suit}")
    print(f"Community cards: {' '.join(f'{c.rank}{c.suit}' for c in community_cards)}")
    print(f"\nPlayer 1 has {hand1[1]}")
    print(f"\nPlayer 2 has {hand2[1]}")
    
    if comparison > 0:
        print(f"{Fore.GREEN}Player 1 wins!{Style.RESET_ALL}")
    elif comparison < 0:
        print(f"{Fore.GREEN}Player 2 wins!{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}It's a tie!{Style.RESET_ALL}")


def main():
    """Run all tests."""
    print(f"{Fore.CYAN}=== POKER HAND EVALUATOR TESTS ==={Style.RESET_ALL}")
    
    tester = PokerHandTester()
    results = tester.run_all_tests()
    
    # Display results
    passed = 0
    failed = 0
    
    print(f"\n{Fore.CYAN}=== TEST RESULTS ==={Style.RESET_ALL}")
    for result in results:
        print(result)
        if result.passed:
            passed += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{Fore.CYAN}=== SUMMARY ==={Style.RESET_ALL}")
    print(f"Total tests: {len(results)}")
    print(f"Passed: {Fore.GREEN}{passed}{Style.RESET_ALL}")
    print(f"Failed: {Fore.RED}{failed}{Style.RESET_ALL}")
    
    # Run a full game test
    test_game_outcome()
    
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main() 