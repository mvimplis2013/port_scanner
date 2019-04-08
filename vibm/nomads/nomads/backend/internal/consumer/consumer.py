import pika, logging, functools

def on_message(chan, method_frame, _header_frame, body,  userdata=None):
    print("Userdata: " + userdata + " ... MessageBody: " + body)
    chan.basic_ack(delivery_tag=method_frame.delivery_tag)
    
def main():
    credentials = pika.PlainCredentials('nice_user', 'nice_user')

    parameters = pika.ConnectionParameters(host="rabbit-server", credentials=credentials)

    connection = pika.BlockingConnection( parameters )

    channel = connection.channel()

    channel.exchange_declare(
        exchange="test_exchange",
        exchange_type='direct',
        passive=False,
        durable=True,
        auto_delete=False
    )

    channel.queue_declare(queue='standard', auto_delete=False)

    channel.queue_bind(
        queue='standard', exchange='test_exchange', routing_key='standard_key'
    )

    channel.qos(prefetch_count=1)

    on_message_callback = functools.partial(
        on_message, userdata='on_message_userdata'
    )

    channel.basic_consume('standard', on_message_callback)

    try: 
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()

    connection.close()

if __name__ == '__main__':
    main()

print("Consumer Planet")