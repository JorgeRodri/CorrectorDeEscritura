import pickle
from collections import Counter

if __name__ == '__main__':

    with open('data/idiomas_por_pais.pkl', 'r') as f:
        dic = pickle.load(f)
        # dic = {i: ['es']*(i+1)+['en']*(20-i) for i in range(10)}
    results = {k: Counter(v) for k, v in dic.iteritems()}
    for item, value in results.iteritems():
        # print(item, value.most_common(2), sum([y for x, y in value.most_common(2)]))
        print(item, filter(lambda a: a[1] > 25, value.items()))
