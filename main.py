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
    if episode_number == 0:
        return df1
    elif episode_number > 0:
        df2 = get_more_data(programs, archivo_credenciales, episodes=episode_number)
        print(len(df2), time.time()-t0)
        return df1.append(df2)
    else:
        print('Wrong valid number of episode, no data added from that source, try values equal or bigger than 0')
        return df1


def main(country, mode, test=True,  save_path='', value=5,  archivo=None, **kwargs):
    if mode == 'download':
        print(datetime.now())
    stop_words = get_stopwords_by_country(country)
    text_file_name = 'texts_dataframe_cc{0}_ep{1}_progs{2}.pkl'.format(country,
                                                                       kwargs['episode_number'],
                                                                       kwargs['program_number'])
    if country == 1 and mode == 'pickle':
        df = pd.read_pickle(save_path + text_file_name)
    elif mode == 'pickle':
        df = pd.read_pickle(save_path + text_file_name)
    elif mode == 'download' and archivo is not None:
        df = get_title_description(archivo, country=country, **kwargs)
        df.to_pickle(save_path + text_file_name)
    elif archivo is None:
        print('No credential file, try pickle')
        return None
    else:
        print('Wrong mode, try pickle or download')
        return None
    print(len(df))
    text = df['title'] + ' ' + df['description']
    text = text.apply(normalize_text)
    text = word_tokenize(' '.join(text.values))
    cor = Corrector(text, min_count=value)

    if mode == 'download':
        print(datetime.now())

    while test:
        input_text = raw_input('Frase a corregir: ').decode(sys.stdin.encoding or locale.getpreferredencoding(True))
        if input_text == 'exit' or input_text.isdigit() or len(input_text) < 1:
            break
        t1 = time.time()
        # if len(input_text.split()) == 1:
            # print('Word: %s: %d' % (input_text, cor.WORDS[input_text]))
        correction = cor.final_correction(input_text)
        # print(list(map(lambda x: (x, cor.WORDS[x]), correction)))
        print(' '.join(correction))
        print('Esta correccion necesito de %.4f segundos.\n' % (time.time()-t1))
        # for i in all_ngrams(correction, stop_words, n_grams):
        #     print(i)  
        #     l = i.split()
        #     for j in range(1, len(l)-1):
        #         print(' '.join(l[:j]+l[j+1:]))


if __name__ == '__main__':
    # value = entre episodes/2 y episodes/20 permite mantener términos erróneos en los episodios controlados
    test_boo = False
    print('Modelo 1')
    main(1, 'pickle', test=test_boo, archivo=arch, value=5, save_path=path, program_number=500, episode_number=10)
    print('Modelo 2')
    main(1, 'pickle', test=test_boo, archivo=arch, value=1, save_path=path, program_number=5000, episode_number=0)
    print('Modelo 3')
    main(1, 'pickle', test=test_boo, archivo=arch, value=5, save_path=path, program_number=50, episode_number=100)
    print('All done')
