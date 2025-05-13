from mitmproxy import http
import requests
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
from pathlib import Path


"""
1. 启动命令
mitmweb -s crawling_data_hook.py --set upstream_proxy=http://127.0.0.1:10808 --set flow_detail=0 --listen-port 8008 --mode regular
mitmweb -s crawling_data_hook.py --set upstream_proxy=http://127.0.0.1:7897 --set flow_detail=0 --listen-port 8008 --mode regular

2. 设置手机 Wi-Fi HTTP 代理
在 Android 手机上设置：
代理方式：手动
代理主机名：电脑 IP（如 192.168.1.100）
代理端口：8008（或你 mitmproxy 设置的端口）

⚠️ 注意：
手机和电脑必须在同一局域网（同一个 Wi-Fi）
代理端口要匹配（mitmproxy 用的是多少，手机就填多少）

3. 在手机浏览器中访问 http://mitm.it（使用系统浏览器）
证书下载并安装

4. 访问 http://127.0.0.1:10808 启动APP
可以看到请求被抓取到
在 response 中可以跑自定义脚本，作逻辑处理
"""

# 创建下载目录
download_dir = Path("./downloads-mp4")
download_dir.mkdir(exist_ok=True)

# 定义保存URL的文件路径
url_file_path = Path("./urls.txt")
url_file_path.touch(exist_ok=True)

# 创建线程池
download_pool = ThreadPoolExecutor(max_workers=50)

# 用于跟踪正在处理的URL，避免重复写入文件
processed_urls = set()
processed_urls_lock = threading.Lock()


# 初始化 processed_urls 集合
def load_processed_urls():
    if url_file_path.exists():
        with open(url_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                processed_urls.add(line.strip())
        print(f"已从 {url_file_path} 加载 {len(processed_urls)} 条已处理的 URL。")

# 脚本启动时加载已处理的URL
load_processed_urls()


def download_video(url, save_path):
    """
    下载数据的函数
    """
    try:
        print(f"⬇️ 正在下载数据到: {save_path}")
        r = requests.get(url, stream=True, timeout=120)
        r.raise_for_status()

        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print(f"✅ 数据下载完成: {save_path}")
        return True
    except Exception as e:
        print(f"❌ 下载失败: {str(e)}")
        return False
    finally:
        # 无论成功失败，都从下载集合中移除
        with processed_urls_lock:
            if url in processed_urls:
                processed_urls.remove(url)


def response(flow: http.HTTPFlow):
    if not flow.response:
        return
    if "mp4" in flow.request.pretty_url or "webp" in flow.request.pretty_url:
        url = flow.request.pretty_url
        print("📹 数据链接:", url)
        
        # 检查URL是否已经处理过
        with processed_urls_lock:
            if url in processed_urls:
                print(f"⚠️ 该数据链接已记录: {url}")
                return
        
        try:
            # 将URL写入文件
            with open(url_file_path, 'a', encoding='utf-8') as f:
                f.write(url + '\n')
            print(f"✅ URL已保存到文件: {url_file_path}")
            
            # 将URL添加到已处理集合中
            with processed_urls_lock:
                processed_urls.add(url)

        except Exception as e:
            print(f"❌ 处理数据链接失败: {str(e)}")

def start_download():
    with processed_urls_lock:
        for url in processed_urls:
            if ".mp4" not in url:
                print(f"⚠️ 不是mp4文件: {url}")
                continue
            # 从URL中提取文件名
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)

            # 完整的保存路径
            save_path = os.path.join(download_dir, filename)

            # 检查是否已经下载过该数据
            if os.path.exists(save_path):
                print(f"⚠️ 文件已存在: {save_path}")
                return

            # 使用线程池提交下载任务
            download_pool.submit(download_video, url, save_path)

if __name__ == '__main__':
    start_download()