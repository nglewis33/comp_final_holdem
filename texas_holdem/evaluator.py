from collections import Counter

class HandEvaluator:
    """Class for evaluating poker hands."""
    
    # Hand rankings from highest to lowest
    HAND_RANKINGS = [
        "Royal Flush",
        "Straight Flush",
        "Four of a Kind",
        "Full House",
        "Flush",
        "Straight",
        "Three of a Kind", 
        "Two Pair",
        "One Pair",
        "High Card"
    ]
    
    @classmethod
    def evaluate_hand(cls, hole_cards, community_cards):
        """Evaluate the best 5-card hand from hole cards and community cards.
        
        Args:
            hole_cards (list): List of 2 Card objects (player's hole cards)
            community_cards (list): List of up to 5 Card objects (community cards)
            
        Returns:
            tuple: (hand_rank_index, hand_rank_name, best_hand)
                hand_rank_index: Index of the hand rank (lower is better)
                hand_rank_name: Name of the hand rank (e.g., "Full House")
                best_hand: List of 5 Card objects representing the best hand
        """
        all_cards = hole_cards + community_cards
        
        # Check all possible 5-card combinations
        best_hand_rank = len(cls.HAND_RANKINGS) - 1  # Default to high card (worst hand)
        best_hand = []
        
        # 1. Check for Royal Flush and Straight Flush
        flush_cards = cls._get_flush_cards(all_cards)
        if flush_cards:
            straight_flush_cards = cls._get_straight_cards(flush_cards)
            if straight_flush_cards:
                if straight_flush_cards[0].rank == 'A':  # Check if it's a royal flush
                    return 0, cls.HAND_RANKINGS[0], straight_flush_cards
                else:
                    return 1, cls.HAND_RANKINGS[1], straight_flush_cards
        
        # 2. Check for Four of a Kind
        four_kind = cls._get_n_of_a_kind(all_cards, 4)
        if four_kind:
            # Add a kicker to make 5 cards total
            kickers = [card for card in all_cards if card.rank != four_kind[0].rank]
            kickers.sort(key=lambda x: x.rank_value, reverse=True)
            best_hand = four_kind + [kickers[0]]
            return 2, cls.HAND_RANKINGS[2], best_hand
        
        # 3. Check for Full House
        three_kind = cls._get_n_of_a_kind(all_cards, 3)
        if three_kind:
            remaining = [card for card in all_cards if card.rank != three_kind[0].rank]
            pair = cls._get_n_of_a_kind(remaining, 2)
            if pair:
                best_hand = three_kind + pair
                return 3, cls.HAND_RANKINGS[3], best_hand
        
        # 4. Check for Flush
        if flush_cards:
            return 4, cls.HAND_RANKINGS[4], flush_cards[:5]
        
        # 5. Check for Straight
        straight_cards = cls._get_straight_cards(all_cards)
        if straight_cards:
            return 5, cls.HAND_RANKINGS[5], straight_cards
        
        # 6. Check for Three of a Kind
        if three_kind:
            # Add two kickers
            kickers = [card for card in all_cards if card.rank != three_kind[0].rank]
            kickers.sort(key=lambda x: x.rank_value, reverse=True)
            best_hand = three_kind + kickers[:2]
            return 6, cls.HAND_RANKINGS[6], best_hand
        
        # 7. Check for Two Pair
        pairs = cls._get_pairs(all_cards)
        if len(pairs) >= 4:  # We have at least 2 pairs (4 cards)
            # Group pairs by rank and take the two highest pairs
            pair_dict = {}
            for card in pairs:
                if card.rank not in pair_dict:
                    pair_dict[card.rank] = []
                pair_dict[card.rank].append(card)
            
            # Sort pairs by rank value
            sorted_pairs = sorted(pair_dict.items(), key=lambda x: x[1][0].rank_value, reverse=True)
            best_pairs = []
            for rank, cards in sorted_pairs[:2]:  # Take top 2 pairs
                best_pairs.extend(cards)
            
            # Add a kicker
            used_ranks = [card.rank for card in best_pairs]
            kickers = [card for card in all_cards if card.rank not in used_ranks]
            kickers.sort(key=lambda x: x.rank_value, reverse=True)
            best_hand = best_pairs + [kickers[0]]
            return 7, cls.HAND_RANKINGS[7], best_hand
        
        # 8. Check for One Pair
        if pairs:
            # Add three kickers
            pair_rank = pairs[0].rank
            kickers = [card for card in all_cards if card.rank != pair_rank]
            kickers.sort(key=lambda x: x.rank_value, reverse=True)
            best_hand = pairs + kickers[:3]
            return 8, cls.HAND_RANKINGS[8], best_hand
        
        # 9. High Card
        all_cards.sort(key=lambda x: x.rank_value, reverse=True)
        return 9, cls.HAND_RANKINGS[9], all_cards[:5]
    
    @classmethod
    def _get_flush_cards(cls, cards):
        """Get the cards that form a flush (5 or more cards of the same suit)."""
        suits = {}
        for card in cards:
            if card.suit not in suits:
                suits[card.suit] = []
            suits[card.suit].append(card)
        
        for suit, suited_cards in suits.items():
            if len(suited_cards) >= 5:
                # Sort by rank and return the 5 highest cards
                suited_cards.sort(key=lambda x: x.rank_value, reverse=True)
                return suited_cards[:5]
        
        return None
    
    @classmethod
    def _get_straight_cards(cls, cards):
        """Get the cards that form a straight (5 consecutive ranks)."""
        if len(cards) < 5:
            return None
        
        # Sort cards by rank
        sorted_cards = sorted(cards, key=lambda x: x.rank_value, reverse=True)
        
        # Remove duplicates of the same rank
        unique_ranks = []
        prev_rank = None
        for card in sorted_cards:
            if card.rank != prev_rank:
                unique_ranks.append(card)
                prev_rank = card.rank
        
        # Check for A-5-4-3-2 straight
        if (len(unique_ranks) >= 5 and
            unique_ranks[0].rank == 'A' and
            any(c.rank == '5' for c in unique_ranks) and
            any(c.rank == '4' for c in unique_ranks) and
            any(c.rank == '3' for c in unique_ranks) and
            any(c.rank == '2' for c in unique_ranks)):
            # Find the actual cards for A-5-4-3-2
            ace = next(c for c in unique_ranks if c.rank == 'A')
            five = next(c for c in unique_ranks if c.rank == '5')
            four = next(c for c in unique_ranks if c.rank == '4')
            three = next(c for c in unique_ranks if c.rank == '3')
            two = next(c for c in unique_ranks if c.rank == '2')
            return [five, four, three, two, ace]  # Note: A is low in this case
        
        # Check for regular straights
        for i in range(len(unique_ranks) - 4):
            if unique_ranks[i].rank_value == unique_ranks[i+4].rank_value + 4:
                return unique_ranks[i:i+5]
        
        return None
    
    @classmethod
    def _get_n_of_a_kind(cls, cards, n):
        """Get n cards of the same rank."""
        rank_counts = Counter(card.rank for card in cards)
        for rank, count in rank_counts.items():
            if count >= n:
                matching_cards = [card for card in cards if card.rank == rank]
                return matching_cards[:n]
        return None
    
    @classmethod
    def _get_pairs(cls, cards):
        """Get all pairs from the cards."""
        pairs = []
        rank_counts = Counter(card.rank for card in cards)
        for rank, count in rank_counts.items():
            if count >= 2:
                matching_cards = [card for card in cards if card.rank == rank]
                pairs.extend(matching_cards[:2])
        return pairs 