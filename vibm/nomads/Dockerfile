FROM python:3.6-alpine

ENV FLASK_APP server.py
ENV FLASK_CONFIG production

RUN adduser -D vlab
USER vlab 

WORKDIR /home/vlab

COPY requirements_gui.txt requirements.txt

RUN python -m venv venv_vlab
RUN venv_vlab/bin/pip install -r requirements.txt

COPY nomads nomads

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]