import json
import pika


class Sender:
    def __init__(self, connect, **args):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(connect))
        self.channel = self.connection.channel()

    def send(self, queue_name, data, durable=True, exchange=''):
        body = data
        self.channel.queue_declare(queue=queue_name, durable=durable)
        self.channel.basic_publish(exchange=exchange,
                                   routing_key=queue_name,
                                   body=body)
        print(f" [x] Message sent to {queue_name}")

    def close(self):
        self.connection.close()
