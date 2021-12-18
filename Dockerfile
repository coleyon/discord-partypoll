FROM node:16-slim

ENV TZ Asia/Tokyo
ENV DISCORD_BOT_TOKEN ${DISCORD_BOT_TOKEN}

COPY . /app/
WORKDIR /app
RUN apt update
RUN npm install
ENTRYPOINT ["npm", "run", "start"]
