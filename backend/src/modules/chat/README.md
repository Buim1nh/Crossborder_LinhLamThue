# MODULE 6: LLM Chat Interface

Toàn bộ module nằm gọn trong folder này. Muốn gỡ module → xoá folder + 1 dòng
`include_router` trong `src/api/main.py`. Không file nào bên ngoài import vào
đây (trừ dòng wiring đó).

## Luồng xử lý

```
User message
   │
   ├─ 1. SAFETY FILTER      safety_filter.py   ← chặn trước, không chạm DB/LLM
   │      └─ blocked? → trả lời từ chối lịch sự → STOP
   │
   ├─ 2. BUILD CONTEXT      context_builder.py ← đọc DB
   ├─ 3. BUILD PROMPT       prompt_builder.py  ← system + user prompt
   ├─ 4. CALL LLM           llm_client.py      ← OpenAI / Anthropic / Gemini / mock
   ├─ 5. RECEIVE RESPONSE
   ├─ 6. ADD DISCLAIMER     service.py         ← bắt buộc, mọi nhánh
   └─ 7. RETURN CHAT RESPONSE
```

## Cấu trúc file

| File | Vai trò |
|---|---|
| `__init__.py` | Public API của module (`chat_router`, `handle_chat`, ...) |
| `config.py` | Settings riêng (provider, model, key) + text disclaimer |
| `schemas.py` | Pydantic models: request, response, context |
| `safety_filter.py` | Bước 1 — regex chặn hành vi thay mặt người dùng |
| `context_builder.py` | Bước 2 — gom dữ liệu tài chính từ DB |
| `prompt_builder.py` | Bước 3 — system prompt + template câu hỏi |
| `llm_client.py` | Bước 4–5 — client đa provider, có `mock` để chạy offline |
| `service.py` | Điều phối pipeline + bước 6 (disclaimer) |
| `router.py` | Bước 7 — FastAPI endpoints |
| `tests/test_chat.py` | Test cho toàn bộ module |

## Endpoints

| Method | Path | Mô tả |
|---|---|---|
| `POST` | `/api/chat` | Hỏi trợ lý tài chính |
| `POST` | `/api/chat/check` | Chạy thử safety filter, không gọi LLM |
| `GET`  | `/api/chat/info` | Provider đang dùng + text disclaimer |

```bash
curl -X POST http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "Tháng này tôi chi bao nhiêu?"}'
```

Request bị chặn vẫn trả **HTTP 200** kèm `blocked: true` — từ chối là một lượt
hội thoại hợp lệ, không phải lỗi client.

## Safety filter

Chặn (`Decline`) khi người dùng yêu cầu **hệ thống hành động thay mình** hoặc
**cam kết an toàn**:

| Pattern | Lý do |
|---|---|
| "huỷ gói", "cancel subscription" | `action_cancel` |
| "khiếu nại cho [shop]", "chargeback" | `action_complaint` |
| "tài khoản an toàn không" | `assurance_safety` |
| "chuyển tiền giúp" | `action_money_move` |

Cho qua (`OK`) các câu hỏi phân tích: "chi bao nhiêu", "khoản này là gì",
"gói định kỳ nào".

Filter chuẩn hoá tiếng Việt trước khi so khớp (bỏ dấu + lowercase), nên
"huỷ gói", "hủy gói", "HUY GOI" đều bị bắt.

## Cấu hình

Thêm vào `backend/.env` (mọi biến đều optional — thiếu key thì module tự
chuyển sang provider `mock` và app vẫn chạy):

```env
CHAT_PROVIDER=anthropic          # anthropic | openai | gemini | mock
CHAT_MODEL=                      # để trống → dùng model mặc định của provider
ANTHROPIC_API_KEY=sk-ant-...
# OPENAI_API_KEY=sk-...
# GOOGLE_API_KEY=...
CHAT_MAX_TOKENS=1024
CHAT_TEMPERATURE=0.3
CHAT_TIMEOUT_SECONDS=30
```

SDK được import lazy trong từng provider, nên chỉ cần cài thư viện của
provider bạn dùng:

```bash
pip install anthropic          # hoặc openai / google-generativeai
```

## Chạy test

```bash
cd backend && pytest src/modules/chat/tests/ -v
```
