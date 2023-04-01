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
                if not is_exists:
                    cat_col.insert_one(
                        {"name": item['title'], "href": item['href']})
                get_sub_cat(item['href'])
    print('done!')


def get_sub_cat(cat):
    sub_page = requests.get(url + cat)
    soup_sub_page = BeautifulSoup(sub_page.text, 'html.parser')
    find_sub_cat = soup_sub_page.find(
        'ul', attrs={'class': 'ul-nav-folder'})
    if find_sub_cat != None:
        for item in find_sub_cat.find_all('a'):
            is_sub_cat = re.search("^\/.*", item['href'])
            if is_sub_cat:

                for num in range(10):
                    link = item['href']

                    is_exists = sub_cat_col.find_one(
                        {"href": link})
                    if not is_exists:
                        sub_cat_col.insert_one(
                            {"name": item['title'], "href": link})
                    if num > 0:
                        link += "-p%s" % num
                    get_article_by_sub_cat(cat, item['href'], link)


def get_article_by_sub_cat(cat, sub_cat, sub_cat_page):
    sub_page = requests.get(url + sub_cat_page)
    soup_sub_page = BeautifulSoup(sub_page.text, 'html.parser')
    article = soup_sub_page.find_all('article')
    for item in article:
        title_new = item.select_one('.title-news')
        if title_new != None:
            link = title_new.find('a')
            if link:
                get_detail_article(link['href'], cat, sub_cat)


def get_detail_article(link, cat, sub_cat):
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
            article_col.insert_one({"href": link, "title": title,
                                   'description': description, 'thumbnail_url': thumbnail_url, 'content': content, 'cat': cat, 'sub_cat': sub_cat})


get_cat(url)
