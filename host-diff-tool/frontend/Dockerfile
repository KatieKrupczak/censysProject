# Build React app
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./


# If you don't use package-lock.json, the wildcard won't match (that's fine)
RUN npm install
COPY . .
RUN npm run build


# Nginx to serve static + proxy /api to backend
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html


# Minimal nginx config with /api proxy to FastAPI service name `api`
RUN rm /etc/nginx/conf.d/default.conf
COPY <<'NGINX' /etc/nginx/conf.d/default.conf
server {
listen 80;
server_name _;


location /api/ {
proxy_pass http://api:8000/api/;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}


location / {
root /usr/share/nginx/html;
try_files $uri /index.html;
}
}
NGINX


EXPOSE 80