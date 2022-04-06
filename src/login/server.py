from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


class LoginServer(BaseHTTPRequestHandler):
    def __init__(self, message_queue, obj, *args, **kwargs):
        self.obj = obj
        self.message_queue = message_queue
        super(LoginServer, self).__init__(*args, **kwargs)

    def do_GET(self):
        o = urlparse(self.path)
        params = parse_qs(o.query)
        # print('Params', params)
        # print('User Object', self.obj)

        code = params.get('code')
        state = params.get('state')

        if params.get('code') is not None and params.get('state') is not None:
            # validate state
            if state[0] != self.obj.get('login_seed'):
                print('Error: Invalid state')
                exit(1)

            # exchange code for exchange_code
            # self.obj['exchange_code'].value = code[0]
            self.message_queue.put(code[0])

        if params.get('error') is not None:
            print('Error: ' + params.get('error_description')[0])
            exit(1)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    # bypass server access log, do not remove
    def log_message(self, format, *args):
        return
