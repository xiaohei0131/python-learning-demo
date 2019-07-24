import os
import threading
import time
from queue import Queue

import requests
from bs4 import BeautifulSoup

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36"}
queue = Queue()
for i in range(1, 21):  # 下载第一页到20页图片
    queue.put(i)


def download_page(url):
    r = requests.get(url, headers=headers)
    return r.text


def get_pic_list(pgnum, html):
    soup = BeautifulSoup(html, 'html.parser')
    pic_list = soup.find_all('li', class_='comment')
    for i in pic_list:
        img_tag = i.find('div', class_='comment-body').find('img')
        pic_link = img_tag.get('data-original')  # 拿到图片的具体 url
        print('下载第{}页，图片{}'.format(pgnum, pic_link))
        r = requests.get(pic_link, headers=headers)  # 下载图片，之后保存到文件
        create_dir('pic/{}'.format(pgnum))
        with open('pic/{}/{}'.format(pgnum, pic_link.split('/')[-1]), 'wb') as f:
            f.write(r.content)
            time.sleep(1)  # 休息一下，不要给网站太大压力，避免被封


def create_dir(name):
    if not os.path.exists(name):
        os.makedirs(name)


def execute():
    while not queue.empty():
        cur_page = queue.get()
        print('{}正在下载{}页'.format(threading.current_thread().name, cur_page))
        url = 'https://www.mzitu.com/zipai/comment-page-{}/'.format(cur_page)
        page_html = download_page(url)
        get_pic_list(cur_page, page_html)


def main():
    create_dir('pic')
    threads = []
    while len(threads) < 5:  # 最大线程数设置为 5
        thread = threading.Thread(target=execute)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    print("下载完成")


if __name__ == '__main__':
    main()
