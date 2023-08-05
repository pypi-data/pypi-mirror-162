import pandas as pd
from jieba import analyse
from sklearn.feature_extraction.text import TfidfVectorizer
from ..stop_words import stop_words_path
from pick_up_tools.v0.nlp.tools.cut import cut_word_filter


def fit_idf(words_of_sentence: list, path='idf.txt.extra'):
    corpus = [' '.join(i) for i in words_of_sentence]
    vectorized = TfidfVectorizer(stop_words=None)
    vectorized.fit_transform(corpus)
    df_word_idf = pd.DataFrame(list(zip(vectorized.get_feature_names(), vectorized.idf_)), columns=['word', 'idf'])
    df_word_idf.to_csv(path, sep=' ', index=False, header=False)
    analyse.set_idf_path(path)
    return df_word_idf


def tfidf_keyword(words, topK=5, withWeight=False, allowPOS=(), withFlag=False) -> list:
    sentence = '，'.join(words)
    analyse.set_stop_words(stop_words_path)
    kws = analyse.extract_tags(sentence, topK=topK, withWeight=withWeight, allowPOS=allowPOS, withFlag=withFlag)
    kws = cut_word_filter(kws)
    return kws
