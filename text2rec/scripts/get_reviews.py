import argparse
from typing import List
from datetime import datetime

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.remote.webdriver import WebDriver

__all__ = ["get_reviews_from_content_list"]


def get_review_type(classes: List):
    if "good" in classes:
        return "POSITIVE"
    if "bad" in classes:
        return "NEGATIVE"
    return "NEUTRAL"


RU_MONTH_VALUES = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}


def int_value_from_ru_month(date_str: str):
    for k, v in RU_MONTH_VALUES.items():
        date_str = date_str.replace(k, str(v))
    return date_str


def kinopoisk_date_str_to_datetime(date_str: str):
    date_str = int_value_from_ru_month(date_str)
    return datetime.strptime(date_str, "%d %m %Y | %H:%M")


def get_review_info(review: BeautifulSoup):
    review_id = review["data-id"]
    review_type_data = review.findChild("div", {"itemprop": "reviews"})
    review_type = get_review_type(review_type_data["class"])
    review_text_data = review.findChild("div", {"class": "brand_words"})
    review_text = review_text_data.text
    review_title = review.findChild("p", {"class": "sub_title"}).text
    pos_and_neg_data = review.findChild("li", {"id": f"comment_num_vote_{review_id}"})
    pos, neg = map(int, pos_and_neg_data.text.replace("/", "").split())
    author_data = review.findChild("p", {"class": "profile_name"})
    author_id_data = author_data.findChild("a")["href"]
    author_id = int(author_id_data.lstrip("/user/").rstrip("/"))
    author_name = author_data.text
    date_raw = review.findChild("span", {"class": "date"}).text
    date = kinopoisk_date_str_to_datetime(date_raw)
    return (
        review_id,
        author_id,
        author_name,
        review_title,
        review_type,
        pos,
        neg,
        review_text,
        date,
    )


def parse_reviews(soup: BeautifulSoup, content_id: int):
    try:
        film_title_raw = soup.findChild("a", {"class", "breadcrumbs__link"})
        film_title = film_title_raw.text
    except Exception:
        print(f"Cant parse film title with ID: {content_id}")
    reviews = soup.find_all("div", {"class": ["reviewItem", "userReview"]})
    reviews_info = [(content_id, film_title) + get_review_info(r) for r in reviews]
    columns = [
        "film_id",
        "film_title",
        "review_id",
        "author_id",
        "author_name",
        "review_title",
        "review_type",
        "pos",
        "neg",
        "review_text",
        "date",
    ]
    return pd.DataFrame(data=reviews_info, columns=columns)


def get_content_reviews_at_page(driver: WebDriver, content_id: int, page: int):
    review_url = (
        "https://www.kinopoisk.ru/film/{}/reviews/ord"
        "/rating/status/all/perpage/200/page/{}/"
    )
    driver.get(review_url.format(content_id, page))
    html = driver.page_source
    soup = BeautifulSoup(html, features="html.parser")
    return parse_reviews(soup, content_id)


def get_checked_types(content_type: str):
    checked_types = ["film", "series"]
    if content_type.lower() in ["series", "cериал"]:
        return checked_types[::-1]
    return checked_types


def get_pages_count_from_content(driver: WebDriver, content_id: int):
    review_url = (
        "https://www.kinopoisk.ru/film/{}/reviews/ord"
        "/rating/status/all/perpage/200/page/{}/"
    )
    driver.get(review_url.format(content_id, 1))
    html = driver.page_source
    soup = BeautifulSoup(html, features="html.parser")
    soup.findChild("a", {"class", "breadcrumbs__link"})
    review_count_raw = soup.find("li", {"class": "all"})
    review_count = int(review_count_raw.findChild("b").text)
    pages_count = int(np.ceil(review_count / 200))
    return pages_count


def get_reviews_from_content(driver: WebDriver, content_id: int, show_progress=False):
    try:
        pages_count = get_pages_count_from_content(driver, content_id)
    except Exception:
        return
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    total_reviews = [parse_reviews(soup, content_id)]
    for page in tqdm(range(2, pages_count + 1), disable=not show_progress):
        try:
            reviews_at_page = get_content_reviews_at_page(driver, content_id, page)
        except Exception:
            break
        total_reviews.append(reviews_at_page)
    return pd.concat(total_reviews, ignore_index=True)


def get_reviews_from_content_list(
    driver: WebDriver, content_ids: List[int], show_progress=False
):
    result = []
    for content_id in tqdm(content_ids, disable=not show_progress):
        reviews = get_reviews_from_content(driver, content_id)
        if reviews is None:
            continue
        result.append(reviews)
    if result is None:
        return
    return pd.concat(result, ignore_index=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename", help="path to input .csv file")
    parser.add_argument("output_filename", help="path to output .csv file")
    parser.add_argument("-i", "--id_column_name", nargs="?", default="film_id")
    parser.add_argument("-s", "--start_index", nargs="?", default=0)
    parser.add_argument("-e", "--end_index", nargs="?", default=-1)
    parser.add_argument("--show_progress", action="store_true")
    args = parser.parse_args()

    input_filename: str = args.input_filename
    output_filename: str = args.output_filename
    id_column_name = args.id_column_name
    df = pd.read_csv(input_filename, usecols=[id_column_name])
    start_index = int(args.start_index)
    end_index = int(args.end_index)
    end_index = len(df) if end_index == -1 else end_index
    df_slice = df.iloc[start_index:end_index].copy(deep=True)
    content_ids = df_slice[id_column_name]
    show_progress = args.show_progress

    chrome_options = ChromeOptions()
    chrome_options.debugger_address = "localhost:9222"
    chrome_driver = webdriver.Chrome(options=chrome_options)

    reviews: pd.DataFrame = get_reviews_from_content_list(
        chrome_driver, content_ids, show_progress=show_progress
    )
    if reviews is None:
        return
    reviews.to_csv(output_filename, index=False)


if __name__ == "__main__":
    main()
