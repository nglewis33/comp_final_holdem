#!/usr/bin/env python3

import random
import time
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
from colorama import init, Fore, Style

from texas_holdem.card import Card
from texas_holdem.deck import Deck
from texas_holdem.evaluator import HandEvaluator

class PokerProbabilitySimulator:
    """Simulates poker hands and calculates hand probabilities."""
    
    # Theoretical probabilities for 7-card poker hands (Texas Hold'em)
    # Source: https://en.wikipedia.org/wiki/Poker_probability
    THEORETICAL_PROBABILITIES = {
        "Royal Flush": 0.0032,      # 0.0032%
        "Straight Flush": 0.0279,   # 0.0279%
        "Four of a Kind": 0.168,    # 0.168%
        "Full House": 2.60,         # 2.60%
        "Flush": 3.03,              # 3.03%
        "Straight": 4.62,           # 4.62%
        "Three of a Kind": 4.83,    # 4.83%
        "Two Pair": 23.5,           # 23.5%
        "One Pair": 43.8,           # 43.8%
        "High Card": 17.4,          # 17.4%
    }
    
    def __init__(self):
        """Initialize the simulator."""
        init()  # Initialize colorama
        self.hand_counts = Counter()
        self.total_hands = 0
    
    def run_simulation(self, num_simulations=100000, num_players=4, show_progress=True):
        """Run poker hand simulations.
        
        Args:
            num_simulations (int): Number of hands to simulate
            num_players (int): Number of players in each hand
            show_progress (bool): Whether to show progress updates
        """
        start_time = time.time()
        
        if show_progress:
            print(f"{Fore.CYAN}Starting simulation of {num_simulations} hands with {num_players} players...{Style.RESET_ALL}")
        
        for i in range(num_simulations):
            # Update progress every 5% of simulations
            if show_progress and i % max(1, num_simulations // 20) == 0:
                progress = (i / num_simulations) * 100
                elapsed = time.time() - start_time
                remaining = (elapsed / (i + 1)) * (num_simulations - i - 1) if i > 0 else 0
                print(f"Progress: {progress:.1f}% - Elapsed: {elapsed:.1f}s - Estimated remaining: {remaining:.1f}s")
            
            # Deal a new hand
            self._simulate_hand(num_players)
        
        total_time = time.time() - start_time
        
        if show_progress:
            print(f"{Fore.GREEN}Simulation complete! {num_simulations} hands simulated in {total_time:.2f} seconds.{Style.RESET_ALL}")
            print(f"Total hands evaluated: {self.total_hands}")
    
    def _simulate_hand(self, num_players):
        """Simulate a single poker hand.
        
        Args:
            num_players (int): Number of players in the hand
        """
        # Create and shuffle a deck
        deck = Deck()
        deck.shuffle()
        
        # Deal hole cards to each player
        hole_cards = []
        for _ in range(num_players):
            player_cards = deck.deal(2)
            hole_cards.append(player_cards)
        
        # Deal community cards
        community_cards = deck.deal(5)
        
        # Evaluate each player's hand and count the hand types
        for player_cards in hole_cards:
            hand_eval = HandEvaluator.evaluate_hand(player_cards, community_cards)
            hand_type = hand_eval[1]  # hand_name is at index 1
            self.hand_counts[hand_type] += 1
            self.total_hands += 1
    
    def get_probabilities(self):
        """Calculate the probabilities of each hand type from simulation results.
        
        Returns:
            dict: Hand types and their probabilities
        """
        probabilities = {}
        for hand_type in HandEvaluator.HAND_RANKINGS:
            count = self.hand_counts.get(hand_type, 0)
            prob = (count / self.total_hands) * 100 if self.total_hands > 0 else 0
            probabilities[hand_type] = prob
        
        return probabilities
    
    def compare_with_theoretical(self):
        """Compare simulated probabilities with theoretical probabilities.
        
        Returns:
            dict: Hand types and their probability differences (simulated - theoretical)
        """
        simulated = self.get_probabilities()
        differences = {}
        
        for hand_type, theoretical in self.THEORETICAL_PROBABILITIES.items():
            if hand_type in simulated:
                diff = simulated[hand_type] - theoretical
                differences[hand_type] = diff
        
        return differences
    
    def print_results(self):
        """Print the simulation results."""
        simulated = self.get_probabilities()
        
        print(f"\n{Fore.CYAN}=== HAND PROBABILITY SIMULATION RESULTS ==={Style.RESET_ALL}")
        print(f"Total hands evaluated: {self.total_hands}")
        
        print(f"\n{'Hand Type':<15} {'Count':<10} {'Simulated %':<15} {'Theoretical %':<15} {'Difference':<15}")
        print("-" * 70)
        
        # Print in order of hand ranking (best to worst)
        for hand_type in HandEvaluator.HAND_RANKINGS:
            count = self.hand_counts.get(hand_type, 0)
            simulated_prob = simulated.get(hand_type, 0)
            theoretical_prob = self.THEORETICAL_PROBABILITIES.get(hand_type, 0)
            diff = simulated_prob - theoretical_prob
            
            # Color code the difference
            if abs(diff) < 0.2:
                diff_str = f"{Fore.GREEN}{diff:+.3f}%{Style.RESET_ALL}"
            elif abs(diff) < 0.5:
                diff_str = f"{Fore.YELLOW}{diff:+.3f}%{Style.RESET_ALL}"
            else:
                diff_str = f"{Fore.RED}{diff:+.3f}%{Style.RESET_ALL}"
            
            print(f"{hand_type:<15} {count:<10} {simulated_prob:.3f}%{' ':<10} {theoretical_prob:.3f}%{' ':<10} {diff_str}")
    
    def plot_results(self, filename="poker_probabilities.png"):
        """Plot the simulation results and save to a file.
        
        Args:
            filename (str): Output file name
        """
        simulated = self.get_probabilities()
        
        # Prepare data for plotting
        hand_types = []
        simulated_probs = []
        theoretical_probs = []
        
        # Collect data in order of hand ranking (worst to best for plotting)
        for hand_type in reversed(HandEvaluator.HAND_RANKINGS):
            hand_types.append(hand_type)
            simulated_probs.append(simulated.get(hand_type, 0))
            theoretical_probs.append(self.THEORETICAL_PROBABILITIES.get(hand_type, 0))
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Set width of bars
        bar_width = 0.35
        
        # Set position of bars on x axis
        r1 = np.arange(len(hand_types))
        r2 = [x + bar_width for x in r1]
        
        # Create bars
        ax.bar(r1, simulated_probs, width=bar_width, label='Simulated', color='skyblue')
        ax.bar(r2, theoretical_probs, width=bar_width, label='Theoretical', color='orange')
        
        # Add labels and title
        ax.set_xlabel('Hand Type')
        ax.set_ylabel('Probability (%)')
        ax.set_title('Poker Hand Probabilities: Simulated vs. Theoretical')
        ax.set_xticks([r + bar_width/2 for r in range(len(hand_types))])
        ax.set_xticklabels(hand_types, rotation=45, ha='right')
        
        # Add legend
        ax.legend()
        
        # Add text with number of simulations
        plt.figtext(0.5, 0.01, f"Total hands simulated: {self.total_hands}", 
                   ha="center", fontsize=10)
        
        # Adjust layout and save
        plt.tight_layout()
        plt.savefig(filename)
        print(f"\nPlot saved to {filename}")


def main():
    """Run the poker hand probability simulation."""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Simulate poker hands and calculate probabilities')
    parser.add_argument('--simulations', type=int, default=100000,
                        help='Number of hands to simulate')
    parser.add_argument('--players', type=int, default=4,
                        help='Number of players in each hand')
    parser.add_argument('--no-plot', action='store_true',
                        help='Disable plotting of results')
    parser.add_argument('--output', type=str, default='poker_probabilities.png',
                        help='Output file name for plot')
    
    args = parser.parse_args()
    
    # Create simulator and run simulation
    simulator = PokerProbabilitySimulator()
    simulator.run_simulation(num_simulations=args.simulations, num_players=args.players)
    
    # Print results
    simulator.print_results()
    
    # Plot results if enabled
    if not args.no_plot:
        try:
            simulator.plot_results(filename=args.output)
        except ImportError:
            print(f"\n{Fore.YELLOW}Warning: matplotlib not installed. Skipping plot generation.{Style.RESET_ALL}")
            print("To install matplotlib, run: pip install matplotlib")


if __name__ == "__main__":
    main() 