from http.server import HTTPServer, BaseHTTPRequestHandler
from flask import Flask, request, make_response, jsonify
from mongo_connect import DB
from prometheus_client import MetricsHandler
import mongo_utils 
import socket
import socketserver
import logging
import time
import json
import re
import requests
import pymongo
import threading
import logging 
import datetime

hostName = "0.0.0.0"
PROMETHEUS_PORT = 8000
CRAWL_PERIOD = 86400

class PrometheusEndpointServer(threading.Thread):
    """A thread class that holds an http and makes it serve_forever()."""
    def __init__(self, httpd, *args, **kwargs):
        self.httpd = httpd
        super(PrometheusEndpointServer, self).__init__(*args, **kwargs)

    def run(self):
        self.httpd.serve_forever()


def start_prometheus_server():
    try:
        httpd = HTTPServer((hostName, PROMETHEUS_PORT), MetricsHandler)
    except (OSError, socket.error):
        return

    thread = PrometheusEndpointServer(httpd)
    thread.daemon = True
    thread.start()
    logging.info("Exporting Prometheus /metrics/ on port %s", PROMETHEUS_PORT)

server = Flask(__name__)
start_prometheus_server()
database = None

def response_form(error):
    if error == None:
        return_message = {"results" : "Operation Succeed"}
        return return_message
    else:
        return_message = {"error" :  "%s field is wrong or missing." % str(error)}
        return return_message


@server.route('/spam-data', methods = ['POST'])
def save_request():
    data_handle = request.get_json()
    er = None #error message
    #connect to mongodb
    global database
    if database is None:
        database = DB
    
    try:
        #Traverse through message
        for item in data_handle["items"]:
            mongo_util = mongo_utils.MongoUtils(database, item, CRAWL_PERIOD)
            er = mongo_util.check_type_attribute()
            if er != None:
                break
            mongo_util.to_database()           
    except KeyError as error:
        er = error

    #Construct POST return message
    return response_form(er)



