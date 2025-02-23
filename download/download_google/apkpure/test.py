
# Import the API

# Get the first result from app
# top_result = API.get_first_app_result(name='EVMap - EV chargers')

# # # Get all apps from result
# # all_results = API.get_all_apps_results(name='App Name')

# # # Get info from an app
# # app_info = API.get_info(name='App Name')

# # # Get the versions of an app
# # versions = API.get_versions(name='App Name')

# # # Downlaod an app, you can pass a version and also the type of file between apk and xapk
# # # version and xapk are optional parameters
# # API.download(name='App Name', version='1.1.1', xapk=True)
# print(top_result)
# Import the API
# Import the API
from apkpure import ApkPure
import os

API = ApkPure()

def is_app_downloaded(app_name, download_dir):
    """
    检查文件夹中是否已经存在包含 app_name 的文件。
    """
    # 遍历下载目录中的所有文件
    for filename in os.listdir(download_dir):
        # 如果文件名中包含 app_name，认为已下载
        if app_name in filename:
            return True
    return False

# 设置下载目录
download_dir = r'C:\Users\22863\Desktop\毕设\app数据集_google\app集合'

# 打开包含应用名称的文件
with open('namelist.txt', 'r', encoding='utf-8') as file:
    # 逐行读取文件
    for line in file:
        # 去除每行末尾的换行符
        app_name = line.strip()
        
        # 检查应用是否已经下载
        if is_app_downloaded(app_name, download_dir):
            print(f'{app_name} already downloaded, skipping...')
            continue  # 如果应用已下载，则跳过
        
        # 打印当前下载的应用名
        print(f'Downloading {app_name}...')
        
        # 下载应用
        try:
            result = API.download(name=app_name)
            if result is None:
                print(f"Failed to download {app_name}. Skipping...")
        except Exception as e:
            print(f"Error: Failed to download {app_name}. Reason: {e}")
# API.download(name = 'EVMap - EV chargers')