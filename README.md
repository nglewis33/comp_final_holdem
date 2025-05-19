# Texas Hold'em Poker Environment

This project implements a Texas Hold'em poker environment suitable for both human play and AI agent development. The environment is designed with reinforcement learning in mind, supporting the implementation of the Bellman equation for training poker agents.

## Features

- Complete Texas Hold'em rules implementation
- Support for playing against AI agents or watching AI agents play against each other
- Clear visualization of game state in the CLI (valid actions, betting phase, cards, etc.)
- Modular design for easy extension
- Multiple agent types with different strategies:
  - Simple rule-based agents
  - Probability-based agents with hand strength evaluation
  - Enhanced probability agents using preflop hand rankings
  - Reinforcement learning agents using the Bellman equation
- Preflop hand value analysis based on professional poker strategy
- Ability to train and save RL agents

## Installation

1. Clone the repository
2. Install dependencies:
```
pip install -r requirements.txt
```

## Playing the Game

To start a game, run:

```
python main.py
```

You can customize the game with the following options:

- `--mode`: Game mode ('manual' for human player, 'ai' for AI-only play)
- `--agent-type`: Type of AI agent to use ('simple', 'probability', or 'enhanced')
- `--hands`: Number of hands to play
- `--chips`: Starting chips for each player
- `--small-blind`: Small blind amount
- `--big-blind`: Big blind amount
- `--players`: Number of players
- `--show-information`: Show helpful hand information during play

Example:

```
python main.py --mode manual --hands 5 --players 4 --chips 2000 --show-information
```

To play with enhanced probability agents that use preflop hand values:

```
python main.py --mode ai --agent-type enhanced --hands 10
```

## Using Poker Probability Tables

To make informed decisions in poker, it's recommended to reference established poker probability tables which can be found online. While playing, the game will show basic information like pot odds, but for accurate win probabilities at different stages (preflop, flop, turn, river), refer to these external resources.

Useful poker probability resources:
- Preflop hand charts - showing the relative strength of starting hands
- Odds charts for common drawing hands (flush draws, straight draws, etc.)
- Pot odds calculators

## Preflop Hand Values

The project includes preflop hand values based on professional poker strategy. These values group hands into strength categories and are used by the enhanced probability agents to make better preflop decisions. The preflop hand values are stored in CSV format and can be expanded into specific card combinations using the provided utility:

```
python tests/expand_preflop_hands.py preflop_values.csv
```

## Training an RL Agent

To train a reinforcement learning agent, run:

```
python scripts/train_rl_agent.py
```

Training options:

- `--episodes`: Number of training episodes
- `--opponents`: Number of opponents to train against
- `--chips`: Starting chips for each player
- `--small-blind`: Small blind amount
- `--big-blind`: Big blind amount
- `--verbose`: Show detailed training progress
- `--output`: Output file to save the trained agent

Example:

```
python scripts/train_rl_agent.py --episodes 5000 --opponents 3 --verbose
```

## Project Structure

- `core/`: Core poker game implementation
  - `card.py`: Card class
  - `deck.py`: Deck management
  - `evaluator.py`: Hand evaluation
  - `game.py`: Game engine
  - `player.py`: Player classes
- `agents/`: Agent implementations
  - `base_agent.py`: Base agent interface
  - `simple_agent.py`: Simple rule-based agent
  - `probability_agent.py`: Heuristic-based agent using basic hand strength
  - `enhanced_probability_agent.py`: Advanced agent using preflop hand values
  - `rl_agent.py`: Reinforcement learning agent
- `knowledge/`: Knowledge bases and utilities
  - `preflop_hand_values.py`: Utility for managing preflop hand values
- `scripts/`: Utility scripts
  - `train_rl_agent.py`: Script for training RL agents
- `tests/`: Test modules and utilities
  - `test_poker_hands.py`: Tests for hand evaluation
  - `test_hand_probabilities.py`: Tests for poker probabilities
  - `test_final.py`: Final integration tests
  - `expand_preflop_hands.py`: Utility for expanding hand notations
- `main.py`: Main entry point for playing the game

## Extending with Custom Agents

To create your own agent:

1. Create a new file in the `agents/` directory
2. Implement a class that inherits from `BaseAgent`
3. Implement the `decide_action` method that returns an action and amount

Example:

```python
from agents.base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    def __init__(self, name):
        super().__init__(name)
        
    def decide_action(self, game_state, valid_actions, player):
        # Your decision logic here
        return 'fold', 0
```

## Reinforcement Learning Details

The reinforcement learning agent uses:

- The Bellman equation for Q-learning
- State representation based on game phase, hand strength, pot odds, etc.
- Epsilon-greedy exploration strategy
- Experience replay for training stability

The agent learns from the rewards obtained after each hand, where the reward is the change in chip stack.

## License

MIT 