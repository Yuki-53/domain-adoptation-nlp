import re
import argparse
import unicodedata

import pandas as pd
from unidecode import unidecode

__all__ = ["filter_reviews_new"]


def func(match: re.Match):
    group = match.group(1)
    if group == "":
        return ". "
    return f"{group[0]} "


def func2(match: re.Match):
    group = match.group(1)
    return unicodedata.normalize("NFKC", group[0])


def func3(match: re.Match):
    group = match.group(1)
    return unidecode(group[0])


def replace_repeated_html_tags(series: pd.Series):
    def tags(match: re.Match):
        return match.group(1)

    new = series
    while True:
        old = new
        new = old.str.replace(r"<\w+>([^<>]*)<\/\w+>", tags, regex=True)
        if (old == new).all():
            break
    return new


def filter_reviews_new(reviews: pd.DataFrame, column_name: str):
    filtered = reviews.copy(deep=True)
    # Remove new line at beginning of every review
    filtered[column_name] = filtered[column_name].str.removeprefix("\n")
    # Remove urls
    url_regex = (
        "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|"
        r"[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    )
    filtered[column_name] = filtered[column_name].str.replace(url_regex, "", regex=True)
    # Remove html and nested tags
    filtered[column_name] = replace_repeated_html_tags(filtered[column_name])
    filtered[column_name] = filtered[column_name].str.replace(
        r"<\/?[\w\d\. =':\/]+>", "", regex=True
    )
    # FIXME: we need to replace to ascii or delete specific utf8 symbols
    filtered[column_name] = filtered[column_name].str.replace(" *\t *", " ", regex=True)
    filtered[column_name] = filtered[column_name].str.replace(
        "([^\u0410-\u044f\u0451])", func3, regex=True
    )
    filtered[column_name] = filtered[column_name].str.replace(
        "[\u0301\u200b\u2122\ufeff]", "", regex=True
    )
    filtered[column_name] = filtered[column_name].str.replace("\u2028", ", ")
    filtered[column_name] = filtered[column_name].str.replace("\u00E9", "e")
    filtered[column_name] = filtered[column_name].str.replace(
        "([\u2460-\u2473])", func2, regex=True
    )
    filtered[column_name] = filtered[column_name].str.replace(
        "([\u00c0-\u00ff\u0100-\u024f])", func3, regex=True
    )
    # Restore punctuation on end of sentences
    filtered[column_name] = filtered[column_name].str.replace(
        "([…:!\\.\\?]?) *(?:[\r\n])+", func, regex=True
    )
    return filtered


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename")
    parser.add_argument("output_filename")
    parser.add_argument("-c", "--column_name", nargs="?", default="review_text")
    args = parser.parse_args()

    input_filename = args.input_filename
    output_filename = args.output_filename
    column_name = args.column_name
    reviews = pd.read_csv(input_filename)
    filtered = filter_reviews_new(reviews, column_name)

    filtered.to_csv(output_filename, index=False)


if __name__ == "__main__":
    main()
