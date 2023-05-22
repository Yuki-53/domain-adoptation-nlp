import time
import pathlib
import argparse

import pandas as pd
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.remote.webdriver import WebDriver

from text2rec import start_daemon, get_reviews_from_content_list


def callback(
    oldest_file_path: str,
    driver: WebDriver,
    id_column_name: str,
    savepath: str,
    interval: int,
    show_progress=False,
    skipped_first_chunks=0,
):
    filename = pathlib.Path(oldest_file_path).stem
    with pd.read_csv(
        oldest_file_path, usecols=[id_column_name], chunksize=interval
    ) as reader:
        for i, df in enumerate(reader):
            if i < skipped_first_chunks:
                continue
            content_ids = df[id_column_name]
            start_index = i * interval
            end_index = (i + 1) * interval
            print(
                f"Getting reviews from {oldest_file_path}"
                f"with indexes {start_index}-{end_index}",
                flush=True,
            )
            path = f"{savepath}/{filename}_{start_index}" f"-{end_index}_reviews.csv"
            result: pd.DataFrame = get_reviews_from_content_list(
                driver, content_ids, show_progress=show_progress
            )
            if result is None:
                continue
            print(f"Saving reviews from {oldest_file_path} to {path}", flush=True)
            result.to_csv(path, index=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("watched_dir")
    parser.add_argument("-i", "--id_column_name", nargs="?", default="film_id")
    parser.add_argument("-sp", "--save_path", nargs="?")
    parser.add_argument("--interval", nargs="?", default=1000)
    parser.add_argument("--skipped_first_chunks", nargs="?", default=0, type=int)
    args = parser.parse_args()

    watched_dir = args.watched_dir
    id_column_name = args.id_column_name
    savepath = args.save_path
    interval = args.interval
    skipped_first_chunks = args.skipped_first_chunks

    chrome_options = ChromeOptions()
    chrome_options.debugger_address = "localhost:9222"
    chrome_driver = webdriver.Chrome(options=chrome_options)

    start_daemon(
        watched_dir,
        "csv",
        callback,
        args=(chrome_driver, id_column_name, savepath, interval),
        kwargs=dict(show_progress=False, skipped_first_chunks=skipped_first_chunks),
        threshold_ts=time.time(),
    )


if __name__ == "__main__":
    main()
