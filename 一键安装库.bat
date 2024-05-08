@echo off
setlocal enabledelayedexpansion

REM 设置控制台编码为UTF-8
chcp 65001

REM 定义需要安装的Python包
set "PACKAGES=attrs beautifulsoup4 certifi cffi charset-normalizer colorama decorator exceptiongroup glob2 h11 idna imageio imageio-ffmpeg importlib-metadata MouseInfo moviepy numpy opencv-python outcome packaging pillow pip platformdirs proglog PyAutoGUI pycparser PyGetWindow PyMsgBox pyperclip PyRect PyScreeze PySocks python-dateutil python-dotenv pytweening regex requests selenium setuptools six sniffio sortedcontainers soupsieve tomli tqdm trio trio-websocket typing_extensions urllib3 webdriver-manager wechatarticles wsproto yapf zipp
"

REM 循环遍历所有包并尝试安装，使用阿里云的镜像源
for %%p in (%PACKAGES%) do (
    echo 正在检查并尝试安装 %%p...
    pip install %%p -i https://mirrors.aliyun.com/pypi/simple/
)

echo.
echo 所有必要的Python包安装检查完成。
pause