import re
import time
import requests
import telebot
import pandas as pd
from bs4 import BeautifulSoup
from auth_data import token


def collect_categories():
    r = requests.get('https://en.hostistanbulfair.com/2023-exhibitor-list.html')
    soup = BeautifulSoup(r.content, 'html.parser')
    categories_list = soup.find(id='MainProductCategories').text

    categories = categories_list.replace('\n', ',').split(',')
    categories.pop(-1)
    del categories[0:2]

    return categories


def collect_urls(categories):
    all_urls = {}
    for i in range(len(categories))[:]:
        all_urls[categories[i]] = []
        r_pag = requests.get(
            f'https://en.hostistanbulfair.com/2023-exhibitor-list.html?search=&MainProductCategories={i + 1}&ProductCategories=&CompanyType=&Countries=&Halls=&letter=')
        soup = BeautifulSoup(r_pag.content, 'html.parser')
        last_page = soup.find('div', class_='pagination').find_all('a')[-2].text
        for k in range(int(last_page))[:]:
            print(f'Категория {categories[i]}, стр {k + 1}')
            time.sleep(1)
            r = requests.get(
                f'https://en.hostistanbulfair.com/2023-exhibitor-list.html?p={k + 1}&search=&MainProductCategories={i + 1}&ProductCategories=&CompanyType=&Countries=&Halls=&letter=')
            soup = BeautifulSoup(r.content, 'html.parser')
            url_list = soup.find('ul', class_='katilimciListesiBlok')
            url_list = url_list.find_all('a')
            for item in url_list[:]:
                all_urls[categories[i]].append('https://en.hostistanbulfair.com/' + item.get('href'))

    return all_urls


def collect_info(all_urls):
    writer = pd.ExcelWriter('data.xlsx', engine='xlsxwriter')
    cat_sheets = {}
    for item in all_urls.keys():
        print(item)
        sellers_list = all_urls[item]
        sheet = {
            'Наименование': [],
            'Адрес': [],
            'Телефон': [],
            'Факс': [],
            'Сайт': [],
            'Почта': [],
        }
        for i in range(len(sellers_list))[:]:
            res = requests.get(sellers_list[i])
            soup = BeautifulSoup(res.content, 'html.parser')
            name = soup.find('section', class_='main').text.strip().replace('\n', '').replace('\t', '')
            contact_info = soup.find(class_='row ekbilgiler').find_all(class_='col')[-1].find_all('p')

            # print(name)
            # print(contact_info[0].text.strip())
            info_list = contact_info[1].text.replace('\n', ', ').replace('\t', '').strip().split(',')
            # print(info_list)

            sheet['Наименование'].append(str(name))
            sheet['Адрес'].append(contact_info[0].text.strip().replace('\n', ' ').replace('\t', '').replace('\r', ''))
            sheet['Телефон'].append(info_list[0].replace('Tel:', ''))
            sheet['Факс'].append(info_list[1].replace(' Fax: ', ''))
            sheet['Сайт'].append(info_list[5].replace(' Web: ', '').replace('.tr', ''))
            sheet['Почта'].append(info_list[6].replace(' E-Mail: ', '').replace('.tr', ''))

        sheet = pd.DataFrame(sheet)
        cat_sheets[item] = sheet
        cat_sheets[item].to_excel(writer, sheet_name=re.sub("[:*?/]", "", item)[:30], index=False)

    writer.close()

    return 'data.xlsx'


def full_collect():
    categories = collect_categories()
    all_urls = collect_urls(categories)
    file = collect_info(all_urls)

    return file


if __name__ == '__main__':
    categories = collect_categories()
    all_urls = collect_urls(categories)
    collect_info(all_urls)
