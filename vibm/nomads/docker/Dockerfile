FROM python:3

RUN apt-get update 

ADD ../test /usr/local/vlab

RUN pip install -r requirements.txt

CMD ["pytest", "./tests/*"]