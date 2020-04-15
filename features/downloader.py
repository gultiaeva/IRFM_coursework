import io
import re
from functools import lru_cache
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage

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


@lru_cache(50)
def get_document(link, year):
    """
    Загружает с сайта ЦБ РФ отчет по переданной ссылке

    :param link: URL документа
    :type link: str
    :param year: Год отчета
    :type year: str/int

    :return: Имя сохраненного документа
    :rtype: str
    """

    response = requests.get(link, stream=True)
    pdf = io.BytesIO(response.content)
    fname = f"data/CBR_report{year}.txt"
    report_txt = open(fname, "wb+")
    resource_manager = PDFResourceManager()
    converter = TextConverter(resource_manager, report_txt)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    for page in PDFPage.get_pages(pdf, caching=True, check_extractable=True):
        page_interpreter.process_page(page)
    converter.close()
    report_txt.close()
    return fname

