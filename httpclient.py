#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def parse_url(self, url):
        '''
        If the path is not present, assigned "/" to it 
        If the port is not provided, use the default port 80
        '''
        o = urllib.parse.urlparse(url)
        path = o.path or "/"
        port = o.port or 80
        return path, port, o

    def get_code(self, data):
        '''
        extract status code from header
        '''
        lines = data.split("\r\n")
        status_code = lines[0].split(" ")[1]
        return int(status_code)  # second element 
       
    def request_GET(self, host, path):
        return (
        "GET {} HTTP/1.1\r\n".format(path) +
        "Host: {}\r\n".format(host) +
        "Accept: */*\r\n" +
        "Connection: close\r\n\r\n"
        )
        

    def request_POST(self, host, path, args):
        request = "POST {} HTTP/1.1\r\n".format(path)
        request += "Host: {}\r\n".format(host)
        request += "Accept: */*\r\n"
        request += "Connection: close\r\n"

        # get the length of args
        args_length = "0"
        if args is not None:
            args_length = len(args)

        request += "Content-Length: {}\r\n".format(args_length)
        request += "\r\n"

        # get content of body
        if args is not None:
            request += "{}\r\n".format(args)
        return request

    def none_chacker(self, args):
        '''
        check if args is none 
        '''
        if args is not None:
            args = urllib.parse.urlencode(args)
        return args

    # def get_headers(self,data):
    #     lines = data.split("\r\n\r\n") # header with status code
    #     header = lines[0].split("\r\n")
    #     header.pop(0)  # remove the first line 
    #     return header 

    def get_body(self, data):
        lines = data.split("\r\n\r\n")
        body = lines[1]
        return body

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        path, port, o = self.parse_url(url)

        self.connect(o.hostname, port) 
        self.sendall(self.request_GET(o.hostname, path))
        request = self.recvall(self.socket)
        code = self.get_code(request)
        body = self.get_body(request)
        self.close()
        
        print(body)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        args = self.none_chacker(args)
        path, port, o = self.parse_url(url)

        self.connect(o.hostname, port) 
        self.sendall(self.request_POST(o.hostname, path, args))
        request = self.recvall(self.socket)
        code = self.get_code(request)
        body = self.get_body(request)
        self.close()
        
        print(body)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        '''
        used to call either the GET or POST method based on the first argument
        '''
        # only one arg provided, we assume it is url and use GET by default 
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
