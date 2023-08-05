import jiagu


def predict(text):
    s = jiagu.sentiment(text)
    score = s[1]
    if s[0] == 'negative':
        score = 1 - s[1]
    return score
