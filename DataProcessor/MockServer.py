#!/usr/bin/env python

import socket, asyncore, sys
import simplejson as json

class BufferHandler(asyncore.dispatcher_with_send):
    def __init__(self, sock):
        asyncore.dispatcher_with_send.__init__(self, sock)
        #self.message_list = message_list
    def handle_read(self):
        data = self.recv(1024)
        if data:
            print data
            sys.exit(0)

class MockServer(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            handler = BufferHandler(sock)

def main():
    configfile = sys.argv[1]
    config = json.load(open(configfile, 'r'))
    host = socket.gethostname()
    port = config['socket_port']
    server = MockServer(host, port)
    asyncore.loop(5)

if __name__ == '__main__':
    main()
