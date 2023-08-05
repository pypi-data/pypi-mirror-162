from .html import *
from ..extractor import Extractor

extractor = Extractor()

clean_text = extractor.clean_text

del extractor


def clean_all(text):
    _text = remove_weibo_at(clean_text(text))
    return _text
