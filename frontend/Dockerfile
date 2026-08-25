FROM node:22-alpine AS dependencies
WORKDIR /app
COPY package.json package-lock.json ./
COPY frontend/package.json ./frontend/package.json
RUN npm ci --workspace @kenkomirai/frontend

FROM node:22-alpine AS builder
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=dependencies /app/node_modules ./node_modules
COPY package.json package-lock.json ./
COPY frontend ./frontend
RUN npm run build --workspace @kenkomirai/frontend

FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

RUN addgroup --system --gid 10001 kenko \
    && adduser --system --uid 10001 --ingroup kenko kenko
COPY --from=builder --chown=kenko:kenko /app/frontend/public ./frontend/public
COPY --from=builder --chown=kenko:kenko /app/frontend/.next/standalone ./
COPY --from=builder --chown=kenko:kenko /app/frontend/.next/static ./frontend/.next/static

USER kenko
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:3000/').then(r=>{if(!r.ok)process.exit(1)}).catch(()=>process.exit(1))"

CMD ["node", "frontend/server.js"]
