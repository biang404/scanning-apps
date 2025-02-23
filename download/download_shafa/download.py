import os
import json
import requests
from tqdm import tqdm
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 SLBrowser/9.0.5.12181 SLBChan/103 SLBVPV/64-bit"
}

def download_file(name, download_link, save_path):
    """下载文件并保存到指定路径。
    """
    # 拼接完整路径，文件名为name.apk
    file_path = os.path.join(save_path, f"{name}.apk")

    # 检查文件是否已经存在
    if os.path.exists(file_path):
        return f'{name}.apk already exists at {file_path}'

    # 确保目录存在
    os.makedirs(save_path, exist_ok=True)

    # 发起请求
    response = requests.get(download_link,headers = headers, stream=True)
    if response.status_code == 200:
        # 获取文件总大小
        file_size = int(response.headers.get('content-length', 0))

        try:
            with open(file_path, 'wb') as package_file:
                progress_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc=f'Downloading {name}.apk', dynamic_ncols=True, leave=True)
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        package_file.write(chunk)
                        progress_bar.update(len(chunk))
                progress_bar.close()
        except IOError as e:
            print(f"Error: Failed to save {name}.apk. Reason: {e}")
            return None

        return f'{name}.apk was downloaded to {file_path}'
    else:
        return f'Error while trying to download {download_link}'

def main():
    # JSON文件路径
    json_file_path = 'links.json'
    # 目标保存路径
    save_path = r"C:\Users\22863\Desktop\毕设\app数据集_shafa\app_data"

    # 读取JSON文件
    with open(json_file_path, 'r', encoding='utf-8') as file:
        download_links = json.load(file)

    # 遍历字典并下载文件
    for name, download_link in download_links.items():
        result = download_file(name, download_link, save_path)
        print(result)

if __name__ == '__main__':
    main()

