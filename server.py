#!/usr/bin/env python3

# SPDX-License-Identifier: GPL-3.0-or-later
#
# Very simple HTTP server in python for logging mapper coordinates
# from a Helium GPS tracker.
# Usage::
#    ./server.py [<port>]

from http.server import BaseHTTPRequestHandler, HTTPServer
import ssl
import logging
import tracker

class Server(BaseHTTPRequestHandler):
    def __init__(self, *args):
        self.tracker = tracker.Tracker()
        BaseHTTPRequestHandler.__init__(self, *args)

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.debug("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("42".encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.debug("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))
        try:
            self.tracker.record(post_data)
        except Exception as e:
            print('Exception occurred with the following json: {}'.format(post_data))
            print('Exception: ' + str(e))
        logging.info('Received: json: {}'.format(post_data))
        self._set_response()
        self.wfile.write("42".encode('utf-8'))

def run(server_class=HTTPServer, handler_class=Server, port=8080):
    # TODO - why Helium console refuses the LetsEncrypt certificate?
    #KEYPATH='/etc/letsencrypt/live/my-local-server.duckdns.org'
    KEYPATH=None

    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    if KEYPATH is not None:
        # Keypath provided. Activate SSL.
        sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        sslctx.load_cert_chain(certfile=KEYPATH+'/cert.pem', keyfile=KEYPATH+'/privkey.pem')
        httpd.socket = sslctx.wrap_socket(httpd.socket, server_side=True)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
