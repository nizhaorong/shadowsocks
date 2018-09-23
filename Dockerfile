FROM python:3-alpine

ENV APP_ROOT /app

WORKDIR ${APP_ROOT}

RUN pip3 install requests

COPY . ${APP_ROOT}

CMD [ "python3", "servers.py" ]