General concepts
=====================

In this section, we want to set the fundamentals knowledge required to understand how greenlets, pthreads (python threading for multithreading) and processes (python's multiprocessing) module work, so we can better understand the details involved in implementing python gevent.

What's the difference between concurrency and parallelism?
--------------------------------------------------------------

When we talk about implementing threads (whether greenlets or pthreads) and processes, what we are really trying to achieve is concurrency and/or parallelism.

So what's the difference, you ask?

Concurrency and parallelism are distinct concepts. Concurrency is concerned with managing access to shared state from different threads, whereas parallelism is concerned with utilizing multiple processors/cores to improve the performance of a computation.

.. _threads-label:

What is a thread?
------------------------

A thread is a basic unit of CPU utilization.  It is also referred to as a "lightweight process".

A thread is a sequence of instructions within a process and it behaves like "a process within a process". It differs from a process because it does not have its own Process Control Block (collection of information about the processes).  Usually, multiple threads are created within a process.  Threads execute within a process and processes execute within the operating system kernel.

A thread comprises:

* thread ID
* program counter
* register set
* stack

A thread shares resources with its peer threads (all other threads in a particular task), such as:

* code section
* data section
* any operating resources which are available to the task

In a multi-threaded task, one server thread may be blocked and waiting for something and another thread in the same task may be running.  If a process blocks, then the whole process stops.  But a multithreaded process is useful in programs such as web browsers when we want to download a file, view an animation and print something all at the same time.  When multiple threads cooperate in a single job, there is a higher throughput.  If one thread must wait, the whole process does not stop because another thread may still run.

.. _processes-label:

What is a process?
-------------------------

In computing, a process is an instance of a computer program that is being executed.  It contains the program code and its current activity.  Depending on the operating system, a process may be made up of multiple threads of execution that execute instructions concurrently.

Most modern operating systems prevent direct communication between independent processes, providing strictly mediated and controlled inter-process communication (IPC).

A process typically contains the following resources:

* an image of the executable machine code associated with the program
* memory, which includes:

  + executable code
  + process-specific data (input and output)
  + call stack that keeps track of active subroutines and/or other events
  + heap which holds intermediate computation data during run time

* operating system descriptors of resources that are allocated to the process such as file descriptors (unix/linux) and handles (windows), dat sources and sinks
* security attributes (process owner and set of permissions, e.g. allowable operations)
* processor state (context) such as registers and physical memory addressing

The operating system holds most of this information about active processes in data structures called process control blocks (PCB).

The operating system keeps its processes separated and allocates the resources they need, so that they are less likely to interfere with each other and cause system failures (e.g. deadlock or thrasing).  The operating system may provide mechanisms for inter-process communication to enable processes in safe and predictable ways.

What's the difference between threads and processes?
-----------------------------------------------------

A process is an executing instance of an application.  What does that mean? When we launch a python shell or executing a python script, we start a process that runs our python shell or our python script. The operating system creates a process in response to us starting the python shell or python script and the `primary thread` of our process begins executing.

A thread is simply a path of execution within a process and in the case of python programs, our (python) process can contain multiple threads  - implemented via the python threading module for example.  

On a single processor, multithreading typically happens by time-division multiplexing (also referred to as multitasking), i.e. the single processor switches between different threads.  This context switching happens fast enough so that we perceive the threads to be running at the same time.

On a multiprocessor and a multi-core system, threads can be truly concurrent, with every processor or CPU core executing a separate thread simultaneously (concurrently *and* in parallel). 

What does that mean in the context of a python application?
---------------------------------------------------------------
 
python's (CPython) Global Interpretor Lock (GIL) prevents parallel threads of execution on multiple cores and as such, threading implementation on python is useful only for concurrent thread implementation for webservers.

This is what it means when people say "python manage.py runserver" development server for django is a `single-threaded server (process)`.  There's only one thread running inside the "runserver" program.  To solve the limitation of I/O and http network bottlenecks, third party source code (such as django-devserver by David Cramer) implements multiple threads to override the standard django runserver.  Because our python server primarily deals with http traffic, our network I/O is the bottleneck and having multiple threads will improve its (data transfer) throughput.  

However, if our python application is not a webserver and it bottlenecks due to CPU-intensive computation instead of network I/O, having multiple threads will not help at all (and in fact, such a CPU-bound python application will perform badly if we attempt to implement multiple threads).  This is because of python's Global Interpreter Lock (GIL).  There are some python interpreter implementation (such as Jython and IronPython) that do not have a GIL and so multithreaded execution for a CPU-bound python application will work well but the typical python interpreters that we use - CPython - is not appropriate for multithreaded CPU execution.

If CPython python has GIL, why do we still use it?
--------------------------------------------------------

We know that the java implementation of Python (Jython) supports true threading (concurrent and parallel) by taking advantage of the underlying JVM.  We also know that the IronPython port (running on Microsoft's CLR) do not have GIL. We could use them if we want to run code that has true threading capabilities.

The problem is that these platforms are always playing catch-up with new language features or library features, so unfortunately, it boils down to a trade-off between being able to use updated python features and python library features versus being able to run true threading code on Jython/IronPython.

So we cannot execute in parallel with python?
-----------------------------------------------------

Actually, we can. But not using threads.

Using the threading module on standard python (CPython interpreter), we **cannot** execute parallel CPU computation and we cannot execute parallel I/O operation because of GIL.  The threading module is *still useful* for implementing I/O concurrency (e.g. webserver implementation) but causes more harm than good for CPU-intensive operations.

However, we **can** execute parallel CPU computation and parallel I/O operation in python with python's multiprocessing module, or subprocess module or a 3rd party library called parallel python - http://www.parallelpython.com/.  Each approach has its own features and limitations but note that none of them use threads to achieve parallelism.

Advanced distributed, parallel computing with python
----------------------------------------------------------

Beyond some of the solutions offered in the previous paragraph, large scale data processing tools include discoproject (python with erlang and includes map/reduce capabilities) and PySpark on top of the spark framework (scala based).

For data analysis which can become compute-intensive, augustus is an open source system for building and scoring scalable data mining and statistical algorithms.

For GPU computing, numbapro and pycuda are the emerging players.

Useful references
~~~~~~~~~~~~~~~~~~~~~~~~

* http://doughellmann.com/2007/10/multiprocessing.html
* http://eli.thegreenplace.net/2011/12/27/python-threads-communication-and-stopping/
* http://eli.thegreenplace.net/2012/01/16/python-parallelizing-cpu-bound-tasks-with-multiprocessing/
