# Back-Robot
FROM python:3.7-alpine3.8

WORKDIR /usr/src/app

COPY requirements-back-robot.txt ./

# Alpine Package Manager
RUN apk update 
RUN apk add mysql-client
RUN apk add nmap

ADD nomads/backend ./nomads/
ADD config ./config

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app"

RUN pip install -r requirements-back-robot.txt

RUN mkdir logs && touch logs/back-robot.log

RUN ls ./

CMD ["python", "-m", "nomads.engine"]