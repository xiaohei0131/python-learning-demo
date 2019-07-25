import asyncio
import os
import time
from asyncio import Queue

import requests
from bs4 import BeautifulSoup

DIR = 'asyncpic-zipai'
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36"}
# 图片列表
pics = Queue()


async def download_page(cur_page):
    print('开始下载{}页'.format(cur_page))
    create_dir('{}/{}'.format(DIR, cur_page))
    url = 'https://www.mzitu.com/zipai/comment-page-{}/'.format(cur_page)
    r = requests.get(url, headers=headers)
    await get_pic_list(cur_page, r.text)
    # await asyncio.sleep(0.1)


async def get_pic_list(pgnum, html):
    soup = BeautifulSoup(html, 'html.parser')
    pic_list = soup.find_all('li', class_='comment')
    for i in pic_list:
        img_tag = i.find('div', class_='comment-body').find('img')
        pic_link = img_tag.get('data-original')  # 拿到图片的具体 url
        await pics.put((pgnum, pic_link))


async def save_file():
    while not pics.empty():
        pgnum, pic_link = await pics.get()
        print('下载第{}页，图片{}'.format(pgnum, pic_link))
        r = requests.get(pic_link, headers=headers)  # 下载图片，之后保存到文件
        with open('{}/{}/{}'.format(DIR, pgnum, pic_link.split('/')[-1]), 'wb') as f:
            f.write(r.content)
            # await asyncio.sleep(0.5)  # 休息一下，不要给网站太大压力，避免被封


def create_dir(name):
    if not os.path.exists(name):
        os.makedirs(name)


def execute():
    loop = asyncio.get_event_loop()
    # 获取所有待下载图片地址
    tasks = [download_page(cur_page) for cur_page in range(1, 21)]
    loop.run_until_complete(asyncio.wait(tasks))
    print(pics)
    # 开始下载图片
    save_tasks = [save_file() for _ in range(40)]
    loop.run_until_complete(asyncio.wait(save_tasks))
    loop.close()


def main():
    start_time = time.time()
    create_dir(DIR)
    execute()
    print('下载完成,cost', time.time() - start_time)


if __name__ == '__main__':
    main()
