import requests
from bs4 import BeautifulSoup
import json


def request_douban(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/88.0.4324.146 Safari/537.36',
    }

    try:
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            return response.text
    except requests.RequestException:
        return None


def parse_movies(soup):
    movies = []
    movie_list = soup.find(class_='grid_view').find_all('li')

    for item in movie_list:
        item_name = item.find(class_='title').string
        item_img = item.find('a').find('img').get('src')
        item_index = item.find(class_='').string
        item_score = item.find(class_='rating_num').string
        item_author = item.find('p').text
        if item.find(class_='inq') is not None:
            item_intr = item.find(class_='inq').string
        else:
            item_intr = 'NOT AVAILABLE'        

        print('爬取电影：' + item_index + ' | ' + item_name + ' | ' + item_score + ' | ' + item_intr)

        movie_data = {
            '名称': item_name,
            '图片': item_img,
            '排名': item_index,
            '评分': item_score,
            '作者': item_author.strip(),
            '简介': item_intr
        }
        
        movies.append(movie_data)
    
    return movies


def main(page):
    url = 'https://movie.douban.com/top250?start=' + str(page * 25) + '&filter='
    html = request_douban(url)
    if html:
        soup = BeautifulSoup(html, 'lxml')
        return parse_movies(soup)
    return []


if __name__ == '__main__':
    all_movies = []  # 存储所有电影数据的列表
    
    for i in range(0, 10):
        print(f'正在爬取第{i+1}页数据...')
        movies = main(i)
        all_movies.extend(movies)
        print(f'第{i+1}页获取到{len(movies)}部电影')

    # 将所有数据保存到data.json文件
    with open('douban_movies.json', 'w', encoding='UTF-8') as f:
        json.dump(all_movies, f, ensure_ascii=False, indent=2)
    
    print(f'数据爬取完成！总共获取到{len(all_movies)}部电影，已保存到douban_movies.json文件')