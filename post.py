import requests


def query_whois(domain):
    # 接口URL
    url = "https://whois.ls/api/whois"

    # 请求参数
    payload = {"domain": domain}

    # 发送POST请求
    try:
        response = requests.post(url, json=payload)

        # 检查是否成功收到响应
        if response.status_code == 200:
            # 返回whois字符串
            return response.text
        else:
            print(f"请求失败，状态码：{response.status_code}")
            return None
    except Exception as e:
        print(f"请求过程中发生错误：{e}")
        return None


# 示例用法
domain_to_query = "qwp.icu"
whois_info = query_whois(domain_to_query)

if whois_info:
    print(f"{domain_to_query} 的 whois 信息：\n{whois_info}")
