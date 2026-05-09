FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# Создаем символическую ссылку или копируем index.html в нужное место
#RUN mkdir -p public && \
#    ( [ -f index.html ] && cp index.html public/ || true )
EXPOSE 3000
CMD ["npm", "start"]