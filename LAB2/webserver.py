import socket
from datetime import datetime
import os
import mimetypes

####################################
class WebServer():
  
  def __init__(self, buffer_size = 10242, format_type = "UTF-8", server = '127.0.0.1', port = 10501, queue_size=1):
    self.BUFFER_SIZE = buffer_size
    self.FORMAT = format_type
    self.SERVER = server
    self.PORT = port
    self.QUEUE_SIZE = queue_size
    self.server_socket = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM) # TCP 
    self.server_socket.bind((self.SERVER, self.PORT)) 
  
  def start(self):
    # print(f"[SERVER] starting server ... ")
    
    # Listening for new connections
    self.server_socket.listen(self.QUEUE_SIZE)

    # print(f"[SERVER] Listening on {self.PORT}")
    while(True):
      client, addr = self.server_socket.accept() 
      # client = new socket object usable to send and receive data on the connection
      # addr = address bound to the socket on the other end of the connection (requestor's addr)
      self.handle_client(client, addr)

  # SEND MESSAGE THROUGH CONNECTION
  def send(self, conn, message):
    msg = message.encode(self.FORMAT)
    msg_len = len(msg)
    send_length = str(msg_len).encode(self.FORMAT)
    send_length += b" "*(self.BUFFER_SIZE - len(send_length))
    conn.send(send_length)
    conn.send(msg)

  # GENERATE RESPONSE HEADER
  def create_resp_header(self, version, filepath):
    file_length = len(filepath)

    modification_time = os.path.getmtime(filepath)
    modification_datetime = datetime.fromtimestamp(modification_time)
    formatted_mod_datetime = modification_datetime.strftime("%Y-%m-%d %H:%M:%S")

    content_type, encoding = mimetypes.guess_type(filepath)

    date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    header = "Connection: close\n" if (version == "HTTP/1.0") else  "Connection: keep-alive\n"
    header += f"Date: {date}\n"
    header += f"Server: {self.SERVER}\n"
    header += f"Last_Modified: {formatted_mod_datetime}\n"
    header += f"Content_Length: {file_length}\n"
    header += f"Content_Type: {content_type}\n"

    return header

  # HANDLE CLIENT
  def handle_client(self, conn, addr):    
    # Receive the HTTP request header
    request = conn.recv(self.BUFFER_SIZE).decode(self.FORMAT)
    
    # Check if the request is empty (end of connection)
    if not request:
      conn.close()
      return

    request_lines = request.split("\r\n")
    first_line = request_lines[0]
    method, path, version = first_line.split()
    print(f"[CLIENT HANDLER] {method} request")

    try:
      fin = open("."+path)
      content = fin.read()
      fin.close()
      header = f'{version} 200 OK \n'+self.create_resp_header(version, "."+path)

      if (method == "GET"):
        response = header+'\n'+content
        conn.sendall(response.encode(self.FORMAT))

      if (method == "HEAD"):
        response = header+'\n'
        conn.sendall(response.encode(self.FORMAT))

    except(FileNotFoundError, IsADirectoryError):
      header = f"{version} 404 NOT FOUND\n\n <h1><b>404 Not Found</b></h1>"
      response = header+'\n'
      conn.sendall(response.encode(self.FORMAT))


    conn.close()
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

socket.makefile(mode='r', buffering=None, *, encoding=None, errors=None, newline=None)
  Return a file object associated with the socket. The exact returned type 
  depends on the arguments given to makefile(). These arguments are 
  interpreted the same way as by the built-in open() function, 
  except the only supported mode values are 'r' (default), 'w' and 'b'.

  The socket must be in blocking mode; it can have a timeout, 
  but the file object’s internal buffer 
  may end up in an inconsistent state if a timeout occurs.

  Closing the file object returned by makefile() won’t close the original socket 
  unless all other file objects have been closed 
  and socket.close() has been called on the socket object.

"""
