from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from src.core.database import get_db
from src.models.transaction import Transaction, TransactionType, AlertLevel

router = APIRouter()


# Pydantic schemas for API
class TransactionResponse(BaseModel):
    id: int
    source: str
    amount: float
    type: str
    description: str
    merchant_name: Optional[str] = None
    category: Optional[str] = None
    transaction_date: datetime
    is_flagged: bool
    alert_level: Optional[str] = None
    alert_reason: Optional[str] = None
    is_subscription: bool
    subscription_name: Optional[str] = None
    masked_card: Optional[str] = None

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    total: int
    transactions: list[TransactionResponse]


class StatementUploadResponse(BaseModel):
    message: str
    transactions_imported: int
    source: str


# ============== TRANSACTION ENDPOINTS ==============

@router.get("", response_model=TransactionListResponse)
async def get_transactions(
    source: Optional[str] = None,
    flagged_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """Get all transactions with optional filters."""
    query = select(Transaction)
    
    if source:
        query = query.where(Transaction.source == source)
    if flagged_only:
        query = query.where(Transaction.is_flagged == True)
    
    result = await db.execute(query)
    transactions = result.scalars().all()
    
    return TransactionListResponse(
        total=len(transactions),
        transactions=[TransactionResponse.model_validate(t) for t in transactions]
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single transaction by ID."""
    result = await db.execute(
        select(Transaction).where(Transaction.id == transaction_id)
    )
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return TransactionResponse.model_validate(transaction)


@router.post("/upload/statement", response_model=StatementUploadResponse)
async def upload_statement(
    source: str = Form(...),  # "account" | "wallet" | "card"
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload and parse a statement file (CSV or PDF).
    
    - **source**: One of "account", "wallet", or "card"
    - **file**: CSV or PDF statement file
    """
    if source not in ["account", "wallet", "card"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid source. Must be 'account', 'wallet', or 'card'"
        )
    
    if not file.filename.endswith(('.csv', '.pdf')):
        raise HTTPException(
            status_code=400,
            detail="File must be CSV or PDF"
        )
    
    # Read file content
    content = await file.read()
    
    # Import parser dynamically based on file type
    if file.filename.endswith('.csv'):
        from src.parsers.csv_parser import parse_csv_statement
        transactions = await parse_csv_statement(content, source)
    else:
        from src.parsers.pdf_parser import parse_pdf_statement
        transactions = await parse_pdf_statement(content, source)
    
    # Save to database
    for trans_data in transactions:
        trans = Transaction(**trans_data)
        db.add(trans)
    
    await db.commit()
    
    return StatementUploadResponse(
        message="Statement parsed successfully",
        transactions_imported=len(transactions),
        source=source,
    )


@router.get("/summary/monthly")
async def get_monthly_summary(
    year: int,
    month: int,
    db: AsyncSession = Depends(get_db),
):
    """Get monthly spending summary."""
    from datetime import datetime
    
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    result = await db.execute(
        select(Transaction).where(
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date < end_date,
        )
    )
    transactions = result.scalars().all()
    
    # Calculate summary
    total_spent = sum(t.amount for t in transactions if t.type == TransactionType.CARD_SPEND)
    total_income = sum(t.amount for t in transactions if t.type == TransactionType.PAYIN)
    total_fees = sum(abs(t.amount) for t in transactions if t.type == TransactionType.FEE)
    
    # Count by category
    by_category = {}
    for t in transactions:
        cat = t.category or "Uncategorized"
        by_category[cat] = by_category.get(cat, 0) + abs(t.amount)
    
    # Flagged transactions
    flagged = [t for t in transactions if t.is_flagged]
    
    return {
        "year": year,
        "month": month,
        "total_spent": total_spent,
        "total_income": total_income,
        "total_fees": total_fees,
        "net_flow": total_income - total_spent - total_fees,
        "by_category": by_category,
        "flagged_count": len(flagged),
        "flagged_transactions": [TransactionResponse.model_validate(t) for t in flagged],
    }
