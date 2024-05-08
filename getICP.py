import requests
import time
import os
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from logging import getLogger

logger = getLogger(__name__)

# 这里可以根据需要增加更多的状态码
ERROR_CODES = [500, 502, 503, 504, 400, 401, 403, 404, 405]

# 禁用不安全请求的警告
urllib3.disable_warnings(InsecureRequestWarning)


def fetch_icp_info(domain):
    """请求获取ICP备案信息，带重试逻辑"""
    query_url = f"https://icpcode.ddnsip.cn/?domain={domain}"
    max_retries = 8  # 最大重试次数
    retry_delay = 5  # 重试等待时间（秒）
    for attempt in range(max_retries):
        try:
            response = requests.get(query_url, timeout=10)  # 设置响应超时时间
            response.raise_for_status()  # 检查响应状态码，如果是4xx或5xx，则抛出异常
            icp_data = response.json()  # 请求成功，返回响应数据
            icp_code = icp_data.get("IcpCode")
            if icp_code and icp_code != "未知状态":
                return icp_data  # 如果获取到ICP信息，返回整个JSON数据
            else:
                return None  # 如果ICP备案信息是"未知状态"，返回None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in ERROR_CODES:
                logger.error(
                    f"{e.response.status_code}:{domain} 第{attempt + 1}次请求遇到错误，等待{retry_delay}秒后重试..."
                )
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)  # 等待一段时间后重试
                else:
                    logger.error(
                        f"重试{max_retries}次后仍然不能访问{domain}的ICP信息。"
                    )
            else:
                logger.error(f"请求{domain}时遇到错误：{e}")
                break  # 如果是其他HTTP错误，则跳出循环，不进行重试
        except requests.exceptions.RequestException as e:
            logger.error(f"请求{domain}时出现异常：{e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)  # 等待一段时间后重试
            else:
                break  # 如果重试次数耗尽，则跳出循环
    return None  # 若所有重试都失败，则返回None


# 实际使用fetch_icp_info函数的例子
if __name__ == "__main__":
    domain_to_check = "10086.hk"
    icp_info = fetch_icp_info(domain_to_check)
    if icp_info:
        print(f"域名 {domain_to_check} 的ICP备案信息: {icp_info['IcpCode']}")
    else:
        print(f"域名 {domain_to_check} 未查询到ICP备案信息。")
    print(icp_info)
