# ─── Base ────────────────────────────────────────────────────────────
FROM node:22-alpine AS base
ENV NEXT_TELEMETRY_DISABLED=1

# ─── Dependencies ────────────────────────────────────────────────────
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* ./
RUN if [ -f pnpm-lock.yaml ]; then \
      corepack enable && corepack prepare pnpm@9 --activate && pnpm install --frozen-lockfile --prod; \
    else \
      npm ci; \
    fi

# ─── Builder ─────────────────────────────────────────────────────────
FROM base AS builder
WORKDIR /app
COPY . .
RUN if [ -f pnpm-lock.yaml ]; then \
      corepack enable && corepack prepare pnpm@9 --activate && pnpm install --frozen-lockfile && pnpm exec next build; \
    else \
      npm ci && npm run build; \
    fi

# ─── Runner (Production) ─────────────────────────────────────────────
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000
ENV HOST=0.0.0.0

# Non-root user
RUN addgroup -S nodejs -g 1001 && adduser -S nextjs -u 1001
RUN apk add --no-cache curl libc6-compat

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

RUN chown -R nextjs:nodejs /app
USER nextjs

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s \
    CMD curl -f http://localhost:3000 || exit 1

CMD ["node", "server.js"]
