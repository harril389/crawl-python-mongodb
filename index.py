from bs4 import BeautifulSoup
import requests
import re
from pymongo import MongoClient


db_client = MongoClient('mongodb://localhost:27017/')

db = db_client['crawl-vnexpress']
cat_col = db["cat"]
sub_cat_col = db["sub_cat"]
article_col = db["article"]

url = 'https://vnexpress.net'


def get_cat(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    nav = soup.find('nav', attrs={'class': 'main-nav'})
    if nav != None:
        cats = nav.find_all('a')
        for item in cats:
            is_cat = re.search("^\/.*", item['href'])
            if is_cat:
                is_exists = cat_col.find_one({"href": item['href']})
                id_cat = ''
                if is_exists:
                    id_cat = is_exists['_id']
                if not is_exists:
                    new_cat = cat_col.insert_one(
                        {"name": item['title'], "href": item['href']})
                    if new_cat:
                        id_cat = new_cat.inserted_id
                get_sub_cat(item['href'], id_cat)

    print('done!')


def get_sub_cat(cat, id_cat):
    sub_page = requests.get(url + cat)
    soup_sub_page = BeautifulSoup(sub_page.text, 'html.parser')
    find_sub_cat = soup_sub_page.find(
        'ul', attrs={'class': 'ul-nav-folder'})
    if find_sub_cat != None:
        for item in find_sub_cat.find_all('a'):
            is_sub_cat = re.search("^\/.*", item['href'])
            if is_sub_cat:

                for num in range(2):
                    link = item['href']
                    id_sub_cat = ''
                    is_exists = sub_cat_col.find_one(
                        {"href": link})
                    if is_exists:
                        id_sub_cat = is_exists['_id']
                    if not is_exists:
                        new_sub_cat = sub_cat_col.insert_one(
                            {"name": item['title'], "href": link, 'id_cat': id_cat})
                        if new_sub_cat:
                            id_sub_cat = new_sub_cat.inserted_id

                    if num > 0:
                        link += "-p%s" % num
                    get_article_by_sub_cat(link, id_cat, id_sub_cat)


def get_article_by_sub_cat(sub_cat_page, id_cat, id_sub_cat):
    sub_page = requests.get(url + sub_cat_page)
    soup_sub_page = BeautifulSoup(sub_page.text, 'html.parser')
    article = soup_sub_page.find_all('article')
    for item in article:
        title_new = item.select_one('.title-news')
        if title_new != None:
            link = title_new.find('a')
            if link:
                get_detail_article(link['href'], id_cat, id_sub_cat)


def get_detail_article(link, id_cat, id_sub_cat):
    is_exists = article_col.find_one({"href": link})
    if not is_exists:
        article_detail = requests.get(link)
        soup_article_detail = BeautifulSoup(article_detail.text, 'html.parser')
        if soup_article_detail:
            title = ''
            title_soup = soup_article_detail.find(
                'h1', attrs={'class': 'title-detail'})
            if title_soup:
                title = title_soup.string
            description = ''
            description_soup = soup_article_detail.find(
                'p', attrs={'class': 'description'})
            if description_soup:
                description = description_soup.string
            content_soup = soup_article_detail.find_all(
                'p', attrs={'class': 'Normal'})
            thumbnail = soup_article_detail.find(
                'img', attrs={'itemprop': 'contentUrl'})
            thumbnail_url = ''
            if thumbnail != None:
                thumbnail_url = thumbnail['data-src']
            content = ''
            for text in content_soup:
                if text.string:
                    content += text.string + '\n'
            date = ''
            date_soup = soup_article_detail.find(
                'span', attrs={'class': 'date'})
            if date_soup:
                date = date_soup.string
            article_col.insert_one({"href": link, "title": title,
                                   'description': description, 'thumbnail_url': thumbnail_url, 'content': content, 'id_cat': id_cat, 'id_sub_cat': id_sub_cat, 'date': date})


get_cat(url)
