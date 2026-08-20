"""
CSV Statement Parser for Wealify Financial Assistant.

Parses account, wallet, and card statements from CSV files.
"""
import io
from datetime import datetime
from typing import Optional
import pandas as pd

from src.models.transaction import TransactionType


async def parse_csv_statement(content: bytes, source: str) -> list[dict]:
    """
    Parse a CSV statement file.
    
    Args:
        content: Raw CSV file content
        source: One of "account", "wallet", "card"
    
    Returns:
        List of transaction dictionaries ready for database insertion
    """
    # Decode content
    text = content.decode('utf-8', errors='replace')
    df = pd.read_csv(io.StringIO(text))
    
    transactions = []
    
    for _, row in df.iterrows():
        try:
            trans = _parse_row(row, source)
            if trans:
                transactions.append(trans)
        except Exception as e:
            # Log error but continue parsing
            print(f"Error parsing row: {e}")
            continue
    
    return transactions


def _parse_row(row: pd.Series, source: str) -> Optional[dict]:
    """Parse a single CSV row into transaction data."""
    # Common column name mappings
    date_col = None
    amount_col = None
    desc_col = None
    
    # Try common column names
    for col in row.index:
        col_lower = str(col).lower()
        if 'date' in col_lower:
            date_col = col
        elif 'amount' in col_lower or 'sum' in col_lower or 'value' in col_lower:
            amount_col = col
        elif 'desc' in col_lower or 'memo' in col_lower or 'merchant' in col_lower or 'nội dung' in col_lower:
            desc_col = col
    
    if not date_col or not amount_col:
        return None
    
    # Parse date
    date_str = str(row[date_col])
    try:
        # Try multiple date formats
        for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']:
            try:
                transaction_date = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        else:
            transaction_date = datetime.now()
    except Exception:
        transaction_date = datetime.now()
    
    # Parse amount
    amount_str = str(row[amount_col]).replace(',', '').replace('$', '').replace(' ', '')
    try:
        amount = float(amount_str)
    except ValueError:
        amount = 0.0
    
    # Parse description
    description = str(row[desc_col]) if desc_col and pd.notna(row.get(desc_col)) else ""
    
    # Determine transaction type based on source and amount
    trans_type = _classify_transaction(source, amount, description)
    
    # Extract merchant name if possible
    merchant_name = _extract_merchant(description)
    
    # Create transaction dict
    trans = {
        'source': source,
        'source_id': f"{source}_{transaction_date.strftime('%Y%m%d')}_{abs(amount)}",
        'type': trans_type,
        'amount': abs(amount),
        'description': description,
        'merchant_name': merchant_name,
        'transaction_date': transaction_date,
        # Masked card (last 4 digits) - only for card source
        'masked_card': row.get('last_4', None) if source == 'card' else None,
    }
    
    return trans


def _classify_transaction(source: str, amount: float, description: str) -> TransactionType:
    """Classify transaction type based on source, amount, and description."""
    desc_lower = description.lower()
    
    if source == "account":
        if amount > 0:
            if 'transfer' in desc_lower or 'chuyển' in desc_lower:
                return TransactionType.CARD_TRANSFER
            return TransactionType.PAYIN
        else:
            if 'fee' in desc_lower or 'phí' in desc_lower:
                return TransactionType.FEE
            return TransactionType.PAYOUT
    elif source == "wallet":
        if amount > 0:
            return TransactionType.PAYIN
        else:
            return TransactionType.PAYOUT
    elif source == "card":
        if amount > 0:
            return TransactionType.CARD_SPEND
        else:
            return TransactionType.REFUND
    
    return TransactionType.CARD_SPEND


def _extract_merchant(description: str) -> Optional[str]:
    """Extract merchant name from transaction description."""
    if not description:
        return None
    
    # Common patterns to remove
    patterns_to_remove = [
        'POS ', 'DEBIT ', 'CREDIT ', 'ATM ',
        'PURCHASE ', 'PAYMENT ', 'TRANSFER ',
        'IC/', 'OC/', 'VC/',  # Bank codes
    ]
    
    merchant = description
    for pattern in patterns_to_remove:
        merchant = merchant.replace(pattern, '')
    
    # Take first meaningful part
    parts = merchant.split()
    if parts:
        # Remove numbers and special chars from first part
        name = ''.join(c for c in parts[0] if c.isalpha())
        return name if len(name) > 2 else None
    
    return None
