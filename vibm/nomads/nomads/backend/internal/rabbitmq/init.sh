#!/bin/sh

(sleep 5 ; \
rabbitmqctl add_user $RABBITMQ_USER $RABBITMQ_PASSWORD 2>/dev/null; \
rabbitmqctl set_user_tags $RABBITMQ_USER administrator; \
rabbitmqctl set_permissions -p / $RABBITMQ_USER ".*" ".*" ".*"; \
) &

# Call original entrypoint 
rabbitmq-server $@