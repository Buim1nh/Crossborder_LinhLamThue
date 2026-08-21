"""Kiểm chứng thực nghiệm các bug P0 đã nêu trong REVIEW.md.

Chạy: ./.venv-test/bin/python verify_p0.py
Script này KHÔNG sửa gì, chỉ chứng minh bug có thật hay không.
"""
import sys
from datetime import datetime

from src.modules.chat.safety_filter import check_message, normalize
from src.modules.chat.context_builder import _summary
from src.models.transaction import Transaction, TransactionType

FAIL = 0


def report(claim, is_bug, detail):
    global FAIL
    if is_bug:
        FAIL += 1
        print(f"  [BUG XÁC NHẬN] {claim}\n      {detail}")
    else:
        print(f"  [KHÔNG TÁI HIỆN] {claim}\n      {detail}")


print("=" * 70)
print("P2-2: SAFETY FILTER BYPASS (regex-only)")
print("=" * 70)


# Các cách diễn đạt cùng ý định "huỷ gói" mà người Việt thực sự dùng.
bypass_attempts = [
    "huỷ giùm mình cái Netflix",
    "cho mình ngưng gói Spotify",
    "gỡ đăng ký gói này giúp mình",
    "dừng gói Netflix nhé",
    "tắt gia hạn tự động giúp mình",
    "ngừng thu tiền gói này",
    "unsub gói Netflix",
    "huy  goi  netflix",
]
for msg in bypass_attempts:
    v = check_message(msg)
    status = "LỌT" if v.allowed else f"chặn ({v.reason})"
    marker = "  <-- BYPASS" if v.allowed else ""
    print(f"    {status:22} | {msg!r}{marker}")

leaked = [m for m in bypass_attempts if check_message(m).allowed]
report(
    "Filter chỉ khớp từ khoá cứng, bỏ lọt cách nói tương đương",
    bool(leaked),
    f"{len(leaked)}/{len(bypass_attempts)} câu cùng ý định 'huỷ gói' vẫn lọt qua: {leaked}",
)

print()
print("  Kiểm tra chiều ngược lại - false positive (câu an toàn bị chặn oan):")
safe_msgs = [
    "tháng này mình chi bao nhiêu cho Netflix?",
    "có gói định kỳ nào đang chạy không?",
    "khoản khiếu nại tháng trước đã xong chưa?",
    "phí cancel của gói này là bao nhiêu?",
]
for msg in safe_msgs:
    v = check_message(msg)
    status = "OK" if v.allowed else f"CHẶN OAN ({v.reason})"
    marker = "" if v.allowed else "  <-- FALSE POSITIVE"
    print(f"    {status:22} | {msg!r}{marker}")

false_pos = [m for m in safe_msgs if not check_message(m).allowed]
report(
    "Câu hỏi phân tích hợp lệ bị chặn oan",
    bool(false_pos),
    f"{len(false_pos)}/{len(safe_msgs)} câu an toàn bị chặn: {false_pos}",
)

print()
print("=" * 70)
print("P0-4: TRỘN LẪN ĐA TIỀN TỆ TRONG FINANCIAL SUMMARY")
print("=" * 70)


def tx(amount, currency, ttype=TransactionType.CARD_SPEND):
    t = Transaction()
    t.amount = amount
    t.currency = currency
    t.type = ttype
    t.category = "Shopping"
    t.transaction_date = datetime(2026, 1, 15)
    return t


mixed = [tx(100.0, "USD"), tx(2_000_000.0, "VND"), tx(50.0, "EUR")]
s = _summary(mixed)
print(f"    Input: 100 USD + 2.000.000 VND + 50 EUR (3 giao dịch chi tiêu)")
print(f"    Output total_spending = {s.total_spending}")
print(f"    Output currency       = {s.currency!r}  <- lấy từ transactions[0]")
print(f"    Phép tính thực tế: 100 + 2000000 + 50 = {100 + 2000000 + 50}")

report(
    "Cộng thẳng số tiền khác đơn vị, gắn nhãn currency của giao dịch đầu",
    s.total_spending == 2000150.0 and s.currency == "USD",
    f"Báo cáo '{s.total_spending:,.0f} {s.currency}' - sai hoàn toàn về mặt tài chính. "
    f"LLM sẽ đọc con số này và nói với user rằng họ tiêu 2 triệu USD.",
)

print()
print("=" * 70)
print("P0-1: THIẾU XÁC THỰC - user_id do CLIENT tự khai (IDOR)")

print("=" * 70)
import inspect
from src.modules.chat import router as chat_router
from src.modules.chat.schemas import ChatRequest

src_router = inspect.getsource(chat_router)
has_auth = any(k in src_router for k in ("current_user", "get_current_user", "Security", "oauth2", "verify_token"))
uses_payload_uid = "payload.user_id" in src_router
print(f"    router.py có dependency xác thực?      {has_auth}")
print(f"    router.py lấy user_id từ body request? {uses_payload_uid}")
print(f"    ChatRequest.user_id là field client gửi lên: {'user_id' in ChatRequest.model_fields}")

report(
    "Bất kỳ ai cũng đọc được dữ liệu tài chính của user khác (IDOR)",
    uses_payload_uid and not has_auth,
    "POST /api/chat {\"message\":\"...\",\"user_id\":42} -> trả về context tài chính của user 42, "
    "không hề kiểm tra người gọi là ai.",
)

print()
print("=" * 70)
print(f"KẾT LUẬN: {FAIL} nhóm bug được xác nhận bằng thực nghiệm")
print("=" * 70)
sys.exit(0)
