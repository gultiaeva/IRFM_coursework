import re
from functools import lru_cache
from multiprocessing import Pool
from multiprocessing import cpu_count

from Levenshtein import distance
from nltk import SnowballStemmer

stemmer = SnowballStemmer('russian')


@lru_cache(maxsize=100000)
def stem_word(word):
    """
    Стеммировать отдельное слово

    :param word: Слово для стемминга
    :type word: str

    :return: Основа слова
    :rtype: str
    """

    return stemmer.stem(word)


def stem_text(text):
    """
    Стеммировать все слова в тексте

    :param text: Текст для обработки
    :type text: str

    :return: Список из основ всех слов в тексте в порядке следования
    :rtype: list
    """

    with Pool(processes=cpu_count()) as pool:
        result = pool.map(stem_word,
                          [word for word in re.findall(r'[a-zа-яё]+',
                                                       text.lower())
                           ])
    return result


@lru_cache(maxsize=100000)
def levenshtein_distance(word1, word2):
    """
    Вычислить расстояние Левенштекна для двух слов

    :return: Рассточние Левенштейна
    :rtype: int
    """

    return distance(word1, word2)


def full_text_search(search_request, text, metric='levenshtein', n_pad_words=5, exact=True):
    """
    Полнотекстовый поиск по тексту

    :param search_request: Поисковый запрос
    :type search_request: str
    :param text: Текст, в котором осуществляется поиск
    :type text: str
    :param metric: Метрика рассчета близости слов default=levenshtein
    :type metric: str
    :param n_pad_words: Количество слов,
                        которое необходимо вернуть до и после найденного фрагмента
    :type n_pad_words: int
    :param exact: Флаг точного совпадения
    :type exact: bool

    :return: Найденный фрагмент текста с указанным количеством слов до и после,
             если такой фрагмент найден, и None -- если не найден
    :rtype: str
    """

    assert metric in ['levenshtein']
    if metric == 'levenshtein':
        calculate_distance = levenshtein_distance

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
    """
    Функция-обертка. Полнотекстовый поиск по файлу отчета

    :param pattern: Поисковый запрос
    :type pattern: str
    :param year: Год отчета
    :type year: str/int
    :param metric: Метрика рассчета близости слов default=levenshtein
    :type metric: str
    :param n_pad_words: Количество слов,
                        которое необходимо вернуть до и после найденного фрагмента
    :type n_pad_words: int
    :param exact: Флаг точного совпадения
    :type exact: bool

    :return: Результат выполнения понотекстового поиска по отчету
    :rtype: str
    """

    fname = f'app/static/data/txt/CBR_report{year}.txt'
    with open(fname, encoding='utf8') as f:
        data = f.read()
        result = full_text_search(pattern, data, metric, n_pad_words, exact)
        return result
