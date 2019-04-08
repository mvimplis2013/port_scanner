FROM rabbitmq:3-management-alpine

# Define environment variables
ENV RABBITMQ_USER nice_user
ENV RABBITMQ_PASSWORD nice_user

RUN rabbitmq-plugins enable --offline rabbitmq_mqtt

RUN echo 'NODENAME=rabbit@my-rabbit' > /etc/rabbitmq/rabbitmq-env.conf

COPY ./init.sh /
RUN chmod +x /init.sh

ENTRYPOINT ["/init.sh"]

EXPOSE 15672
EXPOSE 5672
EXPOSE 1883