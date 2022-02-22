import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from msedge.selenium_tools import Edge, EdgeOptions
from selenium.common.exceptions import NoSuchElementException
from utils import getHTMLText

options = EdgeOptions()
options.use_chromium = True
options.binary_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"  # 浏览器的位置
driver = Edge(options=options, executable_path=r"D:\edgeDriver_win64\msedgedriver.exe")  # 相应的浏览器的驱动位置​


basic_url = "https://www.shicihui.com/"
dynastic_url = "shicidynasty"
shiren_url = "shicishiren"
poetry_list = []
f = open("crawled_data/shicihui_shiren.txt", "a", encoding="utf-8")


def getText(url):
    try:
        poetry_demo = getHTMLText(url)
        poetry_soup = BeautifulSoup(poetry_demo, 'html.parser')
    except:
        print("2爬取失败")
        return

    try:
        driver.get(url)
        input = driver.find_element_by_partial_link_text('译')
        input.click()
        input = driver.find_element_by_partial_link_text('注')
        input.click()
    except NoSuchElementException:
        print("没有找到译文或注释按钮")

    poetry_dict = {"诗名": "", "朝代": "", "作者": "", "原文": "", "翻译": "", "注释": "", "鉴赏": "", "新解": "", "创作背景": ""}

    # 找标题
    title = poetry_soup.find("a", attrs={"class": "shici-title"})
    title = title.get_text().replace(" ", "").replace("\n", "").replace("\r", "")
    poetry_dict['诗名'] = title
    # 找作者和朝代
    authorD = poetry_soup.select("p[class='shici-author'] > a")
    dynastic = authorD[0].get_text().replace(" ", "").replace("\n", "").replace("\r", "")
    poetry_dict['朝代'] = dynastic
    author = authorD[1].get_text().replace(" ", "").replace("\n", "").replace("\r", "")
    poetry_dict['作者'] = author

    # 找原文
    content = poetry_soup.select("article > div > p.shici-text")
    contentString = ""
    for item in content:
        item = item.get_text().replace("\n", "").replace("\r", "").replace(" ", "")
        contentString += item + "|"
    poetry_dict['原文'] = contentString

    # 找对齐的译文
    yiwen = poetry_soup.select(".shici-fanyi")
    yiwenString = ""
    for item in yiwen:
        item = item.get_text().replace("\n", "").replace("\r", "").replace(" ", "")
        yiwenString += item + "|"
    poetry_dict['翻译'] = yiwenString

    # 找对齐的注释
    annotate = poetry_soup.select(".shici-zhushi")
    annotateString = ""
    for item in annotate:
        item = item.get_text().replace("\n", "").replace("\r", "").replace(" ", "")
        annotateString += item + "|"
    poetry_dict['注释'] = annotateString

    # 赏析
    analyze = poetry_soup.find("div", attrs={"id": "shangxi"})
    analyze_title = analyze.find_all("h2", attrs={"class": "shici-yzs-title"})
    analyze_content = analyze.select("div.shici-yzs-content > div")
    title_list = []
    analyze_content_list = []

    for item in analyze_title:
        item = item.get_text().replace("\n", "").replace("\r", "").replace(" ", "")
        if item != "":
            title_list.append(item)

    for item in analyze_content:
        item = item.get_text().replace("\n", "").replace("\r", "").replace(" ", "")
        if item != "":
            analyze_content_list.append(item)

    # if len(title_list) != len(analyze_content_list):
    #     print("不对齐！")
    #     return
    if title_list != "":
        for i in range(len(title_list)):
            poetry_dict[title_list[i]] = analyze_content_list[i]
        poetry_list.append(poetry_dict)

    print("第" + str(len(poetry_list)) + "首")
    poetry_key = list(poetry_dict.keys())
    for i in range(len(poetry_key)):
        if poetry_dict[poetry_key[i]] != "":
            f.write(poetry_key[i] + " " + poetry_dict[poetry_key[i]] + '\n')
    f.write('\n')


for number in range(1, 8402):
    print("开始第" + str(number) + "位诗人")
    for page in range(1, 11):
        print("开始第" + str(page) + "页")
        http_url = basic_url + shiren_url + str(number) + "-page" + str(page) + ".html"
        print(http_url)
        try:
            demo = getHTMLText(http_url)
            soup = BeautifulSoup(demo, 'html.parser')
        except:
            print("3爬取失败")
            continue

        lista = soup.find_all("a", href=re.compile("/shici/[0-9]*.html"))
        for a_item in lista:
            poetry_url = basic_url + a_item.get("href")
            try:
                getText(poetry_url)
            except:
                print("4爬取失败")
                continue

f.close()

total_number = 0
translation_number = 0
annotated_number = 0
shangxi_number = 0
background_number = 0

# "诗名": "", "朝代": "", "作者": "", "原文": "", "翻译": "", "注释": "", "鉴赏": "", "新解": "", "创作背景": ""
for poetry_item in poetry_list:
    # 统计数量
    print(poetry_item)
    poetry_key = list(poetry_item.keys())
    if poetry_item['翻译'] != '':
        translation_number += 1
    if poetry_item['注释'] != '':
        annotated_number += 1
    if poetry_item['鉴赏'] != '':
        shangxi_number += 1
    if poetry_item['创作背景'] != '':
        background_number += 1


total_number = len(poetry_list)
print("共" + str(len(poetry_list)) + "首")
print("有" + str(translation_number) + "首有翻译")
print("有" + str(annotated_number) + "首有注释")
print("有" + str(shangxi_number) + "首有鉴赏")
print("有" + str(background_number) + "首有背景")
