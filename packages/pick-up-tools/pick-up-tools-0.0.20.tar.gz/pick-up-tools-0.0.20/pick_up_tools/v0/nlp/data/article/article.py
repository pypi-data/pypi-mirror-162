from pick_up_tools.v0.nlp.tools import object_uuid
from pick_up_tools.v0.nlp.tools.cut import (
    cut_sentence, cut_word,
)
from pick_up_tools.v0.nlp.algorithm.keyword import get_keyword
from pick_up_tools.v0.nlp.algorithm.sentiment import sentiment_score


class Text(object):
    def __init__(self, text, index=None, ):
        self.index = index
        self.uuid = object_uuid(text)
        self.text = text

        self._word = None
        self._keyword = None
        self._sentiment = None

    @property
    def word(self) -> list:
        if self._word is None:
            self._word = cut_word(self.text) if self.text else []
        return self._word

    @property
    def keyword(self) -> list:
        if self._keyword is None:
            self._keyword = get_keyword(words=self.word) if self.text else []
        return self._keyword

    @property
    def sentiments(self) -> float:
        if self._sentiment is None:
            self._sentiment = sentiment_score(self.text) if self.text else 0.5
        return self._sentiment

    def __str__(self):
        return self.text


class Sentence(Text):
    def __init__(self, text, index=None, sentence_mini_length=0, sentence_drop_topic=True,
                 sentence_cut_half_length=25):
        super(Sentence, self).__init__(text=text, index=index)
        self._sentence = None
        self.sentence_mini_length = sentence_mini_length
        self.sentence_drop_topic = sentence_drop_topic
        self.sentence_cut_half_length = sentence_cut_half_length

    @property
    def half_sentence(self):
        if self._sentence is None:
            _sentence = cut_sentence(
                self.text, min_length=self.sentence_mini_length, drop_topic=self.sentence_drop_topic,
                cut_half=True, cut_half_length=self.sentence_cut_half_length,
            )
            self._sentence = [HalfSentence(i) for i in _sentence]
        return self._sentence


class HalfSentence(Text):
    ...


class Article(Text):
    def __init__(self, text, index=None, sentence_min_length=2, sentence_drop_topic=True,
                 sentence_cut_half_length=25):
        super(Article, self).__init__(text=text, index=index)
        self._sentence = None
        self.sentence_min_length = sentence_min_length
        self.sentence_drop_topic = sentence_drop_topic
        self.sentence_cut_half_length = sentence_cut_half_length

    @property
    def sentence(self) -> Sentence:
        if self._sentence is None:
            _sentence = cut_sentence(
                self.text, min_length=self.sentence_min_length, drop_topic=self.sentence_drop_topic,
                cut_half=False
            )
            self._sentence = [Sentence(i, sentence_cut_half_length=self.sentence_cut_half_length) for i in _sentence]
        return self._sentence


if __name__ == '__main__':
    ...
