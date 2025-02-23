import requests
from bs4 import BeautifulSoup

url = "https://play.google.com/store/apps?device=car"

try:
    response = requests.get(url)
    # 确保请求成功
    if response.status_code == 200:
        print("成功获取响应!")
        # print(response.text)  # 打印HTML内容
    else:
        print(f"请求失败，状态码：{response.status_code}")
except Exception as e:
    print(f"发生错误：{e}")

html_element  = BeautifulSoup(response.text, "html.parser")

list_section = html_element.find_all('div', class_ = 'aoJE7e b0ZfVe')
print(list_section[0].text)

# names = list_section.find_all('div', class_ = 'Ekprse')


# print(len(list_section))
# for div in list_section[0]:
#     print(div.text.strip()  )