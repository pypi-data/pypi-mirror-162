import sys


def i(*vargs):
    """

    :param *vargs: 

    """
    log("[INFO]:", *vargs)


def w(*vargs):
    """

    :param *vargs: 

    """
    log("[WARN]:", *vargs)


def d(*vargs):
    """

    :param *vargs: 

    """
    log("[DEBUG]:", *vargs)


def e(*vargs):
    """

    :param *vargs: 

    """
    log("[ERROR]:", *vargs)


def f(*vargs):
    """

    :param *vargs: 

    """
    log("[FATAL]:", *vargs)


def log(tag, *vargs):
    """

    :param tag: param *vargs:
    :param *vargs: 

    """
    write(tag)
    write(' '.join(map(str, [*vargs])))
    write('\n')


def write(sz):
    """

    :param sz: 

    """
    sys.stderr.write(sz)
