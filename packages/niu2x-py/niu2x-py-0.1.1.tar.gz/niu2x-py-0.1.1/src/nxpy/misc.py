import os
import sys
import hashlib
import contextlib

from . import log


def abort(*vargs):
    """

    :param *vargs: 

    """
    log.f(*vargs)
    sys.exit(1)


@contextlib.contextmanager
def pushd(new_dir):
    """

    :param new_dir: dir's pathname

    """
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(previous_dir)


def env(name, default):
    """

    :param name: environment variable'name
    :param default: default value

    """
    if name in os.environ:
        return os.environ[name]
    return default


def env_required(name):
    """

    :param name: environment variable'name

    """
    if name in os.environ:
        return os.environ[name]
    abort(f"please set {name}")


def md5_file(pathname):
    """

    :param pathname: file's pathname

    """
    hashmd5 = hashlib.md5()
    with open(pathname, 'rb') as myfile:
        while True:
            b = myfile.read(8096)
            if not b:
                break
            hashmd5.update(b)
    return hashmd5.hexdigest()


def md5(bs):
    """

    :param bs: bytes

    """
    hashmd5 = hashlib.md5()
    hashmd5.update(bs)
    return hashmd5.hexdigest()


def ensure_dir(dir):
    """

    :param dir: dir's pathname

    """
    if not os.path.exists(dir):
        os.makedirs(dir)
