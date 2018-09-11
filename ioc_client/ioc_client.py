import time
import uuid

import pika

import ioc_client.pb_ioc_detection_service_pb2 as ioc
from ioc_client.pb_rpc_pb2 import RPCall

class IocClient:
    def __init__(self, url=None):
        print("IOC|RMQ_init:",url)

        if url is None:
            url = 'amqp://rabbitmq:password@localhost:5672/'
            print("no RMQ url passed in, using the default URL", url)

        self.url = url
        self.model = None   # for callbacks


    # setup RMQ connection at start of interval
    def open(self):
        print("IOC|RMQ_open")
        return None   # FIXME/REMOVEME

        self.connection = pika.BlockingConnection(pika.URLParameters(self.url))
        self.channel = self.connection.channel()
        # self.channel.exchange_declare(exchange='e.rpc', type='topic', durable=True, auto_delete=False, passive=False)
        self.callback_queue = self.channel.queue_declare(
            exclusive=True).method.queue  # Sets up response queue (but what is that method crap?)
        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)  # Start rabbitmq response queue consumer

        self.corr_id = None
        self.response = None

#    def __del__(self):
    # close/free RMQ connection on end of interval because pause is coming
    def close(self):
        print("IOC|RMQ_close")
        return None   # FIXME/REMOVEME

        self.channel.stop_consuming()
        self.connection.close()


    # Called when rabbitmq delivers rpc response
    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:  # Make sure we respond to the right rpc
            print(props.headers)
            self.response = props


    def create_mark_ioc_msg(self, event_id, comment="Cogitated", async=False):
        msg = ioc.MarkIOCRequest()
        msg.comment = comment
        msg.eventIds.append(event_id)
        msg.async = async
        return msg

    def create_req(self, event_id, comment):
        request = RPCall()
        request.method = 'markIOC'
        request.parameters = self.create_mark_ioc_msg(event_id=event_id, comment=comment).SerializeToString()
        return request

    # called from model to mark a specific event
    def mark_ioc(self, event_id: str, comment: str):
        print("IOC|RMQ_mark_ioc: ",event_id, comment)
        return None   # FIXME/REMOVEME

        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='e.rpc',
                              routing_key='iocdetectionservice',
                              properties=pika.BasicProperties(headers={'CT-DID': '0000-0000', 'CT-User-Id': 'admin',
                                                                       'API-Version': '1',
                                                                       'Accepted-Content-Type': 'application/x-protobuf'},
                                                              reply_to=self.callback_queue,
                                                              correlation_id=self.corr_id),
                              body=self.create_req(event_id, comment).SerializeToString())
        # Wait for response until timeout (FIXME: actually waits forever)
        while self.response is None and time.time() < (10.0 + time.time()):
            self.connection.process_data_events()
