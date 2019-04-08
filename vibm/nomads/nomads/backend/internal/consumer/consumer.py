import pika, logging

credentials = pika.PlainCredentials('nice_user', 'nice_user')

parameters = pika.ConnectionParameters(host="rabbit-server", credentials=credentials)

connection = pika.BlockingConnection( parameters )

main_channel = connection.channel()

print("Consumer Planet")