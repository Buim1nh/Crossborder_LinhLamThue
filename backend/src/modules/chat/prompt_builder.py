"""
MODULE 6 - Step 3: BUILD PROMPT.

Turns a `UserContext` + the user's question into the exact strings sent to
the LLM. Pure functions, no I/O — which makes prompt changes trivially
testable and reviewable.
"""
from src.modules.chat.config import DISCLAIMER
from src.modules.chat.schemas import UserContext


SYSTEM_PROMPT = f"""Bạn là trợ lý tài chính của Wealify.

VAI TRÒ CỦA BẠN
Bạn giúp người dùng RÀ SOÁT và HIỂU dữ liệu tài chính của chính họ: giải \
thích các khoản chi, chỉ ra giao dịch bất thường, liệt kê các gói định kỳ, \
và tổng hợp thu chi.

GIỚI HẠN TUYỆT ĐỐI - KHÔNG BAO GIỜ VI PHẠM
1. KHÔNG thực hiện bất kỳ hành động nào thay người dùng: không huỷ gói, \
không gửi khiếu nại, không chuyển tiền, không liên hệ ngân hàng/nhà bán.
2. KHÔNG đưa ra bảo đảm về mức độ an toàn của tài khoản, và không khẳng \
định một giao dịch chắc chắn là gian lận.
3. KHÔNG đưa ra lời khuyên đầu tư hay tư vấn pháp lý.
4. KHÔNG bịa số liệu. Chỉ dùng dữ liệu trong phần "DỮ LIỆU NGƯỜI DÙNG". \
Nếu thiếu dữ liệu, hãy nói thẳng là chưa đủ dữ liệu.
5. Khi người dùng muốn huỷ/khiếu nại: hãy chỉ cho họ CÁCH tự làm, và cung \
cấp thông tin giao dịch liên quan để họ chủ động.

CÁCH TRẢ LỜI
- Dùng tiếng Việt, ngắn gọn, thân thiện, đi thẳng vào câu hỏi.
- Khi nhắc đến số tiền, luôn kèm đơn vị tiền tệ.
- Khi nêu một giao dịch, kèm ngày và tên đơn vị bán để người dùng đối chiếu.
- Kết thúc MỌI câu trả lời bằng đúng dòng lưu ý sau:
{DISCLAIMER}"""


def _money(amount: float, currency: str) -> str:
    """Format an amount with thousands separators + currency."""
    return f"{amount:,.2f} {currency}"


def build_context_block(context: UserContext) -> str:
    """
    Render the user's financial data as a readable block for the prompt.

    Plain labelled text (rather than raw JSON) keeps token usage low and is
    easier for models to quote accurately.
    """
    summary = context.financial_summary

    if context.is_empty:
        return (
            "DỮ LIỆU NGƯỜI DÙNG:\n"
            "- Chưa có giao dịch nào được tải lên hệ thống."
        )

    lines: list[str] = ["DỮ LIỆU NGƯỜI DÙNG:"]

    # --- Financial summary -------------------------------------------------
    lines.append("\n[Tổng quan tài chính]")
    if summary.period_start and summary.period_end:
        lines.append(f"- Kỳ dữ liệu: {summary.period_start} → {summary.period_end}")
    lines.append(f"- Tổng chi: {_money(summary.total_spending, summary.currency)}")
    lines.append(f"- Tổng thu: {_money(summary.total_income, summary.currency)}")
    lines.append(f"- Tổng phí: {_money(summary.total_fees, summary.currency)}")
    lines.append(f"- Dòng tiền ròng: {_money(summary.net_flow, summary.currency)}")
    lines.append(f"- Số giao dịch: {summary.transaction_count}")

    if summary.by_category:
        top = sorted(summary.by_category.items(), key=lambda kv: kv[1], reverse=True)
        breakdown = ", ".join(
            f"{name}: {_money(value, summary.currency)}" for name, value in top
        )
        lines.append(f"- Chi theo nhóm: {breakdown}")

    # --- Recent transactions ----------------------------------------------
    lines.append("\n[Giao dịch gần đây]")
    if context.recent_transactions:
        for t in context.recent_transactions:
            parts = [f"- {t.date}", _money(t.amount, t.currency)]
            parts.append(t.merchant or t.description or "không rõ")
            if t.category:
                parts.append(f"({t.category})")
            lines.append(" | ".join(parts))
    else:
        lines.append("- Không có.")

    # --- Anomalies ---------------------------------------------------------
    lines.append("\n[Giao dịch bất thường được đánh dấu]")
    if context.anomalies:
        for a in context.anomalies:
            detail = f"- {a.description}"
            if a.date:
                detail += f" | ngày {a.date}"
            if a.level:
                detail += f" | mức: {a.level}"
            if a.reason:
                detail += f" | lý do: {a.reason}"
            if a.dispute_deadline:
                detail += f" | hạn khiếu nại: {a.dispute_deadline}"
            lines.append(detail)
    else:
        lines.append("- Không có giao dịch nào bị đánh dấu.")

    # --- Subscriptions -----------------------------------------------------
    lines.append("\n[Gói định kỳ đang hoạt động]")
    if context.subscriptions:
        for s in context.subscriptions:
            detail = f"- {s.name} | {_money(s.amount, s.currency)}"
            if s.last_charge:
                detail += f" | lần gần nhất: {s.last_charge}"
            if s.next_charge:
                detail += f" | dự kiến kế tiếp: {s.next_charge}"
            lines.append(detail)
    else:
        lines.append("- Không phát hiện gói định kỳ nào.")

    # --- Reconciliation ----------------------------------------------------
    rec = context.reconciliation_status
    lines.append("\n[Đối soát với email hoá đơn]")
    lines.append(
        f"- Khớp: {rec.matched} | Không tìm thấy email: {rec.no_email_found} "
        f"| Nghi vấn: {rec.suspicious} | Chưa đối soát: {rec.unchecked}"
    )

    return "\n".join(lines)


def build_user_prompt(message: str, context: UserContext) -> str:
    """Combine the context block with the user's actual question."""
    return (
        f"{build_context_block(context)}\n\n"
        f"CÂU HỎI CỦA NGƯỜI DÙNG:\n{message.strip()}\n\n"
        "Hãy trả lời dựa CHỈ trên dữ liệu ở trên. Nếu dữ liệu không đủ để trả "
        "lời, hãy nói rõ điều đó thay vì suy đoán."
    )


def build_prompt(message: str, context: UserContext) -> tuple[str, str]:
    """Return `(system_prompt, user_prompt)` ready for the LLM client."""
    return SYSTEM_PROMPT, build_user_prompt(message, context)
