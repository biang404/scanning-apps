import os
import requests
import time

# MobSF配置
MOBSF_URL = "http://localhost:8000"
API_KEY = "2cddef7661e32a182cf590f62375be1cce66ed60b25ea78bf4891f19135b475d"
REPORT_DIR = "reports"  # 报告保存目录
ADB_DEVICE_ID = "<adb device identifier>"  # 替换为你的ADB设备ID

# 创建报告保存目录
if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)

# MobSF API端点
UPLOAD_URL = f"{MOBSF_URL}/api/v1/upload"
DYNAMIC_SCAN_URL = f"{MOBSF_URL}/api/v1/dynamic_scan"
REPORT_URL = f"{MOBSF_URL}/api/v1/report_json"

# 上传APK文件
def upload_apk(file_path):
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f, "application/octet-stream")}
        headers = {"Authorization": API_KEY}
        response = requests.post(UPLOAD_URL, files=files, headers=headers)
        if response.status_code == 200:
            return response.json()["hash"]
        else:
            print(f"上传失败: {response.text}")
            return None

# 启动动态扫描
def start_dynamic_scan(file_hash):
    data = {"hash": file_hash, "device_id": ADB_DEVICE_ID}
    headers = {"Authorization": API_KEY}
    response = requests.post(DYNAMIC_SCAN_URL, data=data, headers=headers)
    if response.status_code == 200:
        print(f"动态扫描已启动: {file_hash}")
        return True
    else:
        print(f"动态扫描启动失败: {response.text}")
        return False

# 下载报告
def download_report(file_hash, output_path):
    params = {"hash": file_hash}
    headers = {"Authorization": API_KEY}
    response = requests.get(REPORT_URL, params=params, headers=headers)
    if response.status_code == 200:
        with open(output_path, "w") as f:
            f.write(response.text)
        print(f"报告已保存: {output_path}")
    else:
        print(f"报告下载失败: {response.text}")

# 主流程
def process_apk(file_path):
    # 上传APK
    file_hash = upload_apk(file_path)
    if not file_hash:
        return

    # 启动动态扫描
    if not start_dynamic_scan(file_hash):
        return

    # 等待扫描完成
    time.sleep(20)  # 动态扫描可能需要更长时间

    # 下载报告
    report_file = os.path.join(REPORT_DIR, f"{os.path.basename(file_path)}_dynamic_report.json")
    download_report(file_hash, report_file)

# 遍历APK文件列表
def process_apk_list(apk_list):
    for apk_file in apk_list:
        if os.path.exists(apk_file):
            print(f"正在处理: {apk_file}")
            process_apk(apk_file)
        else:
            print(f"文件不存在: {apk_file}")

# 示例APK文件列表
apk_list = [
    "app1.apk",
    "app2.apk",
    "app3.apk"
]

# 开始处理
process_apk_list(apk_list)