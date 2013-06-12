Spawning greenlets via gevent
=======================================

Gevent provides a wrapper `Greenlet` class around base `greenlet` library. Reference https://github.com/surfly/gevent/blob/master/gevent/greenlet.py

In our own source code, we will therefore depend on 

.. code:: python

    import gevent
    from gevent import Greenlet

to implement our custom logic.

1. Via the base `Greenlet` class:

   .. code:: python

       import gevent
       from gevent import Greenlet

       def foo(message, n):
           """
           Each thread will be passed the message, and n arguments
           in its initialization.
           """
           gevent.sleep(n)
           print(message)

       # Initialize a new Greenlet instance running the named function
       # foo
       thread1 = Greenlet.spawn(foo, "Hello", 1)

       # Wrapper for creating and runing a new Greenlet from the named 
       # function foo, with the passed arguments
       thread2 = gevent.spawn(foo, "I live!", 2)

       # Lambda expressions
       thread3 = gevent.spawn(lambda x: (x+1), 2)

       threads = [thread1, thread2, thread3]

       # Block until all threads complete.
       gevent.joinall(threads)

2.  Subclassing the base `Greenlet` class and using internal method `_run`

   .. code:: python

       import gevent
       from gevent import Greenlet

       class MyGreenlet(Greenlet):

           def __init__(self, message, n):
               Greenlet.__init__(self)
               self.message = message
               self.n = n

           def _run(self):
               print(self.message)
               gevent.sleep(self.n)

       g = MyGreenlet("Hi there!", 3)
       g.start()
       g.join()

Full Tutorial on gevent
----------------------------

See http://sdiehl.github.io/gevent-tutorial/ for all the detailed explanations of gevent functionalities.


