FROM python:3.7-alpine3.8

WORKDIR /usr/src/app
ENV PYTHONPATH /usr/src/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

ADD producer.py /usr/src/app/

# Environment Variable 
ENV RABBIT_HOST_IP 172.17.0.2

CMD ["python", "producer.py", "-p 5672", "-s 'my-rabbit'", "-m 'Hello'", "-r 30"]