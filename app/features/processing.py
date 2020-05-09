import re
import time
from collections import Counter
from functools import lru_cache
from multiprocessing import Pool
from multiprocessing import cpu_count

import matplotlib.pyplot as plt
import pymorphy2
import seaborn as sns
from nltk.corpus import stopwords

stop_words = stopwords.words('russian')
morph = pymorphy2.MorphAnalyzer()


def benchmark(func):
    """
    Декоратор, измеряющий время работы функции

    :param func: Декорируемая функция
    """

    def wrapper(*args, **kwargs):
        start = time.time()
        return_value = func(*args, **kwargs)
        end = time.time()
        print('[*] Время выполнения функции {}: {} секунд.'.format(func.__name__, end - start))
        return return_value

    return wrapper


@lru_cache(maxsize=10000000)
def normalize_word(word):
    """
    Получить нормальную форму одного слова на русском языке
    Пример:
        красивая -> красивый
        детей -> ребенок

    :param word: Слово
    :type word: str

    :return: Нормальная форма слова
    :rtype: str
    """

    return morph.normal_forms(word)[0]


def normalize_text(text):
    """
    Нормализовать все слова в заданном тексте

    :param text: Текст для нормализации
    :type text: str

    :return: Нормализованный текст
    :rtype: str
    """

    result = [normalize_word(word) for word in re.findall(r'[a-zа-яё]+',
                                                          text.lower())
              if word not in stop_words]
    return ' '.join(result)


def normalizer(year):
    """
    Нормализует файл отчета за определенный год и записывает его по пути
        app/static/data/norm/CBR_report<год>_norm.txt

    :param year: Год отчета
    :type year: str/int

    :return: None
    """

    fname = f'app/static/data/txt/CBR_report{year}.txt'
    with open(fname, 'r', encoding='utf8') as f:
        with Pool(processes=cpu_count()) as pool:
            normalized_text = '\n'.join(pool.map(normalize_text, f.readlines()))
    fname = f'app/static/data/norm/CBR_report{year}_norm.txt'
    with open(fname, 'w', encoding='utf8') as f:
        f.write(normalized_text)


def plot_freq_table(year):
    """
    Построить график самых частотных слов в отчете

    :param year: Год отчета
    :type year: str/int

    :return: График
    :rtype: matplotlib.pyplot.figure
    """

    counter = Counter()
    fname = f'app/static/data/norm/CBR_report{year}_norm.txt'
    with open(fname, 'r', encoding='utf8') as f:
        for i, line in enumerate(f, start=1):
            counter.update(line.split())
    vals = dict(counter.most_common(25))
    fig = plt.figure()
    ax = fig.add_subplot(111)
    sns.barplot(x=list(vals.keys()), y=list(vals.values()), ax=ax)
    plt.xticks(rotation='vertical')
    ax.set_title(f'Частота встречаемости слов в отчете {year} года')
    ax.set_ylabel('Количество вхождений')
    plt.tight_layout()
    fname = f'app/static/images/freq{year}.png'
    fig.savefig(fname)
    return fname


def plot_dict_size(year):
    """
    Построить график зависимости количества слов в отчете от размера словаря

    :param year: Год отчета
    :type year: str/int

    :return: График
    :rtype: matplotlib.pyplot.figure
    """

    fname = f'app/static/data/norm/CBR_report{year}_norm.txt'
    words = set()
    sizes = []
    num_words = 0
    with open(fname, 'r', encoding='utf8') as f:
        for line in f:
            for word in line.split():
                words.add(word)
                sizes.append(len(words))
                num_words += 1
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(range(num_words), sizes)
    ax.set_title('График зависимости количества слов в тексте от размера словаря')
    ax.set_xlabel('Количество слов в тексте')
    ax.set_ylabel('Размер словаря')
    plt.tight_layout()

    fname = f'app/static/images/dict{year}.png'
    fig.savefig(fname, dpi=300)
    return fname
