"""
Report Generation Service.

Generates:
- Monthly/Quarterly/Yearly spending reports
- Anomaly reports
- Export-ready reports (PDF, Markdown)
"""
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass

from src.models.transaction import Transaction, TransactionType


@dataclass
class SpendingReport:
    """Monthly/quarterly/annual spending report."""
    period: str  # "monthly" | "quarterly" | "yearly"
    year: int
    month: Optional[int]
    quarter: Optional[int]
    
    # Totals
    total_income: float
    total_spent: float
    total_fees: float
    net_flow: float
    
    # Breakdown
    by_category: dict[str, float]
    by_merchant: dict[str, float]
    by_transaction_type: dict[str, float]
    
    # Anomalies
    subscriptions: list[dict]
    flagged_transactions: list[dict]
    
    # Insights
    top_expenses: list[dict]
    avg_daily_spend: float
    largest_transaction: Optional[dict]
    
    generated_at: datetime


class ReportGenerator:
    """Service for generating financial reports."""
    
    def generate_monthly_report(
        self,
        transactions: list[Transaction],
        year: int,
        month: int
    ) -> SpendingReport:
        """Generate monthly spending report."""
        return self._generate_report(transactions, "monthly", year, month)
    
    def generate_quarterly_report(
        self,
        transactions: list[Transaction],
        year: int,
        quarter: int
    ) -> SpendingReport:
        """Generate quarterly spending report."""
        return self._generate_report(transactions, "quarterly", year, None, quarter)
    
    def generate_yearly_report(
        self,
        transactions: list[Transaction],
        year: int
    ) -> SpendingReport:
        """Generate yearly spending report."""
        return self._generate_report(transactions, "yearly", year)
    
    def _generate_report(
        self,
        transactions: list[Transaction],
        period: str,
        year: int,
        month: Optional[int] = None,
        quarter: Optional[int] = None
    ) -> SpendingReport:
        """Internal method to generate report."""
        
        # Filter by period
        filtered = self._filter_by_period(transactions, period, year, month, quarter)
        
        # Calculate totals
        total_income = sum(t.amount for t in filtered if t.type == TransactionType.PAYIN)
        total_spent = sum(t.amount for t in filtered if t.type == TransactionType.CARD_SPEND)
        total_fees = sum(abs(t.amount) for t in filtered if t.type == TransactionType.FEE)
        net_flow = total_income - total_spent - total_fees
        
        # Breakdown by category
        by_category: dict[str, float] = {}
        for t in filtered:
            cat = t.category or "Uncategorized"
            by_category[cat] = by_category.get(cat, 0) + abs(t.amount)
        
        # Breakdown by merchant
        by_merchant: dict[str, float] = {}
        for t in filtered:
            if t.merchant_name:
                by_merchant[t.merchant_name] = by_merchant.get(t.merchant_name, 0) + abs(t.amount)
        
        # Breakdown by type
        by_type: dict[str, float] = {}
        for t in filtered:
            type_name = t.type.value
            by_type[type_name] = by_type.get(type_name, 0) + abs(t.amount)
        
        # Top expenses
        sorted_by_amount = sorted(filtered, key=lambda x: x.amount, reverse=True)
        top_expenses = [
            {
                "amount": t.amount,
                "merchant": t.merchant_name,
                "description": t.description,
                "date": t.transaction_date.strftime("%Y-%m-%d")
            }
            for t in sorted_by_amount[:5]
        ]
        
        # Flagged transactions
        flagged = [t for t in filtered if t.is_flagged]
        flagged_data = [
            {
                "amount": t.amount,
                "reason": t.alert_reason,
                "level": t.alert_level.value if t.alert_level else None,
                "date": t.transaction_date.strftime("%Y-%m-%d")
            }
            for t in flagged
        ]
        
        # Subscriptions
        subscriptions = [
            {
                "merchant": t.merchant_name,
                "amount": t.amount,
                "frequency": "monthly",  # Would need more logic to determine
            }
            for t in filtered if t.is_subscription
        ]
        
        # Calculate average daily spend
        if filtered:
            days_in_period = self._get_days_in_period(period, year, month, quarter)
            avg_daily = total_spent / days_in_period
        else:
            avg_daily = 0.0
        
        # Largest transaction
        largest = sorted_by_amount[0] if sorted_by_amount else None
        largest_data = None
        if largest:
            largest_data = {
                "amount": largest.amount,
                "merchant": largest.merchant_name,
                "description": largest.description,
                "date": largest.transaction_date.strftime("%Y-%m-%d")
            }
        
        return SpendingReport(
            period=period,
            year=year,
            month=month,
            quarter=quarter,
            total_income=total_income,
            total_spent=total_spent,
            total_fees=total_fees,
            net_flow=net_flow,
            by_category=by_category,
            by_merchant=by_merchant,
            by_transaction_type=by_type,
            subscriptions=subscriptions,
            flagged_transactions=flagged_data,
            top_expenses=top_expenses,
            avg_daily_spend=avg_daily,
            largest_transaction=largest_data,
            generated_at=datetime.utcnow()
        )
    
    def _filter_by_period(
        self,
        transactions: list[Transaction],
        period: str,
        year: int,
        month: Optional[int],
        quarter: Optional[int]
    ) -> list[Transaction]:
        """Filter transactions by time period."""
        if period == "monthly" and month:
            start = datetime(year, month, 1)
            if month == 12:
                end = datetime(year + 1, 1, 1)
            else:
                end = datetime(year, month + 1, 1)
        elif period == "quarterly" and quarter:
            start_month = (quarter - 1) * 3 + 1
            end_month = start_month + 3
            start = datetime(year, start_month, 1)
            if end_month > 12:
                end = datetime(year + 1, 1, 1)
            else:
                end = datetime(year, end_month, 1)
        else:  # yearly
            start = datetime(year, 1, 1)
            end = datetime(year + 1, 1, 1)
        
        return [
            t for t in transactions
            if start <= t.transaction_date < end
        ]
    
    def _get_days_in_period(
        self,
        period: str,
        year: int,
        month: Optional[int],
        quarter: Optional[int]
    ) -> int:
        """Get number of days in period."""
        if period == "monthly" and month:
            if month == 12:
                return 31
            end = datetime(year, month + 1, 1)
            start = datetime(year, month, 1)
        elif period == "quarterly" and quarter:
            start_month = (quarter - 1) * 3 + 1
            end_month = start_month + 3
            if end_month > 12:
                end = datetime(year + 1, 1, 1)
            else:
                end = datetime(year, end_month, 1)
            start = datetime(year, start_month, 1)
        else:  # yearly
            start = datetime(year, 1, 1)
            end = datetime(year + 1, 1, 1)
        
        return (end - start).days
    
    def to_markdown(self, report: SpendingReport) -> str:
        """Convert report to Markdown format."""
        md = f"# {report.period.capitalize()} Spending Report\n\n"
        md += f"**Period:** {report.year}"
        if report.month:
            md += f" - {report.month:02d}"
        elif report.quarter:
            md += f" - Q{report.quarter}"
        md += "\n\n"
        
        md += "## Summary\n\n"
        md += f"- **Total Income:** ${report.total_income:,.2f}\n"
        md += f"- **Total Spent:** ${report.total_spent:,.2f}\n"
        md += f"- **Total Fees:** ${report.total_fees:,.2f}\n"
        md += f"- **Net Flow:** ${report.net_flow:,.2f}\n"
        md += f"- **Avg Daily Spend:** ${report.avg_daily_spend:,.2f}\n\n"
        
        if report.by_category:
            md += "## Spending by Category\n\n"
            for cat, amount in sorted(report.by_category.items(), key=lambda x: x[1], reverse=True):
                md += f"- {cat}: ${amount:,.2f}\n"
            md += "\n"
        
        if report.top_expenses:
            md += "## Top Expenses\n\n"
            for exp in report.top_expenses:
                md += f"- **${exp['amount']:,.2f}** - {exp['merchant']} ({exp['date']})\n"
            md += "\n"
        
        if report.flagged_transactions:
            md += "## Flagged Transactions\n\n"
            for flag in report.flagged_transactions:
                md += f"- **${flag['amount']:,.2f}** - {flag['reason']} ({flag['date']})\n"
            md += "\n"
        
        md += f"\n*Report generated at {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')} UTC*\n"
        
        return md
