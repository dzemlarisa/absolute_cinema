FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
ENV NODE_OPTIONS="--max-old-space-size=4096"
RUN npm run build || true
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]