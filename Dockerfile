FROM rust:1.31

ENV DEBIAN_FRONTEND noninteractive
ENV TZ Asia/Tokyo
ENV APPDIR /app
ENV APP_OPTIONS noopt
ENV TERM xterm
ENV DISCORD_BOT_TOKEN ${DISCORD_BOT_TOKEN}

RUN mkdir -p ${APPDIR}
WORKDIR ${APPDIR}
COPY . .

RUN apt-get update && apt-get install -y apt-utils
RUN cargo install --path .

CMD ["main"]
