 #coding=utf-8
import requests
import re
import json
import importlib
import os
dbUtils = importlib.import_module('mysqlDBUtils')

# 定义图片存储位置
global save_path
save_path = 'D:/doubanfilm'


# 创建文件夹
def createFile(file_path):
    if os.path.exists(file_path) is False:
        os.makedirs(file_path)
    # 切换路径至上面创建的文件夹
    os.chdir(file_path)


def parse_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0"}
    response = requests.get(url, headers=headers)
    text = response.text
    regix = '<div class="pic">.*?<em class="">(.*?)</em>.*?<img.*?src="(.*?)" class="">.*?div class="info.*?class="hd".*?class="title">(.*?)</span>.*?class="other">' \
            '(.*?)</span>.*?<div class="bd">.*?<p class="">(.*?)<br>(.*?)</p>.*?class="star.*?<span class="(.*?)"></span>.*?' \
            'span class="rating_num".*?average">(.*?)</span>'
    results = re.findall(regix, text, re.S)
    mysql = dbUtils.MyPymysqlPool("dbMysql")
    for item in results:
        filepath = down_image(item[1],headers = headers)
        print("文件路径"+filepath)
        print(item)
        # item[2] 电影主流名字 item[3] 电影别名
        film_name =  item[2] + ' ' + re.sub('&nbsp;','',item[3])
        info = re.sub('&nbsp;','',item[4].strip()).split(":")
        # 导演
        director = info[1].split('主')[0]
        # 主演
        print(len(info))
        if len(info) > 2:
            actor = info[2]
        else:
            actor = "..."
        score_mark = star_transfor(item[6].strip()) + '/' + item[7] + '分'
        rank_num = item[0]
        print(film_name)
        # 写sql 语句
        sql = 'insert into film (film_name,director,actor,score_mark,rank_num,filepath) value("' + film_name + '","' + director + '","' + actor + '","' + score_mark + '","' + rank_num + '","'+filepath+'")'
        # 执行插入
        result = mysql.insert(sql)
        yield {
            '电影名称' : film_name,
            '导演和演员' :  director,
            '评分': score_mark,
            '排名' : rank_num
        }
    mysql.dispose()
def main():
    for offset in range(0, 250, 25):
        url = 'https://movie.douban.com/top250?start=' + str(offset) +'&filter='
        for item in parse_html(url):
            # 将每个条目写入txt
            write_movies_file(item)

def write_movies_file(str):
    with open('douban_film.txt','a',encoding='utf-8') as f:
        f.write(json.dumps(str,ensure_ascii=False) + '\n')

def down_image(url,headers):
    r = requests.get(url,headers = headers)
    createFile(save_path)
    filepath = save_path +'/'+ re.search('/public/(.*?)$', url, re.S).group(1)
    print("下载的海报名字"+filepath)
    with open(filepath,'wb') as f:
         f.write(r.content)
    return filepath
def star_transfor(str):
    if str == 'rating5-t':
        return '五星'
    elif str == 'rating45-t' :
        return '四星半'
    elif str == 'rating4-t':
        return '四星'
    elif str == 'rating35-t' :
        return '三星半'
    elif str == 'rating3-t':
        return '三星'
    elif str == 'rating25-t':
        return '两星半'
    elif str == 'rating2-t':
        return '两星'
    elif str == 'rating15-t':
        return '一星半'
    elif str == 'rating1-t':
        return '一星'
    else:
        return '无星'

if __name__ == '__main__':
    main()
