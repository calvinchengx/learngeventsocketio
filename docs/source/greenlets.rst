What are greenlets?
==============================

Greenlets are lightweight thread-like structures that are scheduled and managed inside the process. They are references to the part of the stack that is used by the thread.  Compared to POSIX threads (pthreads), there is no stack allocated up front and there is only as much stack as is actually used by the greenlet

In python, we implement greenlets via the gevent package and we implement pthreads via python's built-in threading module.

Both green threads (greenlets) and POSIX threads (pthreads) are mechanisms to support multithreaded execution of programs.

POSIX threads use the operating system's native ability to manage multithreaded processes.  When we run pthreads, the kernel schedules and manages the various threads that make up the process.

Green threads emulate multithreaded environments without relying on any native operating system capabilities. Green threads run code in user space that manages and schedules threads.

The key differences between greenlets and pthreads can be summarized as such:

+-----------------------------------------------------------------------+--------------------------------------------------------------+
|                   pthreads                                            |             greenlets                                        |
+=======================================================================+==============================================================+
|                                                                       |                                                              |
| pthreads can switch between threads pre-emptively, switching control  | greenlets only switch when control is explicitly given up by |
| from a running thread to a non-running thread at any time             | a thread - when using yield() or wait() - or when a thread   |
|                                                                       | performs a I/O blocking operation such as read or write      |
|                                                                       |                                                              |
+-----------------------------------------------------------------------+--------------------------------------------------------------+
|                                                                       |                                                              |
| On multicore machines, pthreads can run more than one thread. However | greenlets can only run on one single CPU and is useful for   |
| python's Global Interpreter Lock (CPython Intepreter) prevents        | I/O-bound programs                                           |
| parallelism and concurrency is only effective for I/O-bound programs  |                                                              |
|                                                                       |                                                              |
+-----------------------------------------------------------------------+--------------------------------------------------------------+
|                                                                       |                                                              |
| Race conditions can occur when implementing multi-threading code.     | There's no possibility of two threads of control accessing   |
| Use locks to manage mutex to avoid race conditions.                   | the same shared memory at the same time for greenlets so     |
|                                                                       | there will not be any race conditions.                       |
+-----------------------------------------------------------------------+--------------------------------------------------------------+

Installation 
-----------------------------

When we install gevent, greenlet as a dependency will be downloaded, compiled (since it is a c extension) and installed.

We can also install greenlet directly:

    .. code:: sh

            pip install greenlet

            Downloading/unpacking greenlet
              Downloading greenlet-0.4.1.zip (75kB): 75kB downloaded
              Running setup.py egg_info for package greenlet

            Installing collected packages: greenlet
              Running setup.py install for greenlet
                /usr/bin/clang -fno-strict-aliasing -fno-common -dynamic -pipe -O2 -fwrapv -arch x86_64 -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes -fno-tree-dominator-opts -I/opt/local/Library/Frameworks/Python.framework/Versions/2.7/include/python2.7 -c /var/folders/kl/_52jng9s6sl2knv_0jds9w140000gn/T/tmp15ttlr/simple.c -o /var/folders/kl/_52jng9s6sl2knv_0jds9w140000gn/T/tmp15ttlr/var/folders/kl/_52jng9s6sl2knv_0jds9w140000gn/T/tmp15ttlr/simple.o
                clang: warning: argument unused during compilation: '-fno-tree-dominator-opts'
                building 'greenlet' extension
                /usr/bin/clang -fno-strict-aliasing -fno-common -dynamic -pipe -O2 -fwrapv -arch x86_64 -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes -fno-tree-dominator-opts -I/opt/local/Library/Frameworks/Python.framework/Versions/2.7/include/python2.7 -c greenlet.c -o build/temp.macosx-10.7-x86_64-2.7/greenlet.o
                clang: warning: argument unused during compilation: '-fno-tree-dominator-opts'
                In file included from greenlet.c:416:
                In file included from ./slp_platformselect.h:12:
                ./platform/switch_amd64_unix.h:40:26: warning: unknown attribute 'noclone' ignored [-Wattributes]
                __attribute__((noinline, noclone)) int fancy_return_zero(void);
                                         ^
                ./platform/switch_amd64_unix.h:41:26: warning: unknown attribute 'noclone' ignored [-Wattributes]
                __attribute__((noinline, noclone)) int
                                         ^
                2 warnings generated.
                /usr/bin/clang -bundle -undefined dynamic_lookup -L/opt/local/lib -L/opt/local/lib/db46 -arch x86_64 build/temp.macosx-10.7-x86_64-2.7/greenlet.o -o build/lib.macosx-10.7-x86_64-2.7/greenlet.so
                Linking /Users/calvin/.virtualenvs/pyconsg2013/build/greenlet/build/lib.macosx-10.7-x86_64-2.7/greenlet.so to /Users/calvin/.virtualenvs/pyconsg2013/build/greenlet/greenlet.so

            Successfully installed greenlet
            Cleaning up...
    
Notice that the c code gets built and the shared object file `greenlet.so` is now available for us to import inside our python code.


Example
---------------

Here\'s a simple example extracted from greenlet docs that explains the nature of greenlet execution:

    .. code:: python

        from greenlet import greenlet


        def test1():
            print 12
            gr2.switch()
            print 34


        def test2():
            print 56
            gr1.switch()
            print 78

        gr1 = greenlet(test1)
        gr2 = greenlet(test2)
        gr1.switch()


