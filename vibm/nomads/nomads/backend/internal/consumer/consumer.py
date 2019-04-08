import pika, logging

connection = pika.BlockingConnection( 
    pika.ConnectionParameters(host="rabbit-server")
)

main_channel = connection.channel()

print("Consumer Planet")