#!/usr/bin/env python
# -*- coding: utf8 -*-
from nltk.tokenize import word_tokenize
import pandas as pd
from engine.corrector import Corrector
from engine.utils import normalize_text
import time
import sys
import pickle
from MySQL.downloads import get_data, get_more_data, get_top_by_country
from flask import Flask, request

app = Flask(__name__)


def get_title_description(archivo_credenciales):
    programs = get_top_by_country(1, 5000, archivo_credenciales)
    t0 = time.time()
    df1 = get_data(programs, archivo_credenciales)
    print(len(df1), time.time()-t0)

    t0 = time.time()
    df2 = get_more_data(programs, archivo_credenciales, episodes=10)
    print(len(df2), time.time()-t0)
    return df1.append(df2)


def main(archivo_credenciales):
    data = get_title_description(archivo_credenciales)
    data.to_pickle('texts_dataframe.pkl')
    print(len(data))


@app.route('/correct', methods=['GET'])
def correct():
    try:
        word = request.args.get('word')
    except TypeError as e:
        print(e)
        return str(-1)

    t1 = time.time()
    try:
        correction = ' '.join(cor.final_correction(word))
    except TypeError as e:
        print(e)
        return str(-1)

    print('Esta correccion necesito de %.4f segundos.' % (time.time()-t1))
    return correction


@app.errorhandler(404)
def page_not_found(e):
    print(e)
    return str(-1)


if __name__ == '__main__':
    archivo = 'credenciales_server.json'
    # main(archivo)
    df = pd.read_pickle('texts_dataframe.pkl')
    print(len(df))
    text = df['title'] + ' ' + df['description']
    text = text.apply(normalize_text)
    text = word_tokenize(' '.join(text.values))
    cor = Corrector(text)
    # with open('correct_model.pkl', 'rb') as f:
    #     print('Loading the object')
    #     cor = pickle.load(f)
    #     print('Model loaded')

    if len(sys.argv) == 3:
        arg1 = sys.argv[1]
        arg2 = sys.argv[2]
        app.run(host=arg1, port=int(arg2))
    elif len(sys.argv) == 2:
        arg = sys.argv[1]
        app.run(host='127.0.0.1', port=int(arg))
    else:
        app.run(host='127.0.0.1', port=5000)
