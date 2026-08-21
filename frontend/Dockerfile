# ==============================================================================
# Multi-Stage Optimized Slim Dockerfile for Wealify Frontend (Next.js Standalone)
# ==============================================================================

# ── Stage 1: Dependencies Cache ──────────────────────────────────────────────
FROM node:18-alpine AS deps
RUN apk add --no-cache libc6-compat && \
    rm -rf /var/cache/apk/* /tmp/*
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --prefer-offline --no-audit && \
    npm cache clean --force

# ── Stage 2: Application Builder ─────────────────────────────────────────────
FROM node:18-alpine AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production

RUN npm run build && \
    npm cache clean --force && \
    rm -rf /tmp/* /root/.npm

# ── Stage 3: Production Runner (Ultra-Slim Alpine) ───────────────────────────
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000

# Install non-root system group/user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs && \
    rm -rf /var/cache/apk/* /tmp/*

# Copy static public assets if present
COPY --from=builder /app/public ./public 2>/dev/null || true

# Copy standalone Next.js server bundle and static chunks only
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

CMD ["node", "server.js"]
