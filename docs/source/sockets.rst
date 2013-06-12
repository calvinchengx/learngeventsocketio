What are sockets?
=======================

Written in C, Berkeley sockets (BSD sockets) is a computing library with an API for internet sockets and other unix domain sockets used for inter-process communication.  The API has not changed much in its POSIX equivalent, so POSIX sockets are basically Berkeley sockets.

All modern operating systems come with some implementation of the Berkeley socket interface because it has become the standard interface for connecting to the internet.

Various programming languages provide similar interfaces and are essentially wrappers around the BSD socket C API.

Python sockets
--------------------

Gordon McMillan wrote a great overview of sockets and how python's standard socket module can easily be used to create a socket for IPC (Inter-Process Communication).

* python2:  http://docs.python.org/2/howto/sockets.html
* python3:  http://docs.python.org/3/howto/sockets.html

When a socket is created, an endpoint for communication becomes available and a corresponding file descriptor is returned.  A file descriptor is simply an abstract indicator for accessing a file and has integer values of 0, 1, 2 corresponding to standard input (stdin), standard output (stdout) and standard error (stderr).

A simple example illustrates how a server socket and a client socket can be created to send data to each other.

.. code:: python

   # server.py
   import socket

   serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   serversocket.bind(('localhost', 8089))
   serversocket.listen(5)

   while True:
       connection, address = serversocket.accept()
       buf = connection.recv(64)
       if len(buf)>0:
           print buf
  
   # client.py
   import socket

   clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   clientsocket.connect(('localhost', 8089))
   clientsocket.send('hello')

After we run server.py

.. code:: sh

   python server.py

We run client.py

.. code:: sh

   python client.py

And "hello" gets printed out on the `python server.py` process stdout (standard output).

Our webservers can be implemented in python or C or golang or any other languages but the basis from which data is passed between each other via the HTTP (TCP) protocol rest upon sockets. Sockets are the fundamental building block from which HTTP, HTTPS, FTP, SMTP protocols (all of these are TCP-type protocols) are defined.

DNS, DHCP, TFTP, SNMP, RIP, VOIP protocols are UDP protocols but they too are built on top of sockets.


So what's WebSocket?
----------------------------

WebSocket is a full-duplex communication channel over one single TCP-type connection. It is an independent TCP-type protocol and its only association to HTTP is that its handshake is intepreted by HTTP servers as an Upgrade request. HTTP 1.1 introduced an "Upgrade" header field and this connection "Upgrade" must be sent by the client (in other words, this "Upgrade" header is sent by SocketIO javascript client to tell the server that this is a WebSocket connection).  The server can also enforce an upgrade by sending a "426 upgrade required" response back to the client and the client will have to handle this response accordingly - either upgrade or fail the websocket connection attempt.

This is how our WebSocket can work seamlessly with a HTTP server.

WebSocket is a browser/client feature and only works on browsers (or custom clients, if you are writing your custom native app) that support it.  Socket.IO client library intelligently determines if the browser it is loaded up on supports WebSocket or not.  If it does, it will use WebSocket to communicate with the server-side SocketIO server.  If it does not, it will attempt to use one of the fallback transport mechanisms.

WebSocket differs from TCP protocols like HTTP in that it enables a stream of messages instead of a stream of bytes. Before WebSocket, port 80 full-duplex communication was attainable using Comet.  However, compared to WebSocket, comet implementation is non-trivial and is inefficient for small messages because of TCP handshake and HTTP header overheads.

A WebSocket protocol handshake looks like this:

**Client sends a WebSocket handshake request.**

.. code:: sh 

    GET /mychat HTTP/1.1
    Host: server.example.com
    Upgrade: websocket
    Connection: Upgrade
    Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==
    Sec-WebSocket-Protocol: chat
    Sec-WebSocket-Version: 13
    Origin: http://example.com

**Server returns a WebSocket handshake response.**

.. code:: sh

    HTTP/1.1 101 Switching Protocols
    Upgrade: websocket
    Connection: Upgrade
    Sec-WebSocket-Accept: HSmrc0sMlYUkAGmm5OPpG2HaGWk=
    Sec-WebSocket-Protocol: chat


A protocol like HTTP uses a (BSD socket) socket for only one transfer. The client sends the request, then reads the reply and the socket is discarded.  This means that a HTTP client can detect the end of the reply by receiving 0 bytes.

For WebSocket, once a connection is established, the client and server can send WebSocket data or text frames back and forth in full-duplex mode.  The data itself is minimally framed, containing a small header and the payload.  WebSocket transmissions are described as "messages" where a single message can optionally be splitted across several data frames. This can allow for sending of messages where initial data is available but the complete length of the message is unknown (it sends one data frame after another until the end is reached and marked with the FIN bit). With extensions to the protocol, this can also be used for multiplexing several streams simultaneously (for instance to avoid monopolizing use of a socket for a single large payload).
