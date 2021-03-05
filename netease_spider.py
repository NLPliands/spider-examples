import requests
from bs4 import BeautifulSoup
import json
import re
import multiprocessing
import xlwt
import time

def netease_spider(headers, news_class, i):

    if i == 1:
        url = "https://temp.163.com/special/00804KVA/cm_{0}.js?callback=data_callback".format(news_class)
    else:
        url = 'https://temp.163.com/special/00804KVA/cm_{0}_0{1}.js?callback=data_callback'.format(news_class, str(i))
    pages = []
    try:
        response = requests.get(url, headers=headers).text
    except:
        print("当前主页面爬取失败")
        return
    start = response.index('[')
    end = response.index('])') + 1
    data = json.loads(response[start:end])
    try:
        for item in data:
            title = item['title']
            docurl = item['docurl']
            label = item['label']
            source = item['source']
            doc = requests.get(docurl, headers=headers).text
            soup = BeautifulSoup(doc, 'lxml')
            news = soup.find_all('div', class_='post_body')[0].text
            news = re.sub('\s+', '', news).strip()
            pages.append([title, label, source, news])
            time.sleep(3)

    except:
        print("当前详情页面爬取失败")
        pass

    return pages


def run(news_class, nums):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36'}
    tmp_result = []
    for i in range(1, nums + 1):
        tmp = netease_spider(headers, news_class, i)
        if tmp:
            tmp_result.append(tmp)

    return tmp_result


if __name__ == '__main__':

    book = xlwt.Workbook(encoding='utf-8')
    sheet = book.add_sheet('网易新闻数据')
    sheet.write(0, 0, '文章标题')
    sheet.write(0, 1, '文章标签')
    sheet.write(0, 2, '文章来源')
    sheet.write(0, 3, '文章内容')

    news_calsses = {'guonei', 'guoji'}
    nums = 3
    index = 1
    pool = multiprocessing.Pool(30)
    for news_class in news_calsses:
        result = pool.apply_async(run, (news_class, nums))
        for pages in result.get():
            for page in pages:
                if page:
                    title, label, source, news = page
                    sheet.write(index, 0, title)
                    sheet.write(index, 1, label)
                    sheet.write(index, 2, source)
                    sheet.write(index, 3, news)
                    index += 1
    pool.close()
    pool.join()
    print("共爬取{0}篇新闻".format(index))
    book.save(u"网易新闻爬虫结果.xls")
