#!/usr/bin/env python3

import os
import sys
import argparse
from colorama import init, Fore, Style

from texas_holdem.game import TexasHoldemGame
from texas_holdem.player import HumanPlayer, AIPlayer
from agents.simple_agent import SimpleAgent

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    # Initialize colorama
    init()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Texas Hold\'em Poker')
    parser.add_argument('--mode', type=str, choices=['manual', 'ai'], default=None,
                        help='Game mode: manual for human players, ai for AI players')
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
        # Add a human player
        human_name = input(f"\n{Fore.CYAN}Enter your name: {Style.RESET_ALL}").strip() or "Human"
        players.append(HumanPlayer(human_name, starting_chips))
        
        # Add AI players
        for i in range(1, num_players):
            # Create AI players with varying aggression levels
            aggression = 0.3 + (i * 0.2)  # Varying aggression from 0.3 to 0.9
            agent = SimpleAgent(f"AI-{i}", aggression)
            players.append(AIPlayer(f"AI-{i}", starting_chips, agent))
    
    else:  # AI mode
        # Create AI players
        for i in range(num_players):
            # Create AI players with varying aggression levels
            aggression = 0.3 + (i * 0.6 / num_players)  # Distribute aggression levels
            agent = SimpleAgent(f"AI-{i+1}", aggression)
            players.append(AIPlayer(f"AI-{i+1}", starting_chips, agent))
    
    # Create and start the game
    game = TexasHoldemGame(players, small_blind, big_blind)
    
    print(f"\n{Fore.GREEN}Game starting with {len(players)} players!{Style.RESET_ALL}")
    print(f"Each player starts with ${starting_chips}")
    print(f"Blinds: ${small_blind}/${big_blind}")
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