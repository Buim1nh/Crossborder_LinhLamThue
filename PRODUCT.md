# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Next.js 14 (App Router) + FastAPI + SQLite + LLM (pluggable). UI ships into `frontend/src/app`. The standalone `ui-template.html` is a prototype artifact only.

## Users

Primary: Vietnamese individuals managing personal finances across multiple accounts (bank account, digital wallet, credit card). They are comfortable with digital tools but want AI assistance to understand their spending, detect fraud, and avoid forgotten subscriptions.

Secondary: Hackathon judges and reviewers evaluating the demo at the Cross-Border AI Innovation Hackathon 2026.

## Product Purpose

Wealify is a conversational AI financial guardian. Users upload account statements (CSV/PDF) and the system parses, categorizes, and cross-references transactions across three sources. The AI detects anomalies, forgotten subscriptions, and generates spending reports. It sends proactive alerts only after user confirmation.

**Success** = User understands where money goes, feels protected from fraud, and has reduced surprise charges from subscriptions.

## Positioning

Not a budgeting app. Not a bank aggregator. A document-intelligent AI that reads the statements the user already has and acts as their financial analyst — finding what they would miss.

## Operating Context

- User has statements from multiple sources (bank, wallet, card) saved locally
- User uploads files; the system never connects to bank APIs
- Analysis happens on-demand via LLM
- Alerts are read-only recommendations; all money operations require user action
- Hackathon demo runs locally; backend at `localhost:8000`, frontend at `localhost:3000`

## Capabilities and Constraints

**Capabilities (confirmed):**
- Upload CSV/PDF bank, wallet, and card statements
- Parse and categorize transactions by source
- Cross-reference transactions across three sources
- Detect anomalies via AI pattern analysis
- Identify forgotten recurring subscriptions
- Generate monthly spending reports
- Conversational AI chat interface for follow-up questions
- Bilingual UI: Vietnamese primary, English secondary

**Constraints:**
- Read-only; no money movement, no actual transactions initiated
- CVV never stored or displayed
- Card numbers masked (show last 4 digits only)
- Email alerts require user confirmation before sending
- LLM provider is pluggable but not yet finalized (Claude/GPT-4o/Gemini TBD)
- No persistent user accounts in current build (session-based)

## Brand Commitments

- Product name: **Wealify**
- Tagline: AI Financial Guardian
- Accent color (binding): `#FF6B1A`
- Hackathon reference: Cross-Border AI Innovation Hackathon 2026, WLF-01
- Team: 4 members, VinGroup/VinUni AI Thực Chiến program

## Evidence on Hand

- Existing Next.js 14 frontend at `frontend/src/` with: Header, FileUpload (×3), TransactionList, SummaryCard, ChatInterface, Tabs
- Backend FastAPI at `backend/src/` with parsers, services, API routes
- Standalone HTML prototype at `ui-template.html` (prototype only, not the deliverable)
- No user testing data. No real bank data. Sample data path at `data/sample/`

## Product Principles

1. **Documents, not connections.** The system reads files the user uploads. It never logs into anything.
2. **Analyst, not operator.** Wealify informs and recommends. Every action stays with the user.
3. **Silence by default.** No alerts sent without explicit user confirmation.
4. **Explain in plain language.** AI responses should be understandable to a non-technical user.
5. **Vietnamese first.** UI labels, alerts, and explanations in Vietnamese, with English as secondary.

## Accessibility & Inclusion

No confirmed accessibility standard required. Basic keyboard navigation and semantic HTML should be met by default. No known color-blind considerations have been raised.

## Language Strategy

| Layer | Language |
|-------|----------|
| UI labels, navigation | Vietnamese |
| Error messages, alerts | Vietnamese |
| AI chat responses | Vietnamese |
| Technical/hackathon content | English |
| Variable/code | English |
