#!/usr/bin/env python3

import argparse
import re
import json
import csv
import os
import sys
import itertools
import pandas as pd

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.card import Card

# Card ranks and suits from the codebase
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
SUITS = ['h', 'd', 'c', 's']

def parse_hand_range(hand_range):
    """
    Parse a hand range like 'A9s-A2s' and return a list of all hands in that range.
    
    Args:
        hand_range (str): The hand range string
        
    Returns:
        list: List of individual hand notations
    """
    range_match = re.match(r"([A-Z]|T)([0-9]|[A-Z]|T)([so]?)\s*-\s*([A-Z]|T)([0-9]|[A-Z]|T)([so]?)", hand_range)
    if not range_match:
        return [hand_range]  # Not a range, return as is
    
    rank1_1, rank1_2, suffix1, rank2_1, rank2_2, suffix2 = range_match.groups()
    
    # Convert T to 10 for ranking
    rank_to_value = {'T': 8, 'J': 9, 'Q': 10, 'K': 11, 'A': 12}
    for i in range(2, 10):
        rank_to_value[str(i)] = i - 2
    
    # Get the actual rank values for comparison
    rank1_1_val = rank_to_value.get(rank1_1, 0)
    rank1_2_val = rank_to_value.get(rank1_2, 0)
    rank2_1_val = rank_to_value.get(rank2_1, 0)
    rank2_2_val = rank_to_value.get(rank2_2, 0)
    
    # If first rank is the same, we're varying the second rank
    if rank1_1 == rank2_1:
        # Determine the range of ranks
        start_rank_val = min(rank1_2_val, rank2_2_val)
        end_rank_val = max(rank1_2_val, rank2_2_val)
        
        # Generate all hands in the range
        hands = []
        for rank_val in range(start_rank_val, end_rank_val + 1):
            rank2 = next((r for r, v in rank_to_value.items() if v == rank_val), str(rank_val + 2))
            # Convert T to 10 for output
            rank2 = '10' if rank2 == 'T' else rank2
            rank1 = '10' if rank1_1 == 'T' else rank1_1
            
            if suffix1:  # If there's a suffix (s/o), add it
                hands.append(f"{rank1}{rank2}{suffix1}")
            else:
                hands.append(f"{rank1}{rank2}")
        
        return hands
    
    # Just return the range as is if we can't parse it
    return [hand_range]

def convert_rank(rank):
    """Convert T to 10."""
    if rank == 'T':
        return '10'
    return rank

def expand_hand_notation(hand_notation):
    """
    Expand a hand notation like 'AKs' to a list of specific hands.
    
    Args:
        hand_notation (str): The hand notation
        
    Returns:
        list: List of hands, where each hand is a list of two cards
    """
    # Clean up the notation
    hand_notation = hand_notation.strip()
    
    # Check if it's a range like "A9s-A2s"
    if '-' in hand_notation:
        hands = []
        for notation in parse_hand_range(hand_notation):
            hands.extend(expand_hand_notation(notation))
        return hands
    
    # Special case for pocket pairs like '99', '88', etc.
    pocket_pair_match = re.match(r"([0-9]+|[A-Z])\1$", hand_notation)
    if pocket_pair_match:
        rank = pocket_pair_match.group(1)
        rank = convert_rank(rank)
        # Generate all combinations of suits
        return [[f"{rank}{suit1}", f"{rank}{suit2}"] 
                for suit1, suit2 in itertools.combinations(SUITS, 2)]
    
    # Regular expression to match hand patterns (like 'AKs', 'AK', 'A5o')
    pattern = r"([A-Z]|T|[0-9]+)([A-Z]|T|[0-9]+)([so]?)"
    match = re.match(pattern, hand_notation)
    
    if not match:
        return []  # Unable to parse this notation
    
    rank1, rank2, suffix = match.groups()
    
    # Convert T to 10
    rank1 = convert_rank(rank1)
    rank2 = convert_rank(rank2)
    
    # For paired hands like AA, KK
    if rank1 == rank2:
        # Generate all combinations of suits
        return [[f"{rank1}{suit1}", f"{rank1}{suit2}"] 
                for suit1, suit2 in itertools.combinations(SUITS, 2)]
    
    # For suited hands like AKs
    if suffix == 's':
        return [[f"{rank1}{suit}", f"{rank2}{suit}"] for suit in SUITS]
    
    # For offsuit hands like AK or AKo
    if suffix == 'o' or suffix == '':
        return [[f"{rank1}{suit1}", f"{rank2}{suit2}"] 
                for suit1, suit2 in itertools.product(SUITS, SUITS) 
                if suit1 != suit2]
    
    return []  # Fallback

def process_preflop_values(input_csv, output_csv):
    """
    Process the preflop values CSV and create a new CSV with expanded hand lists.
    
    Args:
        input_csv (str): Path to the input CSV
        output_csv (str): Path to the output CSV
    """
    # Read the input CSV
    print(f"Reading input file: {input_csv}")
    df = pd.read_csv(input_csv)
    
    # Create a new dataframe to store the expanded hands
    expanded_data = []
    
    # Process each group and its hands
    for _, row in df.iterrows():
        group = row['Group']
        
        # Skip the "All other hands" entry
        if isinstance(row['Hands'], str) and "All other hands" in row['Hands']:
            expanded_data.append({
                'Group': group,
                'Hand_Notation': "All other hands",
                'Expanded_Hands': "[]"
            })
            continue
        
        # Split multiple hands in the cell
        hand_notations = row['Hands'].split(',')
        
        for hand_notation in hand_notations:
            hand_notation = hand_notation.strip()
            if not hand_notation:
                continue
                
            # Expand the hand notation
            expanded_hands = expand_hand_notation(hand_notation)
            
            # Format the expanded hands for CSV
            expanded_hands_str = json.dumps(expanded_hands)
            
            # Add to our data
            expanded_data.append({
                'Group': group,
                'Hand_Notation': hand_notation,
                'Expanded_Hands': expanded_hands_str
            })
    
    # Create a new dataframe
    expanded_df = pd.DataFrame(expanded_data)
    
    # Save to CSV
    print(f"Writing expanded hands to: {output_csv}")
    expanded_df.to_csv(output_csv, index=False, quoting=csv.QUOTE_ALL)
    print(f"Expansion complete. Output saved to: {output_csv}")
    
    # Print a sample of the expansions
    print("\nSample of expanded hands:")
    for i, row in expanded_df.head(5).iterrows():
        print(f"Group {row['Group']}, {row['Hand_Notation']}: {row['Expanded_Hands'][:100]}...")
    
    return expanded_df

def main():
    """Parse command-line arguments and run the function."""
    parser = argparse.ArgumentParser(description='Expand poker hand notations in CSV file')
    parser.add_argument('input_csv', help='Path to the input CSV file')
    parser.add_argument('-o', '--output', default='expanded_preflop_hands.csv',
                        help='Path to the output CSV file (default: expanded_preflop_hands.csv)')
    
    args = parser.parse_args()
    
    process_preflop_values(args.input_csv, args.output)

if __name__ == "__main__":
    main() 