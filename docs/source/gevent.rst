What is gevent?
=======================

Gevent is the use of simple, sequential programming in python to achieve scalability provided by asynchronous IO and lightweight multi-threading (as opposed to the callback-style of programming using Twisted's Deferred).

It is built on top of libevent/libev (for asynchronous I/O) and :doc:`greenlets <greenlets>` (lightweight cooperative multi-threading).

Pre-1.0 version, gevent is based on `libevent <http://libevent.org>`_; and from 1.0 onwards, gevent is based on `libev <http://libev.schmorp.de>`_.

Once we understand what each of the building blocks of gevent do - 

* :ref:`libevent-label`, 
* :ref:`libev-label` and 
* :ref:`greenlets-label` 

we will have a clear idea of what it means to implement gevent in our python projects.

.. _libevent-label:

libevent
--------------

Written in C, this library provides asynchronous event notification.  The libevent API provides a mechanism to execute a callback function when a specific event occurs on a file descriptor or after a timeout has been reached. It also supports callbacks triggered by signals and regular timeouts.

Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* /dev/poll
* kqueue
* select
* poll
* epoll
* Solaris' event ports
* experimental support for real-time signals

Notable Applications that use libevent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Chrome web browser (linux and mac version)
* Memcached
* tmux
* tor

etc etc

.. _libev-label:

libev
---------

A forked version of libevent with a view to improve on some (problematic) architectural decisions made in libevent, for instance: 

* the global variable usage in libevent made it hard to use libevent safely in multithreaded environments.
* watcher structures are big because they combine I/O, time and signal handlers in one
* extra components such as the http and dns servers may not be implemented well, resulting in security issues

libev attempts to resolve some of these problems by not using global variables and use a loop context for all functions.  The http and dns related components were completely removed and focuses on doing only one specific thing - POSIX event library

gevent 1.0 onwards has been refactored to use libev instead of libevent.  Details of the rationale for this decision is `explained by gevent author Denis Bilenko <http://blog.gevent.org/2011/04/28/libev-and-libevent/>`_.

The `c-ares <http://c-ares.haxx.se/>`_ library is used to replace libevent-dns since libev does not handle http and dns functionality as explained above.

Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Exactly the same as libevent's

* /dev/poll
* kqueue
* select
* poll
* epoll
* Solaris' event ports
* experimental support for real-time signals

libevent has better windows-support implementation since libevent accepts windows handles while libev needs to convert windows handles into C runtime handles.

.. _greenlets-label:

greenlets
----------------

Greenlets are a lightweight cooperative threads - which is different from our conventional understanding of POSIX threads (pthreads).

It is a spin-off of Stackless, a version of CPython which supports microthreads called "tasklets".  Tasklets (Stackless) run pseudo-concurrently (in a single or a few OS-level threads) and are synchronized with data exchanged in "channels".  Greenlet is more primitive compared to these "tasklet" microthreads and is more accurately described as a "coroutines" - cooperative routines. Meaning that greenlets has no implicit scheduling like "tasklets" and we can control exactly when our code runs.

The greenlet source code can be found `here <https://github.com/python-greenlet/greenlet>`_ and is provided as a C extension module for python.

We dive into further details about greenlets :doc:`here <greenlets>`.

gevent API design
-------------------

gevent's interface follows the conventions set by python standard modules

* `gevent.event.Event <https://github.com/surfly/gevent/blob/master/gevent/event.py>`_ has the same interface and the same semantics as python's built-in modules threading.Event and multiprocessing.Event.
* wait() does not raise an exception
* get() can raise an exception or return a value
* join() is like wait() but for units of execution

Having consistent code interfaces like these helps programmers read and reason with the code in a much more efficient manner.

gevent with other python extensions
---------------------------------------

If some kind of transaction involves I/O, the greenlet might get switched away waiting for a write-acknowledgement (or other kinds of I/O block), we have to explicitly lock the transaction. If our code ever gets back to the old blocking I/O style, our entire application will fail.  To prevent this from happening, only use extensions that make use of the built-in python socket module.

gevent's monkey patch
-------------------------

A monkey patch is a way to extend or modify the run-time code of dynamic languages without altering the original source code.  Monkey patching as a programming technique is very powerful but can result in hard-to-debug code in the wrong hands.  Jeff Atwood wrote a good post about these issues here - http://www.codinghorror.com/blog/2008/07/monkeypatching-for-humans.html. 

    ::

    Monkey patching is the new black [in the Ruby community]. It's what all the hip kids are doing. To the point that smart, experienced hackers reach for a monkey patch as their tool of first resort, even when a simpler, more traditional solution is possible.

    I don't believe this situation to be sustainable. Where I work, we are already seeing subtle, difficult-to-debug problems crop up as the result of monkey patching in plugins. Patches interact in unpredictable, combinatoric ways. And by their nature, bugs caused by monkey patches are more difficult to track down than those introduced by more traditional classes and methods. As just one example: on one project, it was a known caveat that we could not rely on class inheritable attributes as provided by ActiveSupport. No one knew why. Every Model we wrote had to use awkward workarounds. Eventually we tracked it down in a plugin that generated admin consoles. It was overwriting Class.inherited(). It took us months to find this out.

    This is just going to get worse if we don't do something about it. And the "something" is going to have to be a cultural shift, not a technical fix. I believe it is time for experienced Ruby programmers to wean ourselves off of monkey patching, and start demonstrating more robust techniques.

Whenever we decide to use a library which uses a monkey patch approach, it is important that we read the source code and documentation fully and understand how that library's monkey patch affects our standard source code, modules and libraries.

One of gevent's most important features is monkey patching, so we will need to understand what monkey patching actually does - http://www.gevent.org/gevent.monkey.html

    The functions in this module patch parts of the standard library with compatible cooperative counterparts from gevent package.

    To patch an individual module call the corresponding patch_* function. For example, to patch socket module only, call patch_socket(). To patch all default modules, call gevent.monkey.patch_all().

    Monkey can also patch thread and threading to become greenlet-based. So thread.start_new_thread() starts a new greenlet instead and threading.local becomes a greenlet-local storage.

Examples
~~~~~~~~~~~~

This works:-

    .. code:: python

        import gevent.monkey; gevent.monkey.patch_thread()
        import threading

This explodes (try it):-

    .. code:: python

        import threading
        import gevent.monkey; gevent.monkey.patch_thread()

When the threading module is imported, it uses the main thread ID as a key in a module-level thread dictionary.  When the program exits, the threading module tries to obtain the thread instance from the dictionary (using the current thread ID) to perform clean up.

However, because of `gevent.monkey.patch_thread()`, the ID of the main thread is no longer the same!  Stackoverflow question and answer here with all the `gory details <http://stackoverflow.com/questions/8774958/keyerror-in-module-threading-after-a-successful-py-test-run/12639040#12639040>`_.

Long story short, the `order in which we monkey patch gevent is important`.  Always execute the monkey patch first before running your python code, particularly if your code uses threading at some point.  Note that the `logging` module also uses `threading` so when `logging` your application, monkey patch first! 
