"""
CSV Statement Parser for Wealify Financial Assistant.

Parses account, wallet, and card statements from CSV files.
Outputs rows in the column format expected by the ML feature pipeline
(ml/pipeline/features.py COLUMN_ALIASES).
"""
import io
import re
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
        List of transaction dictionaries with ML-feature-pipeline column names:
        So_tien, So_du, Phi, Ty_gia, Loai_giao_dich, Trang_thai,
        Don_vi_tien_te, Noi_dung, So_the, Thoi_gian.
        Plus DB fields: source, source_id, type, masked_card, category, etc.
    """
    text = content.decode('utf-8', errors='replace')
    df = pd.read_csv(io.StringIO(text))

    transactions = []
    for _, row in df.iterrows():
        try:
            trans = _parse_row(row, source)
            if trans:
                transactions.append(trans)
        except Exception as e:
            print(f"Error parsing row: {e}")
            continue

    return transactions


def _parse_row(row: pd.Series, source: str) -> Optional[dict]:
    """Parse a single CSV row into ML-feature + DB column format."""
    # Flexible column discovery
    date_col = _find_col(row, 'date', 'ngay', 'thoi gian', 'time')
    amount_col = _find_col(row, 'amount', 'sum', 'value', 'tien', 'số tiền', 'so tien')
    desc_col = _find_col(row, 'desc', 'memo', 'merchant', 'nội dung', 'noi dung',
                         'chuyen khoan', 'description', 'narr')
    card_col = _find_col(row, 'card', 'the', 'thẻ', 'masked', 'last4', 'last_4')
    balance_col = _find_col(row, 'balance', 'du', 'số dư', 'so du')
    fee_col = _find_col(row, 'fee', 'phi', 'phí', 'charge')
    currency_col = _find_col(row, 'currency', 'tien te', 'tiền tệ', 'unit')
    rate_col = _find_col(row, 'rate', 'ty gia', 'tỷ giá')
    status_col = _find_col(row, 'status', 'trang thai', 'trạng thái')
    type_col = _find_col(row, 'type', 'loai', 'loại')

    if not date_col or not amount_col:
        return None

    # Parse amount
    amount_str = str(row[amount_col]).replace(',', '').replace('$', '').replace(' ', '').strip()
    try:
        amount = float(amount_str)
    except ValueError:
        amount = 0.0

    # Parse date
    transaction_date = _parse_date(str(row[date_col]))

    # Parse optional fields
    balance = _parse_float(row.get(balance_col)) if balance_col else 0.0
    fee = _parse_float(row.get(fee_col)) if fee_col else 0.0
    currency = str(row[currency_col]) if currency_col and pd.notna(row.get(currency_col)) else 'VND'
    rate = _parse_float(row.get(rate_col)) if rate_col else 1.0
    description = str(row[desc_col]) if desc_col and pd.notna(row.get(desc_col)) else ""
    status_val = str(row[status_col]) if status_col and pd.notna(row.get(status_col)) else 'SUCCESS'
    type_val = str(row[type_col]) if type_col and pd.notna(row.get(type_col)) else ''

    # Extract card number
    card_raw = row.get(card_col) if card_col else None
    masked_card = None
    if card_raw and pd.notna(card_raw):
        card_str = str(card_raw)
        masked_card = card_str[-4:] if len(card_str) >= 4 else card_str if card_str else None

    # Build output dict with both ML-feature columns and DB columns
    return {
        # ML numeric features (required)
        'So_tien': abs(amount),
        'So_du': balance,
        'Phi': fee,
        'Ty_gia': rate,
        # ML categorical features (required)
        'Loai_giao_dich': type_val or _classify_type(source, amount),
        'Trang_thai': status_val,
        'Don_vi_tien_te': currency,
        'Noi_dung': description,
        'So_the': masked_card or '',
        # ML time feature (required - used to extract gio, ngay_trong_tuan, etc.)
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


def _find_col(row: pd.Series, *patterns: str) -> Optional[str]:
    """Find first column matching any pattern (normalized, case-insensitive)."""
    for col in row.index:
        col_lower = re.sub(r'[^a-z0-9]', '', str(col).lower())
        for pat in patterns:
            pat_norm = re.sub(r'[^a-z0-9]', '', pat.lower())
            if pat_norm and (pat_norm in col_lower or col_lower in pat_norm):
                return col
    return None


def _parse_float(val) -> float:
    if val is None or (hasattr(val, '__float__') and pd.isna(val)):
        return 0.0
    try:
        return float(str(val).replace(',', '').replace('$', '').strip())
    except ValueError:
        return 0.0


def _parse_date(date_str: str) -> datetime:
    date_str = str(date_str).strip()
    for fmt in [
        '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d',
        '%d/%m/%Y %H:%M:%S', '%d/%m/%Y', '%m/%d/%Y',
        '%Y/%m/%d', '%d-%m-%Y',
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
    for pattern in ['POS ', 'DEBIT ', 'CREDIT ', 'ATM ', 'PURCHASE ', 'PAYMENT ', 'TRANSFER ', 'IC/', 'OC/', 'VC/']:
        merchant = merchant.replace(pattern, '')
    parts = merchant.split()
    if parts:
        name = ''.join(c for c in parts[0] if c.isalpha())
        return name if len(name) > 2 else None
    return None
