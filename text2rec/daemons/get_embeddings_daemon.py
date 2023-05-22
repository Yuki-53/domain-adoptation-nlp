import time
import pathlib
import argparse

import numpy as np
import torch
import pandas as pd
from sentence_transformers import SentenceTransformer

from text2rec import TextPipeline, start_daemon, get_embeddings


def callback(
    oldest_file_path: str,
    model: SentenceTransformer,
    column_name: str,
    savepath: str,
    text_pipeline: TextPipeline,
    batch_size: int,
):
    print(f"Getting embeddings from {oldest_file_path}", flush=True)
    reviews = pd.read_csv(oldest_file_path, usecols=["film_id", column_name])
    reviews.dropna(subset=[column_name], inplace=True)
    embs = get_embeddings(
        model,
        reviews,
        column_name,
        text_pipeline,
        batch_size=batch_size,
        show_progress_bar=False,
    )
    film_ids = reviews["film_id"]
    filename = pathlib.Path(oldest_file_path).stem
    np.save(f"{savepath}/{filename}_embs_en.npy", embs)
    np.save(f"{savepath}/{filename}_film_ids.npy", film_ids)
    print(f"Saving embeddings to {savepath}/{filename}_embs_en.npy", flush=True)
    print(f"Saving film_ids to {savepath}/{filename}_film_ids.npy", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("watched_dir")
    parser.add_argument("-d", "--device", nargs="?", default="cpu")
    parser.add_argument("-b", "--batch_size", nargs="?", default=32, type=int)
    parser.add_argument("-c", "--column_name", nargs="?", default="description")
    parser.add_argument("-t", "--threshold_ts", default=time.time(), type=float)
    parser.add_argument("-sp", "--save_path", nargs="?")
    args = parser.parse_args()

    device = args.device
    batch_size = args.batch_size
    if device == "cuda:0" and not torch.cuda.is_available():
        print("Error: GPU is not available, fallback to CPU")
        device = "cpu"
    text_pipeline = TextPipeline()
    watched_dir = args.watched_dir
    column_name = args.column_name
    threshold_ts = args.threshold_ts
    savepath = args.save_path

    model = SentenceTransformer(
        "sentence-transformers/all-mpnet-base-v2", device=device
    )

    start_daemon(
        watched_dir,
        "csv",
        callback,
        args=(model, column_name, savepath, text_pipeline, batch_size),
        threshold_ts=threshold_ts,
    )


if __name__ == "__main__":
    main()
