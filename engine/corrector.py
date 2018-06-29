# -*- coding: utf8 -*-
from collections import Counter
from engine.utils import normalize_text
import re
import itertools
import numpy as np


def memo(f):
    """Memoize function f, whose args must all be hashable."""
    cache = {}

    def fmemo(*args):
        if args not in cache:
            cache[args] = f(*args)
        return cache[args]

    fmemo.cache = cache
    return fmemo


class Corrector(object):
    author = 'Jorge Rodriguez'
    for_ = 'iVoox'
    when = 'March2018'

    def __init__(self, big_text, min_count=1):
        """
        Constructor para el corrector
        :param big_text: texto a usar como diccionario
        :param min_count: minimo numero de apariciones para que una palabra se tenga en cuenta (confianza de la fuente)
        """
        self.WORDS = Counter(big_text)  # {k: v for k, v in Counter(big_text).iteritems() if v >= 5}
        self.__total__ = sum(self.WORDS.values())
        self.min_count = min_count

    # Static methods
    @staticmethod
    def edits_tildes(word):
        split = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        a = [L + u'á' + R[1:] for L, R in split if R and R[0] == 'a']
        e = [L + u'é' + R[1:] for L, R in split if R and R[0] == 'e']
        i = [L + u'í' + R[1:] for L, R in split if R and R[0] == 'i']
        o = [L + u'ó' + R[1:] for L, R in split if R and R[0] == 'o']
        u = [L + u'ú' + R[1:] for L, R in split if R and R[0] == 'u']
        return a + e + i + o + u

    @staticmethod
    def edits0(word):
        split = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        ache = [L + 'h' + R for L, R in split]
        uve = [L + 'v' + R[1:] for L, R in split if R and R[0] == 'b']
        be = [L + 'b' + R[1:] for L, R in split if R and R[0] == 'v']
        ge = [L + 'g' + R[1:] for L, R in split if R and R[0] == 'j']
        jot = [L + 'j' + R[1:] for L, R in split if R and R[0] == 'g']
        ere = [L + 'r' + R for L, R in split if
               L and R and L[-1] == 'r' and R[0] != 'r' and L[-2:] != 'rr' and len(L) > 1]
        ll = [L + 'y' + R[2:] for L, R in split if R if R[:2] == 'll']
        y = [L + 'll' + R[1:] for L, R in split if R if R[0] == 'y']
        tildes = Corrector.edits_tildes(word)
        return set(ache + uve + be + jot + ge + ere + ll + y + tildes)

    @staticmethod
    def edits1(word):
        """All edits that are one edit away from `word`."""
        letters = u'abcdefghijklmnñopqrstuvwxyzáéíóú'
        split = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in split if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in split if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in split if R for c in letters]
        inserts = [L + c + R for L, R in split for c in letters]
        return set(deletes + transposes + replaces + inserts)

    @staticmethod
    def edits2(word):
        """All edits that are two edits away from `word`."""
        return (e2 for e1 in Corrector.edits1(word) for e2 in Corrector.edits1(e1).union(Corrector.edits0(e1)))

    @staticmethod
    def product(nums):
        """Multiply the numbers together.  (Like `sum`, but with multiplication.)"""
        result = 1
        for x in nums:
            result *= x
        return result

    @staticmethod
    def splits(text, start=0, s=20):
        """Return a list of all (first, rest) pairs; start <= len(first) <= L."""
        return ((text[:i], text[i:]) for i in range(start, min(len(text), s) + 1))

    @staticmethod
    def n_grams(text, n=None):
        search_list = text.split()
        if n is None:
            n = len(search_list) - 1
        if n == 0:
            return ['']
        elif n > len(search_list):
            return [' '.join(search_list)]
        return [' '.join(search_list[i:i + n]) for i in range(len(search_list) - n + 1)]

    def p(self, word):
        """Probability of `word`."""
        return np.float64(self.WORDS[word]) / self.__total__

    def correction(self, word):
        """Most probable spelling correction for word."""
        c = self.__candidates__(word.lower())
        if len(c) == 1 and not self.__known__(c):
            return ' '.join(self.true_segment(c[0]))
        return max(c, key=self.p)

    def __word_correction__(self, word):
        """Most probable spelling correction for word."""
        c = self.__candidates__(word.lower())
        return max(c, key=self.p)

    def __candidates__(self, word):
        """Generate possible spelling corrections for word."""
        if word[-1] == 's':
            return self.__known__([word]) or self.__known__([word[0:-1]]) or self.__known__(Corrector.edits0(word)) or \
                   self.__known__(Corrector.edits1(word[0:-1])) or self.__known__(Corrector.edits1(word)) or \
                   self.__known__(Corrector.edits2(word)) or [word]
        return self.__known__([word]) \
            or self.__known__(Corrector.edits0(word)) \
            or self.__known__(Corrector.edits1(word)) \
            or self.__known__(Corrector.edits2(word))\
            or [word]

    def __known__(self, words):
        """The subset of `words` that appear in the dictionary of WORDS."""
        return set(w for w in words if w in self.WORDS and self.WORDS[w] >= self.min_count)

    def p_words(self, words):
        """Probability of words, assuming each word is independent of others."""
        return np.float64(Corrector.product(self.p(w) for w in words))

    @memo
    def __segment__(self, text):
        """Return a list of words that is the most probable segmentation of text."""
        if not text:
            return []
        else:
            candidates = [[first] + self.__segment__(rest)
                          for (first, rest) in Corrector.splits(text, 1)]
            # print(candidates)
            return max(candidates, key=self.p_words)

    def true_segment(self, word):
        candidates = self.__segment__(word)
        return self.correct_text(' '.join(candidates))
        # return list(filter(lambda x: len(x) > 1, candidates))

    def correct_text(self, text):
        word_list = normalize_text(text).split()
        for word in word_list:
            yield self.correction(word)

    def joins(self, text):
        word_list = text.split()
        candidates = [word_list[:i] + [''.join(word_list[i:i+w])] + word_list[i+w:]
                      for i in range(len(word_list)-1)
                      for w in range(2, len(word_list)-i+1)]
        candidates = [word_list] + candidates
        probs = map(self.p_words, candidates)
        coef = [0.95] + (len(probs)-1)*[0.05]
        final_probability = {' '.join(candidates[i]): probs[i]*coef[i] for i in range(len(probs))}
        return max(candidates, key=lambda x: final_probability[' '.join(x)])

    def __final_correction__(self, text):
        """
        Correccion de los fragmentos de texto sin numeros, usando dos metodos y eligiendo el que tiene mas posibilidades
        :param text: texto a corregir
        :return: correccion
        """
        p = re.compile('(\d+\.?\d *)')
        if text.isdigit() or p.match(text):
            return [text]
        norm_text = normalize_text(text)
        try:
            cor1 = list(self.correct_text(' '.join(self.joins(norm_text))))
            cor2 = self.joins(' '.join(self.correct_text(norm_text)))
        except RuntimeError:
            cor1 = self.__word_correction__(text)
            cor2 = cor1
        return max([cor1, cor2], key=self.p_words)

    def final_correction(self, text):
        """
        Devuelve la correccion final, para ello separa la frase con cuidado por los numeros y corrigiendo cada grupo
        de paralabras
        :param text: texto a corregir
        :return: texto corregido
        """
        numb_match = re.findall('[a-zA-Z]+\d[a-zA-Z]+', text)
        for match in numb_match:
            changed = re.sub('\d', '', match)
            text = text.replace(match, changed)
        by_numbers = re.split(r'(\d+(?:[.,]\d*)?)', text)
        correction = map(lambda x: self.__final_correction__(x), by_numbers)
        return list(itertools.chain.from_iterable(correction))
