import sys

from pyjano.server import create_server


if __name__ == '__main__':

    server = create_server(debug=True)
    if len(sys.argv) > 1:
        server.run(port=int(sys.argv[1]))
    else:
        server.run()
