FROM node:18-bullseye
WORKDIR /usr/src/app
COPY package.json package-lock.json* ./
RUN npm install --no-audit --no-fund
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
