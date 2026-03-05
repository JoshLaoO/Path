# Build stage
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .
# Build with /api so the app calls same-origin /api; nginx will proxy to backend
ENV VITE_API_URL=/api
RUN npm run build

# Run stage: nginx serves static files and proxies /api to backend
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
