FROM node:20-alpine AS builder
WORKDIR /app
RUN npm config set registry https://registry.npmmirror.com
COPY H5/package.json H5/package-lock.json* ./H5/
COPY packages/shared ./packages/shared
RUN cd H5 && npm install
COPY . .
RUN cd H5 && npx vite build

FROM nginx:1.25-alpine3.18
COPY --from=builder /app/H5/dist /usr/share/nginx/html
COPY docker/nginx-spa.conf /etc/nginx/conf.d/default.conf
RUN adduser -D -u 1001 appuser && chown -R appuser:appuser /usr/share/nginx/html
USER appuser
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
