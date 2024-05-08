import requests
import re
import json


def fetch_last_update_date(domain):
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


# 测试用例
domain = "qwp.icu"
print(fetch_last_update_date(domain))
