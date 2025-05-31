import requests
import re
import json
import pandas as pd


def request_dandan(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    except requests.RequestException as e:
        print(e)
        return None


def parse_result(html):
    pattern = re.compile(
        '<li.*?list_num.*?(\d+)\.</div>.*?<img src="(.*?)".*?class="name".*?title="(.*?)">.*?class="star">.*?class="tuijian">(.*?)</span>.*?class="publisher_info">.*?target="_blank">(.*?)</a>.*?class="biaosheng">.*?<span>(.*?)</span></div>.*?<p><span class="price_n">(.*?)</span>.*?</li>', re.S)
    items = re.findall(pattern, html)

    for item in items:
        yield {
            'range': item[0],
            'image': item[1],
            'title': item[2],
            'recommend': item[3],
            'author': item[4],
            'times': item[5],
            'price': item[6]
        }


def main(page):
    url = 'http://bang.dangdang.com/books/fivestars/01.00.00.00.00.00-recent30-0-0-1-' + str(page)
    html = request_dandan(url)
    if html:
        items = parse_result(html)  # 解析过滤我们想要的信息
        return list(items)
    return []


if __name__ == "__main__":
    all_books = []  # 存储所有图书数据的列表
    
    for i in range(1, 26):
        print(f'正在爬取第{i}页数据...')
        books = main(i)
        all_books.extend(books)
        print(f'第{i}页获取到{len(books)}本书')
    
    # 将所有数据保存到data.json文件
    with open('book.json', 'w', encoding='UTF-8') as f:
        json.dump(all_books, f, ensure_ascii=False, indent=2)
    
    print(f'数据爬取完成！总共获取到{len(all_books)}本书，已保存到book.json文件')