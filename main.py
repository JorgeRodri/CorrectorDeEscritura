#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function, unicode_literals
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pandas as pd
from engine.corrector import Corrector
from engine.utils import normalize_text, get_stopwords_by_country
from datetime import datetime
import time
import sys
import pickle
import locale
from engine.ngramCorrector import BiCorrector
from engine.ngramUtils import all_ngrams
from MySQL.downloads import get_data, get_more_data, get_top_by_country

path = 'data/'
arch = 'credenciales_server.json'


def tokenize(text):
    return word_tokenize(text)  # + ['ohmylol']*5


def download_save(archivo_credenciales, country, save_path='', episode_number=10, prog_num=500):
    data = get_title_description(archivo_credenciales, program_number = prog_num, episode_number=episode_number, country=country)
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
    elif episode_number < 0:
        df2 = get_more_data(programs, archivo_credenciales, episodes=-episode_number)
        print(len(df2), time.time() - t0)
        return df2
    else:
        print('Wrong valid number of episode, no data added from that source, try integers positive or negatives')
        return df1


def main(country, mode, test=True,  save_path='', value=5,  archivo=None, **kwargs):
    if mode == 'download':
        print(datetime.now())
    stop_words = get_stopwords_by_country(country)
    text_file_name = 'texts_dataframe_cc{0}_ep{1}_progs{2}.pkl'.format(country,
                                                                       kwargs['episode_number'],
                                                                       kwargs['program_number'])
    if country == 1 and mode == 'pickle' and False:
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
    text = tokenize(' '.join(text.values))
    cor = Corrector(text, min_count=value)

    if mode == 'download':
        print(datetime.now())

    while test:
        input_text = raw_input('Frase a corregir: ').decode(sys.stdin.encoding or locale.getpreferredencoding(True))
        if input_text == 'exit' or input_text.isdigit() or len(input_text) < 1:
            break
        t1 = time.time()
        if len(input_text.split()) == 1:
            print('Word: %s: %d' % (input_text, cor.WORDS[input_text]))
        correction = cor.final_correction(input_text)
        # print(list(map(lambda x: (x, cor.WORDS[x]), correction)))
        print(' '.join(correction))
        print('Esta correccion necesito de %.4f segundos.\n' % (time.time()-t1))
        # for i in all_ngrams(correction, stop_words, Corrector.n_grams):
        #     print(i)
        #     l = i.split()
        #     for j in range(1, len(l)-1):
        #         print(' '.join(l[:j]+l[j+1:]))


def main2(country, mode, test=True, save_path='', value=5, archivo=None):
    if mode == 'download':
        print(datetime.now())
    stop_words = get_stopwords_by_country(country)
    text_file_name = 'texts_dataframe_mixture_cc{0}.pkl'.format(country)
    if country == 1 and mode == 'pickle' and False:
        df = pd.read_pickle(save_path + text_file_name)
    elif mode == 'pickle':
        df = pd.read_pickle(save_path + text_file_name)
    elif mode == 'download' and archivo is not None:
        df = get_title_description(archivo, country=country, program_number=5000, episode_number=0)
        df2 = get_title_description(archivo, country=country, program_number=500, episode_number=-10)
        df = df.append(df2)
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
    text = tokenize(' '.join(text.values))
    cor = Corrector(text, min_count=value)

    if mode == 'download':
        print(datetime.now())

    while test:
        input_text = raw_input('Frase a corregir: ').decode(sys.stdin.encoding or locale.getpreferredencoding(True))
        if input_text == 'exit' or input_text.isdigit() or len(input_text) < 1:
            break
        t1 = time.time()
        if len(input_text.split()) == 1:
            print('Word: %s: %d' % (input_text, cor.WORDS[input_text]))
        correction = cor.final_correction(input_text)
        # print(list(map(lambda x: (x, cor.WORDS[x]), correction)))
        print(' '.join(correction))
        print('Esta correccion necesito de %.4f segundos.\n' % (time.time() - t1))
        # for i in all_ngrams(correction, stop_words, Corrector.n_grams):
        #     print(i)
        #     l = i.split()
        #     for j in range(1, len(l)-1):
        #         print(' '.join(l[:j]+l[j+1:]))


def main_all(country):
    models = ['data/texts_dataframe_cc1_ep0_progs5000.pkl',
              'data/texts_dataframe_cc1_ep10_progs500.pkl',
              'data/texts_dataframe_cc1_ep100_progs50.pkl',
              'data/texts_dataframe_mixture_cc1.pkl']
    for i in range(len(models)):
        print('Model {}: '.format(i+1) + models[i])

    values = [1, 5, 5, 4]

    # load model 1
    df = pd.read_pickle(models[0])
    text = df['title'] + ' ' + df['description']
    text = text.apply(normalize_text)
    text = tokenize(' '.join(text.values))
    cor0 = Corrector(text, min_count=values[0])

    # load model 2
    values = [1, 5, 5, 4]
    df = pd.read_pickle(models[1])
    text = df['title'] + ' ' + df['description']
    text = text.apply(normalize_text)
    text = tokenize(' '.join(text.values))
    cor1 = Corrector(text, min_count=values[1])

    # load model 3
    values = [1, 4, 4, 4]
    df = pd.read_pickle(models[2])
    text = df['title'] + ' ' + df['description']
    text = text.apply(normalize_text)
    text = tokenize(' '.join(text.values))
    cor2 = Corrector(text, min_count=values[2])

    # load model 4
    df = pd.read_pickle(models[3])
    text = df['title'] + ' ' + df['description']
    text = text.apply(normalize_text)
    text = tokenize(' '.join(text.values))
    cor3 = Corrector(text, min_count=values[3])

    while True:
        input_text = raw_input('Frase a corregir: ').decode(sys.stdin.encoding or locale.getpreferredencoding(True))
        if input_text == 'exit' or input_text.isdigit() or len(input_text) < 1:
            break
        t1 = time.time()
        print('Model 1:' + ' '.join(cor0.final_correction(input_text)))
        # print('Model 1:' + str(cor0.WORDS[input_text]))
        print('Esta correccion necesito de %.4f segundos.' % (time.time()-t1))
        t1 = time.time()
        print('Model 2:' + ' '.join(cor1.final_correction(input_text)))
        # print('Model 2:' + str(cor1.WORDS[input_text]))
        print('Esta correccion necesito de %.4f segundos.' % (time.time()-t1))
        t1 = time.time()
        print('Model 3:' + ' '.join(cor2.final_correction(input_text)))
        # print('Model 3:' + str(cor2.WORDS[input_text]))
        print('Esta correccion necesito de %.4f segundos.' % (time.time()-t1))
        t1 = time.time()
        print('Model 4:' + ' '.join(cor3.final_correction(input_text)))
        # print('Model 4:' + str(cor3.WORDS[input_text]))
        print('Esta correccion necesito de %.4f segundos.\n' % (time.time()-t1))


def main3():
        # text_file_name = 'texts_dataframe_cc1_ep10_progs500.pkl'

        # download_save('credenciales_server.json', 1, save_path='data/Big_', episode_number=10, prog_num=5000)
        df = pd.read_pickle('data/Big_texts_dataframe1.pkl')  # + text_file_name)
        print(len(df))
        text = df['title'] + ' ' + df['description']
        # with open('data/Big_original.txt', 'r') as f:
        #     text2 = f.read()
        #     text2 = normalize_text(text2)
        #     text = tokenize(text2)
        text = text.apply(normalize_text)
        text = tokenize(' '.join(text.values))
        cor = BiCorrector(text)
        test = True
        while test:
            input_text = raw_input('Frase a corregir: ').decode(sys.stdin.encoding or locale.getpreferredencoding(True))
            if input_text == 'exit' or input_text.isdigit() or len(input_text) < 1:
                break
            t1 = time.time()
            if len(input_text.split()) == 1:
                print('Word: %s: %d' % (input_text, cor.WORDS[input_text]))
            elif len(input_text.split()) == 2:
                print('Bigram: %s: %d' % (input_text, cor.BIGRAMS[tuple(input_text.split())]))
            correction = cor.final_correct(input_text)
            print(correction)
            # correction = cor.numb_treatment(input_text)
            # print('Numb treatment corr: %s' % correction)
            print('Esta correccion necesito de %.4f segundos.\n' % (time.time() - t1))


if __name__ == '__main__':
    # value = entre episodes/2 y episodes/20 permite mantener términos erróneos en los episodios controlados
    # test_boo = True
    # print('Modelo 1')
    # main(1, 'pickle', test=test_boo, archivo=arch, value=4, save_path=path, program_number=500, episode_number=10)
    # print('Modelo 2')
    # main(1, 'pickle', test=test_boo, archivo=arch, value=1, save_path=path, program_number=5000, episode_number=0)
    # print('Modelo 3')
    # main(1, 'pickle', test=test_boo, archivo=arch, value=4, save_path=path, program_number=50, episode_number=100)
    # print('Modelo 4 (Modelo 1+2)')
    # main2(1, 'pickle', test=test_boo, archivo=arch, value=4, save_path=path)
    # print('All done')
    # main_all(1)
    main3()
