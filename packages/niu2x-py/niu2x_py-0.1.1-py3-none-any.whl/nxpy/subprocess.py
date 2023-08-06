import subprocess
from . import log
from .misc import abort

children_process = {}


def spawn(cmd, **kwargs):
    """

    :param cmd: command
    :param **kwargs: 

    """
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, shell=True, **kwargs)
    children_process[proc] = cmd + str(kwargs)
    return proc


def kill_all():
    """ """
    for proc in children_process:
        proc.kill()
    children_process.clear()


def wait(proc, quite=False, stdin="", stop_if_child_fail=True):
    """

    :param proc: 要执行的命令
    :param stdin: 标准输入 (Default value = "")
    :param stop_if_child_fail: 子进程失败时，父进程是否立即中止 (Default value = True)
    :param quite: 是否为安静模式(不显示子进程的输出) (Default value = False)

    """
    stdout, stderr = proc.communicate(stdin)

    if stdout and (not quite):
        log.d(f'STDOUT[{children_process[proc]}]:')
        log.d(stdout.decode('utf-8'))
    if stderr:
        log.d(f'STDERR[{children_process[proc]}]:')
        log.d(stderr.decode('utf-8'))

    if proc.returncode != 0 and stop_if_child_fail:
        abort(f'{children_process[proc]} exit with code: {proc.returncode}')

    del children_process[proc]
    return stdout


def shell(cmd_list, quite=False, stop_if_child_fail=True):
    """

    :param cmd_list: list of command
    :param stop_if_child_fail: Default value = True)
    :param quite: Default value = False)

    """
    cache = ""
    for v in cmd_list:
        p = spawn(v)
        cache = wait(p, stdin=cache, quite=quite,
                     stop_if_child_fail=stop_if_child_fail)
    return cache
