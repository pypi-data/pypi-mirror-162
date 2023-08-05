import jieba
from .sentence import text_filter
from ...algorithm.stop_words import stop_words_set


def jieba_cut_for_search(text):
    return [i for i in jieba.cut_for_search(text)]


def jieba_cut(text):
    return [i for i in jieba.cut(text, use_paddle=True, HMM=True)]


def cut_word_filter(words):
    return [i for i in filter(text_filter, words) if i not in stop_words_set]


def cut_word(text, func=jieba_cut):
    _text = func(text)
    _text = cut_word_filter(_text)
    return _text
