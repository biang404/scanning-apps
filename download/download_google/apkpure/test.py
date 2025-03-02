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
download_dir = r'C:\Users\22863\Desktop\毕设\app数据集\OBD app'

# 打开包含应用名称的文件
with open('namelist_OBD.txt', 'r', encoding='utf-8') as file:
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