import pika, sys, os
import json


class Receiver:
    def __init__(self, connect ):
        self.connect = connect
        self.body = None
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.connect))
        self.channel = self.connection.channel()

    def get_message(self, queue, durable=True, auto_ack=True):
        self.channel.queue_declare(queue=queue, durable=durable)

        def callback(ch, method, properties, body):
            print(f" [x] Received message from {queue}")
            self.body = body
            self.channel.close()
        self.channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=auto_ack)
        self.channel.start_consuming()
        return self.body

    def open_channel(self):
        self.channel = self.connection.channel()

    def close(self):
        self.connection.close()
        sys.exit(0)
        os._exit(0)

