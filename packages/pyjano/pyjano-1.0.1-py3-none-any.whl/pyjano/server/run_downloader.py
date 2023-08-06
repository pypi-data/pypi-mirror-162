import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler


class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super(CORSRequestHandler, self).end_headers()

if __name__ == '__main__':

    port = 5000
    if len(sys.argv) > 1:
        port=int(sys.argv[1])

    httpd = HTTPServer(('localhost', port), CORSRequestHandler)
    httpd.serve_forever()
