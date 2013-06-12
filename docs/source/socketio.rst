What is Socket.IO?
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


ServerIOServer example
----------------------------------------------

The simplest way to launch a `SocketIOServer`:-

.. code:: python

    from gevent import monkey
    from socketio.server import SocketIOServer


    monkey.patch_all()

    PORT = 5000

    if __name__ == '__main__':
        print 'Listening on http://127.0.0.1:%s and on port 10843 (flash policy server)' % PORT
        SocketIOServer(('', PORT), app, resource="socket.io").serve_forever()

SocketIOServer is our python implementation of the original Socket.IO server-side nodejs library.

The full source code can be referred to here - https://github.com/abourget/gevent-socketio/blob/master/socketio/server.py

And we can see that it accepts a `(host, port)` argument, the `app` instance argument, a `resource` argument and optionally a list of `transports`, the flash `policy_server` as a boolean and an arbitrary list of keyword arguments.

SocketIOServer host and port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The `host and port tuple` argument is straightforward - provide the IP address and the port that we would like to run our `SocketIOServer` on.

SocketIOServer app
~~~~~~~~~~~~~~~~~~~~~~~~~~

The `app` argument is simply an instance of the python application that we will run.

Here's a `django` example:

.. code:: python

    # runserver_socketio.py

    #!/usr/bin/env python
    from gevent import monkey
    from socketio.server import SocketIOServer
    import django.core.handlers.wsgi
    import os
    import sys

    monkey.patch_all()

    try:
        import settings
    except ImportError:
        sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
        sys.exit(1)

    PORT = 9000

    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

    app = django.core.handlers.wsgi.WSGIHandler()

    sys.path.insert(0, os.path.join(settings.PROJECT_ROOT, "apps"))

    if __name__ == '__main__':
        print 'Listening on http://127.0.0.1:%s and on port 10843 (flash policy server)' % PORT
        SocketIOServer(('', PORT), app, resource="socket.io").serve_forever()

SocketIOServer resource
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The `resource` argument is where we will have to define our actual python application's Socket.IO `url`.

For a django application, we define in our `urls.py`, like this

.. code:: python

    # urls.py

    from django.conf.urls.defaults import patterns, include, url
    import socketio.sdjango

    socketio.sdjango.autodiscover()

    urlpatterns = patterns("chat.views",
        url("^socket\.io", include(socketio.sdjango.urls)),

`sdjango` is a pre-written integration module available in `gevent-socketio` library and it contains the following definition for `sdjango.urls`:

.. code:: python

    SOCKETIO_NS = {}

    class namespace(object):
        def __init__(self, name=''):
            self.name = name
 
        def __call__(self, handler):
            SOCKETIO_NS[self.name] = handler
            return handler

    @csrf_exempt
    def socketio(request):
        try:
            socketio_manage(request.environ, SOCKETIO_NS, request)
        except:
            logging.getLogger("socketio").error("Exception while handling socketio connection", exc_info=True)
        return HttpResponse("")

    urls = patterns("", (r'', socketio))


SocketIO Namespace example
------------------------------

A simple example of implementing a namespace on the client (javascript) side is:

.. code:: javascript

    var socket = io.connect("/chat");

A namespace can be confused as a "url" for people new to SocketIO.  It is actually not a `url` (`router` in MVC design pattern speak) but in fact a `controller`.

On the server side, our namespaces are implemented via the `BaseNamespace` class:

.. code:: python

    from socketio.namespace import BaseNamespace
    from socketio import socketio_manage

    class ChatNamespace(BaseNamespace):
        
        def on_user_msg(self, msg):
            self.emit('user_msg', msg)

    def socketio_service(request):
        socketio_manage(request.environ, {'/chat': ChatNamespace}, request)
        return 'out'

In this example, the `user_msg` event will be in the `/chat` namespace. So we can say that the `/chat` namespace contains the `on_user_msg` method.

`socketio_manage()` is the method that runs when the `SocketIOServer` gets started and the real-time communication between the client and the server happens through that method.

The `socketio_manage()` function is going to be called only once per socket opening, even though we are using a long polling mechanism. The subsequent calls (for long polling) will be hooked directly at the server-level, to interact with the active Socket instance. This means we will not get access to the future request or environ objects. This is of particular importance regarding sessions. The session will be opened once at the opening of the Socket, and not closed until the socket is closed. We are responsible for opening and closing the cookie-based session ourselves if we want to keep its data in sync with the rest of our GET/POST calls.

A slightly more complex `django` example here`:

.. code:: python

    # sockets.py

    import logging

    from socketio.namespace import BaseNamespace
    from socketio.mixins import RoomsMixin, BroadcastMixin
    from socketio.sdjango import namespace

    @namespace('/chat')
    class ChatNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
        nicknames = []

        def initialize(self):
            self.logger = logging.getLogger("socketio.chat")
            self.log("Socketio session started")
        
        def log(self, message):
            self.logger.info("[{0}] {1}".format(self.socket.sessid, message))
    
        def on_join(self, room):
            self.room = room
            self.join(room)
            return True
        
        def on_nickname(self, nickname):
            self.log('Nickname: {0}'.format(nickname))
            self.nicknames.append(nickname)
            self.socket.session['nickname'] = nickname
            self.broadcast_event('announcement', '%s has connected' % nickname)
            self.broadcast_event('nicknames', self.nicknames)
            return True, nickname

        def recv_disconnect(self):
            # Remove nickname from the list.
            self.log('Disconnected')
            nickname = self.socket.session['nickname']
            self.nicknames.remove(nickname)
            self.broadcast_event('announcement', '%s has disconnected' % nickname)
            self.broadcast_event('nicknames', self.nicknames)
            self.disconnect(silent=True)
            return True

        def on_user_message(self, msg):
            self.log('User message: {0}'.format(msg))
            self.emit_to_room(self.room, 'msg_to_room',
                self.socket.session['nickname'], msg)
            return True

The `sdjango` module has defined a nice namespace class which accepts the name of our namespace (`/chat` in this case) which we can use as a decorator corresponding to our fully defined `ChatNamespace` subclass (subclass of `BaseNamespace`).  All our event handling methods are implemented in this class and will work with a javascript client that connects via 

.. code:: javascript

    var socket = io.connect("/chat");`

, the `io.connect("/chat")` call.

Summary of gevent-socketio API 
-----------------------------------


The key concepts and usage that we have covered are:

* **socketio.socketio_manage**  (usage seen in the `sdjango.py` module)
* **socketio.namespace**        (usage seen in by the implementation of the `BaseNamespace` parent class and the `@namespace` decorator in django)
* **socketio.server**           (usage seen in the instantiation of a `SocketIOServer` instance)

In the django example above, we also notice the use of **socketio.mixins** to pass in (specifically `RoomsMixin` and `BroadcastMixin`) pre-written classes that contain methods useful for a typical chat project.

Other APIs include:

* **socketio.virtsocket**
* **socketio.packet**
* **socketio.handler**
* **socketio.transports**

Reference document - https://gevent-socketio.readthedocs.org/en/latest/#api-docs

From SocketIO client to SocketIOServer logic and back
---------------------------------------------------------

Here's an example django *chat* app layout (inside a django project):

.. code::

    chat
    ├── __init__.py
    ├── admin.py
    ├── management
    │   ├── __init__.py
    │   └── commands
    │       ├── __init__.py
    │       ├── runserver_socketio.py
    ├── models.py
    ├── sockets.py
    ├── static
    │   ├── css
    │   │   └── chat.css
    │   ├── flashsocket
    │   │   └── WebSocketMain.swf
    │   └── js
    │       ├── chat.js
    │       └── socket.io.js
    ├── templates
    │   ├── base.html
    │   ├── room.html
    │   └── rooms.html
    ├── tests.py
    ├── urls.py
    └── views.py

Our client-side logic resides in `chat.js`

.. code:: javascript

    // chat.js

    var socket = io.connect("/chat");

    socket.on('connect', function () {
        $('#chat').addClass('connected');
        socket.emit('join', window.room); 
    });

    socket.on('announcement', function (msg) {
        $('#lines').append($('<p>').append($('<em>').text(msg)));
    });

    socket.on('nicknames', function (nicknames) {
        console.log("nicknames: " + nicknames);
        $('#nicknames').empty().append($('<span>Online: </span>'));
        for (var i in nicknames) {
            $('#nicknames').append($('<b>').text(nicknames[i]));
        }
    });

    socket.on('msg_to_room', message);

    socket.on('reconnect', function () {
        $('#lines').remove();
        message('System', 'Reconnected to the server');
    });

    socket.on('reconnecting', function () {
        message('System', 'Attempting to re-connect to the server');
    });

    socket.on('error', function (e) {
        message('System', e ? e : 'A unknown error occurred');
    });

    function message (from, msg) {
        $('#lines').append($('<p>').append($('<b>').text(from), msg));
    }

    // DOM manipulation
    $(function () {
        $('#set-nickname').submit(function (ev) {
            socket.emit('nickname', $('#nick').val(), function (set) {
                if (set) {
                    clear();
                    return $('#chat').addClass('nickname-set');
                }
                $('#nickname-err').css('visibility', 'visible');
            });
            return false;
        });

        $('#send-message').submit(function () {
            //message('me', "Fake it first: " + $('#message').val());
            socket.emit('user message', $('#message').val());
            clear();
            $('#lines').get(0).scrollTop = 10000000;
            return false;
        });

        function clear () {
            $('#message').val('').focus();
        }
    });

The client side SocketIO library is straightforward to use: 

* **socket.on** receives 2 arguments, the *event_name* (which the server side code will emit to) as the first argument and the *event callback function* as the second argument.  When an event happens, the (callback) function gets triggered.
* **socket.emit** also receives 2 arguments, the first being the *event_name* and the 2nd being the *message*.  **emit('<event_name>', <message>)** sends a message to the server - the python method **on_<event_name>(<message>)** is waiting for the client side **emit()** call.

Here's the corresponding server-side code in our **ChatNamespace** class.

.. code:: python

    # sockets.py

    @namespace('/chat')
    class ChatNamespace(BaseNamespace, LonelyRoomMixin, BroadcastMixin):
        nicknames = []

        def initialize(self):
            self.logger = logging.getLogger("socketio.chat")
            self.log("Socketio session started")

        def log(self, message):
            self.logger.info("[{0}] {1}".format(self.socket.sessid, message))

        def on_join(self, room):
            self.room = room
            self.join(room)
            return True

        def on_nickname(self, nickname):
            print("Creating the nickname: " + nickname)
            self.log('Nickname: {0}'.format(nickname))
            self.socket.session['nickname'] = nickname
            self.nicknames.append(nickname)
            self.broadcast_event('announcement', '%s has connected' % nickname)
            self.broadcast_event('nicknames', self.nicknames)
            return True, nickname

        def recv_disconnect(self):
            self.log('Disconnected')
            nickname = self.socket.session['nickname']
            self.nicknames.remove(nickname)
            self.broadcast_event('announcement', '%s has disconnected' % nickname)
            self.broadcast_event('nicknames', self.nicknames)
            self.disconnect(silent=True)
            return True

        def on_user_message(self, msg):
            self.log('User message: {0}'.format(msg))
            # TODO: dig into the logic of emit_to_room
            self.emit_to_room(self.room, 'msg_to_room',
                              self.socket.session['nickname'], msg)
            return True

