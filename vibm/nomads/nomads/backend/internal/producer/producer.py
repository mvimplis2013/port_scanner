import pika, logging, sys, argparse
from argparse import RawTextHelpFormatter
from time import sleep

if __name__ == '__main__':
    examples = sys.argv[0] + " -p 5672 -s rabbitmq -m 'Hello' "

    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter, description='Run producer.py', epilog=examples)

    parser.add_argument('-p', '--port', action='store', dest='port', help='The port to listen on.')
    parser.add_argument('-s', '--server', action='store', dest='server', help='The RabbitMQ server.')
    parser.add_argument('-m', '--message', action='store', dest='message', help='The message to send', required=False, default='Hello')
    parser.add_argument('-r', '--repeat', action='store', dest='repeat', help='Number of times to repeat the message', required=False, default='30')

    args = parser.parse_args()
    if args.port == None:
        print('Missing required argument: -p/--port')
        sys.exit(1)
    if args.server == None:
        print('Missing required argument: -s/--server')
        sys.exit(1)

    sleep(5)

    logging.basicConfig(level=logging.INFO)
    LOG = logging.getLogger(__name__)

    LOG.info( "Producer is Comming Up ... " + args.server + " !")
    
    credentials = pika.PlainCredentials('nice_user', 'nice_user')

    parameters = pika.ConnectionParameters(host="rabbit-server", credentials=credentials) #args.server, int(args.port), '/', credentials)

    connection = pika.BlockingConnection(parameters)

    LOG.info( "Immediately after connection" )

    channel = connection.channel()

    channel.exchange_declare(
        exchange='test_exchange',
        exchange_type='direct',
        passive=False,
        durable=True,
        auto_delete=False
    )

    print('Sending message to create a queue')

    channel.basic_publish(
        'test_exchange', 'standard_key', 'queue:group',
        pika.BasicProperties(content_type="text/plain", delivery_mode=1)
    )

    connection.sleep(5)

    print("Sending text message to queue")

    channel.basic_publish(
        'test_exchange', 'group_key', 'Message to Group Key',
        pika.BasicProperties(content_type="text/plain", delivery_mode=1)
    )

    connection.sleep(5)
    print( "Sending text message" )

    channel.basic_publish(
        'test_exchange', 'standard_key', 'Message to standard key',
        pika.BasicProperties(content_type="text/plain", delivery_mode=1)
    )
    
    connection.close()