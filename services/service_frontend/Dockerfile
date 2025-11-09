FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build

# Install a static file server
RUN npm install -g serve

EXPOSE 8000

CMD ["serve", "-s", "dist", "-l", "8000"]