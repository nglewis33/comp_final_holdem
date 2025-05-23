# Texas Hold'em Architecture

This document provides a detailed explanation of the architecture of the Texas Hold'em poker game implementation, including the purpose of different files, algorithms used, and how the game state is managed.

## High-Level Architecture

The project follows a modular architecture with clear separation of concerns:

1. **Core Game Logic**: Implementation of poker rules, card management, hand evaluation
2. **Agent System**: Different AI strategies that can make decisions during gameplay
3. **Knowledge Base**: Preflop hand values and other poker knowledge
4. **Testing Framework**: Comprehensive tests for different components
5. **Main Game Interface**: Entry point for playing the game

## Core Components

### Card Representation (`core/card.py`)

The `Card` class represents a playing card with:
- Rank (2-10, J, Q, K, A)
- Suit (hearts, diamonds, clubs, spades)
- Methods for comparison and string representation
- Rank values for numeric comparison (2=0, 3=1, ..., A=12)

### Deck Management (`core/deck.py`)

The `Deck` class handles:
- Creating a standard 52-card deck
- Shuffling using Python's random module
- Dealing cards
- Tracking remaining cards

### Hand Evaluation (`core/evaluator.py`)

The `HandEvaluator` contains algorithms for:
- Evaluating the best 5-card poker hand from 7 cards (5 community + 2 hole cards)
- Identifying hand types (Royal Flush, Straight Flush, Four of a Kind, etc.)
- Computing tiebreakers for same hand types
- Comparing hands to determine winners

Key algorithms:
- Pattern matching for hand types (pairs, straights, flushes)
- Sorting and grouping cards by rank and suit
- Recursive evaluation of hand strength

### Game Engine (`core/game.py`)

The `TexasHoldemGame` class manages:
- Game flow through betting rounds (preflop, flop, turn, river)
- Betting rules and valid actions
- Pot management
- Showdown evaluation
- Player turns and dealer position

### Player Management (`core/player.py`)

Contains multiple player classes:
- `Player`: Base class for tracking cards, chips, and bets
- `HumanPlayer`: Handles console input for human players
- `AIPlayer`: Delegates decision-making to an agent

## Agent System

### Base Agent (`agents/base_agent.py`)

The `BaseAgent` abstract class defines the interface all agents must implement:
- `decide_action`: Takes game state, valid actions, and player info and returns an action

### Simple Agent (`agents/simple_agent.py`)

A rule-based agent that:
- Uses simple heuristics based on hand strength
- Factors in aggression level when making decisions
- Makes decisions based on basic pot odds

### Probability Agent (`agents/probability_agent.py`)

A more sophisticated agent that:
- Evaluates hand strength more accurately
- Uses position and pot odds in decision-making
- Varies bet sizing based on hand strength
- Implements strategic bluffing

### Enhanced Probability Agent (`agents/enhanced_probability_agent.py`)

An advanced agent that:
- Uses preflop hand values from professional poker strategy
- Makes more informed preflop decisions
- Adjusts strategy based on position
- Implements tight-aggressive or loose-aggressive playing styles

### Reinforcement Learning Agent (`agents/rl_agent.py`)

A learning agent that:
- Implements Q-learning using the Bellman equation
- Maintains a state-action value function (Q-values)
- Uses epsilon-greedy exploration/exploitation
- Learns from rewards after each hand
- Simplifies game state into a manageable representation

## Game State Management

The game state is primarily managed in `core/game.py` through the `TexasHoldemGame` class. The game state consists of:

### Key Game State Components

1. **Players**: List of player objects with their respective:
   - Chip stacks
   - Current bet amounts
   - Hole cards
   - Folded status
   - All-in status

2. **Community Cards**: Shared cards on the board

3. **Pot Information**:
   - Main pot amount
   - Side pots (if players are all-in)
   - Eligible players for each pot

4. **Betting Information**:
   - Current bet amount
   - Minimum raise amount
   - Last raiser position

5. **Game Phase**:
   - Preflop, Flop, Turn, River, or Showdown

6. **Positional Information**:
   - Dealer position
   - Current player to act
   - Small blind and big blind positions

### State Transitions

The game moves through phases:
1. **Initial State**: Dealer position set, blinds posted
2. **Preflop**: Hole cards dealt, first betting round
3. **Flop**: Three community cards dealt, betting round
4. **Turn**: Fourth community card dealt, betting round
5. **River**: Fifth community card dealt, final betting round
6. **Showdown**: Hand evaluation, pot distribution
7. **End of Hand**: Reset for next hand, dealer moves

The game state is passed to agents via a dictionary containing:
```python
{
    'phase': current_phase,
    'community_cards': list_of_community_cards,
    'pot': pot_amount,
    'current_bet': current_bet_amount,
    'min_raise': minimum_raise_amount,
    'players': list_of_player_objects,
    'dealer_idx': dealer_position,
    'current_idx': current_player_position
}
```

## Hand Evaluation Algorithms

The poker hand evaluation in `core/evaluator.py` uses the following approach:

1. **Hand Type Detection**:
   - First checks for the strongest hand types (Royal Flush, Straight Flush)
   - Then progressively tries weaker hand types
   - Returns the strongest hand type found

2. **Hand Comparison**:
   - First compares hand types (e.g., Flush beats Straight)
   - If hand types are equal, uses tiebreakers specific to that hand type:
     - For pairs: Compare pair rank, then kickers
     - For flushes: Compare highest card, then next highest, etc.
     - For straights: Compare highest card

3. **Best Hand Selection**:
   - For each hand type, selects the 5 best cards that form that hand
   - From the 7 available cards (2 hole + 5 community), finds optimal combination

## Preflop Hand Values

The system in `knowledge/preflop_hand_values.py` implements:

1. **Hand Grouping**:
   - Groups poker starting hands into 9 strength categories (1 being strongest)
   - Based on professional poker strategy

2. **Hand Expansion**:
   - Expands shorthand notations (like "AKs" or "TT") into specific card combinations
   - Maps each specific hand to its strength group

3. **Lookup System**:
   - Allows agents to quickly determine the strength of their preflop hand
   - Converts between hand notations and specific card combinations

## Utility Scripts

### Training RL Agents (`scripts/train_rl_agent.py`)

Implements:
- Environment for training RL agents against other agent types
- Episode-based training with configurable parameters
- Saving trained agents to files

### Hand Expansion (`utils/expand_preflop_hands.py`)

Used for:
- Converting poker hand notations to specific card combinations
- Processing preflop value charts into a usable format
- Supporting the preflop hand value system

## Testing Framework

The test modules include:

1. **Hand Evaluation Tests** (`tests/integration/test_poker_hands.py`):
   - Tests for correct hand ranking
   - Tests for tiebreaker resolution
   - Tests for special cases

2. **Probability Tests** (`tests/performance/test_hand_probabilities.py`):
   - Simulates large numbers of hands
   - Verifies hand probabilities match theoretical values
   - Creates charts of hand distribution

3. **Integration Tests** (`tests/e2e/test_final.py`):
   - End-to-end tests of game mechanics
   - Verifies correct winner determination in complex scenarios

## Conclusion

The architecture separates concerns well, with clear boundaries between:
- Core poker game logic
- AI agent strategies
- Knowledge representation
- Utilities and testing

This modular design allows for:
- Easy extension with new agent types
- Independent testing of components
- Clear game flow management

The use of algorithms from different domains (poker hand evaluation, reinforcement learning, probabilistic decision-making) creates a rich environment for poker AI research and development. 