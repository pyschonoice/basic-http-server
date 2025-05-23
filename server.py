import json
import socket
import os
import mimetypes

import urllib
import urllib.parse

class HTTPServer:

    STATUS_CODES ={
        200: "OK",
        404: "Not Found",
        405: "Method Not Allowed",
        415: "Unsupported Media Type",
        500: "Internal Server Error"
    }

    def __init__(self,host = '127.0.0.1', port=8080,static_folder="static"):
        self.host = host
        self.port = port
        self.static_folder = static_folder

    def create_socket(self):
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.bind((self.host,self.port))
        s.listen(5)
        self.server_socket = s
        print(f"Listening at {self.host}: {self.port}")

    def accept_connections(self):
        while True:
            client_socket,address = self.server_socket.accept()
            print(f"Connection from {address}")
            self.handle_client(client_socket)

    def handle_client(self,client_socket):
        data = self.read_full_request(client_socket)
        parsed_data = self.parse_request(data)
        
        method = parsed_data["method"]
        path = parsed_data["path"]
        headers = parsed_data["headers"]
        body = parsed_data["body"]
        response = self.handle_routes(method,path,headers,body)

        client_socket.sendall(response.encode())
        client_socket.close()

        
        
    
    def read_full_request(self,client_socket):
        buffer = b""
        headers_parsed = False
        content_length = 0

        while True:
            chunk = client_socket.recv(1024)
            if not chunk:
                break
            buffer+=chunk

            if not headers_parsed:
                try:
                    text = buffer.decode()
                    if "\r\n\r\n" in text:
                        headers_parsed = True
                        header, _ = text.split("\r\n\r\n",1)
                        lines = header.split("\r\n")
                        for line in lines[1:]:
                            key,value = line.split(": ",1)
                            if key.lower() == "content-length":
                                content_length = int(value)
                except UnicodeDecodeError:
                    continue
            
            if headers_parsed:
                body_start = buffer.find(b"\r\n\r\n") + 4
                body_length = len(buffer) - body_start
                if body_length >= content_length:
                    break

        return buffer.decode()

    def parse_request(self,raw_text):

        lines = raw_text.split("\r\n")
        request_line = lines[0]
        method,path,version = request_line.split()

        headers = {}
        body =""
        for idx, line in enumerate(lines[1:],1):
            if line == "": 
                header_end_index = idx
                break
            if ": " in line:
                key,value = line.split(": ",1)
                headers[key]= value
        
        if 'Content-Length' in headers:
            header_size = len("\r\n".join(lines[:header_end_index])+"\r\n\r\n")
            body = raw_text[header_size:]

        data = {
            "method" : method,
            "path" : path,
            "version" : version,
            "headers" : headers,
            "body" : body
        }
    

        return data

    def build_response(self,status_code,body, content_type = "text/plain"):
        reason =  self.STATUS_CODES.get(status_code,"unknown")
        body_bytes =  body.encode()
        headers = {
            "Content-Type": content_type,
            "Content-Length": len(body_bytes),
            "Connection": "close"
        }

        response_line = f"HTTP/1.1 {status_code} {reason}\r\n"
        headers_lines = "".join([
            f"{key}: {value}\r\n" for key,value in headers.items()
        ])
        blank_line ="\r\n"
        
        return response_line + headers_lines + blank_line + body
    
    def handle_routes(self,method,path,headers,body):

        if method == "GET":
            response = self.handle_get(path)
        elif method == "POST":
            response = self.handle_post(path,headers,body)
        else:
            response = self.build_response(405,f"Method {method} Not Allowed ")

        return response

    def handle_get(self,path):
        if path == "/":
            path = "/index.html"

        file_path = os.path.join(self.static_folder,path.lstrip("/"))
        if os.path.isfile(file_path):
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = "application/octet-stream"
            try:
                with open(file_path,"r",encoding="utf-8") as f:
                    body = f.read()
                return self.build_response(200,body,content_type)
            except Exception as e:
                return self.build_response(500,f"Internal Server error {e}")
       
        return self.build_response(404,"Page Not Found")
    
    def handle_post(self,path,headers,body):
        content_type = headers.get("Content-Type","").lower()
        if content_type.startswith("application/json"):
            try:
                parsed_body = json.loads(body)
                response_body = f"Recieved JSON:\n{json.dumps(parsed_body,indent=2)}"
                return self.build_response(200,response_body)
            except json.JSONDecodeError:
                return self.build_response(400,"Invalid JSON")
        elif content_type.startswith("application/x-www-form-urlencoded"):
            parsed_body = urllib.parse.parse_qs(body)
            response_body = f"Recieved Form Data:\n{json.dumps(parsed_body,indent=2)}"
            return self.build_response(200, response_body)
        else:
            return self.build_response(415, f"Unsupported Content-Type: {content_type}")


        
    def start(self):
        try:
            self.create_socket()
            self.accept_connections()
        except KeyboardInterrupt:
            print("Shutting down the server")
        finally:
            self.server_socket.close()
        


server = HTTPServer()
server.start()