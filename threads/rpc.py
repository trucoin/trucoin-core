from trucoin.RPC import RPC
from trucoin.Mempool import Mempool
from trucoin.Transaction import Transaction
import time
import sys
import socket
import http.server
import selectors
import types
import json
import cgi
import socketserver
import threading
import zmq
import settings
from include.bottle import route, run, template, get, post, request, response, hook
import wsgiserver
from include import bottle
# Defining host and port
host = '0.0.0.0'
port = settings.RPC_PORT

# Handling Incoming RPC response
def response_handler(data):
    rpc = RPC()
    response = rpc.handlecommand(data)
    return response

@hook('after_request')
def enable_cors():
    response.headers['Content-Type'] = 'application/json'

@post('/')
def posting_handler():
    data = request.json
    if "command" not in data.keys():
        return {"status": "rejected"}
    return response_handler(data)

def rpc_receive():
    # RPC server
    print("Starting RPC Server at port %s" % settings.RPC_PORT)
    wsgiapp = bottle.default_app()
    httpd = wsgiserver.Server(wsgiapp)
    httpd.serve_forever()
