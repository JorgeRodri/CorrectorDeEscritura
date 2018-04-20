# -*- coding: utf8 -*-
# import re
# from string import punctuation


def zipngram(text, n=2):
    words = text.split()
    return zip(*[words[i:] for i in range(n)])


def all_ngrams(tokenized_sentence,stop_words, func):
    search = [word for word in tokenized_sentence if word not in stop_words]
    for j in range(len(search), 0, -1):
        ngrams_list = func(' '.join(search), n=j)
        for du in ngrams_list:
            yield du
