#!/usr/bin/env python3

import unittest
import random
import os
import sys
from colorama import init, Fore, Style

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.card import Card
from core.deck import Deck
from core.evaluator import HandEvaluator
from core.game import TexasHoldemGame
from core.player import AIPlayer
from agents.simple_agent import SimpleAgent
from agents.probability_agent import ProbabilityAgent

def print_hand_details(name, hole_cards, community_cards):
    """Print details of a hand."""
    print(f"\n--- {name} ---")
    print(f"Hole cards: {', '.join(str(c.rank) + c.suit for c in hole_cards)}")
    print(f"Community: {', '.join(str(c.rank) + c.suit for c in community_cards)}")
    
    # Evaluate the hand
    evaluation = HandEvaluator.evaluate_hand(hole_cards, community_cards)
    rank_idx, hand_name, best_hand, tiebreakers = evaluation
    
    print(f"Hand: {hand_name}")
    print(f"Best 5 cards: {', '.join(str(c.rank) + c.suit for c in best_hand)}")
    print(f"Rank index: {rank_idx} (lower is better)")
    print(f"Tiebreakers: {tiebreakers}")
    
    return evaluation

def compare_hands(name, eval1, eval2):
    """Compare two hands and print the result."""
    print("\n--- Comparison ---")
    comparison = HandEvaluator.compare_hands(eval1, eval2)
    
    if comparison > 0:
        result = "Hand 1 wins"
    elif comparison < 0:
        result = "Hand 2 wins"
    else:
        result = "It's a tie"
    
    print(f"{name}: {result}")
    print(f"Hand 1: {eval1[1]} with tiebreakers {eval1[3]}")
    print(f"Hand 2: {eval2[1]} with tiebreakers {eval2[3]}")
    
    return comparison

def test_straight_flush_vs_four_of_a_kind():
    """Test straight flush beats four of a kind."""
    print("\n=== TEST: Straight Flush vs Four of a Kind ===")
    
    # Create cards for Player 1 (Straight Flush)
    p1_hole = [Card('9', 's'), Card('8', 's')]
    
    # Create cards for Player 2 (Four of a Kind)
    p2_hole = [Card('A', 'h'), Card('A', 'd')]
    
    # Community cards
    community = [
        Card('7', 's'), 
        Card('6', 's'), 
        Card('5', 's'), 
        Card('A', 's'), 
        Card('A', 'c')
    ]
    
    # Evaluate both hands
    eval1 = print_hand_details("Player 1 (Straight Flush)", p1_hole, community)
    eval2 = print_hand_details("Player 2 (Four of a Kind)", p2_hole, community)
    
    # Compare the hands
    comparison = compare_hands("Straight Flush vs Four of a Kind", eval1, eval2)
    
    # Check if Player 1 (Straight Flush) wins
    return comparison > 0

def test_two_pair_tiebreaker():
    """Test two pair tiebreaker."""
    print("\n=== TEST: Two Pair Tiebreaker ===")
    
    # Create cards for Player 1 (Higher Two Pair: A-A-Q-Q-x)
    p1_hole = [Card('A', 'h'), Card('A', 's')]
    
    # Create cards for Player 2 (Lower Two Pair: K-K-Q-Q-x) 
    p2_hole = [Card('K', 'h'), Card('K', 's')]
    
    # Make sure we have exactly 5 community cards (to avoid having 4 kings)
    community = [
        Card('Q', 'd'), 
        Card('Q', 'c'), 
        Card('2', 's'), 
        Card('3', 'd'), 
        Card('4', 'c')
    ]
    
    # Evaluate both hands
    eval1 = print_hand_details("Player 1 (A-A Two Pair)", p1_hole, community)
    eval2 = print_hand_details("Player 2 (K-K Two Pair)", p2_hole, community)
    
    # Compare the hands
    comparison = compare_hands("Two Pair Tiebreaker", eval1, eval2)
    
    # Check if Player 1 (Higher Two Pair) wins
    return comparison > 0

def test_royal_flush_vs_straight_flush():
    """Test royal flush beats straight flush."""
    print("\n=== TEST: Royal Flush vs Straight Flush ===")
    
    # Create cards for Player 1 (Royal Flush)
    p1_hole = [Card('A', 's'), Card('K', 's')]
    
    # Create cards for Player 2 (Straight Flush)
    p2_hole = [Card('9', 'h'), Card('8', 'h')]
    
    # Community cards
    community = [
        Card('Q', 's'), 
        Card('J', 's'), 
        Card('10', 's'), 
        Card('7', 'h'), 
        Card('6', 'h'),
        Card('5', 'h')
    ]
    
    # Evaluate both hands
    eval1 = print_hand_details("Player 1 (Royal Flush)", p1_hole, community)
    eval2 = print_hand_details("Player 2 (Straight Flush)", p2_hole, community)
    
    # Compare the hands
    comparison = compare_hands("Royal Flush vs Straight Flush", eval1, eval2)
    
    # Check if Player 1 (Royal Flush) wins
    return comparison > 0

def test_full_house_tiebreaker():
    """Test full house tiebreaker."""
    print("\n=== TEST: Full House Tiebreaker ===")
    
    # Create cards for Player 1 (Full House: A-A-A-K-K)
    p1_hole = [Card('A', 'h'), Card('A', 's')]
    
    # Create cards for Player 2 (Full House: K-K-K-A-A)
    p2_hole = [Card('K', 'h'), Card('K', 's')]
    
    # Community cards
    community = [
        Card('A', 'd'), 
        Card('K', 'd'), 
        Card('K', 'c'), 
        Card('A', 'c'), 
        Card('2', 's')
    ]
    
    # Evaluate both hands
    eval1 = print_hand_details("Player 1 (Full House A over K)", p1_hole, community)
    eval2 = print_hand_details("Player 2 (Full House K over A)", p2_hole, community)
    
    # Compare the hands
    comparison = compare_hands("Full House Tiebreaker", eval1, eval2)
    
    # Check if Player 1 (Aces full) wins
    return comparison > 0

def main():
    """Run all tests."""
    print("=== POKER HAND EVALUATOR TESTS ===")
    
    # Run tests
    test_results = {
        "Straight Flush vs Four of a Kind": test_straight_flush_vs_four_of_a_kind(),
        "Two Pair Tiebreaker": test_two_pair_tiebreaker(),
        "Royal Flush vs Straight Flush": test_royal_flush_vs_straight_flush(),
        "Full House Tiebreaker": test_full_house_tiebreaker()
    }
    
    # Print summary
    print("\n=== TEST RESULTS ===")
    for test_name, passed in test_results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"{test_name}: {status}")
    
    # Overall result
    all_passed = all(test_results.values())
    print(f"\nOverall: {'All tests PASSED' if all_passed else 'Some tests FAILED'}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    main() 