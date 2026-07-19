# ─── Base ────────────────────────────────────────────────────────────
FROM node:20-alpine AS base
 
# ─── Dependencies ────────────────────────────────────────────────────
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
 
# ─── Builder ─────────────────────────────────────────────────────────
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
 
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
 
RUN npm run build
 
# ─── Runner (Production) ─────────────────────────────────────────────
FROM nginx:1.27-alpine AS runner
WORKDIR /usr/share/nginx/html
 
COPY --from=builder /app/dist /usr/share/nginx/html
 
RUN printf '%s\n' \
    'server {' \
    '    listen 3001;' \
    '    server_name localhost;' \
    '    root /usr/share/nginx/html;' \
    '    index index.html;' \
    '    location / {' \
    '        try_files $uri $uri/ /index.html;' \
    '    }' \
    '}' > /etc/nginx/conf.d/default.conf
 
EXPOSE 3001
 
CMD ["nginx", "-g", "daemon off;"]