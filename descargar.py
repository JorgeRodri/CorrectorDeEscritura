#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import print_function, unicode_literals
import time
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
    elif episode_number < 0:
        df2 = get_more_data(programs, archivo_credenciales, episodes=-episode_number)
        print(len(df2), time.time() - t0)
        return df2
    else:
        print('Wrong valid number of episode, no data added from that source, use integers positive or negatives')
        return df1


def main():
    country = 1
    df = get_title_description(arch, country=country, program_number=5000, episode_number=100)
    df.to_pickle(path + 'big_data.pkl')


if __name__ == '__main__':
    main()
