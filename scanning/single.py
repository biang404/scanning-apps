import os
import subprocess
import requests
import time
import json
from datetime import datetime

# MobSF配置
MOBSF_URL = "http://localhost:8000"
API_KEY = "d3444787153aa641768e9d883e822484e972be794e86338be0442b882845c7ac"
REPORT_DIR = r"C:\Users\22863\Desktop\git\bishe\scanning-apps\scanning\mobsf_report"  # 报告保存目录

# 创建报告保存目录
if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)

# MobSF API端点
UPLOAD_URL = f"{MOBSF_URL}/api/v1/upload"
SCAN_URL = f"{MOBSF_URL}/api/v1/scan"
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

# 启动扫描
def start_scan(file_hash):
    data = {"hash": file_hash}
    headers = {"Authorization": API_KEY}
    response = requests.post(SCAN_URL, data=data, headers=headers)
    if response.status_code == 200:
        print(f"扫描已启动: {file_hash}")
        return True
    else:
        print(f"扫描启动失败: {response.text}")
        return False

# 获取JSON报告
def get_json_report(hash_value, api_key):
    """
    通过hash值和API Key获取JSON报告
    :param hash_value: 扫描的哈希值
    :param api_key: MobSF的API Key
    :return: JSON报告内容（字典格式）
    """
    # 构建curl命令
    curl_command = [
        "curl.exe",
        "-X", "POST",
        "--url", f"{MOBSF_URL}/api/v1/report_json",
        "--data", f"hash={hash_value}",
        "-H", f"X-Mobsf-Api-Key: {api_key}"
    ]

    # 执行curl命令
    try:
        result = subprocess.run(curl_command, capture_output=True, text=True, check=True)
        # 解析返回的JSON内容
        report = json.loads(result.stdout)
        return report
    except subprocess.CalledProcessError as e:
        print(f"获取报告失败: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        print(f"解析JSON失败: {e}")
        return None

# 主流程
def process_apk(file_path):
    # 上传APK
    file_hash = upload_apk(file_path)
    if not file_hash:
        return

    # 启动扫描
    if not start_scan(file_hash):
        return

    # 等待扫描完成
    time.sleep(10)  # 根据文件大小调整等待时间

    # 获取报告
    report = get_json_report(file_hash, API_KEY)
    if report:
        # 生成报告文件名
        apk_name = os.path.splitext(os.path.basename(file_path))[0]  # 去掉文件扩展名
        report_filename = f"report_{apk_name}.json"
        report_path = os.path.join(REPORT_DIR, report_filename)

        # 保存报告到文件
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)
        print(f"报告已保存至: {report_path}")
    else:
        print("未能获取报告。")

# 测试单个APK文件
if __name__ == "__main__":
    apk_file = r"C:\Users\22863\Desktop\毕设\app数据集\OBD app\latest_Elm327OBDInfo_1.1_APKPure.apk"  # 替换为你的APK文件路径
    if os.path.exists(apk_file):
        print(f"正在处理: {apk_file}")
        process_apk(apk_file)
    else:
        print(f"文件不存在: {apk_file}")