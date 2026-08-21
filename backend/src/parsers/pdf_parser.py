"""
PDF Statement Parser for Wealify Financial Assistant.

Parses account, wallet, and card statements from PDF files.
Outputs rows in the column format expected by the ML feature pipeline.
"""
import io
import re
from datetime import datetime
from typing import Optional
import pdfplumber

from src.models.transaction import TransactionType


async def parse_pdf_statement(content: bytes, source: str) -> list[dict]:
    """
    Parse a PDF statement file.

    Args:
        content: Raw PDF file content
        source: One of "account", "wallet", "card"

    Returns:
        List of transaction dictionaries with ML-feature-pipeline column names.
    """
    transactions = []

    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            # Extract tables
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

            # Also try plain text extraction
            text = page.extract_text()
            if text:
                text_transactions = _parse_text_lines(text, source)
                transactions.extend(text_transactions)

    return transactions


def _parse_table_row(row: list, source: str) -> Optional[dict]:
    """Parse a single table row into transaction data."""
    if len(row) < 3:
        return None

    # Find date column (usually first)
    date_str = str(row[0]) if row[0] else ""
    if not date_str.strip():
        return None

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
    description = ' '.join(description_parts).strip()

    # Parse date
    transaction_date = _parse_date(date_str)

    # Build output
    masked_card = None
    return {
        # ML numeric features
        'So_tien': abs(amount),
        'So_du': 0.0,
        'Phi': 0.0,
        'Ty_gia': 1.0,
        # ML categorical features
        'Loai_giao_dich': _classify_type(source, amount),
        'Trang_thai': 'SUCCESS',
        'Don_vi_tien_te': 'VND',
        'Noi_dung': description,
        'So_the': masked_card or '',
        'Thoi_gian': transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
        # DB fields
        'source': source,
        'source_id': f"{source}_{transaction_date.strftime('%Y%m%d')}_{abs(amount)}",
        'type': _classify_db_type(source, amount),
        'amount': abs(amount),
        'description': description,
        'merchant_name': _extract_merchant(description),
        'transaction_date': transaction_date,
        'masked_card': masked_card,
        'category': _categorize(source, amount, description),
    }


def _parse_text_lines(text: str, source: str) -> list[dict]:
    """Parse transactions from plain text lines (fallback when table extraction fails)."""
    import re as _re
    transactions = []
    date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
    amount_pattern = r'(-?\$?[\d,]+\.?\d*)'

    lines = text.split('\n')
    for line in lines:
        date_match = _re.search(date_pattern, line)
        amount_matches = _re.findall(amount_pattern, line)

        if date_match and len(amount_matches) >= 1:
            try:
                date_str = date_match.group(1)
                amount_str = amount_matches[-1].replace('$', '').replace(',', '')
                amount = float(amount_str)

                if abs(amount) < 0.01:
                    continue

                transaction_date = _parse_date(date_str)
                description = line.strip()

                transactions.append({
                    'So_tien': abs(amount),
                    'So_du': 0.0,
                    'Phi': 0.0,
                    'Ty_gia': 1.0,
                    'Loai_giao_dich': _classify_type(source, amount),
                    'Trang_thai': 'SUCCESS',
                    'Don_vi_tien_te': 'VND',
                    'Noi_dung': description,
                    'So_the': '',
                    'Thoi_gian': transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'source': source,
                    'source_id': f"{source}_{transaction_date.strftime('%Y%m%d')}_{abs(amount)}",
                    'type': _classify_db_type(source, amount),
                    'amount': abs(amount),
                    'description': description,
                    'merchant_name': _extract_merchant(description),
                    'transaction_date': transaction_date,
                    'masked_card': None,
                    'category': _categorize(source, amount, description),
                })
            except (ValueError, Exception):
                continue

    return transactions


def _parse_date(date_str: str) -> datetime:
    date_str = date_str.strip()
    for fmt in [
        '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y',
        '%Y/%m/%d', '%b %d, %Y', '%B %d, %Y',
        '%d/%m/%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S',
    ]:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return datetime.now()


def _classify_db_type(source: str, amount: float) -> TransactionType:
    if amount >= 0:
        return TransactionType.PAYIN
    if source == 'card':
        return TransactionType.CARD_SPEND
    return TransactionType.PAYOUT


def _classify_type(source: str, amount: float) -> str:
    if amount >= 0:
        return 'PAYIN'
    if source == 'card':
        return 'CARD_SPEND'
    if source == 'wallet':
        return 'WALLET_PAYOUT'
    return 'PAYOUT'


def _categorize(source: str, amount: float, description: str) -> str:
    desc_lower = description.lower()
    if any(w in desc_lower for w in ['netflix', 'spotify', 'youtube', 'apple', 'amazon', 'disney', 'hbo', 'prime', 'tidal']):
        return 'Giải trí'
    if any(w in desc_lower for w in ['grab', 'gojek', 'be ', 'shopee', 'lazada', 'tiki']):
        return 'Mua sắm'
    if any(w in desc_lower for w in ['evn', 'điện', 'nước', 'internet', 'fpt', 'viettel', 'vnpt']):
        return 'Hóa đơn'
    if any(w in desc_lower for w in ['fee', 'phí', 'charge', 'annual', 'phí thường niên']):
        return 'Phí ngân hàng'
    if amount > 0:
        return 'Thu nhập'
    return 'Khác'


def _extract_merchant(description: str) -> Optional[str]:
    if not description:
        return None
    merchant = description
    for pattern in ['POS ', 'DEBIT ', 'CREDIT ', 'PURCHASE ', 'PAYMENT ']:
        merchant = merchant.replace(pattern, '')
    parts = merchant.split()
    if parts:
        name = ''.join(c for c in parts[0] if c.isalpha())
        return name if len(name) > 2 else None
    return None
