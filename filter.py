import time
from datetime import datetime, timezone
from dateutil.parser import parse as parse_datetime
from dateutil import parser as date_parser
from tqdm import tqdm
import requests
import glob
import re
import os
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from logging import getLogger

logger = getLogger(__name__)

# 定义自定义的头部信息，伪装成浏览器
headers = {
    "Content-Type": "application/json",
    # 可以添加更多的项...
}

# 这里可以根据需要增加更多的状态码
ERROR_CODES = [500, 502, 503, 504, 400, 401, 403, 404, 405]

# 禁用不安全请求的警告
urllib3.disable_warnings(InsecureRequestWarning)


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


def mak_date_folder():
    # 获取当前日期和时间
    now = datetime.now()
    # 格式化日期和时间为指定格式
    formatted_date = now.strftime("%Y-%m-%d-%H-%M-%S")
    # 检查tmp文件夹是否已存在
    folder_path = "tmp"
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    return formatted_date


def get_latest_txt_content(directory):
    """
    获取指定文件夹中最新的txt文件内容。

    :param directory: 要搜索的文件夹路径
    :return: 最新txt文件的内容，如果文件夹不存在或没有txt文件则返回None
    """
    # 检查文件夹是否存在
    if not os.path.exists(directory):
        print(f"文件夹 {directory} 不存在。")
        return None

    # 使用glob.glob查找所有的txt文件
    txt_files = glob.glob(os.path.join(directory, "*.txt"))

    print(txt_files)
    # 如果文件夹内没有txt文件，则返回None
    if not txt_files:
        print(f"文件夹 {directory} 中没有找到txt文件。")
        return None

    # 按文件修改时间排序，获取最新的文件
    latest_txt_file = max(txt_files, key=os.path.getmtime)

    # 读取最新txt文件的内容
    with open(latest_txt_file, "r", encoding="utf-8") as file:
        file_content = file.read()

    return file_content


def get_latest_txt_content(directory):
    """获取指定目录下最新的txt文件内容并统计非空行数量，并打印每个非空行的行号"""
    try:
        # 找出所有txt文件
        txt_files = [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if f.endswith(".txt")
        ]
        # 根据修改时间找到最新的文件
        latest_file = max(txt_files, key=os.path.getmtime)

        with open(latest_file, "r", encoding="utf-8") as file:
            non_empty_lines = 0  # 初始化非空行计数器
            line_number = 0  # 初始化行号计数器

            for line in file:
                line_number += 1  # 行号递增
                if line.strip():  # 如果行不为空（移除了头尾的空白字符）
                    non_empty_lines += 1  # 非空行计数器加1
                    print(
                        f"行号 {line_number}: {line.strip()}"
                    )  # 打印行号和非空行的内容

            print(f"非空行总数: {non_empty_lines} 行")  # 打印非空行的总数

            file.seek(0)  # 回到文件开头
            content = file.read()  # 读取文件内容
            return content  # 返回文件内容
    except Exception as e:
        logger.exception(f"获取最新txt文件内容时出错: {e}")
        return None


def save_domain_info(domains_icp, sort_directory):
    today_str = datetime.now().strftime("%Y-%m-%d:%H:%M:%S")
    for tld in set(domain.split(".")[-1] for domain in domains_icp):
        file_path = os.path.join(sort_directory, f"{tld}.txt")
        with open(file_path, "a") as file:
            # 先写入日期作为分隔符
            file.write(f"-------------**{today_str}** -------------\n")
            # 遍历字典并只写入与当前 tld 匹配的域名和ICP信息
            for domain, icp in domains_icp.items():
                if domain.endswith(tld):
                    file.write(f"{domain}:{icp}\n")


def fetch_icp_info(domain, retry=10):
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


def process_domain():
    """处理单行域名数据，返回ICP信息及域名"""

    # 调用fetch_icp_info函数尝试获取该域名的ICP备案信息
    ensure_dir("sort")
    latest_file = get_latest_domain_file("domain")
    with open(latest_file, "r") as file:
        domains = file.read().splitlines()
        line = len(domains)
        print(f"域名总行数：{line}行")
    domains_icp = {
        domain: fetch_icp_info(domain) for domain in tqdm(domains, desc="获取ICP信息")
    }
    # 返回并获取域名及ICP信息
    return save_domain_info(domains_icp, "sort"), line


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


# 增强日期时间解析函数，支持更多常见的日期时间格式
def parse_datetime(date_str):
    try:
        # 解析日期字符串
        return date_parser.parse(date_str, tzinfos={"Z": timezone.utc})
    except ValueError as e:
        # 发生解析错误，抛出异常
        raise ValueError(f"时间数据：“{date_str}”与已知格式不匹配。错误：{e}")


def whoisls_query_domain_expiry(domain):
    # API URL
    api_url = "https://whois.ls/api/whois"

    # 请求参数
    data = {
        "domain": domain,
    }

    # 设定最大重试次数
    max_retries = 10
    retries = 0

    while retries <= max_retries:
        try:
            response = requests.post(api_url, json=data)
            if response.status_code == 200:
                print(f">>{domain}：请求成功，正在提取WHOIS信息...")
                pattern = r".*(?:Expiry|Expiration).*:.*?(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4})(?: \d{2}:\d{2}:\d{2})?.*"
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                formatted_dates = []
                for date_str in matches:
                    if "-" in date_str:
                        parts = date_str.split("-")
                        if len(parts[0]) == 4:
                            formatted_dates.append(date_str)
                        elif len(parts[2]) == 4:
                            formatted_dates.append(f"{parts[2]}-{parts[1]}-{parts[0]}")
                        else:
                            formatted_dates = None
                            break
                    if not formatted_dates:
                        break
                if not formatted_dates:
                    # 如果 formatted_dates 列表为空
                    return None
                else:
                    print(f"日期：{formatted_dates}")
                return formatted_dates
            else:
                print(f"请求失败，状态码: {response.status_code}")
                retries += 1
                print("正在尝试再次发送请求...")
                continue

        except Exception as e:
            print("请求发送时出错:", e)
            retries += 1
            if retries <= max_retries:
                print("正在尝试再次发送请求...")
            continue

    return None


def dnspod_query_domain_expiry(domain):
    url = f"https://whois.ddnsip.cn/{domain}"

    try:
        response = requests.get(url)

        # 处理状态码为403的错误情况
        if response.status_code == 403:
            response_json = response.json()
            if (
                "error" in response_json
                and response_json["error"] == "unexpected status code: 403"
            ):
                return None

        response_json = response.json()

        # 获取"Last Update of Database"的值
        last_update = response_json.get("Last Update of Database", "")

        # 使用正则表达式匹配日期，格式为YYYY-MM-DD
        match = re.search(r"(\d{4}-\d{2}-\d{2})", last_update)
        if match:
            return [match.group()]
        else:
            return None
    except Exception as error:
        print(f"An error occurred: {error}")
        return None


def return_date(domain):
    lswhois = whoisls_query_domain_expiry(domain)
    print(f"whoisls返回信息：{lswhois}")
    if lswhois is not None:
        print("whois判断有日期")
        return lswhois
    else:
        dnswhois = dnspod_query_domain_expiry(domain)
        print(f"dnswhois返回信息：{dnswhois}")
        if dnswhois is not None:
            print("dnspod判断有日期")
            return dnswhois
        else:
            print(f"whoisls与dnspod判断均无有效日期：{domain}")
            with open("outdomain.txt", "a", encoding="utf-8") as file:
                file.write(f"{domain} 有icp但无法获取日期\n")
            return None


# 对比两个日期的函数，优化版本
def compare_domain_dates(domain, expiry_date_str, inputdate, Contrast_number):
    try:
        expiry_date = parse_datetime(expiry_date_str)
        # 去掉语句后半部分的 "T00:00:00Z" 以获得 naive datetime
        input_date = parse_datetime(inputdate)

        # 如果expiry_date是aware的话，就将input_date也转化为aware
        if (
            expiry_date.tzinfo is not None
            and expiry_date.tzinfo.utcoffset(expiry_date) is not None
        ):
            input_date = input_date.replace(tzinfo=timezone.utc)
        else:
            expiry_date = expiry_date.replace(tzinfo=None)

        remaining_days = (expiry_date - input_date).days

        print(remaining_days, expiry_date, input_date)

        if remaining_days < Contrast_number:
            with open("outdomain.txt", "a", encoding="utf-8") as file:
                file.write(f"{domain} - 剩余天数：{remaining_days}\n")
            print(
                f">> 域名 {domain} 到期剩余天数（{remaining_days} 天）已写入 outdomain.txt\n"
            )
        else:
            with open("tmp/error.txt", "a", encoding="utf-8") as file:
                file.write(
                    f"{domain} - 到期时间大于 {Contrast_number} 天，剩余 {remaining_days} 天\n"
                )
            print(
                f">> 域名 {domain} 到期时间大于 {Contrast_number} 天，剩余 {remaining_days} 天\n"
            )
    except ValueError as e:
        with open("tmp/error.txt", "a", encoding="utf-8") as file:
            file.write(f"{domain} - 未知错误：{e}\n")
        print(f"错误：{e}")


def main():
    outdomain_n = 0  # 存放最后剩余个数
    try:
        # 构建输出域名路径
        outdomaintxt = mak_date_folder() + "-Domain.txt"
        print(outdomaintxt)
        # ------------- 可动参数 -------------
        # 对比日期
        inputdate = "2024-04-04"
        # 要对比域名的天数
        Contrast_number = 10
        # --------------------------
        saved_domains_icp = process_domain()

        print(saved_domains_icp)
        for domain, icp in saved_domains_icp[0]:
            # save_domain_expiration(domain, inputdate)
            outdomain_n = outdomain_n + 1
            print(f"行号：{outdomain_n}")
            if icp != "未知状态":
                expiry_dates = return_date(domain)  # 返回一个yyyy-mm-dd类型日期
                if expiry_dates:  # 确保列表不为空
                    expiry_date_str = expiry_dates[0]
                    # 获取列表的第一个（可能也是唯一的）元素
                    compare_domain_dates(
                        domain, expiry_date_str, inputdate, Contrast_number
                    )
            else:
                print(f"\n未备案：{icp}, {domain}\n")
            print(expiry_dates[1])
            if outdomain_n == expiry_dates[1]:
                break
            else:
                continue
        print(f"总共对比了{outdomain_n}个域名，错误信息等内容已写入tmp/error.txt")
    except Exception as e:
        print(f"发生错误：{e}")


if __name__ == "__main__":
    main()
