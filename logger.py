import json
import logging.handlers
import urllib.request

import settings


class WebhookHandler(logging.handlers.BufferingHandler):
    def __init__(self, webhook_url, capacity=200):
        logging.handlers.BufferingHandler.__init__(self, capacity)
        self.webhook_url = webhook_url

    def flush(self):
        if len(self.buffer) > 0:
            message = ''
            for record in self.buffer:
                s = self.format(record)
                message += s + "\r\n"
            self.post(message)
            self.buffer = []

    def post(self, message):
        payload = {
            'text': message,
        }
        data = json.dumps(payload).encode()
        headers = {'content-type': 'application/json'}
        request = urllib.request.Request(self.webhook_url, data, headers)
        urllib.request.urlopen(request).read().decode()


def configure():
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s', 
        level=logging.INFO
    )
    logger = logging.getLogger('')

    webhook_url = getattr(settings, 'WEBHOOK_URL', None)
    if webhook_url:
        handler = WebhookHandler(webhook_url)
        formatter = logging.Formatter(
            fmt='%(asctime)s %(levelname)s %(message)s', 
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
