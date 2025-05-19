#!/usr/bin/env python3

import os
import argparse
import numpy as np
from colorama import init, Fore, Style

from texas_holdem.game import TexasHoldemGame
from texas_holdem.player import AIPlayer
from agents.rl_agent import RLAgent
from agents.simple_agent import SimpleAgent

class TrainingEnvironment:
    """Environment for training RL agents to play Texas Hold'em."""
    
    def __init__(self, num_opponents=3, starting_chips=1000, small_blind=5, big_blind=10):
        """Initialize the training environment.
        
        Args:
            num_opponents (int): Number of opponents to train against
            starting_chips (int): Starting chips for each player
            small_blind (int): Small blind amount
            big_blind (int): Big blind amount
        """
        self.num_opponents = num_opponents
        self.starting_chips = starting_chips
        self.small_blind = small_blind
        self.big_blind = big_blind
        
        # Create the RL agent
        self.rl_agent = RLAgent("RLAgent", learning_rate=0.1, discount_factor=0.9, exploration_rate=0.2)
        
        # Create opponent agents with varying strategies
        self.opponents = []
        for i in range(num_opponents):
            aggression = 0.3 + (i * 0.2)
            agent = SimpleAgent(f"AI-{i+1}", aggression)
            self.opponents.append(agent)
        
        # Initialize the game
        self._setup_game()
    
    def _setup_game(self):
        """Set up a new game with the RL agent and opponents."""
        players = []
        
        # Create the RL player
        rl_player = AIPlayer("RL-Player", self.starting_chips, self.rl_agent)
        players.append(rl_player)
        
        # Create opponent players
        for opponent in self.opponents:
            players.append(AIPlayer(opponent.name, self.starting_chips, opponent))
        
        # Create the game
        self.game = TexasHoldemGame(players, self.small_blind, self.big_blind)
        self.rl_player_idx = 0  # Index of the RL agent in the players list
    
    def train(self, num_episodes=1000, verbose=False):
        """Train the RL agent for a specified number of episodes.
        
        Args:
            num_episodes (int): Number of training episodes (hands)
            verbose (bool): Whether to print detailed training progress
        """
        # Stats tracking
        episode_rewards = []
        win_count = 0
        
        for episode in range(1, num_episodes + 1):
            # Reset the game and player stacks for a new episode
            if episode > 1:
                self._setup_game()
            
            # Reset the RL agent's episode memory
            self.rl_agent.reset_episode()
            
            # Track initial stack
            initial_stack = self.game.players[self.rl_player_idx].stack
            
            # Play a hand
            self.game.play_hand()
            
            # Calculate reward (change in stack)
            final_stack = self.game.players[self.rl_player_idx].stack
            episode_reward = final_stack - initial_stack
            episode_rewards.append(episode_reward)
            
            # Count win
            if episode_reward > 0:
                win_count += 1
            
            # Update the RL agent's Q-values based on the reward
            self.rl_agent.update_q_values(episode_reward)
            
            # Print progress
            if verbose or episode % 100 == 0 or episode == num_episodes:
                win_rate = win_count / episode * 100
                avg_reward = np.mean(episode_rewards[-100:]) if len(episode_rewards) >= 100 else np.mean(episode_rewards)
                
                print(f"Episode {episode}/{num_episodes}")
                print(f"  Win rate: {win_rate:.2f}%")
                print(f"  Average reward (last 100): {avg_reward:.2f}")
                print(f"  Exploration rate: {self.rl_agent.exploration_rate:.4f}")
            
            # Gradually decrease exploration rate
            if self.rl_agent.exploration_rate > 0.05:
                self.rl_agent.exploration_rate *= 0.9999
        
        print(f"\n{Fore.GREEN}Training complete!{Style.RESET_ALL}")
        print(f"Final win rate: {win_count / num_episodes * 100:.2f}%")
        print(f"Final average reward: {np.mean(episode_rewards[-100:]):.2f}")
        
        return self.rl_agent
    
    def save_agent(self, filepath):
        """Save the trained agent to a file.
        
        Args:
            filepath (str): Path to save the agent
        """
        self.rl_agent.save_model(filepath)
        print(f"Agent saved to {filepath}")


def main():
    # Initialize colorama
    init()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Train an RL agent for Texas Hold\'em')
    parser.add_argument('--episodes', type=int, default=10000,
                        help='Number of training episodes')
    parser.add_argument('--opponents', type=int, default=3,
                        help='Number of opponents')
    parser.add_argument('--chips', type=int, default=1000,
                        help='Starting chips for each player')
    parser.add_argument('--small-blind', type=int, default=5,
                        help='Small blind amount')
    parser.add_argument('--big-blind', type=int, default=10,
                        help='Big blind amount')
    parser.add_argument('--verbose', action='store_true',
                        help='Print detailed training progress')
    parser.add_argument('--output', type=str, default='rl_agent.npy',
                        help='Output file to save the trained agent')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else '.', exist_ok=True)
    
    print(f"\n{Fore.CYAN}Starting RL agent training...{Style.RESET_ALL}")
    print(f"Training for {args.episodes} episodes against {args.opponents} opponents")
    
    # Create and train the agent
    env = TrainingEnvironment(
        num_opponents=args.opponents,
        starting_chips=args.chips,
        small_blind=args.small_blind,
        big_blind=args.big_blind
    )
    
    trained_agent = env.train(num_episodes=args.episodes, verbose=args.verbose)
    
    # Save the trained agent
    env.save_agent(args.output)
    
    print(f"\n{Fore.GREEN}Training complete!{Style.RESET_ALL}")
    print(f"Trained agent saved to {args.output}")


if __name__ == "__main__":
    main() 