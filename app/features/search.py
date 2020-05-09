import re
from functools import lru_cache
from multiprocessing import Pool
from multiprocessing import cpu_count

from Levenshtein import distance
from nltk import SnowballStemmer

stemmer = SnowballStemmer('russian')


@lru_cache(maxsize=100000)
def stem_word(word):
    return stemmer.stem(word)


def stem_text(text):
    with Pool(processes=cpu_count()) as pool:
        result = pool.map(stem_word,
                          [word for word in re.findall(r'[a-zа-яё]+',
                                                       text.lower())
                           ])
    return result


@lru_cache(maxsize=100000)
def calculate_distance(word1, word2):
    return distance(word1, word2)


def full_text_search(search_request, text, metric='levenshtein', n_pad_words=5, exact=True):
    accuracy = int(not exact)
    search_request = search_request.strip()
    if not search_request:
        return None
    pattern = stem_text(search_request)
    splitted = [word for word in re.findall(r'[A-ZА-ЯЁa-zа-яё]+', text)]
    text = stem_text(text)
    end_position = None
    n = 0  # Номер слова в искомом паттерне
    pattern_length = len(pattern)
    search_word = pattern[n]
    phrase_start = False  # Флаг первого совпадения
    for i, word in enumerate(text):
        dist = calculate_distance(word, search_word)
        if phrase_start and dist > accuracy:
            phrase_start = False
            n = 0
            search_word = pattern[n]
            continue

        if dist <= accuracy:
            if n < pattern_length - 1:
                n += 1
                search_word = pattern[n]
                phrase_start = True
            else:
                end_position = i
                break

    if end_position is None:
        return None

    start_position = end_position - len(pattern) + 1
    start = start_position - n_pad_words
    end = end_position + n_pad_words
    if start < 0:
        start = 0
    if end > len(text):
        end = len(text)
    result = ' '.join(splitted[start:end+1])
    return result


def file_search(pattern, year, metric='levenshtein', n_pad_words=5, exact=True):
    fname = f'app/static/data/txt/CBR_report{year}.txt'
    with open(fname, encoding='utf8') as f:
        data = f.read()
        result = full_text_search(pattern, data, metric, n_pad_words, exact)
        return result
