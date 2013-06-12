What is socketio?
=======================

Socket.IO is a javascript library for real-time web applications.  It has two parts 

* a client side library that runs in the browser; and 
* a server-side library for node.js. 
  
Both components have identitical API and are event-driven.

There are implementations for the **server-side library in other languages**. 

In python land, we use the gevent-socketio library.

    .. code:: sh

        pip install -e "git://github.com/abourget/gevent-socketio.git#egg=gevent-socketio"

Whichever server-side language implementation we so choose, the following 6 transports are supported:

* WebSocket
* Adobe® Flash® Socket
* AJAX long polling
* AJAX multipart streaming
* Forever Iframe
* JSONP Polling

Socket.IO selects the most capable transport at runtime without affecting its APIs so that we can have realtime connectivity on every browser.


Various Language Implementations
----------------------------------

* Python

  + gevent-socketio -   https://github.com/abourget/gevent-socketio

* Perl   

  + PocketIO -          https://github.com/vti/pocketio

* Java

  + Atmosphere -        https://github.com/Atmosphere/atmosphere
  + Netty-socketio -    https://github.com/mrniko/netty-socketio
  + Gisio for Google's GWT Framework - https://bitbucket.org/c58/gnisio
  + Socket.IO for Vert.x -  https://github.com/keesun/mod-socket-io

* Golang

  + go-socket.io (supports up to socket.io client 0.6) - https://github.com/davies/go-socket.io
  + go-socket.io (supports up to socket.io client 0.8) - https://github.com/murz/go-socket.io    
  
* Erlang

  + Socket.IO-Erlang (supports up to socket.io client 0.6) -    https://github.com/yrashk/socket.io-erlang
  + erlang Socket.IO (supports up to socket.io client 1.0) -    https://code.google.com/p/erlang-scoketio



