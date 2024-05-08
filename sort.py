import os
import requests
import time
from datetime import datetime
from tqdm import tqdm


def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_latest_domain_file(directory="domain"):
    files = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
    ]
    return max(files, key=os.path.getmtime)


def get_icp_info(domain, retry=10):
    # retry重试次数
    api_url = f"https://icpcode.ddnsip.cn/?domain={domain}"
    for attempt in range(retry):
        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                # 返回icpcode的值，不为200就返回null
                return response.json().get("IcpCode", "访问失败")
            else:
                time.sleep(1)  # 简单的延时等待
        except requests.RequestException:
            time.sleep(1)  # 请求异常时的延时等待
    return f"重试{retry}次ICP查询失败"


def save_domain_info(domains_icp, sort_directory):
    today_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    saved_data = []  # 空列表，用于存储和返回数据
    for tld in set(domain.split(".")[-1] for domain in domains_icp):
        file_path = os.path.join(sort_directory, f"{tld}.txt")
        with open(file_path, "a") as file:
            file.write(f"-------------**{today_str}**-------------\n")
            for domain, icp in domains_icp.items():
                if domain.endswith(tld):
                    file.write(f"{domain}:{icp}\n")
                    saved_data.append((domain, icp))  # 将域名和ICP信息添加到列表中
    return saved_data  # 返回列表


# 主程序(示例使用)
ensure_dir("sort")
latest_file = get_latest_domain_file("domain")

with open(latest_file, "r") as file:
    domains = file.read().splitlines()
    print(len(domains))

domains_icp = {
    domain: get_icp_info(domain) for domain in tqdm(domains, desc="获取ICP信息")
}
# 保存并获取域名及ICP信息
saved_domains_icp = save_domain_info(domains_icp, "sort")

# 在这里打印或处理返回的domain和icp信息
for domain, icp in saved_domains_icp:
    print(f"Domain: {domain}, ICP: {icp}")
print("处理完成")
