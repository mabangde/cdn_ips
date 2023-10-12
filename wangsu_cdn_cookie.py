import requests
import time
import ipaddress
from datetime import datetime
import argparse
import urllib3
from concurrent.futures import ThreadPoolExecutor
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
            print(f"{s['ip']} {s['wsIp']}")
            if bool(s['wsIp']):
                file.write(f"{s['ip']}\n")


def process_ip_batch(ip_list, cookies, proxies, headers, output_filename, batch_size):
    for i in range(0, len(ip_list), batch_size):
        batch_ips = ip_list[i:i+batch_size]
        time.sleep(5)

        # Build the query string with parameters
        query_string = f't=1697091702521&ipList={",".join(batch_ips)}'

        # Construct the complete URL with query parameters
        url = f'https://cdn.console.wangsu.com/v2/ip-check?{query_string}'

        try:
            response = requests.get(url,
                                    proxies=proxies,
                                    cookies=cookies,
                                    headers=headers,
                                    verify=False
                                    )
            if response.status_code != 200:
                print(f"HTTP请求失败，状态码：{response.status_code}")
                print(response.text)
                with open('4001.txt', 'a', encoding='utf-8') as file:
                    for ip in batch_ips:
                        file.write(f"{ip}\n")
                time.sleep(240)
                
            else:
                # 打印响应内容
                contents = response.json()
                results = contents['data']

                # 写入结果到文件
                write_results_to_file(results, output_filename)

        except Exception as e:
            print(f"发生异常: {e}")

def main():
    parser = argparse.ArgumentParser(description="查询IP地址信息")
    parser.add_argument("--ip", required=True, help="要查询的IP地址字符串或包含IP地址的文件")
    parser.add_argument("--output", default="results.txt", help="结果输出文件")
    args = parser.parse_args()
    cookies = {
    ## 替换cookie
    }
    proxies = {
        'http': 'http://127.0.0.1:8080',
        'https': 'http://127.0.0.1:8080',
    }

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh,zh-CN;q=0.9,en;q=0.8,zh-TW;q=0.7,eo;q=0.6',
        'Connection': 'keep-alive',
        'MenuCode': 'undefined',
        'ProductCode': 'undefined',
        'Referer': 'https://cdn.console.wangsu.com/v2/index/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'TimeZone': 'GMT+8:00',
        'Timestamp': '1697091702521',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    # 获取IP地址输入
    ip_list = get_ip_list(args.ip)

    # 按批次查询IP
    batch_size = 20
    with ThreadPoolExecutor(max_workers=10) as executor:  # 这里可以调整max_workers以控制并发线程数
        for i in range(0, len(ip_list), batch_size):
            batch_ips = ip_list[i:i+batch_size]
            # 提交任务到线程池
            executor.submit(process_ip_batch, batch_ips, cookies, proxies, headers, args.output, batch_size)

if __name__ == "__main__":
    main()
