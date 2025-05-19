#!/usr/bin/env python3

import json
import os
import sys
import pandas as pd
from core.card import Card

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class PreflopHandValues:
    """
    A utility class for looking up the preflop hand values based on the expanded notation.
    """
    
    def __init__(self, csv_file="expanded_preflop_hands.csv"):
        """
        Initialize with a CSV file containing expanded preflop hand values.
        
        Args:
            csv_file (str): Path to the CSV file with expanded hand values
        """
        self.hand_to_group = {}
        self.hand_to_notation = {}
        self.load_from_csv(csv_file)
    
    def load_from_csv(self, csv_file):
        """
        Load hand values from a CSV file.
        
        Args:
            csv_file (str): Path to the CSV file
        """
        try:
            # Read the CSV file
            df = pd.read_csv(csv_file)
            
            # Process each row to build lookup dictionaries
            for _, row in df.iterrows():
                group = int(row['Group'])
                notation = row['Hand_Notation']
                
                # Skip "All other hands" entry
                if notation == "All other hands":
                    continue
                
                # Parse the expanded hands JSON
                try:
                    expanded_hands = json.loads(row['Expanded_Hands'])
                    
                    # Add each hand to the lookup dictionaries
                    for hand in expanded_hands:
                        # Create a tuple key that's hashable
                        hand_key = tuple(sorted(hand))
                        
                        # Store the group and notation
                        self.hand_to_group[hand_key] = group
                        self.hand_to_notation[hand_key] = notation
                except json.JSONDecodeError:
                    print(f"Warning: Could not parse expanded hands for {notation}")
        
        except Exception as e:
            print(f"Error loading preflop hand values: {str(e)}")
    
    def get_hand_group(self, card1, card2):
        """
        Get the strength group for a given hand.
        
        Args:
            card1 (Card or str): First card
            card2 (Card or str): Second card
            
        Returns:
            int: The strength group (1-9, with 1 being the strongest), or 9 if not found
        """
        # Convert Card objects to strings if needed
        card1_str = str(card1.rank) + str(card1.suit) if isinstance(card1, Card) else card1
        card2_str = str(card2.rank) + str(card2.suit) if isinstance(card2, Card) else card2
        
        # Create a tuple key for lookup (in sorted order)
        hand_key = tuple(sorted([card1_str, card2_str]))
        
        # Return the group, or 9 (weakest) if not found
        return self.hand_to_group.get(hand_key, 9)
    
    def get_hand_notation(self, card1, card2):
        """
        Get the hand notation for a given hand.
        
        Args:
            card1 (Card or str): First card
            card2 (Card or str): Second card
            
        Returns:
            str: The hand notation (e.g., "AKs", "TT"), or None if not found
        """
        # Convert Card objects to strings if needed
        card1_str = str(card1.rank) + str(card1.suit) if isinstance(card1, Card) else card1
        card2_str = str(card2.rank) + str(card2.suit) if isinstance(card2, Card) else card2
        
        # Create a tuple key for lookup (in sorted order)
        hand_key = tuple(sorted([card1_str, card2_str]))
        
        # Return the notation, or None if not found
        return self.hand_to_notation.get(hand_key, None)
    
    def is_playable_hand(self, card1, card2, min_group=6):
        """
        Check if a hand is playable based on a minimum strength group.
        
        Args:
            card1 (Card or str): First card
            card2 (Card or str): Second card
            min_group (int): Minimum strength group to consider playable (1-9)
            
        Returns:
            bool: True if the hand strength group is <= min_group, False otherwise
        """
        group = self.get_hand_group(card1, card2)
        return group <= min_group
    
    def get_hand_percentile(self, card1, card2):
        """
        Get the approximate percentile strength of a hand (higher is better).
        
        Args:
            card1 (Card or str): First card
            card2 (Card or str): Second card
            
        Returns:
            float: Percentile strength from 0.0 to 1.0
        """
        group = self.get_hand_group(card1, card2)
        
        # Convert group to percentile (group 1 is top ~1.7%, group 9 is bottom ~50%)
        # These are approximate values based on common hand groupings
        percentiles = {
            1: 0.983,  # Top 1.7%
            2: 0.95,   # Top 5%
            3: 0.9,    # Top 10%
            4: 0.82,   # Top 18%
            5: 0.7,    # Top 30%
            6: 0.55,   # Top 45%
            7: 0.4,    # Top 60%
            8: 0.2,    # Top 80%
            9: 0.0     # Bottom 20%
        }
        
        return percentiles.get(group, 0.0)


# Example usage
if __name__ == "__main__":
    # Initialize the preflop hand values
    hand_values = PreflopHandValues()
    
    # Test some hands
    test_hands = [
        ["As", "Ah"],  # AA
        ["Ks", "Kh"],  # KK
        ["As", "Ks"],  # AKs
        ["As", "Kh"],  # AKo
        ["10s", "9s"],  # T9s
        ["10s", "9h"],  # T9o
        ["2s", "7h"],  # 72o (weak hand)
    ]
    
    print("Preflop Hand Values Test:")
    print("-" * 50)
    for hand in test_hands:
        group = hand_values.get_hand_group(hand[0], hand[1])
        notation = hand_values.get_hand_notation(hand[0], hand[1])
        percentile = hand_values.get_hand_percentile(hand[0], hand[1])
        playable = hand_values.is_playable_hand(hand[0], hand[1], min_group=6)
        
        print(f"Hand: {hand[0]}, {hand[1]}")
        print(f"  Notation: {notation}")
        print(f"  Group: {group} (1 is strongest, 9 is weakest)")
        print(f"  Percentile: {percentile:.2f}")
        print(f"  Playable (Group <= 6): {playable}")
        print("-" * 30) 