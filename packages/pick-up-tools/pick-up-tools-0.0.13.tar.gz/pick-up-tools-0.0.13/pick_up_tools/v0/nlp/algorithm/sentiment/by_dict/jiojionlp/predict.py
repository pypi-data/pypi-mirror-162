import jionlp

__jio_sentiment = jionlp.sentiment.LexiconSentiment()


def predict(text):
    return __jio_sentiment(text)


if __name__ == '__main__':
    s = "我坐在椅子上看城市的衰落"
    p = predict(s)
    print(predict(s))
