import os

def setup():
    print "Module setup"
    test_dir = os.path.dirname(os.path.abspath(__file__))
    print test_dir
    os.environ['PATH'] = '%s/tbin/:%s' % (test_dir, os.environ['PATH'])
    # Create __init__

def teardown():
    os.unlink('ssh.out')

