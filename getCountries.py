import datetime
from textblob import TextBlob
from MySQL.downloads import *
import pickle
from collections import Counter


def get_title_description(credenciales, country_code=255, top_programs=50, num_episodes=10):
    programs = get_top_by_country(country_code, top_programs, credenciales)
    t0 = time.time()
    df1 = get_data(programs, credenciales)
    print(len(df1), time.time()-t0)

    t0 = time.time()
    df2 = get_more_data(programs, credenciales, episodes=num_episodes)
    print(len(df2), time.time()-t0)
    return df1.append(df2)


country_codes = [1, 2, 3, 4, 7, 51, 91, 101, 119, 183, 235, 254, 255]

lang_by_country = dict()

if __name__ == '__main__':
    num_programs = 500
    for country in country_codes:
        archivo_credenciales = 'credenciales_server.json'
        df = get_title_description(archivo_credenciales, country_code=country, top_programs=num_programs)
        text = df['title'] + ' ' + df['description']

        print('Codigo del pais: %d empieza en %s' % (country, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        languages = []
        for i in text:
            b = TextBlob(i)
            languages.append(b.detect_language())
        lang_by_country[country] = languages
    with open('data/idiomas_por_pais_grande.pkl', 'wb') as f:
        pickle.dump(lang_by_country, f)
    results = {k: Counter(v) for k, v in lang_by_country.iteritems()}
    for item, value in results.iteritems():
        print(item, value)
    print('\n\n')
    for item, value in results.iteritems():
        print(item, filter(lambda a: a[1] > 0.05*num_programs, value.items()))
