from snownlp import SnowNLP


def predict(text):
    score = SnowNLP(text).sentiments if text else 0.5
    return score
