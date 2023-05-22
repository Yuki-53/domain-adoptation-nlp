import argparse

import numpy as np
import torch
import pandas as pd
from sentence_transformers import SentenceTransformer

from .keyword_search import TextPipeline

__all__ = ["get_embeddings"]


def get_embeddings(
    model: SentenceTransformer,
    reviews: pd.DataFrame,
    review_col: str,
    text_pipeline: TextPipeline,
    show_progress_bar=True,
    batch_size=32,
):
    reviews_text = reviews[review_col].apply(text_pipeline).to_list()
    embs = model.encode(
        reviews_text, batch_size=batch_size, show_progress_bar=show_progress_bar
    )
    return embs


def removesuffix(input_str: str, suffix: str):
    if suffix and input_str.endswith(suffix):
        return input_str[: -len(suffix)]
    else:
        return input_str[:]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename")
    parser.add_argument("output_filename")
    parser.add_argument("-d", "--device", nargs="?", default="cpu")
    parser.add_argument("-b", "--batch_size", nargs="?", default=32, type=int)
    parser.add_argument("-i", "--id_column_name", nargs="?", default="film_id")
    parser.add_argument("-c", "--column_name", nargs="?", default="review_text")
    parser.add_argument("--show_progress", nargs="?", default=False, type=bool)
    parser.add_argument("--save_path", nargs="?", default=".")
    args = parser.parse_args()

    device = args.device
    if device == "cuda:0" and not torch.cuda.is_available():
        print("Error: GPU is not available, fallback to CPU")
        device = "cpu"
    input_filename = args.input_filename
    output_filename = args.output_filename
    batch_size = args.batch_size
    text_pipeline = TextPipeline()
    column_name = args.column_name
    id_column_name = args.id_column_name
    show_progress = args.show_progress
    model = SentenceTransformer(
        "sentence-transformers/all-mpnet-base-v2", device=device
    )
    reviews = pd.read_csv(input_filename, usecols=[id_column_name, column_name])
    reviews.dropna(subset=[column_name], inplace=True)

    film_ids = reviews[id_column_name]
    embs = get_embeddings(
        model,
        reviews,
        column_name,
        text_pipeline,
        batch_size=batch_size,
        show_progress_bar=show_progress,
    )
    np.save(output_filename, {"film_ids": film_ids, "embs_en": embs})


if __name__ == "__main__":
    main()
