from pick_up_tools.v0.nlp.tools import object_uuid
from pick_up_tools.v0.nlp.algorithm.sentiment import sentiment_score


class Word(object):
    def __init__(self, text):
        self.uuid = object_uuid(text)
        self.text = text

        self._part_of_speech = None
        self._sentiment = None

    @property
    def sentiments(self) -> float:
        if self._sentiment is None:
            self._sentiment = sentiment_score(self.text)
        return self._sentiment

    @property
    def part_of_speech(self):
        if self._part_of_speech is None:
            self._part_of_speech = ''
        return self._part_of_speech

    def __str__(self):
        return self.text
