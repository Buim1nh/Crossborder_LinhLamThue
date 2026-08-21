# Wealify — AI Financial Guardian (WLF-01)

> **Cross-Border AI Innovation Hackathon 2026**  
> Thử thách: **WLF-01: Quản lý chi tiêu & an toàn giao dịch**

Wealify là trợ lý tài chính thông minh đóng vai trò như một **Chuyên gia phân tích tài chính (Financial Analyst)**. Hệ thống tự động đọc, chuẩn hóa và đối chiếu chéo các bản sao kê tài chính từ 3 nguồn (Tài khoản ngân hàng, Ví điện tử, Thẻ tín dụng/ghi nợ), phát hiện giao dịch trùng lặp, bẫy phí ẩn và đưa ra cảnh báo rủi ro tức thì cho người dùng.

---

## 1. Kiến Trúc & Định Hướng Triển Khai (Deployment Overview)

| Thành Phần | Công Nghệ & Nền Tảng Deploy | Trạng Thái | Mô Tả |
|---|---|---|---|
| **Frontend** | **Next.js 14 (App Router) + TypeScript + Tailwind CSS**<br>🚀 Deploy qua **Vercel** | ✅ Sẵn sàng | Giao diện chuẩn UX/UI Impeccable (Landing, Dashboard, Login, Register), tích hợp `@react-oauth/google` và API client. |
| **Backend API** | **FastAPI (Python 3.11) + SQLAlchemy 2.0 Async + SQLite**<br>🐳 Deploy qua **Render (Docker Multi-Stage Slim)** | ✅ Sẵn sàng | Hệ thống API xác thực (Bcrypt + JWT), đối chiếu sao kê, quản lý giao dịch và phát hiện bất thường. |
| **LLM Service** | **Pluggable Engine (Anthropic Claude / GPT-4o / Gemini)** | ⏳ **Chưa động tới (Placeholder)** | Kiến trúc cắm rút đã được thiết kế sẵn khung (`backend/src/services/llm_service.py`), chưa kích hoạt API key thương mại. |

---

## 2. Cấu Trúc File Môi Trường (`.env`)

Dự án sử dụng **1 file `.env` chung duy nhất** đặt tại thư mục gốc của repository cho môi trường phát triển cục bộ (Local Development).

```
├── .env.example              # File mẫu cấu hình chung cho cả dự án
├── .env                      # File cấu hình thực thi cục bộ (được gitignore)
├── render.yaml               # Blueprint cấu hình tự động Web Service trên Render
├── backend/                  # FastAPI application
│   ├── Dockerfile            # Dockerfile multi-stage slim cho Render
│   ├── src/                  # Mã nguồn FastAPI
│   │   ├── api/              # API routes (auth, transactions, subscriptions)
│   │   ├── core/             # Config, security, database
│   │   ├── models/           # SQLAlchemy / Pydantic models
│   │   ├── parsers/          # Statement, email parsers
│   │   └── services/         # Business logic & ML model inference
│   ├── tests/
│   └── requirements.txt
├── frontend/                 # Next.js application
│   ├── src/                  # Mã nguồn Next.js
│   │   ├── app/              # App router pages (landing, dashboard, login, register)
│   │   ├── components/       # React components (auth, dashboard, common)
│   │   ├── lib/              # Utilities, API client
│   │   └── types/            # TypeScript types
│   └── package.json
├── ml/                       # Subscription detection model + MLOps pipeline
│   ├── config.yaml           # Pipeline config (data, features, model, quality gates)
│   ├── cli.py                # audit | train | evaluate | predict | promote | drift
│   ├── pipeline/             # Feature engineering, training, registry, serving
│   ├── registry/             # Versioned models (committed)
│   └── tests/
└── docs/                     # Documentation
```

---

## 3. Hướng Dẫn Setup Biến Môi Trường Theo Từng Nền Tảng

### A. Môi Trường Chạy Cục Bộ (Local Development)
Chỉ cần sao chép file `.env.example` thành `.env` tại thư mục gốc:
```bash
# Tại thư mục gốc dự án
cp .env.example .env
```
File này chứa sẵn các giá trị mặc định tối ưu cho môi trường local (`localhost:8000` cho Backend và `localhost:3000` cho Frontend).

---

### B. Môi Trường Frontend (Deploy Trên Vercel)
Khi import project lên **Vercel**, chọn **Root Directory** là `frontend`, sau đó vào mục **Settings → Environment Variables** và thêm các biến sau:

| Tên Biến (Key) | Bắt Buộc | Giá Trị Mẫu |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | 🔴 **Bắt buộc** | `https://wealify-backend.onrender.com` (Domain của Backend trên Render) |
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | 🟡 Khuyến nghị | `1092837465-xxx.apps.googleusercontent.com` (Google OAuth Client ID) |
| `NEXT_PUBLIC_APP_NAME` | ⚪ Tùy chọn | `Wealify` |
| `NEXT_PUBLIC_APP_TAGLINE` | ⚪ Tùy chọn | `AI Financial Guardian` |
| `NEXT_PUBLIC_APP_URL` | ⚪ Tùy chọn | `https://wealify.vercel.app` (URL frontend Vercel của bạn) |
| `NEXT_PUBLIC_ENV` | ⚪ Tùy chọn | `production` |

---

### C. Môi Trường Backend (Deploy Docker Trên Render)
Khi tạo **Web Service (Docker)** trên **Render**, vào tab **Environment** và điền các biến:

| Tên Biến (Key) | Bắt Buộc | Giá Trị Mẫu |
|---|---|---|
| `CORS_ORIGINS` | 🔴 **Bắt buộc** | `https://wealify.vercel.app,http://localhost:3000` (Danh sách domain frontend) |
| `SECRET_KEY` | 🔴 **Bắt buộc** | Chuỗi bí mật 64 ký tự (Bấm *Generate* trên Render hoặc tự sinh) |
| `DATABASE_URL` | 🔴 **Bắt buộc** | `sqlite+aiosqlite:///./wealify.db` (Hoặc URL PostgreSQL Render) |
| `ALGORITHM` | ⚪ Tùy chọn | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ⚪ Tùy chọn | `10080` (7 ngày) |
| `GOOGLE_CLIENT_ID` | 🟡 Khuyến nghị | `1092837465-xxx.apps.googleusercontent.com` |
| `LLM_PROVIDER` | ⚪ Tùy chọn | `anthropic` (Hiện đang là placeholder) |
| `LLM_API_KEY` | ⚪ Tùy chọn | `(Để trống - Chưa động tới)` |

---

## 4. Hướng Dẫn Chi Tiết Cách Lấy & Sinh Từng Biến Môi Trường

### 1. `SECRET_KEY` (Khóa bảo mật JWT Backend)
Khóa này dùng để ký và mã hóa token JWT đăng nhập cho người dùng. Yêu cầu tối thiểu 32-64 ký tự ngẫu nhiên.
- **Cách 1 (Terminal Python)**:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(64))"
  ```
- **Cách 2 (OpenSSL)**:
  ```bash
  openssl rand -hex 32
  ```
- **Cách 3**: Khi deploy trên Render, bấm nút **Generate** tại ô `SECRET_KEY`.

---

### 2. `GOOGLE_CLIENT_ID` & `NEXT_PUBLIC_GOOGLE_CLIENT_ID` (Google OAuth 2.0)
Dùng để xác thực đăng nhập Google 1-click cho người dùng.
- **Bước 1**: Truy cập [Google Cloud Console](https://console.cloud.google.com/).
- **Bước 2**: Tạo Project mới (ví dụ: `Wealify App`).
- **Bước 3**: Vào **APIs & Services → OAuth consent screen**:
  - Chọn User Type: **External**.
  - Điền tên App, Email hỗ trợ và lưu lại.
- **Bước 4**: Vào **APIs & Services → Credentials → Create Credentials → OAuth client ID**:
  - Application type: **Web application**.
  - Name: `Wealify Web Client`.
  - **Authorized JavaScript origins**:
    - `http://localhost:3000` (cho local)
    - `https://wealify.vercel.app` (cho Vercel)
  - **Authorized redirect URIs**:
    - `http://localhost:3000`
    - `https://wealify.vercel.app`
- **Bước 5**: Sao chép **Client ID** (dạng `xxxxxxxxxxxx-xxxxxxxxxxxxxxxx.apps.googleusercontent.com`) và dán vào biến `GOOGLE_CLIENT_ID` (Backend) và `NEXT_PUBLIC_GOOGLE_CLIENT_ID` (Frontend).

---

### 3. `NEXT_PUBLIC_API_URL` (URL kết nối Backend)
- **Local**: `http://localhost:8000`
- **Production (Vercel)**: Sau khi tạo Web Service trên Render, Render sẽ cấp cho bạn một đường dẫn dạng `https://wealify-backend.onrender.com`. Hãy lấy URL này điền vào Vercel.

---

### 4. `CORS_ORIGINS` (Danh sách domain Frontend được phép gọi API)
Backend FastAPI cần biết domain nào được phép gửi request. Hãy điền các domain phân cách bằng dấu phẩy `,`:
```env
CORS_ORIGINS="https://wealify.vercel.app,http://localhost:3000,http://127.0.0.1:3000"
```

---

### 5. `DATABASE_URL` (Cơ sở dữ liệu)
- **Mặc định (SQLite)**: `sqlite+aiosqlite:///./wealify.db` (Tự động khởi tạo file database trong container).
- **PostgreSQL (Nếu dùng Render Postgres)**:
  ```env
  DATABASE_URL="postgresql+asyncpg://user:password@hostname:5432/dbname"
  ```

---

### 6. `LLM_PROVIDER` & `LLM_API_KEY` (Trí tuệ nhân tạo LLM)
- **Ghi chú quan trọng**: Tính năng LLM trong phiên bản hiện tại đang ở trạng thái **Placeholder / Mock phân tích cục bộ** để phục vụ chấm thi demo hackathon.
- Bạn có thể để trống `LLM_API_KEY` mà không ảnh hưởng đến bất kỳ luồng đăng ký, đăng nhập, tải sao kê hay hiển thị dashboard nào.

---

### 7. `IMAP_USER` & `IMAP_PASSWORD` (Đối chiếu email hóa đơn - Tùy chọn)
Nếu muốn bật tính năng tự động quét hóa đơn qua email:
- Dùng tài khoản Gmail đã bật 2-Step Verification.
- Vào [Google App Passwords](https://myaccount.google.com/apppasswords), tạo mật khẩu ứng dụng 16 ký tự và dán vào `IMAP_PASSWORD`.

---

## 5. Hướng Dẫn Chạy Cục Bộ (Quickstart Local)

### Yêu Cầu Cài Đặt:
- Python 3.10+
- Node.js 18+ & npm

### Bước 1: Chuẩn bị file `.env`
```bash
cp .env.example .env
```

### Bước 2: Chạy Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn src.api.main:app --reload --port 8000
```
- API Docs Swagger: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

### Bước 3: Chạy Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```
- Giao diện chính: `http://localhost:3000`
- Trang Đăng Ký: `http://localhost:3000/register`
- Trang Đăng Nhập: `http://localhost:3000/login`
- Dashboard Workspace: `http://localhost:3000/dashboard`

<<<<<<< HEAD
---
=======
### ML pipeline

```bash
make -f ml/Makefile setup
make -f ml/Makefile test audit train-promote
```

The backend serves the promoted model at `GET /api/subscriptions/model` and
`POST /api/subscriptions/score`. See [ml/README.md](ml/README.md) for metrics,
the leakage audit, and the MLOps lifecycle.

## Requirements
>>>>>>> 30d389d (mlops)

## 6. Kiểm Thử Tự Động (Automated Testing)

- **Kiểm thử Backend API (Pytest)**:
  ```bash
  python -m pytest backend/tests/ -v
  ```
  *(10/10 test cases passed: Auth, Registration, Login, JWT verification, Transactions)*

- **Kiểm thử Frontend Build (Next.js)**:
  ```bash
  cd frontend && npm run build
  ```
  *(Biên dịch 7/7 route thành công 100% không lỗi)*

---

## 7. Nguyên Tắc Bảo Mật Cốt Lõi (Security Principles)

1. **Documents, Not Connections**: Hệ thống chỉ đọc file sao kê do người dùng chủ động tải lên, không bao giờ yêu cầu mật khẩu Internet Banking.
2. **Không lưu trữ CVV**: Tuyệt đối không bao giờ hiển thị hoặc lưu mã bảo mật thẻ.
3. **Mã hóa số thẻ**: Toàn bộ số thẻ tín dụng được tự động ẩn `**** 8829` (chỉ hiển thị 4 số cuối).
4. **Quyền riêng tư tuyệt đối**: Toàn bộ xử lý phân tích diễn ra cục bộ trong phiên làm việc an toàn.

---

## 8. Đội Ngũ Phát Triển (Team)

Nhóm 4 thành viên thuộc chương trình **VinGroup / VinUni AI Thực Chiến 2026**.
