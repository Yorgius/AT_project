
from bs4 import BeautifulSoup
from tqdm import tqdm
import requests

from datetime import datetime


SITES = [
    {"title": "nitti",
    "url": "https://nitti.by/catalog/pryazha_1/26470/?oid=23622",
    "selector": ".info_item span.price_value"},
    
    {"title": "leonardo",
    "url": "https://leonardohobby.by/ishop/group_6157356002/",
    "selector": ".actual-price"},
    
    {"title": "klubok",
    "url": "https://1klubok.by/pryazha-pehorka/detskaya-novinka",
    "selector": "td.price-amount"},

    {"title": "yarnstore",
    "url": "https://yarnstore.by/products/detskaya-novinka-pehorka",
    "selector": ".tab-content div.price span"},

    # {"title": "https://kupimotok.by/",
    # "url": "",
    # "selector": ""},

    {"title": "zigzagshop",
    "url": "https://zigzagshop.by/pryazha-pehorskaya-pt/16005-26369-detskaya-novinka.html#/14618-cvet-011_yarrozovyj",
    "selector": ".product-price-value > .product-price-col:nth-child(2) span"},

    {"title": "петелька",
    "url": "https://xn--80ajauevw6f.xn--90ais/p103514576-detskaya-novinka.html",
    "selector": ".b-product-cost__price span:first-child"},

    {"title": "kis",
    "url": "https://kis.by/pryazha-detskaya-novinka-1-motka-50g-200m-pekhorka-18-persik",
    "selector": ".price > span"},

    {"title": "miya",
    "url": "https://miya.by/p106143454-pryazha-pehorka-detskaya.html",
    "selector": ".b-product-cost__price span"},
]

class MagicSoup:
    def __init__(self, url: str, selector: str) -> None:
        self.url = url
        self.selector = selector

    def cook_soup(self) -> None:
        html_text = requests.get(self.url).text
        soup = BeautifulSoup(html_text, 'lxml')

        if soup.select(self.selector):
            self.price = soup.select(self.selector)[0].text[:4]
            if self.is_price_correct():
                self.price = self.correct_comma_to_dot()
            self.price = self.convert_price_to_float()
        else:
            self.price = 0

    # проверка на наличие в price символа <,>
    def is_price_correct(self) -> bool:
        return ',' in self.price

    # исправление символа <,> на <.>
    def correct_comma_to_dot(self) -> str:
        return self.price.replace(',', '.')

    # конвертация строкового значения price в float
    def convert_price_to_float(self) -> float:
        return float(self.price)

    # возврат итогового набора значений
    def tasting(self) -> float:
        self.cook_soup()
        if self.price:
            return self.price
        else:
            return 0

def magic_soup() -> list:
    data_set = []
    for site in tqdm(SITES, desc='fetching data...', colour='green'):
        data_set.append({'shop_name': site.get('title'), \
            'shop_url': site.get('url'), 
            'yarn_name': 'Pehorka', 
            'yarn_price': MagicSoup(site.get('url', ''), site.get('selector', '')).tasting()})
    return data_set
    # return [MagicSoup(*site.values()).tasting() for site in tqdm(SITES, 'fetching data...', colour='green')]

if __name__ == '__main__':
    for data_element in magic_soup():
        print(data_element)