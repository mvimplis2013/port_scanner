FROM python:3

ADD ../test /usr/local/vlab

RUN pip install -r requirements.txt

CMD ["pytest", "./test_db_manager.py"]