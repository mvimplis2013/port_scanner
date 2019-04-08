FROM python:3.7-alpine3.8

WORKDIR /usr/src/app
ENV PYTHONPATH /usr/src/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

ADD producer.py /usr/src/app/

# Environment Variable 
ENV RABBIT_HOST_IP 172.24.0.3

RUN ping -c 10 my-rabbit 

#CMD ["python", "producer.py", "-p 5672", "-s 62.46.10.194", "-m 'Hello'", "-r 30"]