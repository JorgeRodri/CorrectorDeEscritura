# -*- coding: utf8 -*-
from collections import Counter
from engine.utils import normalize_text
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from ngramUtils import zipngram
from itertools import chain
import re


def edits_tildes(word):
    split = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    a = [L + u'á' + R[1:] for L, R in split if R and R[0] == 'a']
    e = [L + u'é' + R[1:] for L, R in split if R and R[0] == 'e']
    i = [L + u'í' + R[1:] for L, R in split if R and R[0] == 'i']
    o = [L + u'ó' + R[1:] for L, R in split if R and R[0] == 'o']
    u = [L + u'ú' + R[1:] for L, R in split if R and R[0] == 'u']
    return a + e + i + o + u


def edits0(word):
    split = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    ache = [L + 'h' + R for L, R in split]
    uve = [L + 'v' + R[1:] for L, R in split if R and R[0] == 'b']
    be = [L + 'b' + R[1:] for L, R in split if R and R[0] == 'v']
    ge = [L + 'g' + R[1:] for L, R in split if R and R[0] == 'j']
    jot = [L + 'j' + R[1:] for L, R in split if R and R[0] == 'g']
    ere = [L + 'r' + R for L, R in split if L and R and L[-1] == 'r' and R[0] != 'r' and L[-2:] != 'rr' and len(L) > 1]
    ll = [L + 'y' + R[2:] for L, R in split if R if R[:2] == 'll']
    y = [L + 'll' + R[1:] for L, R in split if R if R[0] == 'y']
    # tildes = edits_tildes(word)
    return set(ache + uve + be + jot + ge + ere + ll + y)


def edits1(word):
    """All edits that are one edit away from `word`."""
    letters = 'abcdefghijklmnopqrstuvwxyz'
    split = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in split if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in split if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in split if R for c in letters]
    inserts = [L + c + R for L, R in split for c in letters]
    return set(deletes + transposes + replaces + inserts)


def edits2(word):
    """All edits that are two edits away from `word`."""
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))


def product(nums):
    """Multiply the numbers together.  (Like `sum`, but with multiplication.)"""
    result = 1
    for x in nums:
        result *= x
    return result


def memo(f):
    """Memoize function f, whose args must all be hashable."""
    cache = {}

    def fmemo(*args):
        if args not in cache:
            cache[args] = f(*args)
        return cache[args]
    fmemo.cache = cache
    return fmemo


def splits(text, start=0, s=20):
    """Return a list of all (first, rest) pairs; start <= len(first) <= L."""
    return [(text[:i], text[i:])
            for i in range(start, min(len(text), s)+1)]


def n_grams(text, n=None):
    search_list = text.split()
    search_list = [word for word in search_list if word not in stopwords.words('Spanish') + stopwords.words('English')]
    if n is None:
        n = len(search_list)-1
    if n == 0:
        return ['']
    elif n > len(search_list):
        return [' '.join(search_list)]
    return [' '.join(search_list[i:i+n]) for i in range(len(search_list)-n+1)]


def get_texts(text):
    text = text.apply(normalize_text)
    text = word_tokenize(' '.join(text.values))
    return text


class BiCorrector:
    def __init__(self, big_text, min_count=2):
        self.WORDS = Counter(big_text)
        self.BIGRAMS = Counter(zipngram(' '.join(big_text)))
        print(self.BIGRAMS.most_common(50))
        self.__total__ = sum(self.WORDS.values())
        self.__bigramtotal__ = sum(self.BIGRAMS.values())
        self.min = min_count

    def p(self, word):
        """Probability of `word`."""
        return float(self.WORDS[word]) / self.__total__

    def pngram(self, first, second):
        """Probability of `word`."""
        return float(self.BIGRAMS[(first, second)]) / self.WORDS[second] if self.WORDS[second] >= self.min else 0

    def pn_last_gram(self, first, second):
        """Probability of `word`."""
        return float(self.BIGRAMS[(first, second)]) / self.WORDS[first] if self.WORDS[first] >= self.min else 0

    def __candidates_n_grams__(self, word, next_word):
        """Generate possible spelling corrections for word."""
        return set([word] if (word, next_word) in self.BIGRAMS else []) \
            or set(w for w in edits0(word) if (w, next_word) in self.BIGRAMS) \
            or set(w for w in edits1(word) if (w, next_word) in self.BIGRAMS) \
            or set(w for w in edits2(word) if (w, next_word) in self.BIGRAMS)

    def __reverse_n_gram_candidates__(self, word, previous):
        return set([word] if (previous, word) in self.BIGRAMS else [])\
               or set(w for w in edits0(word) if (previous, w) in self.BIGRAMS) \
               or set(w for w in edits1(word) if (previous, w) in self.BIGRAMS) \
               or set(w for w in edits2(word) if (previous, w) in self.BIGRAMS)

    def __candidates__(self, word):
        """Generate possible spelling corrections for word."""
        return self.__known__([word]) \
            or self.__known__(edits0(word)) \
            or self.__known__(edits1(word)) \
            or self.__known__(edits2(word)) \
            or [word]

    def __known__(self, words):
        """The subset of `words` that appear in the dictionary of WORDS and BIGRAMS."""
        return set(w for w in words if w in self.WORDS and self.WORDS[w] >= self.min)

    def p_words(self, words):
        """Probability of words, assuming each word is independent of others."""
        return product(self.p(w) for w in words)

    @memo
    def __segment__(self, text):
        """Return a list of words that is the most probable segmentation of text."""
        if not text:
            return []
        else:
            candidates = [[first] + self.__segment__(rest)
                          for (first, rest) in splits(text, 1)]
            return max(candidates, key=self.p_words)

    def true_segment(self, word):
        candidates = self.__segment__(word)
        return ' '.join(candidates)
        # return list(filter(lambda x: len(x) > 1, candidates))

    def correction(self, word):
        """Most probable spelling correction for word."""
        c = self.__candidates__(word)
        if len(c) == 1 and not self.__known__(c):
            return self.true_segment(c[0])
        return max(c, key=self.p)

    def joins(self, text):
        word_list = text.split()
        candidates = [word_list[:i] + [''.join(word_list[i:i+w])] + word_list[i+w:]
                      for i in range(len(word_list)-1)
                      for w in range(2, len(word_list)-i+1)]
        candidates += [word_list]
        probs = map(self.p_words, candidates)
        coef = (len(probs)-1)*[0.1] + [0.9]
        final_probability = {' '.join(candidates[i]): probs[i]*coef[i] for i in range(len(probs))}
        return max(candidates, key=lambda x: final_probability[' '.join(x)])

    def bi_correction(self, word, next_word):
        c = self.__candidates_n_grams__(word, next_word)
        if c:
            return max(c, key=lambda x: self.pngram(x, next_word))
        else:
            return self.correction(word)

    def bi_last_correct(self, word, previous):
        c = self.__reverse_n_gram_candidates__(word, previous)
        if c:
            return max(c, key=lambda x: self.pn_last_gram(previous, x))
        else:
            return self.correction(word)

    def final_correct(self, text):
        word_list = normalize_text(text).split()
        if len(word_list) == 1:
            return self.correction(word_list[0])
        else:
            sentence = [self.bi_correction(word, next_word)
                        for (word, next_word) in zip(*[word_list[i:] for i in range(2)])]
            sentence += [self.bi_last_correct(word_list[-1], sentence[-1])]
            return ' '.join(sentence)

    def __final_correct__(self, text):
        # TODO as in the corrector for the treatment of numbers and special cases

        p = re.compile('(\d+\.?\d *)')
        if text.isdigit() or p.match(text):
            return text

        word_list = normalize_text(text).split()
        if len(word_list) == 1:
            return self.correction(word_list[0])
        else:
            sentence = [self.bi_correction(word, next_word)
                        for (word, next_word) in zip(*[word_list[i:] for i in range(2)])]
            sentence += [self.bi_last_correct(word_list[-1], sentence[-1])]
            return ' '.join(sentence)

    def numb_treatment(self, text):
        numb_match = re.findall('[a-zA-Z]+\d[a-zA-Z]+', text)
        for match in numb_match:
            changed = re.sub('\d', '', match)
            text = text.replace(match, changed)
        by_numbers = re.split(r'(\d+(?:[.,]\d*)?)', text)
        correction = map(lambda x: self.__final_correct__(x), by_numbers)
        print(correction)
        return ' '.join(correction)
