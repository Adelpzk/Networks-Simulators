import socket
from datetime import datetime
import os
import mimetypes

####################################
class WebServer():
  
  def __init__(self, buffer_size = 1024, format_type = "UTF-8", server = '127.0.0.1', port = 10200, queue_size=0):
    self.BUFFER_SIZE = buffer_size
    self.FORMAT = format_type
    self.SERVER = server
    self.PORT = port
    self.QUEUE_SIZE = queue_size
    self.server_socket = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM) # TCP 
    self.server_socket.bind((self.SERVER, self.PORT)) 
  
  def start(self):    
    # Listening for new connections
    self.server_socket.listen(self.QUEUE_SIZE)

    while(True):
      client, addr = self.server_socket.accept() 
      # client = new socket object usable to send and receive data on the connection
      # addr = address bound to the socket on the other end of the connection (requestor's addr)
      self.handle_client(client, addr)

  # GENERATE RESPONSE HEADER
  def create_resp_header(self, version, filepath):

    file_length = os.path.getsize(filepath)
    modification_time = os.path.getmtime(filepath)
    modification_datetime = datetime.fromtimestamp(modification_time)
    formatted_mod_datetime = modification_datetime.strftime("%Y-%m-%d %H:%M:%S")

    content_type, encoding = mimetypes.guess_type(filepath)
    date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    header = "Connection: close\n" if (version == "HTTP/1.0") else  "Connection: keep-alive\n"
    header += f"Date: {date}\n"
    header += f"Server: webserver\n"
    header += f"Last_Modified: {formatted_mod_datetime}\n"
    header += f"Content_Length: {file_length}\n"
    header += f"Content_Type: {content_type}; charset={self.FORMAT}\n"

    return header

  # HANDLE CLIENT
  def handle_client(self, client_connection, addr):    
    # Receive the HTTP request header
    request = client_connection.recv(self.BUFFER_SIZE).decode(self.FORMAT)
    
    # Check if the request is empty (end of connection)
    if not request:
      client_connection.close()
      return

    request_lines = request.split("\r\n")
    first_line = request_lines[0]
    method, path, version = first_line.split()

    try:
      fin = open("."+path)
      content = fin.read()
      fin.close()
      header = f'{version} 200 OK \n'+self.create_resp_header(version, "."+path)

      if (method == "GET"):
        response = header+'\n'+content
        client_connection.sendall(response.encode(self.FORMAT))

      if (method == "HEAD"):
        response = header+'\n'
        client_connection.sendall(response.encode(self.FORMAT))

    except(FileNotFoundError, IsADirectoryError) as e:
      fin = open("./404.html")
      content = fin.read()
      fin.close()

      header = f'{version} 404 NOT FOUND\n'+self.create_resp_header(version, "./404.html")

      response = ""
      if (method == "GET"):
        response = header+'\n'+content
      if (method == "HEAD"):
        response = header+'\n'

      client_connection.sendall(response.encode(self.FORMAT))


    client_connection.close()
    return

if __name__ == '__main__':
  server = WebServer()
  server.start()


################################################################################# 

"""
socket.accept():
  Accept a connection. The socket must be bound to an address 
  and listening for connections. The return value is a pair (conn, address) 
  where conn is a new socket object usable to send and receive data on the connection, 
  and address is the address bound to the socket on the other end of the connection.

socket.close()
  Mark the socket closed. The underlying system resource (e.g. a file descriptor) 
  is also closed when all file objects from makefile() are closed. 
  Once that happens, all future operations on the socket object will fail. 
  The remote end will receive no more data (after queued data is flushed).

socket.connect(addr)
  Connect to a remote socket at address. 
  (The format of address depends on the address family)

  If the connection is interrupted by a signal, the method waits 
  until the connection completes, or raise a TimeoutError on timeout, 
  if the signal handler doesn’t raise an exception and the socket is 
  blocking or has a timeout. For non-blocking sockets, the method raises an 
  InterruptedError exception if the connection is interrupted by a signal 
  (or the exception raised by the signal handler).

socket.bind(addr)
  Bind the socket to address. The socket must not already be bound. 
  (The format of address depends on the address family)

"""
