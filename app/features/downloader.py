import io
import re
import os
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
import tempfile


base_url = "https://cbr.ru/about_br/publ/god/"
cbr_home = "https://cbr.ru"


def get_links():
    """
    Возвращает ссылки, по которым доступны годовые отчеты на сайте ЦБ РФ

    :return: Словарь вида "год": "сслыка"
    :rtype: dict of string:string
    """

    response = requests.get(base_url)
    content = response.content.decode()
    soup = BeautifulSoup(content, features="lxml")
    tags = soup.find_all('a', {'class': 'versions_item'})
    links = {}
    for tag in tags:
        name = re.search(r'\d{4}', tag.text)[0]
        link = urljoin(cbr_home, tag.attrs['href'])
        links[name] = link

    return links


def get_pdf(link, year):
    """
    Загружает с сайта ЦБ отчет по переданной ссылке

    :param link: URL документа
    :type link: str
    :param year: Год отчета
    :type year: str/int

    :return: Имя сохраненного документа
    :rtype: str
    """

    response = requests.get(link, stream=True)
    fname = f"app/static/data/pdf/CBR_report{year}.pdf"
    if os.path.exists(fname):
        return fname
    with open(fname, "wb") as f:
        f.write(response.content)
    return fname


def get_txt(year):
    """
    Преобразует отчет из PDF в TXT

    :param year: Год отчета
    :type year: str/int

    :return: Имя преобразованного документа
    :rtype: str
    """

    fname = f"app/static/data/txt/CBR_report{year}.txt"
    if os.path.exists(fname):
        return fname

    pdf_fname = f"app/static/data/pdf/CBR_report{year}.pdf"
    with open(pdf_fname, 'rb') as f:
        pdf = io.BytesIO(f.read())

    report_txt = tempfile.TemporaryFile(mode='wb+')
    resource_manager = PDFResourceManager()
    converter = TextConverter(resource_manager, report_txt)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    for page in PDFPage.get_pages(pdf, caching=True, check_extractable=True):
        page_interpreter.process_page(page)
    converter.close()
    report_txt.seek(0)
    result = correct_file(report_txt.read().decode('utf8'))
    with open(fname, 'w', encoding='utf8') as f:
        f.write(result)
    return fname


def correct_file(text):
    """
    Фиксит проблемы, которые могут возникнуть при конвертации PDF в TXT
    :param text: Текст для коррекции
    :type text: str

    :return: None
    """

    result = ''
    for line in text:
        line = re.sub(r'\f', r'\n', line)
        line = re.sub(r'\(cid\:\d{1,2}\)', r'', line)
        line = re.sub(r'(\w)\-(\w)', r'\1\2', line)  # убираем дефисы переносов
        line = re.sub(r'([а-яёА-ЯЁa-zA-Z])([0-9])', r'\1 \2', line)  # отделяем от слов цифры с правой стороны
        line = re.sub(r'([0-9])([а-яёА-ЯЁa-zA-Z])', r'\1 \2', line)  # отделяем от слов цифры с левой стороны
        result += re.sub(r'([0-9а-яёa-z])([А-ЯЁA-Z]+)', r'\1 \2', line)  # разделяем слова с левой стороны
    return result
