import time
import pathlib
import argparse

import pandas as pd

from text2rec import start_daemon, filter_reviews, translate_reviews


def callback(oldest_file_path: str, column_name: str, savepath: str):
    print(f"Transforming reviews from {oldest_file_path}", flush=True)
    df = pd.read_csv(oldest_file_path)
    filename = pathlib.Path(oldest_file_path).stem
    transformed = filter_reviews(df, column_name)
    path = f"{savepath}/{filename}_transformed.csv"
    transformed = translate_reviews(transformed, column_name, show_progress_bar=False)
    print(f"Saving transformed reviews to {path}", flush=True)
    transformed.to_csv(path, index=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("watched_dir")
    parser.add_argument("-c", "--column_name", nargs="?", default="description")
    parser.add_argument("-t", "--threshold_ts", default=time.time(), type=float)
    parser.add_argument("-sp", "--save_path", nargs="?")
    args = parser.parse_args()

    watched_dir = args.watched_dir
    column_name = args.column_name
    savepath = args.save_path
    threshold_ts = args.threshold_ts

    start_daemon(
        watched_dir,
        "csv",
        callback,
        args=(column_name, savepath),
        threshold_ts=threshold_ts,
    )


if __name__ == "__main__":
    main()
