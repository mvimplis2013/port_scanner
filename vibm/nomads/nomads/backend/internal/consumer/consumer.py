import pika, logging

credentials = pika.PlainCredentials('nice_user', 'nice_user')

parameters = pika.ConnectionParameters(host="rabbit-server", credentials=credentials)

connection = pika.BlockingConnection( parameters )

channel = connection.channel()

channel.

print("Consumer Planet")