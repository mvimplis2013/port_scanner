FROM rabbitmq:3-management-alpine

RUN rabbitmq-plugins enable --offline rabbitmq_mqtt

RUN echo 'NODENAME=rabbit@localhost' > /etc/rabbitmq/rabbitmq-env.conf

EXPOSE 15672
EXPOSE 1883