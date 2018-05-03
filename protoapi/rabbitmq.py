from time import sleep

import pika

class Rabbitmq:
    # default queue names
    REQUEST_Q  = 'test_request'
    RESPONSE_Q = 'test_response'

    # connect to RMQ and ensure that the two queues exist
    def __init__(self, url:str, queue1:str, queue2:str):
        conparams = pika.URLParameters(url)
        #conparams = pika.ConnectionParameters(host=host, port=port)

        self.connection = pika.BlockingConnection(conparams)
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=queue1)
        self.channel.queue_declare(queue=queue2)

    # push payload to queue
    def publish(self, queue: str, payload: bytes):
        result = self.channel.basic_publish(exchange='',
                                           routing_key=queue,
                                           body=payload)
        if not result:
            print("RMQ: send of", len(payload), "bytes failed!")
        else:
            pass
            # print("RMQ: send", len(payload), "bytes")

        return result


    # blocking read of one payload from queue
    def receive(self, queue: str):
        while True:
            method_frame, header_frame, body = \
                self.channel.basic_get(queue=queue, no_ack=False)

            if method_frame:
                ### print("RMQ: received:", method_frame, header_frame, "with", len(body), "bytes")
                # print("RMQ: received", len(body), "bytes")
                self.channel.basic_ack(method_frame.delivery_tag)
                return body
            else:
                # print('No message returned')
                sleep(0.1)


    def close(self):
        self.connection.close()
