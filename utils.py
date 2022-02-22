import requests


# 请求html文件
def getHTMLText(url):
    try:
        kv = {'user-agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=kv)  # 防止查源user-agent
        r.raise_for_status()  # 确保200
        r.encoding = r.apparent_encoding  # 防止乱码
        demo = r.text
        return demo
    except:
        print("1爬取失败")

