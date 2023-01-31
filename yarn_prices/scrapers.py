
from bs4 import BeautifulSoup
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

    # {"title": "yarnstore",
    # "url": "https://yarnstore.by/products/detskaya-novinka-pehorka",
    # "selector": ""},

    # {"title": "https://kupimotok.by/",
    # "url": "",
    # "selector": ""},

    # {"title": "zigzagshop",
    # "url": "https://zigzagshop.by/pryazha-pehorskaya-pt/16005-26369-detskaya-novinka.html#/14618-cvet-011_yarrozovyj",
    # "selector": ""},

    # {"title": "петелька",
    # "url": "https://xn--80ajauevw6f.xn--90ais/p103514576-detskaya-novinka.html",
    # "selector": ""},

    # {"title": "kis",
    # "url": "https://kis.by/pryazha-detskaya-novinka-1-motka-50g-200m-pekhorka-18-persik",
    # "selector": ""},

#     {"title": "miya",
#     "url": "https://miya.by/g8001755-pryazha-pehorka-detskaya",
#     "selector": ""},
]


class MagicSoup:
    def __init__(self, title: str, url: str, selector: str) -> None:
        self.title = title
        self.url = url
        self.selector = selector

    def cook_soup(self) -> None:
        html_text = requests.get(self.url).text
        soup = BeautifulSoup(html_text, 'lxml')
        
        self.price = soup.select(self.selector)[0].text[:4]
        if self.is_price_correct():
            self.correct_comma_to_dot()

    def is_price_correct(self) -> bool:
        return ',' in self.price

    def correct_comma_to_dot(self) -> str:
        return self.price.replace(',', '.')

    def tasting(self) -> list:
        return [self.title, self.price]

        
def magic_soup() -> list:
    dataset = []
# данные для скрейпинга
    for site in SITES:
        soup = MagicSoup(*site.values())
        soup.cook_soup()
        dataset.append(soup.tasting())
    return dataset
        

if __name__ == '__main__':
    time_start = datetime.now()
    print(magic_soup())
    timer = datetime.now() - time_start
    print(f"timer: {str(timer): >15}")