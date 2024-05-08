from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.edge.service import Service
from datetime import datetime
from tqdm import tqdm
import shutil
import time
import sys
import re
import os

# ————————自定义配置————————

# 最大Edge标签页数
Maximum_tag = 900

# 到达最大页数时关闭全部空标签
Max_tag_off = 30

# ————————自定义配置————————


# 捕获控制台信息
class DualOutput:
    def __init__(self, file_path):
        self.file = open(file_path, "w")
        self.console = sys.stdout

    def write(self, message):
        self.file.write(message)
        self.console.write(message)

    def flush(self):  # flush方法是为了兼容Python的flush操作。
        self.file.flush()
        self.console.flush()


# 信息写入
def mak_console_log():
    # 目标文件夹路径
    target_directory = "consoleLog"
    # 如果目标文件夹不存在，则创建它
    os.makedirs(target_directory, exist_ok=True)
    # 使用示例
    sys.stdout = DualOutput("consoleLog/log.txt")
    sys.stderr = DualOutput("consoleLog/log.txt")


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


def yidong_text(mtime):

    # 源文件路径
    source_path = mtime

    # 目标文件夹路径
    target_directory = "domain"

    # 如果目标文件夹不存在，则创建它
    os.makedirs(target_directory, exist_ok=True)

    # 完整的目标文件路径
    target_path = os.path.join(target_directory, os.path.basename(source_path))

    # 移动文件
    shutil.move(source_path, target_path)


def delete_tmp():
    # 设置tmp文件夹的路径
    directory_path = "tmp"

    # 检查tmp文件夹是否存在
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        # 获取tmp文件夹内所有文件和子目录的列表
        files = os.listdir(directory_path)

        # 检查是否有文件
        if files:
            # 存在文件或子目录，则进行删除操作
            for filename in files:
                file_path = os.path.join(directory_path, filename)
                try:
                    # 检查是否为文件或符号链接，是的话则删除
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    # 检查是否为目录，是的话则递归删除整个目录
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"删除文件{file_path}时发生错误: {e}")
            print("tmp文件夹内的所有文件和子目录已被删除。")
        else:
            print("tmp文件夹内没有文件或子目录。")
    else:
        os.mkdir(directory_path)
        print("根目录下不存在tmp文件夹，创建。")


def merge_domain():
    # 获取到当前时间，构建文件名
    txtname = mak_date_folder() + ".txt"
    # 设定源文件夹和目标文件夹路径
    source_folder = "tmp"
    target_folder = "domain"
    target_file_path = os.path.join(target_folder, txtname)

    # 创建目标文件夹如果它不存在
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # 创建一个空的集合用于存储唯一的内容
    unique_lines = set()

    # 遍历文件夹内的所有txt文件
    for filename in os.listdir(source_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(source_folder, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                unique_lines.update(
                    line.strip() for line in file if line.strip()
                )  # strip去除空白字符，并更新到集合中，空行被忽略

    # 将唯一内容写入目标文件
    with open(target_file_path, "w", encoding="utf-8") as target_file:
        for line in unique_lines:
            target_file.write(f"{line}\n")  # 换行符确保每条记录占一行

    print(f"所有唯一内容已经合并到 {target_file_path} 中。")


def get_end_nub(driver):
    time.sleep(2)  # 先等待5秒，确保页面加载完成
    # 使用find_elements定位所有class属性包含"num"的<a>标签
    elements = driver.find_elements(By.CSS_SELECTOR, ".num")
    # 遍历元素列表并获取它们的文本
    for element in elements:
        text = element.text
        if "..." in text:
            clean_text = text.replace("...", "")
            return clean_text  # 如果找到包含"..."的文本，进行清理并返回
    # 如果没有找到任何符合条件的元素文本，或者列表为空，可以返回None或报错
    return None


def open_link(search, driver, page):
    # 打开新标签页并访问被监管企业信息查询页面
    driver.execute_script("window.open('about:blank', '_blank');")  # 打开一个新标签页
    driver.switch_to.window(driver.window_handles[1])
    driver.get(f"https://beian.tianyancha.com/search/{search}/p{page}")
    check_man_machine_verification(driver)


def sav_domin(driver):
    # 找到所有class为'ranking-ym'的<span>元素
    span_elements = driver.find_elements(By.CSS_SELECTOR, "span.ranking-ym")

    # 创建一个空集合来存储唯一的内容
    unique_contents = set()

    # 遍历找到的元素，并获取它们的文本内容
    for span in span_elements:
        text = span.text.strip()
        # 过滤域名字符（根据需要自定义过滤规则）
        filtered_text = re.sub(r"[^a-zA-Z0-9.-]", "", text)
        unique_contents.add(filtered_text)

    # 将唯一的内容保存到domin.txt文件中
    formatted_date = "tmp/" + mak_date_folder() + ".txt"  # 构建文件路径
    with open(formatted_date, "w", encoding="utf-8") as f:
        for content in unique_contents:
            f.write(f"{content}\n")
    return formatted_date


# 检查人机验证方法
def check_man_machine_verification(driver):
    # 出现验证码元素
    pagination_elements = driver.find_elements(By.ID, "pagination-seo")
    # 检查是否存在ID为"captcha"的元素
    captcha_elements = driver.find_elements(By.ID, "captcha-text")
    if pagination_elements or captcha_elements:
        print("出现人机验证，请20秒内完成验证，然后程序会自动重启")
        time.sleep(20)
        # 重启当前程序
        os.startfile(__file__)
        sys.exit()
    else:
        return False


def login_web(driver):
    try:
        # 打开天眼查登录页面
        driver.get("https://www.tianyancha.com/login")

        # 当`found`为True时，跳出循环
        found = False
        while not found:
            # 尝试重新获取<a>标签元素，以避免StaleElementReferenceException
            try:
                links = driver.find_elements(By.XPATH, "//a")
                for link in links:
                    href = link.get_attribute("href")
                    if (
                        href
                        and "https://www.tianyancha.com/usercenter/personalcenter"
                        in href
                    ):
                        found = True
                        print("登录成功")
                        break  # 成功后跳出循环

            except StaleElementReferenceException:
                # 如果出现StaleElementReferenceException，则重新获取元素
                print("出现了StaleElementReferenceException，重新获取元素。")

            # 未找到，等待一段时间
            if not found:
                print("等待用户登录...")
                time.sleep(10)
    except Exception as e:
        # 处理所有其他异常
        print("运行过程中发生了异常：", e)


# 批量关闭标签方法
def close_blank_tabs(driver):
    main_window_handle = driver.current_window_handle  # 主窗口
    blank_handles_to_close = []  # 空白标签句柄列表

    # 收集所有空白标签页句柄
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if driver.current_url == "about:blank":
            blank_handles_to_close.append(handle)

    # 关闭所有收集到的空白标签页
    for handle in blank_handles_to_close:
        driver.switch_to.window(handle)
        driver.close()  # 关闭当前空白标签页
    # 切换回主窗口
    driver.switch_to.window(main_window_handle)


def main():

    # driver_path = "F:\Python\domainGet\edgedriver_win64\msedgedriver.exe" # 替换为你的msedgedriver路径
    # service = Service(driver_path)
    # driver = webdriver.Edge(service=service)
    global page
    driver = webdriver.Edge()
    driver.minimize_window()  # 最小化窗口

    while True:  # 添加一个循环，让用户可以决定是否重新搜索
        delete_tmp()  # 删除
        page = int(1)
        search = input("关键字：")
        driver.maximize_window()  # 最大化窗口
        login_web(driver)  # 打开页面并手动登录，传递driver

        result = check_man_machine_verification(driver)  # 检查人机验证
        if not result:
            print("验证通过")
            open_link(search, driver, page)  # 打开新标签，传递driver和搜索词

            time.sleep(2)  # 等待2秒
            elements = driver.find_elements(By.CLASS_NAME, "pagination-seo")
            if len(elements) > 0:
                time.sleep(5)  # 再次等待5秒
                endnub = get_end_nub(driver)  # 获取最后一页
                if endnub is None:
                    print("未能获取到结束页码，将页码默认设置为 2")
                    superend = 2
                else:
                    superend = int(endnub)
                # 默认标签数
                label = 0
                if superend < Maximum_tag:
                    # 在注册窗口之前创建一个进度条实例
                    pbar = tqdm(
                        total=superend,
                        initial=page,
                        desc="已完成：",
                        unit="页",
                    )
                    # 存在最后一页
                    for page in range(1, superend + 1):
                        label += 1
                        time.sleep(2)  # 等待2秒
                        open_link(search, driver, page)  # 打开新标签
                        sav_domin(driver)  # 保存域名，传递driver
                        pbar.update(1)  # 更新进度条

                        # 计算剩余标签数
                        superlabel = Max_tag_off - label
                        # 标签到达Max_tag_off关闭空标签
                        if label == Max_tag_off:

                            # 关闭空白标签页的逻辑提取到一个函数中
                            close_blank_tabs(driver)

                            label = 0  # 重置标签计数器

                    # 合并所有域名到domain
                    merge_domain()
                    driver.minimize_window()  # 最小化窗口
                    pbar.close()  # 关闭进度条
                else:
                    driver.minimize_window()  # 最小化窗口
                    print(f"大于{Maximum_tag}页,为了减轻压力，请重新输入搜索内容")
            else:
                # 出现验证码元素
                verify_elements = driver.find_elements(By.ID, "pagination-seo")
                if verify_elements:
                    print("登录时出现人机验证，请20秒内完成验证，然后程序会自动重启")
                    time.sleep(20)
                    # 重启当前程序
                    os.startfile(__file__)
                    sys.exit()
                else:
                    # 不存在最后一页
                    mtime = sav_domin(driver)  # 保存域名，传递driver
                    yidong_text(mtime)  # 移动文件
                    driver.minimize_window()  # 最小化

            # 询问用户是否想要再次搜索
            choice = input("是否想要再次执行搜索？请输入 'yes' 继续或按任意键退出: ")
            if choice.lower() != "yes":
                # 关闭空白标签页的逻辑提取到一个函数中
                close_blank_tabs(driver)
                break  # 如果用户不输入 'yes'，跳出循环结束程序
        else:
            print("验证未通过")
    mak_console_log()
    driver.quit()  # 在循环外关闭浏览器


if __name__ == "__main__":
    main()
