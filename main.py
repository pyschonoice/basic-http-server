import socket

class HTTPServer:

    def __init__(self,host = '127.0.0.1', port=8080):
        self.host = host
        self.port = port

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
        print(parsed_data)
        
    
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