#!/usr/bin/env python3

### uncomment for debugging to see if correct LOCALE is set (when called in Docker container)
#
#import locale; import sys;
#print(locale.getpreferredencoding())
#print(sys.getdefaultencoding())
#print(sys.stdout.encoding)
#sys.exit(1)

#############################################################################

import argparse
from sys import exit
from pprint import pprint

from protoapi.protoserver import Protoserver
from protoapi.rabbitmq import Rabbitmq


parser = argparse.ArgumentParser(add_help=True)

# parser.add_argument("-p", dest='port', required=False,
#                     help="listen port number")
#
# parser.add_argument("-ho", dest='host', required=False,
#                     help="host name")

parser.add_argument("-u", dest='url', required=False,
                    help="RMQ server URL, e.g: amqp://server:5672")

parser.add_argument("-req", dest='req', required=False,
                     help="requests queue name (default: "+Rabbitmq.REQUEST_Q+")")

parser.add_argument("-res", dest='res', required=False,
                     help="responses queue name (default: "+Rabbitmq.RESPONSE_Q+")")

#############################################################################

def run(url=None, req=None, res=None, **kwargs):   # port=None, host=None,
    if res and not req:
        print("requestsQ queue specified but no responses queue"); exit(1)

    if req and not res:
        print("responses queue specified but no requestsQ queue"); exit(1)

    requestsQ = Rabbitmq.REQUEST_Q
    if req:
        requestsQ = req

    responsesQ = Rabbitmq.RESPONSE_Q
    if res:
        responsesQ = res


    if not url:
        print("using URL default: amqp://server:5672 ")
        url = "amqp://server:5672"

    rmq = Rabbitmq(url, requestsQ, responsesQ)
    server = Protoserver()

    print("waiting for requests...")

    while True:
        data = rmq.receive(requestsQ)

        result = server.parse_and_execute(data)

        rmq.publish(responsesQ, result)
        print("request finished")


args = parser.parse_args()
dictargs = vars(args)
#pprint(dictargs)
run(**dictargs)
