# -*- coding: utf-8 -*-


from .utils import load_txt
from .segment_entropy import get_words
from .hyperparameters import Hyperparamters as hp
from .utils import load_excel_only_first_sheet, ToolWord

vocabulary_set = set(load_txt(hp.file_vocabulary))


def get_words_new(corpus, top_k=int(1e4), chunk_size=int(1e6), max_n=int(4), min_freq=5):
    """
    Get these words that not in vocabulary.
    """
    words = get_words(corpus, top_k=top_k, chunk_size=chunk_size, max_n=max_n, min_freq=min_freq)
    print('Length of words:', len(words))
    words_clean = [l for l in words if ToolWord().remove_word_special(l) != '']
    print('Length of words(clean):', len(words_clean))
    return [w for w in words_clean if w not in vocabulary_set]


if __name__ == '__main__':
    ##
    document = ['葫芦屏 武汉 武汉 北京 葫芦屏 葫芦屏 武汉', '武汉 武汉 北京 葫芦屏 葫芦屏 武汉 十四是十四四十是四十，']
    ws = get_words(document)
    print(ws)
    ##
    f = 'data/data.xlsx'
    contents = load_excel_only_first_sheet(f).fillna('')['content'].tolist()  # [:5000]
    print(len(contents))
    words = get_words(contents)
    print(words[:1000])
    nws = get_words_new(contents)
    print(nws[:200])
    print(len(nws))
