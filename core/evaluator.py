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
            tuple: (hand_rank_index, hand_rank_name, best_hand, tiebreakers)
                hand_rank_index: Index of the hand rank (lower is better)
                hand_rank_name: Name of the hand rank (e.g., "Full House")
                best_hand: List of 5 Card objects representing the best hand
                tiebreakers: List of values for tiebreaking (higher is better)
        """
        all_cards = hole_cards + community_cards
        
        # 1. Check for Royal Flush and Straight Flush
        # First, check for flushes by suit
        suits = {}
        for card in all_cards:
            if card.suit not in suits:
                suits[card.suit] = []
            suits[card.suit].append(card)
        
        # For each suit with 5+ cards, check for a straight flush
        for suit, suited_cards in suits.items():
            if len(suited_cards) >= 5:
                # Sort by rank and check for straights
                suited_cards.sort(key=lambda x: x.rank_value, reverse=True)
                
                # Check for royal flush
                royal_ranks = {'A', 'K', 'Q', 'J', '10'}
                royal_flush = [c for c in suited_cards if c.rank in royal_ranks]
                if len(royal_flush) >= 5:
                    # We have a royal flush
                    royal_flush.sort(key=lambda x: x.rank_value, reverse=True)
                    return 0, cls.HAND_RANKINGS[0], royal_flush[:5], [0]
                
                # Check for straight flush - first remove duplicates
                unique_ranks = []
                seen_ranks = set()
                for card in suited_cards:
                    if card.rank not in seen_ranks:
                        unique_ranks.append(card)
                        seen_ranks.add(card.rank)
                
                # Check for A-5-4-3-2 straight flush
                if ('A' in seen_ranks and '5' in seen_ranks and '4' in seen_ranks and 
                    '3' in seen_ranks and '2' in seen_ranks):
                    # Get the cards for A-5-4-3-2 straight flush
                    ace = next(c for c in suited_cards if c.rank == 'A')
                    five = next(c for c in suited_cards if c.rank == '5')
                    four = next(c for c in suited_cards if c.rank == '4')
                    three = next(c for c in suited_cards if c.rank == '3')
                    two = next(c for c in suited_cards if c.rank == '2')
                    straight_flush = [five, four, three, two, ace]
                    return 1, cls.HAND_RANKINGS[1], straight_flush, [5]  # High card of straight is 5
                
                # Check for regular straight flush
                for i in range(len(unique_ranks) - 4):
                    # Check if 5 consecutive ranks
                    is_straight = True
                    for j in range(i, i+4):
                        if unique_ranks[j].rank_value != unique_ranks[j+1].rank_value + 1:
                            is_straight = False
                            break
                    
                    if is_straight:
                        straight_flush = unique_ranks[i:i+5]
                        # Tiebreaker is the high card
                        high_card_value = straight_flush[0].rank_value
                        return 1, cls.HAND_RANKINGS[1], straight_flush, [high_card_value]
                
                # If we got here, we just have a regular flush
                flush = suited_cards[:5]
                tiebreakers = [card.rank_value for card in flush]
                return 4, cls.HAND_RANKINGS[4], flush, tiebreakers
        
        # 2. Check for Four of a Kind
        four_kind = cls._get_n_of_a_kind(all_cards, 4)
        if four_kind:
            # Add a kicker to make 5 cards total
            kickers = [card for card in all_cards if card.rank != four_kind[0].rank]
            kickers.sort(key=lambda x: x.rank_value, reverse=True)
            best_hand = four_kind + [kickers[0]]
            
            # Tiebreakers: rank of the quad, then rank of the kicker
            quad_value = four_kind[0].rank_value
            kicker_value = kickers[0].rank_value
            return 2, cls.HAND_RANKINGS[2], best_hand, [quad_value, kicker_value]
        
        # 3. Check for Full House
        three_kind = cls._get_n_of_a_kind(all_cards, 3)
        if three_kind:
            remaining = [card for card in all_cards if card.rank != three_kind[0].rank]
            pair = cls._get_n_of_a_kind(remaining, 2)
            if pair:
                best_hand = three_kind + pair
                
                # Tiebreakers: rank of the trips, then rank of the pair
                trips_value = three_kind[0].rank_value
                pair_value = pair[0].rank_value
                return 3, cls.HAND_RANKINGS[3], best_hand, [trips_value, pair_value]
        
        # 4. Check for Flush - we already checked above, but check again in case there's no straight flush
        flush_cards = cls._get_flush_cards(all_cards)
        if flush_cards:
            # Tiebreakers: ranks of all 5 cards, from highest to lowest
            tiebreakers = [card.rank_value for card in flush_cards]
            return 4, cls.HAND_RANKINGS[4], flush_cards[:5], tiebreakers
        
        # 5. Check for Straight
        straight_cards = cls._get_straight_cards(all_cards)
        if straight_cards:
            # Tiebreaker: rank of the highest card in the straight
            high_card_value = straight_cards[0].rank_value
            return 5, cls.HAND_RANKINGS[5], straight_cards, [high_card_value]
        
        # 6. Check for Three of a Kind
        if three_kind:
            # Add two kickers
            kickers = [card for card in all_cards if card.rank != three_kind[0].rank]
            kickers.sort(key=lambda x: x.rank_value, reverse=True)
            best_hand = three_kind + kickers[:2]
            
            # Tiebreakers: rank of the trips, then ranks of the kickers
            trips_value = three_kind[0].rank_value
            tiebreakers = [trips_value] + [card.rank_value for card in kickers[:2]]
            return 6, cls.HAND_RANKINGS[6], best_hand, tiebreakers
        
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
            
            # Tiebreakers: rank of higher pair, rank of lower pair, rank of kicker
            high_pair_value = sorted_pairs[0][1][0].rank_value
            low_pair_value = sorted_pairs[1][1][0].rank_value
            kicker_value = kickers[0].rank_value
            return 7, cls.HAND_RANKINGS[7], best_hand, [high_pair_value, low_pair_value, kicker_value]
        
        # 8. Check for One Pair
        if pairs:
            # Add three kickers
            pair_rank = pairs[0].rank
            kickers = [card for card in all_cards if card.rank != pair_rank]
            kickers.sort(key=lambda x: x.rank_value, reverse=True)
            best_hand = pairs + kickers[:3]
            
            # Tiebreakers: rank of the pair, then ranks of the kickers
            pair_value = pairs[0].rank_value
            tiebreakers = [pair_value] + [card.rank_value for card in kickers[:3]]
            return 8, cls.HAND_RANKINGS[8], best_hand, tiebreakers
        
        # 9. High Card
        all_cards.sort(key=lambda x: x.rank_value, reverse=True)
        # Tiebreakers: ranks of all 5 cards, from highest to lowest
        tiebreakers = [card.rank_value for card in all_cards[:5]]
        return 9, cls.HAND_RANKINGS[9], all_cards[:5], tiebreakers
    
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
        
        # Sort cards by rank (descending)
        sorted_cards = sorted(cards, key=lambda x: x.rank_value, reverse=True)
        
        # Remove duplicates of the same rank - keep highest suit for each rank
        unique_ranks = []
        seen_ranks = set()
        for card in sorted_cards:
            if card.rank not in seen_ranks:
                unique_ranks.append(card)
                seen_ranks.add(card.rank)
        
        # Not enough unique ranks for a straight
        if len(unique_ranks) < 5:
            return None
        
        # Check for A-5-4-3-2 straight
        if (unique_ranks[0].rank == 'A' and
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
        
        # Check for regular straights by looking for 5 consecutive ranks
        for i in range(len(unique_ranks) - 4):
            # Check if cards form a sequence: each card is 1 rank lower than previous
            is_straight = True
            for j in range(i, i+4):
                if unique_ranks[j].rank_value != unique_ranks[j+1].rank_value + 1:
                    is_straight = False
                    break
            
            if is_straight:
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
        
    @classmethod
    def compare_hands(cls, hand1, hand2):
        """Compare two hands and determine which is better.
        
        Args:
            hand1 (tuple): First hand evaluation (rank_idx, name, cards, tiebreakers)
            hand2 (tuple): Second hand evaluation (rank_idx, name, cards, tiebreakers)
            
        Returns:
            int: 1 if hand1 is better, -1 if hand2 is better, 0 if equal
        """
        # Compare hand ranks first
        if hand1[0] < hand2[0]:  # Lower rank index is better
            return 1
        elif hand1[0] > hand2[0]:
            return -1
        
        # If ranks are equal, compare tiebreakers
        tiebreakers1 = hand1[3]
        tiebreakers2 = hand2[3]
        
        for i in range(min(len(tiebreakers1), len(tiebreakers2))):
            if tiebreakers1[i] > tiebreakers2[i]:
                return 1
            elif tiebreakers1[i] < tiebreakers2[i]:
                return -1
        
        # If all tiebreakers are equal, it's a tie
        return 0 