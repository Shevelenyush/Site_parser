import requests
from bs4 import BeautifulSoup
import csv
import os

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 OPR/81.0.4196.60',
    'accept': '*/*'}
HOST = 'https://www.avito.ru'
FILE = 'cars.csv'


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all('span', class_='pagination-item-JJq_j')
    if pagination:
        return int(pagination[-2].get_text())
    else:
        return 1


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='iva-item-root-Nj_hb')

    cars = []
    for item in items:
        metro = item.find('div', class_='geo-root-H3eWU').find_all('span')[0]
        if metro:
            metro = metro.get_text()
            if metro == '':
                metro = item.find('div', class_='geo-root-H3eWU').find_all('span')[1]
                metro = metro.get_text()
        else:
            metro = 'Нет информации'
        cars.append({
            'title': item.find('div', class_='iva-item-titleStep-_CxvN').get_text(),
            'link': HOST + item.find('a', class_='link-link-MbQDP').get('href'),
            'price': item.find('meta', itemprop='price').get('content'),
            'metro': metro
        })

    return cars


def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Название', 'Ссылка', 'Цена', 'Местонахождение'])
        for item in items:
            writer.writerow([item['title'], item['link'], item['price'], item['metro']])


def parse():
    URL = input('Введите URL: ')
    URL = URL.strip()
    html = get_html(URL)
    if html.status_code == 200:
        cars = get_content(html.text)
        pages_count = get_pages_count(html.text)
        for page in range(1, pages_count + 1):
            print(f'Парсинг страницы {page} из {pages_count}...')
            html = get_html(URL, params={'page': page})
            cars.extend(get_content(html.text))
        save_file(cars, FILE)
        print(f'Получено {len(cars)} автомобилей')
        os.startfile(FILE)
    else:
        print('Error')


parse()
