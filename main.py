#!/usr/bin/env python3

import os
import sys
import argparse
from colorama import init, Fore, Style

from texas_holdem.game import TexasHoldemGame
from texas_holdem.player import HumanPlayer, AIPlayer
from agents.simple_agent import SimpleAgent
from agents.probability_agent import ProbabilityAgent

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

class EnhancedHumanPlayer(HumanPlayer):
    """Human player with access to basic hand information."""
    
    def __init__(self, name, starting_stack, show_information=False):
        """Initialize an enhanced human player.
        
        Args:
            name (str): The player's name
            starting_stack (int): The player's starting chip stack
            show_information (bool): Whether to show additional hand information
        """
        super().__init__(name, starting_stack)
        self.show_information = show_information
    
    def get_action(self, game_state, valid_actions):
        """Get the human player's action from console input, with optional information display.
        
        Args:
            game_state (dict): The current state of the game
            valid_actions (list): List of valid actions for the player
            
        Returns:
            tuple: (action, amount)
        """
        # Display additional information if enabled
        if self.show_information:
            self._display_hand_information(game_state)
        
        # Use the parent class's implementation for the actual action selection
        return super().get_action(game_state, valid_actions)
    
    def _display_hand_information(self, game_state):
        """Display basic information about the current hand.
        
        Args:
            game_state (dict): The current game state
        """
        # Calculate basic pot odds
        to_call = game_state['current_bet'] - self.current_bet
        if to_call > 0:
            pot_odds = to_call / (game_state['pot'] + to_call) * 100
            print(f"\n{Fore.CYAN}=== HAND INFORMATION ==={Style.RESET_ALL}")
            print(f"Pot: ${game_state['pot']}")
            print(f"To call: ${to_call}")
            print(f"Pot odds: {pot_odds:.2f}%")
            print(f"This means you need to win at least {pot_odds:.2f}% of the time to break even.")
            
            # Show basic advice based on pot size vs. call size
            pot_to_call_ratio = game_state['pot'] / to_call if to_call > 0 else float('inf')
            if pot_to_call_ratio > 4:
                print(f"{Fore.GREEN}The pot is offering good odds for a call.{Style.RESET_ALL}")
            elif pot_to_call_ratio > 2:
                print(f"{Fore.YELLOW}The pot is offering reasonable odds for a call.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}The pot is offering poor odds for a call.{Style.RESET_ALL}")
        
        # Show active opponents count
        active_opponents = sum(1 for p in game_state['players'] if not p.is_folded and p != self)
        print(f"Active opponents: {active_opponents}")
        
        # Display the current hand phase
        phase = game_state['phase'].upper()
        print(f"Current phase: {phase}")
        
        # Remind the player to refer to external win probability resources
        print(f"\n{Fore.CYAN}Note: Refer to your downloaded probability tables for accurate win rates.{Style.RESET_ALL}")

def main():
    # Initialize colorama
    init()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Texas Hold\'em Poker')
    parser.add_argument('--mode', type=str, choices=['manual', 'ai'], default=None,
                        help='Game mode: manual for human players, ai for AI players')
    parser.add_argument('--agent-type', type=str, choices=['simple', 'probability'], default='probability',
                        help='Type of AI agent to use')
    parser.add_argument('--hands', type=int, default=10,
                        help='Number of hands to play')
    parser.add_argument('--chips', type=int, default=1000,
                        help='Starting chips for each player')
    parser.add_argument('--small-blind', type=int, default=5,
                        help='Small blind amount')
    parser.add_argument('--big-blind', type=int, default=10,
                        help='Big blind amount')
    parser.add_argument('--players', type=int, default=4,
                        help='Number of players (including human player in manual mode)')
    parser.add_argument('--show-information', action='store_true',
                        help='Show additional hand information during the game (manual mode only)')
    
    args = parser.parse_args()
    
    # If mode is not specified, ask the user
    if args.mode is None:
        print(f"{Fore.CYAN}Welcome to Texas Hold'em Poker!{Style.RESET_ALL}")
        print("\nSelect game mode:")
        print(f"1. {Fore.GREEN}Manual mode{Style.RESET_ALL} (play against AI opponents)")
        print(f"2. {Fore.MAGENTA}AI mode{Style.RESET_ALL} (watch AI agents play against each other)")
        
        while True:
            choice = input("\nEnter your choice (1/2): ").strip()
            if choice == '1':
                game_mode = 'manual'
                break
            elif choice == '2':
                game_mode = 'ai'
                break
            else:
                print(f"{Fore.RED}Invalid choice. Please enter 1 or 2.{Style.RESET_ALL}")
    else:
        game_mode = args.mode
    
    # Setup game parameters
    num_players = args.players
    small_blind = args.small_blind
    big_blind = args.big_blind
    starting_chips = args.chips
    num_hands = args.hands
    
    # Create players based on game mode
    players = []
    
    if game_mode == 'manual':
        # Ask about showing information if not specified
        show_information = args.show_information
        if not args.show_information and not args.agent_type:
            print(f"\n{Fore.CYAN}Would you like to see additional hand information during the game?{Style.RESET_ALL}")
            print("This will help you make better decisions.")
            info_choice = input("Show information? (y/n): ").strip().lower()
            show_information = info_choice.startswith('y')
        
        # Add a human player with information display if enabled
        human_name = input(f"\n{Fore.CYAN}Enter your name: {Style.RESET_ALL}").strip() or "Human"
        players.append(EnhancedHumanPlayer(human_name, starting_chips, show_information))
        
        # Add AI players
        for i in range(1, num_players):
            # Create AI players with varying characteristics
            if args.agent_type == 'simple':
                aggression = 0.3 + (i * 0.2)  # Varying aggression from 0.3 to 0.9
                agent = SimpleAgent(f"AI-{i}", aggression)
            else:  # probability agent
                # Create more diverse agents
                aggression = 0.3 + (i * 0.2)  # 0.3 to 0.9
                risk_tolerance = 0.3 + ((i % 3) * 0.3)  # 0.3, 0.6, 0.9 cycling
                bluff_frequency = 0.05 + ((i % 4) * 0.05)  # 0.05 to 0.2
                agent = ProbabilityAgent(f"AI-{i}", aggression, risk_tolerance, bluff_frequency)
            
            players.append(AIPlayer(f"AI-{i}", starting_chips, agent))
    
    else:  # AI mode
        # Create AI players
        for i in range(num_players):
            if args.agent_type == 'simple':
                # Create simple agents with varying aggression
                aggression = 0.3 + (i * 0.6 / num_players)  # Distribute aggression levels
                agent = SimpleAgent(f"AI-{i+1}", aggression)
            else:  # probability agent
                # Create more diverse probability-based agents
                aggression = 0.3 + (i * 0.6 / num_players)  # Distribute aggression levels
                risk_tolerance = 0.3 + ((i % 3) * 0.3)  # 0.3, 0.6, 0.9 cycling
                bluff_frequency = 0.05 + ((i % 4) * 0.05)  # 0.05 to 0.2
                agent = ProbabilityAgent(f"AI-{i+1}", aggression, risk_tolerance, bluff_frequency)
                
            players.append(AIPlayer(f"AI-{i+1}", starting_chips, agent))
    
    # Create and start the game
    game = TexasHoldemGame(players, small_blind, big_blind)
    
    # Display game configuration
    print(f"\n{Fore.GREEN}Game starting with {len(players)} players!{Style.RESET_ALL}")
    print(f"Each player starts with ${starting_chips}")
    print(f"Blinds: ${small_blind}/${big_blind}")
    print(f"Agent type: {args.agent_type}")
    print(f"Playing {num_hands} hands\n")
    
    # Play the specified number of hands
    for hand_num in range(1, num_hands + 1):
        print(f"\n{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}HAND #{hand_num}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
        
        # Display player stacks before the hand
        print("\nPlayer stacks:")
        for player in players:
            print(f"  {player}")
        
        # Play a hand
        input("\nPress Enter to start the hand...")
        if game_mode == 'ai':
            clear_screen()
        
        game.play_hand()
        
        # Wait for user input before proceeding to the next hand
        if hand_num < num_hands:
            input("\nPress Enter to continue to the next hand...")
            if game_mode == 'ai':
                clear_screen()
    
    # Game over, display final results
    print(f"\n{Fore.GREEN}{'=' * 50}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}GAME OVER{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'=' * 50}{Style.RESET_ALL}")
    
    # Sort players by stack size
    sorted_players = sorted(players, key=lambda p: p.stack, reverse=True)
    
    print("\nFinal standings:")
    for i, player in enumerate(sorted_players):
        if i == 0:
            print(f"  {Fore.YELLOW}1. {player} 🏆{Style.RESET_ALL}")
        else:
            print(f"  {i+1}. {player}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGame terminated by user.")
        sys.exit(0) 