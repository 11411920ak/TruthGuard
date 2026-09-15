# Stage 1: Build React frontend application
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency specifications and install
COPY package*.json ./
RUN npm install

# Copy source files and build production bundle
COPY . .
RUN npm run build

# Stage 2: Serve static production bundle with Nginx
FROM nginx:alpine

# Copy custom nginx configuration with SPA support and API reverse-proxy
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy compiled assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
