import pika, logging

credentials = pika.PlainCredentials('guest', 'guest')

parameters = pika.ConnectionParameters(host="rabbit-server", credentials=credentials)

connection = pika.BlockingConnection( parameters )

main_channel = connection.channel()

print("Consumer Planet")