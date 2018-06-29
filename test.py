import requests
import pandas as pd
from nltk.corpus import stopwords
import re


def transform(text):
    text = re.sub(r'-?\d+[.,]?\d*%?', ' ', text)
    list_words = text.split()
    stop_words = set(stopwords.words('english') + stopwords.words('spanish'))
    list_words = [w for w in list_words if w not in stop_words]

    return ' '.join(list_words)


request_template = 'http://api.ivoox.com/1-2/?function=getSearchSummary&format=json&search={}'

result = []
terms = []

df = pd.read_pickle('zero_search.pkl')
df = df.sample(500)
for indx in range(len(df)):
    search_terms = df['zeroresultsearch_text'].values[indx]
    search_terms = transform(search_terms)
    terms.append(search_terms)
    search_terms = search_terms.replace(' ', '%20')
    r = requests.get(request_template.format(search_terms))
    d = r.json()
    if d['audios']['numresults'] == 0 and d['radios']['numresults'] == 0 and d['programs']['numresults'] == 0:
        result.append(d['audios']['results'][0]) if d['audios']['results'] \
                                                 else 'otro'
    else:
        result.append(0)

print(result)
df2 = pd.DataFrame({'Original': df['zeroresultsearch_text'].values, 'Buscado': terms, 'Resultados': result},
                   columns=['Original', 'Buscado', 'Resultados'])
df2.to_csv('zero_results_analysis.csv')
