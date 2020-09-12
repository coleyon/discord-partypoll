FROM python:3.7-slim

ENV TZ Asia/Tokyo
ENV APPDIR /app
ENV PYTHONPATH ${APPDIR}
ENV APP_OPTIONS noopt
ENV TERM xterm
ENV DISCORD_BOT_TOKEN ${DISCORD_BOT_TOKEN}

RUN mkdir -p ${APPDIR}
WORKDIR ${APPDIR}
COPY . .

RUN apt-get update
RUN pip install --upgrade pip
RUN pip3 install --upgrade pip \
    && pip3 install --upgrade setuptools \
    && python3 -m pip install -r ./requirements.txt

ENTRYPOINT ["python3", "-u", "main.py"]
