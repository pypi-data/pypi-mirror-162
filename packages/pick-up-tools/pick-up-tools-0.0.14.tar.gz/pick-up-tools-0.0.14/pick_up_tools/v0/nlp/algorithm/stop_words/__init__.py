from pick_up_tools.v0.settings import BASE_DIR, relative

stop_words_path = relative(BASE_DIR, 'nlp/algorithm/stop_words/stop_words.txt')
stop_words = open(stop_words_path, mode='r', encoding='utf=8').readlines()
stop_words = [i.strip('\n') for i in stop_words]
stop_words_set = set(stop_words)
