import os
import glob
import time
from typing import Callable
from argparse import ArgumentParser

__all__ = ["start_daemon"]


class MaxRetryException(Exception):
    pass


def get_oldest_file_and_ts(watched_dir: str, file_ext: str, current_ts: int):
    files = glob.glob(f"{watched_dir}/*.{file_ext}")
    files_ts = [(f, os.path.getctime(f)) for f in files]
    files_ts = filter(lambda x: x[1] > current_ts, files_ts)
    return min(files_ts, key=lambda x: x[1])


def start_daemon(
    watched_dir: str,
    file_ext: str,
    callback: Callable,
    args=(),
    kwargs={},
    delay=1,
    threshold_ts=0,
    retry_count=1000,
    retry_delay=900,
):
    while True:
        try:
            oldest_file, oldest_ts = get_oldest_file_and_ts(
                watched_dir, file_ext, threshold_ts
            )
        except ValueError:
            time.sleep(delay)
            continue
        for i in range(retry_count):
            try:
                callback(oldest_file, *args, **kwargs)
                break
            except Exception as e:
                print(f"Got exception in callback: {str(e)}")
                time.sleep(retry_delay)
        if i + 1 == retry_count:
            raise MaxRetryException()
        threshold_ts = oldest_ts


def main():
    parser = ArgumentParser()
    parser.add_argument("watched_dir")
    parser.add_argument("-e", "--file_ext", required=True)
    args = parser.parse_args()

    def log(filename):
        print(filename)

    watched_dir = args.watched_dir
    file_ext = args.file_ext

    start_daemon(watched_dir, file_ext, log)


if __name__ == "__main__":
    main()
