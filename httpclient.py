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

import json
import sys
import socket
import re
from typing import Dict
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

    def get_code(self, data):
        code = re.findall(r'(?=\d{3})\w+', data)[0]
        code = int(code)
        return code

    def get_headers(self,data): 
        
        data_list = data.split('\r\n')
        split_point = data_list.index('')
        header_list = []

        for x in range(0, split_point):
            header_list.append(data_list[x])

        header_string = ''
        for line in header_list:
            header_string += line + '\r\n'
        
        return header_string

    def get_body(self, data):
        
        data_list = data.split('\r\n')
        split_point = data_list.index('')
        body_list = []
        for x in range(split_point, len(data_list)):
            body_list.append(data_list[x])   
        body_string = ''
        for line in body_list:
            body_string += line + '\r\n'
        return body_string
    
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
        
        hostname, path = self.setup(url)
        
        
        to_send = f'GET {path} HTTP/1.1\r\nUser-Agent: python/3.8.5\r\nHost: {hostname}\r\nAccept: */*\r\nConnection: close\r\n\r\n'        
        
        self.sendall(to_send)
        data = self.recvall(self.socket)
        self.close()
        
        code = self.get_code(data)  
        body = self.get_body(data)
        headers = self.get_headers(data)        
        # print(headers + body)      
        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):

        hostname, path = self.setup(url)
        
    
        bytes = len(json.dumps(args).encode('utf-8'))
        to_send = f'POST {path} HTTP/1.1\r\nUser-Agent: python/3.8.5\r\nHost: {hostname}\r\nAccept: */*\r\nContent-Length: {bytes}\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n{args}'

        #to_send = f'POST {path} HTTP/1.1\r\nUser-Agent: python/3.8.5\r\nHost: {hostname}\r\nAccept: */*\r\nContent-Type: application/x-www-form-urlencoded\r\nConnection: close\r\n\r\n'        
    
        self.sendall(to_send)
        
        data = self.recvall(self.socket)
        
        print('Hey there, this data \n' + data)
        
        self.close()
        code = self.get_code(data)
        body = self.get_body(data)
        headers = self.get_headers(data)

        # print(headers + body)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

    def setup(self, url):
        # check for http
        if 'http' not in url:
            new_url = 'http://' + url
        else:
            new_url = url
        
        # parse url info
        hostname = urllib.parse.urlparse(new_url).hostname
        port = urllib.parse.urlparse(new_url).port
        path = urllib.parse.urlparse(new_url).path

        if path == '':
            path = '/'
        if port == None:
            port = 80
        
        # connect
        self.connect(hostname, port)
        
        return (hostname, path)
    
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
