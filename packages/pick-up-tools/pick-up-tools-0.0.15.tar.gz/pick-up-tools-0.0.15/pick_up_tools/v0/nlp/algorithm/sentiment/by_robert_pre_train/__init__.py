import xmnlp

enable = xmnlp.config.MODEL_DIR

xmnlp_set_model = lambda x: xmnlp.set_model(x)


def predict(text):
    return xmnlp.sentiment(text)[1]
