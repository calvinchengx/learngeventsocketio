"""
The last line jumps to test1, which prints 12, jumps to test2, prints 56, jumps back into test1, prints 34; and then test1 finishes and gr1 dies.
At this point, the execution comes back to the original gr1.switch() call.
Note that 78 is never printed.
"""


from greenlet import greenlet


def test1():
    """
    prints out specific numbers and switch to another greenlet
    """
    print 12
    gr2.switch()
    print 34


def test2():
    """
    prints out specific numbers and switch to another greenlet
    """
    print 56
    gr1.switch()
    print 78

gr1 = greenlet(test1)
gr2 = greenlet(test2)
gr1.switch()
