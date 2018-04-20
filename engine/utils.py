# -*- coding: utf8 -*-
import re
from nltk.corpus import stopwords
from string import punctuation


def un_punctuate(text, p_):
    for char in p_:
        # print(char)
        text = text.replace(char, '')  # ' ' + char + ' ')
    return text


def clean_digit_url(text):
    text = re.sub(r'-?\d+[.,]?\d*%?', '', text)
    text = re.sub(r'https?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b ', '', text)
    return text


def normalize_text(text):
    norm_text = text.lower()
    # Replace breaks with spaces
    norm_text = norm_text.replace('<br />', '')
    # Pad punctuation with spaces on both sides
    non_words = list(punctuation)
    non_words.extend([u'¿', u'¡'])
    non_words.extend(map(str, range(10)))
    non_words.extend(['\n', '\r', '\t'])
    norm_text = un_punctuate(norm_text, non_words)
    norm_text = clean_digit_url(norm_text)
    norm_text = norm_text.replace('ohmylol', 'oh my lol')
    return norm_text


def get_stopwords_by_country(country_code):
    stop_words = []
    if country_code in [1, 2, 3, 4, 7, 254, 255]:
        stop_words += list(set(stopwords.words('Spanish')))
    if country_code in [101, 119, 235, 51, 183]:
        stop_words += list(set(stopwords.words('English')))
    if country_code == 91:
        stop_words += list(set(stopwords.words('French')))
    if country_code == 101:
        stop_words += list(set(stopwords.words('German')))
    if country_code in [51, 183]:
        stop_words += list(set(stopwords.words('Portuguese')))
    if country_code == 119:
        stop_words += list(set(stopwords.words('Italian')))
    return stop_words
