import pika, logging

connection = pika.BlockingConnection( 
    pika.ConnectionParameters(host="my-rabbit")
)

main_channel = connection.channel()

print("Consumer Planet")