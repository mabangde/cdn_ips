import fofa
import csv
from collections import Counter

def write_to_csv(results, csv_filename):
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Host', 'IP', 'Title', 'Product'])

        for result in results:
            protocol, ip, port, host, title, product = result
            csv_writer.writerow([host, ip, title, product])

def query_fofa_data(query_str):
    email = ''     ### 定义fofaemail
    key = ''  ### 定义fofakey
    client = fofa.Client(email, key)

    data_dict = {
        "ips": [],
        "results": []
    }

    for page in range(1, 10):
        data = client.search(query_str, size=1000, page=page, fields="protocol,ip,port,host,title,product")
        #if data['error']:
        #    break

        if data['size'] <=9999:
            break

        if len(data["results"]) == 0:
            break

        print('\n#####################################################')
        print(f'# 正在查询第 {page} 页')
        print(f'# 查询语句: {data["query"].ljust(20)}')
        print(f'# 结果数量: {data["size"]}')
        print('#####################################################\n')
        for protocol, ip, port, host,title,product in data["results"]:
            data_dict["ips"].append(ip)
            data_dict["results"].append((protocol, ip, port, host,title,product))

    return data_dict

def duplicate(query_str):
    duplicate_ips = set()  # 存储重复IP

    while True:
        try:
            result_dict = query_fofa_data(query_str)
            results = result_dict['results']
            ips = result_dict['ips']
            counter = Counter(ips)
            sorted_items = counter.most_common()

            new_query_str = query_str
            new_duplicate_ips = set()  # 存储新一轮查询中的重复IP
            print("重复IP统计:")
            for item, count in sorted_items:
                if count >= 20 and item not in duplicate_ips:  # 仅处理之前未处理过的重复IP
                    print(f'{item}: {count}')
                    new_duplicate_ips.add(item)
                    new_query_str += f' && ip!="{item}"'

            if not new_duplicate_ips:
                break  # 如果没有大于20次的重复IP，退出循环
            else:
                duplicate_ips.update(new_duplicate_ips)  # 将新一轮的重复IP添加到全局集合中
                query_str = new_query_str  # 更新 query_str 以便进行下一次查询
        except:
            break

    return results


if __name__ == "__main__":
    query_str = 'domain="alicdn.com"||host="alicdn.com"'   ## 此处为查询语句
    final_results = duplicate(query_str)
    csv_filename = 'fofa_results.csv'
    write_to_csv(final_results, csv_filename)

    print('\n最终结果:')
    for result in final_results:
        protocol, ip, port, host,title,product = result
        if host.startswith("http://") or host.startswith("https://"):
            print(f"{host.ljust(55)}{ip.ljust(15)}")
        else:
            if protocol == 'unknown':
                if port == '80':
                    protocol = 'http'
                if port == '443':
                    protocol = 'https'
                else:
                    protocol = 'http'
            h = f"{protocol}://{ip}:{port}"
            print(f"{h.ljust(55)}{ip.ljust(15)}")
