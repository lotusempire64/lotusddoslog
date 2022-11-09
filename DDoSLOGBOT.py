
import http.server
import socketserver
import time
import os
import sys
import json
import requests
import datetime

# config
PORT = 8080

# webhook
WEBHOOK_URL = 'your discord webhook'

# log file
LOG_FILE = 'log.txt'

# ddos attack log
DDOS_LOG = 'ddos.txt'

# ddos attack threshold
THRESHOLD = 5

# ddos attack time
TIME = 10

# keep alive
KEEP_ALIVE = True

# keep alive time
KEEP_ALIVE_TIME = 60

# keep alive url
KEEP_ALIVE_URL = 'your webserver'

# keep alive webhook
KEEP_ALIVE_WEBHOOK = 'your discord webhook here'


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # log request
        with open(LOG_FILE, 'a') as f:
            f.write(f'{self.client_address[0]} {self.command} {self.path} {self.request_version}\n')

        # check if ddos attack
        if self.client_address[0] in ddos_attack:
            # check if ddos attack is over
            if time.time() - ddos_attack[self.client_address[0]] > TIME:
                # remove from ddos attack
                del ddos_attack[self.client_address[0]]
            else:
                # log ddos attack
                with open(DDOS_LOG, 'a') as f:
                    f.write(f'{self.client_address[0]} {self.command} {self.path} {self.request_version}\n')

                # send ddos attack to discord
                requests.post(WEBHOOK_URL, json={
                    'content': f'{self.client_address[0]} {self.command} {self.path} {self.request_version}'
                })

                # block request
                return

        # check if ddos attack
        if self.client_address[0] in ddos_attack_count:
            # add to ddos attack count
            ddos_attack_count[self.client_address[0]] += 1
        else:
            # create ddos attack count
            ddos_attack_count[self.client_address[0]] = 1

        # check if ddos attack count is over threshold
        if ddos_attack_count[self.client_address[0]] > THRESHOLD:
            # add to ddos attack
            ddos_attack[self.client_address[0]] = time.time()

            # remove from ddos attack count
            del ddos_attack_count[self.client_address[0]]

        # handle request
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


# create server
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    # log server started
    print(f'Server started on port {PORT}')

    # create ddos attack
    ddos_attack = {}

    # create ddos attack count
    ddos_attack_count = {}

    # keep alive
    if KEEP_ALIVE:
        # create keep alive
        keep_alive = True

        # keep alive loop
        while keep_alive:
            # log keep alive
            print(f'Keep alive {datetime.datetime.now()}')

            # try to get keep alive url
            try:
                # get keep alive url
                requests.get(KEEP_ALIVE_URL)
            except:
                # send keep alive error to discord
                requests.post(KEEP_ALIVE_WEBHOOK, json={
                    'content': f'Keep alive error {datetime.datetime.now()}'
                })

            # sleep
            time.sleep(KEEP_ALIVE_TIME)

    # serve forever
    httpd.serve_forever()
