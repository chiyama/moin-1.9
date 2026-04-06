# taken from Amos' XML-RPC HowTo:

import xmlrpc.client
import http.client
from base64 import encodebytes

class BasicAuthTransport(xmlrpc.client.Transport):
    def __init__(self, username=None, password=None):
        super().__init__()
        self.username = username
        self.password = password
        self.verbose = 0

    def request(self, host, handler, request_body, verbose=False):
        # issue XML-RPC request
        h = http.client.HTTPConnection(host)

        headers = {
            'Host': host,
            'User-Agent': self.user_agent,
            'Content-Type': 'text/xml',
            'Content-Length': str(len(request_body)),
        }

        # basic auth
        if self.username is not None and self.password is not None:
            credentials = ("%s:%s" % (self.username, self.password)).encode('utf-8')
            authhdr = "Basic %s" % encodebytes(credentials).decode('ascii').replace("\n", "")
            headers['Authorization'] = authhdr

        h.request("POST", handler, request_body, headers)
        response = h.getresponse()

        if response.status != 200:
            raise xmlrpc.client.ProtocolError(
                host + handler,
                response.status, response.reason,
                dict(response.getheaders())
                )

        return self.parse_response(response)
