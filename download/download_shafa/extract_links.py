import json
import requests
from bs4 import BeautifulSoup

url = "https://www.shafa.com/car_apps/?page="
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 SLBrowser/9.0.5.12181 SLBChan/103 SLBVPV/64-bit"
}

def check_connection(a):
    try:
        response = requests.get(f"{url}{a}", headers=headers)
        print(f"{url}{a}")
        # 确保请求成功
        if response.status_code == 200:
            print("成功获取响应!")
            return True
        else:
            print(f"请求失败，状态码：{response.status_code}")
            return False
    except Exception as e:
        print(f"错误：{e}")
        return False

def get_download_links(a):
    download_links = []
    names_text = []
    try:
        response = requests.get(f"{url}{a}", headers=headers)
        if response.status_code == 200:
            html_element = BeautifulSoup(response.text, "html.parser")
            links = html_element.find_all('a', class_='app-btn-detail')
            names = html_element.find_all('span', class_='app-name')
            names_text = [name.get_text() for name in names]
            for link in links:
                download_links.append(link.get('href'))
        else:
            print(f"请求失败，状态码：{response.status_code}")
    except Exception as e:
        print(f"错误：{e}")
    return download_links, names_text

# 清空文件内容
with open('links.txt', 'w') as file:
    pass

# 初始化一个空字典来存储所有数据
all_data = {}

for i in range(1, 32):
    if check_connection(i):
        download_links, names_text = get_download_links(i)
        # 将names_text和download_links组合成字典
        page_data = dict(zip(names_text, download_links))
        # 将页面数据合并到总数据字典中
        all_data.update(page_data)

# 将字典转换为JSON格式的字符串
json_data = json.dumps(all_data, ensure_ascii=False, indent=4)

# 写入到文本文件中
with open('links.json', 'w', encoding='utf-8') as file:
    file.write(json_data)
# response = requests.get(f"{url}{1}", headers=headers)
# html_element = BeautifulSoup(response.text, "html.parser")
# names = html_element.find_all('span', class_ = 'app-name')
# print(names)

# if check_connection(1):
# links = get_download_links(1)
# print(links)


# html_element  = BeautifulSoup(response.text, "html.parser")

# list_section = html_element.find_all('div', class_ = 'aoJE7e b0ZfVe')
# print(list_section[0].text)