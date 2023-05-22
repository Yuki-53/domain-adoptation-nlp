import argparse

import pandas as pd
import requests
from tqdm import tqdm

__all__ = ["get_imgs"]


def get_imgs(df: pd.DataFrame, savepath: str, id_col: str):
    film_ids = df[id_col].unique().tolist()

    for id in tqdm(film_ids):
        img_url = "https://st.kp.yandex.net/images/film_iphone/iphone360_{id}.jpg"
        r = requests.get(img_url)
        if r.headers["Content-Type"] == "image/jpeg":
            with open(f"{savepath}{id}.jpg", "wb") as handler:
                handler.write(r.content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath")
    parser.add_argument("-sp", "--save_path", nargs="?", default="path to save")
    parser.add_argument("-c", "--column_name", nargs="?", default="id")
    args = parser.parse_args()

    filepath = args.filepath
    savepath = args.save_path
    column_name = args.column_name
    df = pd.read_csv(filepath, usecols=[column_name])

    print("Starting getting images")
    get_imgs(df, savepath, column_name)


if __name__ == "__main__":
    main()
