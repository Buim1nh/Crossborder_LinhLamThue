"""
File upload & parse endpoints.
Handles CSV / PDF statement uploads from the 3 sources (account, wallet, card).
"""
import io
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.api.deps import get_current_active_user
from src.models.user import User
from src.models.transaction import Transaction, TransactionType
from src.parsers.csv_parser import parse_csv_statement
from src.parsers.pdf_parser import parse_pdf_statement
from src.services.subscription_model import score_transactions

router = APIRouter()

# Map FE source keys to BE source keys
_SOURCE_MAP = {"bank": "account", "wallet": "wallet", "card": "card"}


@router.post("/upload")
async def upload_statement(
    source: str = Form(..., description="bank | wallet | card"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Upload a statement file (CSV or PDF), parse it, store transactions,
    and run ML subscription scoring on them.
    """
    be_source = _SOURCE_MAP.get(source)
    if not be_source:
        raise HTTPException(
            status_code=400,
            detail="source must be one of: bank, wallet, card",
        )

    # Read file content
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    # Parse based on file type
    suffix = file.filename or ""
    if suffix.lower().endswith(".csv"):
        try:
            parsed_rows = await parse_csv_statement(content, be_source)
            # DEBUG: log parsed count
            print(f"[DEBUG] CSV parsed: {len(parsed_rows)} rows, filename={file.filename}")
        except Exception as exc:
            import traceback; traceback.print_exc()
            raise HTTPException(
                status_code=422,
                detail=f"CSV parsing failed: {exc}",
            ) from exc
    elif suffix.lower().endswith(".pdf"):
        try:
            parsed_rows = await parse_pdf_statement(content, be_source)
        except Exception as exc:
            raise HTTPException(
                status_code=422,
                detail=f"PDF parsing failed: {exc}",
            ) from exc
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a .csv or .pdf file.",
        )

    if not parsed_rows:
        raise HTTPException(
            status_code=422,
            detail="No transactions could be parsed from this file.",
        )

    # Run ML scoring (pass raw rows — the model normalizes column names)
    try:
        ml_results = score_transactions(parsed_rows)
    except Exception as exc:
        # ML scoring is best-effort; log and continue without scores
        ml_results = [
            {"subscription_proba": 0.0, "is_subscription": 0, "model_version": "unavailable"}
            for _ in parsed_rows
        ]

    # Save transactions to DB
    saved = []
    for row, ml in zip(parsed_rows, ml_results):
        try:
            # Resolve TransactionType
            type_str = row.get("type")
            if isinstance(type_str, TransactionType):
                tx_type = type_str
            elif isinstance(type_str, str):
                try:
                    tx_type = TransactionType(type_str)
                except ValueError:
                    tx_type = TransactionType.CARD_SPEND
            else:
                tx_type = TransactionType.CARD_SPEND

            tx = Transaction(
                user_id=current_user.id,
                source=be_source,
                source_id=str(row.get("source_id", "")),
                type=tx_type,
                amount=float(row.get("amount", 0)),
                currency=str(row.get("currency", "VND")),
                description=str(row.get("description", "")),
                merchant_name=row.get("merchant_name"),
                category=row.get("category"),
                transaction_date=row.get("transaction_date"),
                masked_card=row.get("masked_card"),
                is_subscription=bool(ml.get("is_subscription", 0)),
            )
            db.add(tx)
            saved.append(ml)
        except Exception:
            # Skip malformed rows
            continue

    await db.commit()

    return {
        "source": source,
        "file_name": file.filename,
        "total_parsed": len(parsed_rows),
        "total_saved": len(saved),
        "n_subscriptions": sum(1 for r in saved if r.get("is_subscription")),
        "scored": [
            {
                "subscription_proba": r.get("subscription_proba", 0),
                "is_subscription": r.get("is_subscription", 0),
                "model_version": r.get("model_version", ""),
            }
            for r in saved
        ],
    }
