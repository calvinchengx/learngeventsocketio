What are threads?
===========================

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

