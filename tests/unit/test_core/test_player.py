import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from core.player import Player, HumanPlayer, AIPlayer
from core.card import Card


class TestPlayer:
    """Test cases for the abstract Player class."""
    
    def test_player_is_abstract(self):
        """Test that Player cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Player("Test", 1000)
    
    def test_player_subclass_implementation(self):
        """Test that a proper subclass can be created."""
        class TestPlayer(Player):
            def get_action(self, game_state, valid_actions):
                return 'fold', 0
        
        player = TestPlayer("Test", 1000)
        assert player.name == "Test"
        assert player.stack == 1000
        assert player.hole_cards == []
        assert player.is_folded == False
        assert player.is_all_in == False
        assert player.current_bet == 0


class TestHumanPlayer:
    """Test cases for the HumanPlayer class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.player = HumanPlayer("Alice", 1000)
    
    def test_human_player_initialization(self):
        """Test HumanPlayer initialization."""
        assert self.player.name == "Alice"
        assert self.player.stack == 1000
        assert self.player.hole_cards == []
        assert self.player.is_folded == False
        assert self.player.is_all_in == False
        assert self.player.current_bet == 0
    
    def test_receive_cards(self):
        """Test receiving cards."""
        cards = [Card('A', '♠'), Card('K', '♥')]
        self.player.receive_cards(cards)
        
        assert len(self.player.hole_cards) == 2
        assert self.player.hole_cards[0].rank == 'A'
        assert self.player.hole_cards[0].suit == 's'  # Internal representation
        assert self.player.hole_cards[1].rank == 'K'
        assert self.player.hole_cards[1].suit == 'h'  # Internal representation
    
    def test_receive_single_card(self):
        """Test receiving a single card."""
        card = Card('Q', '♦')
        self.player.receive_cards([card])
        
        assert len(self.player.hole_cards) == 1
        assert self.player.hole_cards[0].rank == 'Q'
        assert self.player.hole_cards[0].suit == 'd'  # Internal representation
    
    def test_place_bet_valid_amount(self):
        """Test placing a valid bet."""
        result = self.player.place_bet(100)
        
        assert result == 100
        assert self.player.stack == 900
        assert self.player.current_bet == 100
        assert self.player.is_all_in == False
    
    def test_place_bet_all_in(self):
        """Test placing a bet that results in all-in."""
        result = self.player.place_bet(1000)
        
        assert result == 1000
        assert self.player.stack == 0
        assert self.player.current_bet == 1000
        assert self.player.is_all_in == True
    
    def test_place_bet_more_than_stack(self):
        """Test placing a bet for more than available stack."""
        result = self.player.place_bet(1500)
        
        assert result == 1000  # Should only bet what's available
        assert self.player.stack == 0
        assert self.player.current_bet == 1000
        assert self.player.is_all_in == True
    
    def test_place_bet_negative_amount(self):
        """Test placing a negative bet."""
        result = self.player.place_bet(-100)
        
        assert result == -100  # Negative amounts are allowed
        assert self.player.stack == 1100  # stack -= -100 means stack += 100
        assert self.player.current_bet == -100
    
    def test_place_bet_zero_amount(self):
        """Test placing a zero bet."""
        result = self.player.place_bet(0)
        
        assert result == 0
        assert self.player.stack == 1000
        assert self.player.current_bet == 0
        assert self.player.is_all_in == False
    
    def test_multiple_bets(self):
        """Test multiple bets in same round."""
        self.player.place_bet(100)
        self.player.place_bet(200)
        
        assert self.player.stack == 700
        assert self.player.current_bet == 300  # Cumulative
    
    def test_fold(self):
        """Test folding."""
        self.player.fold()
        
        assert self.player.is_folded == True
    
    def test_reset_for_new_hand(self):
        """Test resetting player for new hand."""
        # Set up some state
        self.player.receive_cards([Card('A', '♠'), Card('K', '♥')])
        self.player.place_bet(100)
        self.player.fold()
        
        # Reset
        self.player.reset_for_new_hand()
        
        # Check that state is reset but stack is preserved
        assert self.player.hole_cards == []
        assert self.player.is_folded == False
        assert self.player.is_all_in == False
        assert self.player.current_bet == 0
        assert self.player.stack == 900  # Stack should be preserved
    
    def test_add_to_stack(self):
        """Test adding chips to stack."""
        self.player.add_to_stack(500)
        
        assert self.player.stack == 1500
    
    def test_add_negative_to_stack(self):
        """Test adding negative chips to stack."""
        self.player.add_to_stack(-200)
        
        assert self.player.stack == 800
    
    def test_string_representation(self):
        """Test string representation of player."""
        expected = "Alice ($1000)"
        assert str(self.player) == expected
    
    @patch('builtins.input', return_value='fold')
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_action_fold(self, mock_stdout, mock_input):
        """Test getting fold action from user input."""
        game_state = {'current_bet': 50, 'min_raise': 10}
        valid_actions = ['fold', 'call', 'raise']

        action, amount = self.player.get_action(game_state, valid_actions)
        
        assert action == 'fold'
        assert amount == 0
    
    @patch('builtins.input', return_value='call')
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_action_call(self, mock_stdout, mock_input):
        """Test getting call action from user input."""
        game_state = {'current_bet': 50, 'min_raise': 10}
        valid_actions = ['fold', 'call', 'raise']

        action, amount = self.player.get_action(game_state, valid_actions)
        
        assert action == 'call'
        assert amount == 50  # current_bet - self.current_bet (0)
    
    @patch('builtins.input', return_value='check')
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_action_check(self, mock_stdout, mock_input):
        """Test getting check action from user input."""
        game_state = {'current_bet': 0, 'min_raise': 10}
        valid_actions = ['fold', 'check', 'raise']

        action, amount = self.player.get_action(game_state, valid_actions)
        
        assert action == 'check'
        assert amount == 0
    
    @patch('builtins.input', side_effect=['raise 100'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_action_raise(self, mock_stdout, mock_input):
        """Test getting raise action from user input."""
        game_state = {'current_bet': 50, 'min_raise': 10}
        valid_actions = ['fold', 'call', 'raise']

        action, amount = self.player.get_action(game_state, valid_actions)
        
        assert action == 'raise'
        assert amount == 100
    
    @patch('builtins.input', side_effect=['raise invalid', 'raise 150'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_action_raise_invalid_amount(self, mock_stdout, mock_input):
        """Test getting raise action with invalid amount input."""
        game_state = {'current_bet': 50, 'min_raise': 10}
        valid_actions = ['fold', 'call', 'raise']

        action, amount = self.player.get_action(game_state, valid_actions)
        
        assert action == 'raise'
        assert amount == 150
    
    @patch('builtins.input', side_effect=['invalid', 'fold'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_action_invalid_then_valid(self, mock_stdout, mock_input):
        """Test getting action with invalid input followed by valid input."""
        game_state = {'current_bet': 50, 'min_raise': 10}
        valid_actions = ['fold', 'call', 'raise']

        action, amount = self.player.get_action(game_state, valid_actions)
        
        assert action == 'fold'
        assert amount == 0
    
    @patch('builtins.input', return_value='all-in')
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_action_all_in(self, mock_stdout, mock_input):
        """Test getting all-in action from user input."""
        game_state = {'current_bet': 50, 'min_raise': 10}
        valid_actions = ['fold', 'call', 'raise']
    
        action, amount = self.player.get_action(game_state, valid_actions)
        
        assert action == 'raise'
        assert amount == 1000  # Player's entire stack


class TestAIPlayer:
    """Test cases for the AIPlayer class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_agent = Mock()
        self.player = AIPlayer("Bot", 1000, self.mock_agent)
    
    def test_ai_player_initialization(self):
        """Test AIPlayer initialization."""
        assert self.player.name == "Bot"
        assert self.player.stack == 1000
        assert self.player.agent == self.mock_agent
    
    def test_ai_player_initialization_without_agent(self):
        """Test AIPlayer initialization without agent."""
        player = AIPlayer("Bot", 1000)
        
        assert player.name == "Bot"
        assert player.stack == 1000
        assert player.agent is None
    
    def test_get_action_with_agent(self):
        """Test getting action when AI agent is available."""
        self.mock_agent.decide_action.return_value = ('raise', 100)
        game_state = {'current_bet': 50, 'min_raise': 10}
        valid_actions = ['fold', 'call', 'raise']

        action, amount = self.player.get_action(game_state, valid_actions)
        
        assert action == 'raise'
        assert amount == 100
        self.mock_agent.decide_action.assert_called_once_with(game_state, valid_actions, self.player)
    
    def test_get_action_without_agent_fold(self):
        """Test getting action when no AI agent (should default to check/fold)."""
        player = AIPlayer("Bot", 1000)  # No agent
        game_state = {'current_bet': 50, 'min_raise': 10}
        valid_actions = ['fold', 'call', 'raise']

        action, amount = player.get_action(game_state, valid_actions)
        
        # Call amount is 50, which is 5% of 1000 stack (≤ 20%), so should call
        assert action == 'call'
        assert amount == 50
    
    def test_get_action_without_agent_check(self):
        """Test getting action when no AI agent and check is available."""
        player = AIPlayer("Bot", 1000)  # No agent
        game_state = {'current_bet': 0, 'min_raise': 10}
        valid_actions = ['fold', 'check', 'raise']

        action, amount = player.get_action(game_state, valid_actions)
        
        assert action == 'check'
        assert amount == 0
    
    def test_ai_agent_called_with_correct_parameters(self):
        """Test that AI agent is called with correct parameters."""
        self.mock_agent.decide_action.return_value = ('call', 50)

        # Set up some hole cards
        hole_cards = [Card('A', '♠'), Card('K', '♥')]
        self.player.receive_cards(hole_cards)

        game_state = {'current_bet': 75, 'min_raise': 10}
        valid_actions = ['fold', 'call', 'raise']

        self.player.get_action(game_state, valid_actions)

        # Verify agent was called with correct parameters
        self.mock_agent.decide_action.assert_called_once_with(game_state, valid_actions, self.player)
    
    def test_ai_agent_exception_handling(self):
        """Test handling of exceptions from AI agent."""
        self.mock_agent.decide_action.side_effect = Exception("AI Error")
        game_state = {'current_bet': 50, 'min_raise': 10}
        valid_actions = ['fold', 'call', 'raise']

        # Should propagate exception, not handle it gracefully
        with pytest.raises(Exception, match="AI Error"):
            self.player.get_action(game_state, valid_actions)
    
    def test_ai_player_inherits_player_methods(self):
        """Test that AIPlayer inherits all Player methods correctly."""
        # Test place_bet method
        result = self.player.place_bet(100)
        assert result == 100
        assert self.player.stack == 900
        
        # Test fold method
        self.player.fold()
        assert self.player.is_folded == True
        
        # Test reset method
        self.player.reset_for_new_hand()
        assert self.player.is_folded == False
    
    def test_ai_player_string_representation(self):
        """Test string representation of AI player."""
        expected = "Bot ($1000)"
        assert str(self.player) == expected


class TestPlayerEdgeCases:
    """Test edge cases and error conditions for Player classes."""
    
    def test_player_with_zero_stack(self):
        """Test player with zero stack."""
        player = HumanPlayer("Broke", 0)

        assert player.stack == 0
        assert player.is_all_in == False  # Not all-in until they bet

        # Betting should immediately make them all-in
        result = player.place_bet(100)
        assert result == 0  # min(100, 0) = 0
        assert player.is_all_in == True  # All-in because stack == 0 after place_bet call
    
    def test_player_with_negative_stack(self):
        """Test player with negative stack (debt)."""
        player = HumanPlayer("Debtor", -100)

        assert player.stack == -100
        
        # Betting should work with negative stack
        result = player.place_bet(50)
        assert result == -100  # min(50, -100) = -100
        assert player.stack == 0  # -100 - (-100) = 0
        assert player.is_all_in == True  # Now all-in since stack == 0
    
    def test_receive_empty_cards_list(self):
        """Test receiving empty cards list."""
        player = HumanPlayer("Test", 1000)
        player.receive_cards([])
        
        assert player.hole_cards == []
    
    def test_receive_none_cards(self):
        """Test receiving None as cards."""
        player = HumanPlayer("Test", 1000)
        player.receive_cards(None)
        
        assert player.hole_cards is None
    
    def test_place_bet_after_all_in(self):
        """Test placing bet after going all-in."""
        player = HumanPlayer("Test", 1000)
        
        # Go all-in
        player.place_bet(1000)
        assert player.is_all_in == True
        assert player.stack == 0
        
        # Try to bet more (should not be possible)
        result = player.place_bet(100)
        assert result == 0
        assert player.stack == 0
    
    def test_multiple_folds(self):
        """Test folding multiple times."""
        player = HumanPlayer("Test", 1000)
        
        player.fold()
        assert player.is_folded == True
        
        # Folding again should not change anything
        player.fold()
        assert player.is_folded == True
    
    def test_reset_preserves_stack(self):
        """Test that reset preserves stack count."""
        player = HumanPlayer("Test", 1000)
        
        # Bet some chips
        player.place_bet(300)
        assert player.stack == 700
        
        # Reset for new hand
        player.reset_for_new_hand()
        
        # Stack should be preserved, but current_bet should be reset
        assert player.stack == 700
        assert player.current_bet == 0
    
    @pytest.mark.parametrize("stack_amount", [0, 1, 100, 1000, 10000])
    def test_various_stack_amounts(self, stack_amount):
        """Test players with various stack amounts."""
        player = HumanPlayer("Test", stack_amount)
        
        assert player.stack == stack_amount
        assert player.name == "Test"
    
    @pytest.mark.parametrize("name", ["", "A", "Very Long Player Name", "Player123", "Player-With-Dashes"])
    def test_various_player_names(self, name):
        """Test players with various names."""
        player = HumanPlayer(name, 1000)
        
        assert player.name == name
        assert player.stack == 1000
