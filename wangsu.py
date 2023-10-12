import requests
import hashlib
import base64
import re
import time
import ipaddress
import hmac
from datetime import datetime
import argparse

### 网宿cdn 验证脚本
def parse_ip_range(ip_range):
    start, end = ip_range.split('-')
    start_ip = ipaddress.IPv4Address(start.strip())
    end_ip = ipaddress.IPv4Address(end.strip())
    ip_list = [str(ipaddress.IPv4Address(ip)) for ip in range(int(start_ip), int(end_ip) + 1)]
    return ip_list

def get_ip_list(input_data):
    if input_data.lower().endswith('.txt'):
        ip_list = []
        with open(input_data, encoding='utf-8', mode='r') as file:
            for line in file:
                line = line.strip()
                if line:
                    if '-' in line:
                        ip_list.extend(parse_ip_range(line))
                    else:
                        ip_list.append(line)
        return ip_list
    else:
        ip_list = input_data.split(',')
        ip_list = [ip.strip() for ip in ip_list if ip.strip()]
        expanded_ip_list = []
        for ip in ip_list:
            if '-' in ip:
                expanded_ip_list.extend(parse_ip_range(ip))
            else:
                expanded_ip_list.append(ip)
        return expanded_ip_list

def write_results_to_file(results, filename):
    with open(filename, 'a', encoding='utf-8') as file:
        for s in results:
            print(f"{s['ip']} {s['isCdnIp']}")
            if bool(s['isCdnIp']):
                file.write(f"{s['ip']}\n")

def main():
    parser = argparse.ArgumentParser(description="查询IP地址信息")
    parser.add_argument("--ip", required=True, help="要查询的IP地址字符串或包含IP地址的文件")
    parser.add_argument("--output", default="results.txt", help="结果输出文件")
    args = parser.parse_args()

    try:
        # 设置用户名和API密钥
        username = "wolvez"
        apiKey = "02qQvjN4nR3UO483OO3Xeut6A2C95M"

        # 获取当前时间并格式化为GMT时间
        date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

        # 使用API密钥对日期进行哈希和Base64编码以生成密码
        signature = hmac.new(apiKey.encode('utf-8'), date.encode('utf-8'), hashlib.sha1)
        password = base64.b64encode(signature.digest()).decode('utf-8')

        # 定义请求头
        headers = {
            "X-Time-Zone": "GMT+08:00",
            "Date": date,
            "Accept": "application/json"
        }

        # 获取IP地址输入
        ip_list = get_ip_list(args.ip)

        # 按批次查询IP
        batch_size = 20
        for i in range(0, len(ip_list), batch_size):
            batch_ips = ip_list[i:i+batch_size]
            #print(batch_ips)
            time.sleep(3)

            # 定义请求数据
            data = {
                "ip": batch_ips
            }

            # 发起POST请求
            response = requests.post(
                "https://open.chinanetcenter.com/api/tools/ip-info",
                headers=headers,
                auth=(username, password),
                json=data
            )
            # 检查响应状态码，如果不是200，则打印错误信息
            if response.status_code != 200:
                print(f"HTTP请求失败，状态码：{response.status_code}")
                print(response.text)
                with open('400.txt', 'a', encoding='utf-8') as file:
                    for ip in batch_ips:
                        file.write(f"{ip}\n")
                time.sleep(120)

            else:
                # 打印响应内容
                contents = response.json()
                results = contents['result']

                # 写入结果到文件
                write_results_to_file(results, args.output)

    except Exception as e:
        print(f"发生异常: {e}")

if __name__ == "__main__":
    main()
