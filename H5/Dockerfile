FROM node:18-alpine as builder

WORKDIR /app

# 使用淘宝镜像加速npm
RUN npm config set registry https://registry.npmmirror.com

COPY packages/shared ./packages/shared
COPY H5 ./H5

WORKDIR /app/packages/shared
RUN npm install --registry=https://registry.npmmirror.com

WORKDIR /app/H5
RUN npm install --registry=https://registry.npmmirror.com
RUN chmod -R +x node_modules/.bin && npm run build

FROM nginx:alpine

# 使用阿里云镜像加速apk
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories

COPY --from=builder /app/H5/dist /usr/share/nginx/html
COPY H5/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
