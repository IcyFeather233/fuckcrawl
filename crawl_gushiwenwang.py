import re
from bs4 import BeautifulSoup
from selenium import webdriver
from msedge.selenium_tools import Edge, EdgeOptions
from selenium.common.exceptions import NoSuchElementException

import os

options = EdgeOptions()
options.use_chromium = True
options.binary_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"  # 浏览器的位置
driver = Edge(options=options, executable_path=r"D:\edgedriver_win64\msedgedriver.exe")  # 相应的浏览器的驱动位置​
basic_url = "https://so.gushiwen.cn/search.aspx?value="
basic_url_1 = "https://so.gushiwen.cn/search.aspx?type=title&page="
basic_url_2 = "&value="
ground_url = "https://so.gushiwen.cn"


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


def crawl_the_poetry(url):  # 爬该首诗的所有信息
    try:
        driver.get(url)
        poetry_soup = BeautifulSoup(driver.page_source, 'html.parser')
    except:
        print("3爬取失败")
        return

    poetry_dict = {"诗名": "", "朝代": "", "作者": "", "原文": "", "翻译": "", "注释": "", "鉴赏": "", "新解": "", "创作背景": ""}
    # 找标题
    title = poetry_soup.select("#sonsyuanwen > div.cont > h1")[0].text
    print("标题：" + title)
    poetry_dict['诗名'] = title
    author = poetry_soup.select("#sonsyuanwen > div.cont > p > a:nth-child(1)")[0].text
    print("作者：" + author)
    poetry_dict['作者'] = author
    dynasty = poetry_soup.select("#sonsyuanwen > div.cont > p > a:nth-child(2)")[0].text[1:-1]
    print("朝代：" + dynasty)
    poetry_dict['朝代'] = dynasty
    # 原文
    temp_content1 = poetry_soup.select("#sonsyuanwen > div.cont > div.contson")[0]
    temp_content2 = str(temp_content1)[47:-11].strip().replace("<p>", "").replace("</p>", "|").replace("<br/>", "|").replace("\n", "")
    # 把括号去掉
    no_bracket_content = re.sub(u"\\(.*?\\)|\\{.*?}|\\[.*?]", "", temp_content2)
    content = no_bracket_content + "|"
    print("原文：" + content)
    # 译文
    try:
        input = driver.find_element_by_xpath('//*[@alt="译文"]')
        input.click()
    except:
        print("没有译文按钮")

    poetry_soup = BeautifulSoup(driver.page_source, 'html.parser')
    raw_yiwen = poetry_soup.select("#sonsyuanwen > div.cont > div.contson > p > span")
    yiwen = ""
    for each in raw_yiwen:
        yiwen += each.text + "|"
    print("译文：" + yiwen)
    # 注释
    try:
        input = driver.find_element_by_xpath('//*[@alt="注释"]')
        input.click()
    except:
        print("没有注释按钮")

    # 取消掉
    try:
        input = driver.find_element_by_xpath('//*[@alt="译文2"]')
        input.click()
    except:
        print("没有取消译文按钮")

    poetry_soup = BeautifulSoup(driver.page_source, 'html.parser')
    raw_zhushi = poetry_soup.select("#sonsyuanwen > div.cont > div.contson > p > span")
    zhushi = ""
    for each in raw_zhushi:
        zhushi += each.text + "|"
    print("注释：" + zhushi)
    # 点开“展开阅读全文”
    try:
        buttons = driver.find_elements_by_link_text("展开阅读全文 ∨")
        for button in buttons:
            button.click()
    except:
        print("没有展开全文按钮")

    poetry_soup = BeautifulSoup(driver.page_source, 'html.parser')
    hide_list = poetry_soup.select("div.main3 > div.left > div.sons > div.contyishang")

    all_hide_tags = []
    for each in hide_list:
        if (each.span.text not in all_hide_tags):
            if (each.span.text != '译文及注释'):
                all_hide_tags.append(each.span.text)
    print(all_hide_tags)

    for each in all_hide_tags:
        output = ""
        # print(hide_list)
        for e in hide_list:
            # print(e)
            if (e.span.text == each):
                # print(each_pList)
                each_pList = e.select('p')
                # print(each_pList)
                for p in each_pList:
                    temp = str(p).replace('</p>', '</p>|')
                    a = re.sub(u"\\(.*?\\)|\\{.*?\\}|\\[.*?\\]|\\<.*?\\>", "", temp).strip().replace(' ', '').replace('▲', '').replace('\n', '')
                    # print(a)
                    output += a
        print(each + ": " + output)


def crawl_every_page(url):  # 看该页有哪些诗
    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
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
        crawl_the_poetry(poetry_url)



def crawl_search_result(url, line):   # 看该搜索结果有哪些页
    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
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


# crawl_these_txt("doc")
# crawl_every_page("https://so.gushiwen.cn/search.aspx?value=%E6%AC%A7%E9%98%B3%E4%BF%AE+%E6%B8%94%E5%AE%B6%E5%82%B2")
crawl_the_poetry('https://so.gushiwen.cn/shiwenv_75a1570ff533.aspx')