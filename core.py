import datetime as dt
import errno
import fcntl
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import urllib

import settings


class Client:
    def __init__(self, name, user, host, port):
        self.name = name
        self.user = user
        self.host = host
        self.port = port
        self.plugins = []

    def __str__(self):
        return self.name

    @classmethod
    def from_dict(cls, conf):
        return cls(
            conf['name'],
            conf['user'],
            conf['host'],
            conf.get('port', 22)
        )

    def add_plugin(self, instance):
        self.plugins.append(instance)

    def backup(self):
        for backup in self.plugins:
            backup.create()


def import_class(dotted_names):
    """ Returns plugin class. """
    path_bits = dotted_names.split('.')
    module_name = '.'.join(path_bits[:-1])
    class_name = path_bits[-1]
    module = __import__(module_name, {}, {}, class_name)
    return getattr(module, class_name)


def lock(fd):
    try:
        fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError as e:
        if e.errno in (errno.EACCES, errno.EAGAIN):
            logging.error('Another instance of the script is already running')
        else:
            raise


def single_process(f):
    script_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    lock_file_path = os.path.join(
        script_path, getattr(settings, 'LOCK_FILE', '/tmp/sshbackup.pid')
    )

    def _(*a, **kw):
        fd = os.open(lock_file_path, os.O_CREAT | os.O_RDWR, 0o660)
        try:
            lock(fd)
            return f(*a, **kw)
        finally:
            os.close(fd)

    return _
