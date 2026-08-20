"""
PDF Statement Parser for Wealify Financial Assistant.

Parses account, wallet, and card statements from PDF files.
"""
from datetime import datetime
from typing import Optional
import io
import pdfplumber

from src.models.transaction import TransactionType


async def parse_pdf_statement(content: bytes, source: str) -> list[dict]:
    """
    Parse a PDF statement file.
    
    Args:
        content: Raw PDF file content
        source: One of "account", "wallet", "card"
    
    Returns:
        List of transaction dictionaries ready for database insertion
    """
    transactions = []
    
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            # Extract tables from the page
            tables = page.extract_tables()
            
            for table in tables:
                for row in table:
                    if not row or len(row) < 3:
                        continue
                    
                    try:
                        trans = _parse_table_row(row, source)
                        if trans:
                            transactions.append(trans)
                    except Exception as e:
                        print(f"Error parsing table row: {e}")
                        continue
            
            # Also try to extract text for additional parsing
            text = page.extract_text()
            if text:
                text_transactions = _parse_text_lines(text, source)
                transactions.extend(text_transactions)
    
    return transactions


def _parse_table_row(row: list, source: str) -> Optional[dict]:
    """Parse a single table row into transaction data."""
    # Expected columns: Date, Description, Amount (may vary)
    if len(row) < 3:
        return None
    
    # Find date column (usually first)
    date_str = str(row[0]) if row[0] else ""
    
    # Find amount column
    amount = 0.0
    amount_col_idx = -1
    for i, cell in enumerate(row):
        if cell:
            cell_str = str(cell).replace(',', '').replace('$', '').strip()
            try:
                if '-' in cell_str or cell_str.replace('.', '').replace('-', '').isdigit():
                    amount = float(cell_str)
                    amount_col_idx = i
                    break
            except ValueError:
                continue
    
    if amount_col_idx == -1:
        return None
    
    # Get description from remaining columns
    description_parts = [str(row[i]) for i in range(1, len(row)) if i != amount_col_idx]
    description = ' '.join(description_parts)
    
    # Parse date
    transaction_date = _parse_date(date_str)
    
    # Determine transaction type
    trans_type = _classify_transaction(source, amount, description)
    
    # Extract merchant
    merchant_name = _extract_merchant(description)
    
    return {
        'source': source,
        'source_id': f"{source}_{transaction_date.strftime('%Y%m%d')}_{abs(amount)}",
        'type': trans_type,
        'amount': abs(amount),
        'description': description,
        'merchant_name': merchant_name,
        'transaction_date': transaction_date,
    }


def _parse_text_lines(text: str, source: str) -> list[dict]:
    """
    Parse transactions from plain text lines.
    Useful for extracting data when table extraction fails.
    """
    transactions = []
    
    # Common date patterns
    import re
    
    # Pattern: date followed by amount
    date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
    amount_pattern = r'(-?\$?[\d,]+\.?\d*)'
    
    lines = text.split('\n')
    for line in lines:
        # Try to find date and amount in the same line
        date_match = re.search(date_pattern, line)
        amount_matches = re.findall(amount_pattern, line)
        
        if date_match and len(amount_matches) >= 1:
            try:
                date_str = date_match.group(1)
                amount_str = amount_matches[-1].replace('$', '').replace(',', '')
                amount = float(amount_str)
                
                if abs(amount) < 0.01:  # Skip zero amounts
                    continue
                
                transaction_date = _parse_date(date_str)
                trans_type = _classify_transaction(source, amount, line)
                
                transactions.append({
                    'source': source,
                    'source_id': f"{source}_{transaction_date.strftime('%Y%m%d')}_{abs(amount)}",
                    'type': trans_type,
                    'amount': abs(amount),
                    'description': line.strip(),
                    'merchant_name': _extract_merchant(line),
                    'transaction_date': transaction_date,
                })
            except (ValueError, Exception) as e:
                continue
    
    return transactions


def _parse_date(date_str: str) -> datetime:
    """Parse date string to datetime."""
    # Try multiple formats
    formats = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%m/%d/%Y',
        '%d-%m-%Y',
        '%Y/%m/%d',
        '%b %d, %Y',
        '%B %d, %Y',
    ]
    
    date_str = date_str.strip()
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return datetime.now()


def _classify_transaction(source: str, amount: float, description: str) -> TransactionType:
    """Classify transaction type."""
    desc_lower = description.lower()
    
    if source == "account":
        if amount > 0:
            return TransactionType.PAYIN
        else:
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
    
    # Remove common prefixes
    prefixes = ['POS ', 'DEBIT ', 'CREDIT ', 'PURCHASE ', 'PAYMENT ']
    text = description
    for prefix in prefixes:
        text = text.replace(prefix, '')
    
    parts = text.split()
    if parts:
        return parts[0][:50] if parts[0] else None
    
    return None
