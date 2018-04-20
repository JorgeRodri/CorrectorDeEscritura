#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import print_function, unicode_literals
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pandas as pd
from engine.corrector import Corrector, n_grams
from engine.utils import normalize_text, get_stopwords_by_country
from datetime import datetime
import time
import sys
import pickle
import locale
from engine.ngramUtils import all_ngrams
from MySQL.downloads import get_data, get_more_data, get_top_by_country

path = 'data/'
arch = 'credenciales_server.json'


def download_save(archivo_credenciales, country, save_path='', episode_number=10):
    data = get_title_description(archivo_credenciales, 500, episode_number=episode_number, country=country)
    data.to_pickle(save_path + 'texts_dataframe{}.pkl'.format(country))
    print(len(data))


def get_title_description(archivo_credenciales, program_number=500, episode_number=10, country=1):
    programs = get_top_by_country(country, program_number, archivo_credenciales)
    t0 = time.time()
    df1 = get_data(programs, archivo_credenciales)
    print(len(df1), time.time()-t0)

    t0 = time.time()
    df2 = get_more_data(programs, archivo_credenciales, episodes=episode_number)
    print(len(df2), time.time()-t0)
    return df1.append(df2)


def main(country, mode, save_path='',  archivo=None, **kwargs):
    print(datetime.now())
    stop_words = get_stopwords_by_country(country)
    # print(stop_words)
    if country == 1 and mode == 'pickle':
        df = pd.read_pickle(save_path + 'texts_dataframe.pkl')
    elif mode == 'pickle':
        df = pd.read_pickle(save_path + 'texts_dataframe{}.pkl'.format(country))
    elif mode == 'download' and archivo is not None:
        df = get_title_description(archivo, country=country, **kwargs)
        df.to_pickle(save_path + 'texts_dataframe{}.pkl'.format(country))
    elif archivo is None:
        print('No credential file, try pickle')
        return None
    else:
        print('Wrong mode, try pickle or download')
        return None
    text = df['title'] + ' ' + df['description']
    text = text.apply(normalize_text)
    text = word_tokenize(' '.join(text.values))
    cor = Corrector(text)

    print(datetime.now())

    while True:
        input_text = raw_input('Frase a corregir: ').decode(sys.stdin.encoding or locale.getpreferredencoding(True))
        if input_text == 'exit' or input_text.isdigit() or len(input_text) < 1:
            break
        t1 = time.time()
        if len(input_text.split()) == 1:
            print('Word: %s: %d' % (input_text, cor.WORDS[input_text]))
        correction = cor.final_correction(input_text)
        print(list(map(lambda x: (x, cor.WORDS[x]), correction)))
        print(' '.join(correction))
        print('Esta correccion necesito de %.4f segundos.\n' % (time.time()-t1))
        for i in all_ngrams(correction, stop_words, n_grams):
            print(i)
            l = i.split()
            for j in range(1, len(l)-1):
                print(' '.join(l[:j]+l[j+1:]))


if __name__ == '__main__':
    main(1, 'pickle', archivo=arch, save_path=path, program_number=500, episode_number=10)
