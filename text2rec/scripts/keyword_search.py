import string
from typing import List

from nltk.stem.snowball import SnowballStemmer

__all__ = ["TextPipeline"]


class Handler:
    def __init__(self):
        pass

    def __call__(self, token: str):
        pass


class StopWords(Handler):
    def __init__(self, stopwords):
        super().__init__()
        self.stopwords = set(stopwords)

    def __call__(self, token: str):
        return token if token not in self.stopwords else None


class Lowercase(Handler):
    def __init__(self):
        super().__init__()

    def __call__(self, token: str):
        return token.lower()


class SnowballStemmerWrapper(Handler):
    def __init__(self):
        super().__init__()
        self.stemmer = SnowballStemmer("russian")

    def __call__(self, token: str):
        return self.stemmer.stem(token)


class RemovePunctualion(Handler):
    def __init__(self, additional_punkt=""):
        super().__init__()
        punctuation = string.punctuation + additional_punkt
        self.punct_trans = str.maketrans("", "", punctuation)

    def __call__(self, token: str):
        token = token.translate(self.punct_trans)
        return token if token != "" else None


class TextPipeline:
    def __init__(self, handlers: List[Handler] = list(), tokenizer=str.split):
        self.tokenizer = tokenizer
        self.handlers = handlers

    def __call__(self, text: str):
        result = []
        tokens = self.tokenizer(text)
        for token in tokens:
            for handler in self.handlers:
                token = handler(token)
                if token is None:
                    break
            else:  # если дошли до конца цикла
                result.append(token)
        return " ".join(result)
