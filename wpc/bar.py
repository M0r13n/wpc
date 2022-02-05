import sys
import threading
import time
import typing


class ProgressBar(object):

    def __init__(self, total: int, count: int = 0, status: str = "", out_file: typing.TextIO = sys.stdout,
                 bar_len: int = 60):
        self.count: int = count
        self.total: int = total
        self.status: str = status
        self.out_file: typing.TextIO = out_file
        self.bar_len: int = bar_len

    def __enter__(self) -> "ProgressBar":
        return self

    def __exit__(self, *exc):
        self.out_file.flush()

    def set_count(self, c: int):
        self.count = c

    def set_status(self, status: str):
        self.status = status

    def update_count(self, c: int):
        self.set_count(c)
        self.write()

    def update_status(self, s: str):
        self.status = s
        self.write()

    def update(self, count: int, status: str):
        self.set_count(count)
        self.set_status(status)
        self.write()

    def write(self):
        self.out_file.flush()
        filled_len = int(round(self.bar_len * self.count / float(self.total)))
        percents = round(100.0 * self.count / float(self.total), 1)
        bar = '=' * filled_len + '-' * (self.bar_len - filled_len)
        sys.stdout.write(f'[{bar}] {percents}%...{self.status}\r')
        sys.stdout.flush()


def print_progress_bar(sec: int):
    bar = ProgressBar(sec, status="Scanning in progress")
    for i in range(sec):
        bar.update_count(i)
        time.sleep(1)
    bar.update_count(sec)
    sys.stdout.write('\n')


def print_progress_bar_in_background_thread(duration):
    t1 = threading.Thread(target=print_progress_bar, args=(duration,))
    t1.daemon = True
    t1.start()
    return t1
