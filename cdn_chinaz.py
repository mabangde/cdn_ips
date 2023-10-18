import requests
import csv
import os

from concurrent.futures import ThreadPoolExecutor

cookies = {
    
}

headers = {
    'authority': 'cdn.chinaz.com',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'zh,zh-CN;q=0.9,en;q=0.8,zh-TW;q=0.7,eo;q=0.6',
    # 'cookie': 'cz_statistics_visitor=910f4234-53f1-e4db-181b-b9f833937e48; speedtesthost=www.beianbeian.com; Hm_lvt_ca96c3507ee04e182fb6d097cb2a1a4c=1696850627; ucvalidate=67562171-5f36-3d5a-ca42-935ccf0fdcd4; Hm_lvt_aecc9715b0f5d5f7f34fba48a3c511d6=1696850685; Hm_lpvt_aecc9715b0f5d5f7f34fba48a3c511d6=1696942667; chinaz_zxuser=9b0eb34e-eec1-4bb5-2cc7-708526d62b77; toolbox_urls=zygtr.com.cname4331.yjs-cdn.com|so.xykss.cn.cname3213.yjs-cdn.com|lxdns.com|www.water-cube.com|ffo.changyou.com|bbs.ma.huluxia.net|download.uce.cn|www.5118.com|4399.com|www.12306.cn; pinghost=zygtr.com.cname4331.yjs-cdn.com; qHistory=Ly9waW5nLmNoaW5hei5jb20vX3Bpbmfmo4DmtYs=; toolUserGrade=DA558BECA59696EB6D6F7073658259097496A34F9B3E8B35F3075E72A88B4A268A9771EC1AF80CC8F8EE395D4B5DC0F03CA56B0FECAB8DC357BDD00BCB220444E622E1983DB5A198D2952632B1DCAEBD47461F5A53FD2E9494B91FBBE8A8B4459461A104D04D1D6B83BAEABAFE031432D4A976D4CD3BF3EA; bbsmax_user=1fb5bc8a-2533-ec02-bfff-d144980c80d4; Hm_lpvt_ca96c3507ee04e182fb6d097cb2a1a4c=1697550530; chinaz_topuser=0228e32a-20dd-0459-5efd-dc34db87ca93',
    'referer': 'https://cdn.chinaz.com/server/%E8%85%BE%E8%AE%AF%E4%BA%91',
    'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}


def retrieve_and_write_data(page, csv_filename):
    params = {
        'cdnkey': 'DU/aYNK+yR168KYiq20+1yHS2HiXGqRX',   ## 替换对应的key 每个cdn 对应的key不一样
        'area': '',
        'net': '',
        'pageindex': str(page),
        'cnt': '0',
    }
    try:
        response = requests.get('https://cdn.chinaz.com/ajax/AreaIP', params=params, cookies=cookies, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve data for page {page}: {str(e)}")
        return

    if response.status_code != 200:
        print(f"Failed to retrieve data for page {page}.")
        return

    data = response.json().get('data', [])
    if not data:
        print(f"No data found on page {page}.")
        return False

    # Save the data to a CSV file for this page
    with open(csv_filename, 'a', newline='') as csv_file:
        fieldnames = ['ip', 'IPArea', 'IPCity', 'IPRoute']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        if not os.path.exists(csv_filename):
            writer.writeheader()

        for d in data:
            writer.writerow(d)

        print(f"Saved data for page {page} to '{csv_filename}'")


def main():
    page = 1
    max_threads = 50  # You can adjust the number of threads here
    csv_filename = 'ip_data.csv'
    max_page = 43937  ## 最大页码数

    with ThreadPoolExecutor(max_threads) as executor:
        if page <= max_page:
            retrieve_and_write_data(page, csv_filename)
            page += 1


if __name__ == '__main__':
    main()

