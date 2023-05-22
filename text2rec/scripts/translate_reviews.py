import time
import argparse

import pandas as pd
from tqdm import tqdm
from googletrans import Translator

__all__ = ["translate_reviews"]


class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, typ, value, traceback):
        self.elapsed = time.perf_counter() - self.start


def translate_reviews(
    reviews: pd.DataFrame, column_name, delay=0.5, show_progress_bar=True
) -> pd.DataFrame:
    translated_reviews = []
    service_urls = ["translate.google.com", "translate.google.ru"]
    translator = Translator(service_urls=service_urls, raise_exception=True)
    translated = reviews.copy(deep=True)
    reviews_text = reviews[column_name]
    for i, text_ru in enumerate(tqdm(reviews_text, disable=not show_progress_bar)):
        text_en = None
        with Timer() as timer:
            try:
                text_en = translator.translate(text_ru[:5000], src="ru", dest="en").text
            except TypeError:
                print(f"\rCant translate {i}-th review")
                time.sleep(delay)
            except Exception:
                time.sleep(delay)  # 60 - works
                translator = Translator(service_urls=service_urls, raise_exception=True)
                text_en = translator.translate(text_ru[:5000], src="ru", dest="en").text
            translated_reviews.append(text_en)
        time.sleep(max(delay - timer.elapsed, 0))
    if i + 1 != len(reviews_text):
        translated = translated.iloc[:i].copy(deep=True)
    translated[column_name] = translated_reviews
    translated = translated.dropna(subset=[column_name])
    return translated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename", help="path to .csv file")
    parser.add_argument("output_filename", help="path to .csv file")
    parser.add_argument("-c", "--column_name", nargs="?", default="review_text")
    parser.add_argument("-s", "--start_index", nargs="?", default=0)
    parser.add_argument("-e", "--end_index", nargs="?", default=-1)
    args = parser.parse_args()

    input_filename = args.input_filename
    output_filename = args.output_filename
    df = pd.read_csv(input_filename)
    column_name = args.column_name
    start_index = int(args.start_index)
    end_index = int(args.end_index)
    end_index = len(df) if end_index == -1 else end_index
    reviews = df.iloc[start_index:end_index].copy(deep=True)

    print(f"Starting translating reviews from {start_index} to {end_index}")
    translated = translate_reviews(reviews, column_name)
    translated.to_csv(output_filename, index=False)


if __name__ == "__main__":
    main()
