import re
from bs4 import BeautifulSoup
from msedge.selenium_tools import Edge, EdgeOptions
from crawling_py.crawl_gushiwenwang_util import crawl_the_poetry
import os

options = EdgeOptions()
options.use_chromium = True
options.binary_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"  # 浏览器的位置
driver = Edge(options=options, executable_path=r"D:\edgeDriver\msedgedriver.exe")  # 相应的浏览器的驱动位置​
basic_url = "https://so.gushiwen.cn/search.aspx?value="
basic_url_1 = "https://so.gushiwen.cn/search.aspx?type=title&page="
basic_url_2 = "&value="
ground_url = "https://so.gushiwen.cn"

outputfile = open('../crawled_data/古诗文网/含有重复的.txt', mode='a', encoding='utf-8')


# 获取文件列表
def get_txtName(file_dir):
    L = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if os.path.splitext(file)[1] == '.txt':
                L.append(os.path.join(root, file))
    return L


def crawl_these_txt(dic_path):
    txt_list = get_txtName(dic_path)
    for file in txt_list:
        f = open(file, 'r', encoding='utf-8')
        lines = f.readlines()
        for line in lines:
            line = line.replace("・", " ").replace(" ", "+").replace("\n", "")
            search_url = basic_url + line
            crawl_search_result(search_url, line)


def crawl_every_page(url):  # 看该页有哪些诗
    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'lxml')
    except:
        print("2爬取失败")
        return
    alist = []
    father = soup.select("div.sons > div.cont > p")
    for item in father:
        a = item.find("a", href=re.compile("/shiwenv_[0-9a-z]*.aspx"))
        if a is not None:
            alist.append(a)
    print("该页有", len(alist), "首")
    for i in range(len(alist)):
        print("爬取该页第", i + 1, "首")
        back_url = alist[i].get("href")  # 获取到了该页的所有诗歌
        poetry_url = ground_url + back_url
        crawl_the_poetry(poetry_url, outputfile)


def crawl_search_result(url, line):  # 看该搜索结果有哪些页
    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'lxml')
    except:
        print("1爬取失败")
        return

    page_number = soup.select("form > div.pagesright > span")[0].text
    page_number = page_number.replace("\n", "").replace(" ", "")
    page_number = re.findall(r"\d+\.?\d*", page_number)[0]  # 搜索结果总共有几页
    print(line.replace("+", " "), " 的搜索结果有", page_number, "页")
    for i in range(1, int(page_number) + 1):
        print("当前是第", i, "页")
        search_result_url = basic_url_1 + str(i) + basic_url_2 + line
        crawl_every_page(search_result_url)


crawl_these_txt("../Chinese_poetry/作者_诗名")
outputfile.close()
