import re
from bs4 import BeautifulSoup
from msedge.selenium_tools import Edge, EdgeOptions
from selenium.common.exceptions import NoSuchElementException
from utils import getHTMLText

options = EdgeOptions()
options.use_chromium = True
options.binary_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"  # 浏览器的位置
driver = Edge(options=options, executable_path=r"D:\edgeDriver_win64\msedgedriver.exe")  # 相应的浏览器的驱动位置​

def getText(url):
    try:
        driver.get(url)
        poetry_soup = BeautifulSoup(driver.page_source, 'lxml')
    except:
        print("2爬取失败")
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
    # raw_content = poetry_soup.select("#sonsyuanwen > div.cont > div.contson")[0].text.strip()
    temp_content1 = poetry_soup.select("#sonsyuanwen > div.cont > div.contson")[0]
    temp_content2 = str(temp_content1).replace("<br/>", "|")[50:-11].strip()
    # 把括号去掉
    no_bracket_content = re.sub(u"\\(.*?\\)|\\{.*?}|\\[.*?]", "", temp_content2)
    content = no_bracket_content + "|"
    print("原文：" + content)
    # 译文
    input = driver.find_element_by_xpath('//*[@alt="译文"]')
    input.click()
    poetry_soup = BeautifulSoup(driver.page_source, 'lxml')
    raw_yiwen = poetry_soup.select("#sonsyuanwen > div.cont > div.contson > p > span")
    yiwen = ""
    for each in raw_yiwen:
        yiwen += each.text + "|"
    print("译文：" + yiwen)
    # 注释
    input = driver.find_element_by_xpath('//*[@alt="注释"]')
    input.click()
    # 取消掉
    input = driver.find_element_by_xpath('//*[@alt="译文2"]')
    input.click()
    poetry_soup = BeautifulSoup(driver.page_source, 'lxml')
    raw_zhushi = poetry_soup.select("#sonsyuanwen > div.cont > div.contson > p > span")
    zhushi = ""
    for each in raw_zhushi:
        zhushi += each.text + "|"
    print("注释：" + zhushi)
    # 点开“展开阅读全文”
    buttons = driver.find_elements_by_link_text("展开阅读全文 ∨")
    for button in buttons:
        button.click()
    poetry_soup = BeautifulSoup(driver.page_source, 'lxml')
    hide_list = poetry_soup.select("div.main3 > div.left > div.sons > div.contyishang")

    all_hide_tags = []
    for each in hide_list:
        if (each.span.text not in all_hide_tags):
            if (each.span.text != '译文及注释'):
                all_hide_tags.append(each.span.text)
    print(all_hide_tags)

    for each in all_hide_tags:
        output = ""
        for e in hide_list:
            if (e.span.text == each):
                each_pList = e.select('p')
                for p in each_pList:
                    output += p.text.strip()
        print(each + ": " + output)

