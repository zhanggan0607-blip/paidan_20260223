FROM node:22.12.0-alpine AS builder
WORKDIR /app
COPY . .
RUN cd packages/shared && npm install || true
RUN cd H5 && npm install && npm install terser && npx vite build

FROM nginx:1.25-alpine3.18
COPY --from=builder /app/H5/dist /usr/share/nginx/html
COPY docker/nginx-h5.conf /etc/nginx/conf.d/default.conf

RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup && \
    chown -R appuser:appgroup /usr/share/nginx/html && \
    chown -R appuser:appgroup /var/cache/nginx && \
    chown -R appuser:appgroup /var/log/nginx && \
    touch /var/run/nginx.pid && \
    chown -R appuser:appgroup /var/run/nginx.pid

USER appuser

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q --spider http://0.0.0.0:80/ || exit 1
