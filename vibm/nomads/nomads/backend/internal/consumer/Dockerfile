FROM python:3.7-alpine3.8

WORKDIR /usr/src/app
ENV PYTHONPATH /usr/src/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

ADD consumer.py /usr/src/app