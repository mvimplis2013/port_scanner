FROM python:3.6-alpine

RUN apk update 
RUN apk add iputils
RUN apk add nmap
RUN apk add sudo

RUN apk add mysql-client

ENV FLASK_APP nomads/server.py
ENV FLASK_CONFIG production

RUN adduser -D vlab
USER vlab 

WORKDIR /home/vlab

COPY requirements_gui.txt requirements.txt

RUN python -m venv venv_vlab
RUN venv_vlab/bin/pip install -r requirements.txt

RUN pip install --user -r requirements.txt

COPY nomads nomads
COPY boot.sh ./

RUN mkdir logs && touch logs/back-robot.log

ADD config ./config

ENV PYTHONPATH "${PYTHONPATH}:/home/vlab/"

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
#CMD python -m flask run --host=127.0.0.1 --port=5000
#CMD python -m gunicorn -b :5000 --access-logfile - --error-logfile - server:app