from urllib import request
from bs4 import BeautifulSoup
import requests

headers = [
    ('Content-Type', 'application/json;charset=UTF-8'),
    ('User-Agent',
     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.44')
]
opener = request.build_opener()
opener.addheaders = headers
request.install_opener(opener)

requests_headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.44'
}


def get_content(url):
    # 如果慢的话，关闭代理。
    try:
        return request.urlopen(url).read().decode('UTF-8')
    except:
        # 上面的方法报错时调用
        return requests.get(url, headers=requests_headers).text


def init_bs(url):
    con = get_content(url)
    return BeautifulSoup(con, 'lxml')


def get_text(element):
    return element.get_text().strip()


def find_element(element, class_obj, class_name=''):
    return element.find(class_obj, attrs={'class': class_name})


def find_elements(element, class_obj, class_name=''):
    return element.find_all(class_obj, attrs={'class': class_name})


def select_elements(element, xpath_str):
    # element.select('div.short-field-item > div > p.short-field-title')
    return element.select(xpath_str)
