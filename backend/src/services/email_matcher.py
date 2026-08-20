"""
Email Matching Service.

Matches transactions with email receipts for verification.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta

from src.models.transaction import Transaction


@dataclass
class EmailMatch:
    """Result of matching a transaction with email."""
    transaction_id: int
    email_subject: Optional[str]
    email_date: Optional[datetime]
    email_sender: Optional[str]
    match_status: str  # "matched" | "no_email_found" | "suspicious"
    confidence: float  # 0.0 - 1.0
    notes: Optional[str] = None


class EmailMatcher:
    """
    Service for matching transactions with email receipts.
    
    This is a placeholder implementation. Real implementation would:
    1. Connect to email via IMAP
    2. Search for emails around transaction date
    3. Match based on amount, merchant name, keywords
    """
    
    def __init__(self):
        self.matches: list[EmailMatch] = []
    
    async def match_transaction(
        self,
        transaction: Transaction,
        emails: list[dict]
    ) -> EmailMatch:
        """
        Match a single transaction with emails.
        
        Args:
            transaction: The transaction to match
            emails: List of email data (subject, sender, date, body)
        
        Returns:
            EmailMatch with match status
        """
        best_match = None
        best_confidence = 0.0
        
        for email in emails:
            confidence = self._calculate_confidence(transaction, email)
            if confidence > best_confidence and confidence > 0.5:
                best_match = email
                best_confidence = confidence
        
        if best_match:
            if best_confidence > 0.8:
                status = "matched"
            else:
                status = "suspicious"
            
            return EmailMatch(
                transaction_id=transaction.id,
                email_subject=best_match.get("subject"),
                email_date=best_match.get("date"),
                email_sender=best_match.get("sender"),
                match_status=status,
                confidence=best_confidence,
                notes=f"Matched with {best_match.get('subject', 'unknown')}"
            )
        
        return EmailMatch(
            transaction_id=transaction.id,
            email_subject=None,
            email_date=None,
            email_sender=None,
            match_status="no_email_found",
            confidence=0.0,
            notes="No matching email found"
        )
    
    def _calculate_confidence(self, transaction: Transaction, email: dict) -> float:
        """Calculate confidence score for a match."""
        score = 0.0
        factors = 0
        
        # Amount match (high weight)
        email_body = email.get("body", "").lower()
        transaction_amount = str(abs(transaction.amount))
        
        if transaction_amount in email_body or f"${transaction_amount}" in email_body:
            score += 0.4
        factors += 1
        
        # Merchant name match
        if transaction.merchant_name:
            merchant_lower = transaction.merchant_name.lower()
            if merchant_lower in email_body or merchant_lower in email.get("subject", "").lower():
                score += 0.3
        factors += 1
        
        # Date proximity
        email_date = email.get("date")
        if email_date and transaction.transaction_date:
            days_diff = abs((email_date - transaction.transaction_date).days)
            if days_diff <= 1:
                score += 0.2
            elif days_diff <= 3:
                score += 0.1
        factors += 1
        
        # Keywords match
        keywords = ["receipt", "confirmation", "order", "purchase", "payment", "invoice"]
        subject_lower = email.get("subject", "").lower()
        if any(kw in subject_lower for kw in keywords):
            score += 0.1
        factors += 1
        
        return score / factors if factors > 0 else 0.0
    
    async def match_all_transactions(
        self,
        transactions: list[Transaction],
        emails: list[dict]
    ) -> list[EmailMatch]:
        """Match all transactions with emails."""
        results = []
        for trans in transactions:
            match = await self.match_transaction(trans, emails)
            results.append(match)
        return results
