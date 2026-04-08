import json
import os
import re

def evaluate_psych_signal(content, sender, config, subject_identifiers=None):
    """
    Mult-stage behavioral filter.
    1. Aggressive Spam/Newsletter Rejector
    2. Business/Utility Logic (High Priority Records)
    3. Personal Psychological Density (Interaction Logic)
    """
    content_lower = content.lower()
    word_count = len(content_lower.split())
    
    # --- STAGE 1: THE JUNK GUILLOTINE ---
    # Common markers of automated marketing/newsletters
    junk_markers = [
        'unsubscribe', 'view in browser', 'manage preferences', 
        'privacy policy', 'all rights reserved', 'click here to',
        'sent to you because', 'opt out'
    ]
    
    # If it contains multiple junk markers, it's out
    junk_hits = sum(1 for m in junk_markers if m in content_lower)
    if junk_hits >= 2:
        return 0.0, False, "spam"

    # Stage 1b: Domain rejection (if possible to infer from sender)
    if any(x in sender.lower() for x in ['no-reply', 'noreply', 'notifications@', 'marketing']):
        # Still allow it if it's business high-signal (handled in Stage 2)
        pass
    
    # --- STAGE 2: BUSINESS/UTILITY/OSINT PASS ---
    # High-signal keywords for life-records
    utility_keywords = [
        'receipt', 'confirmation', 'order', 'invoice', 'payment',
        'statement', 'account created', 'security alert', 'login',
        'tracking', 'shipped', 'delivered', 'appointment', 'reservation',
        'subscription', 'banking', 'transaction', 'transfer',
        'discovered', 'registered on', 'breach', 'compromised',
        'court record', 'case record', 'offender record', 'court case'
    ]
    
    is_utility = any(u in content_lower for u in utility_keywords)
    if is_utility and word_count > 2:
        # High score for utility/OSINT records, they are forensics gold
        return 8.0, True, "utility"

    # --- STAGE 3: PERSONAL PSYCHOLOGICAL DENSITY ---
    # Noise floor
    if word_count < 4: return 0.0, False, "noise"

    score = 0.0
    
    # Introspection and Emotional Weight
    introspection = ['i', 'me', 'my', 'mine', 'myself']
    emotional = ['feel', 'think', 'want', 'hope', 'wish', 'believe', 'love', 'hate', 'miss', 'sorry']
    
    # Identity Bonus (Is the subject talking?)
    if subject_identifiers:
        for ident in subject_identifiers:
            if ident.lower() in sender.lower():
                score += 3.0 # Heavy weight for self-authored content
                break

    score += sum(1.5 for w in content_lower.split() if w in introspection)
    score += sum(2.0 for w in content_lower.split() if w in emotional)
    
    # Length Bonuses
    if word_count > 12: score += 1.0
    if word_count > 30: score += 2.0

    min_score = config.get("filter_settings", {}).get("min_psych_score", 3.0)
    
    # Final check
    is_valid = score >= min_score
    return score, is_valid, "personal"
