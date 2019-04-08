FROM rabbitmq:3-management-alpine

# Define environment variables
ENV RABBITMQ_USER nice_user
ENV RABBITMQ_PASSWORD nice_user

RUN rabbitmqctl add_user $RABBITMQ_USER $RABBITMQ_PASSWORD 2>/dev/null; \
    rabbitmqctl set_user_tags $RABBITMQ_USER administrator;
    rabbitmqctl set_permissions -p / $RABBITMQ_USER ".*" ".*" ".*"; 

RUN rabbitmq-plugins enable --offline rabbitmq_mqtt

RUN echo 'NODENAME=rabbit@my-rabbit' > /etc/rabbitmq/rabbitmq-env.conf

EXPOSE 15672
EXPOSE 5672
EXPOSE 1883