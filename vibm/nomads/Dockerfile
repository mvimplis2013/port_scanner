# Back-Robot
FROM python:3.7-alpine3.8

WORKDIR /usr/src/app

COPY requirements-internal-agent.txt ./

# Alpine Package Manager
RUN apk update 
RUN apk add sudo
RUN apk add nmap

ADD nomads/backend ./nomads/
ADD config ./config

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app"

RUN pip install -r requirements-internal-agent.txt

RUN mkdir logs && touch logs/internal-agent.log

RUN ls ./

CMD ["sudo python", "-m", "nomads.internal"]