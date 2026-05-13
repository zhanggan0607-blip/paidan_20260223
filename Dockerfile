FROM node:20-alpine AS builder
WORKDIR /app
RUN npm config set registry https://registry.npmmirror.com
COPY package.json package-lock.json* ./
COPY packages/shared ./packages/shared
RUN npm install
COPY . .
RUN npm run build

FROM nginx:1.25-alpine3.18
COPY --from=builder /app/dist /usr/share/nginx/html
COPY docker/nginx-spa.conf /etc/nginx/conf.d/default.conf
RUN adduser -D -u 1001 appuser && chown -R appuser:appuser /usr/share/nginx/html
USER appuser
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
