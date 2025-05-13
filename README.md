# mitmproxy抓包工具

## 1. 启动命令

使用以下命令启动 `mitmweb` 并加载 `crawling_data_hook.py` 脚本：

```
mitmweb -s crawling_data_hook.py --set upstream_proxy=http://127.0.0.1:10808 --set flow_detail=0 --listen-port 8008 --mode regular
```
```
mitmweb -s crawling_data_hook.py --set upstream_proxy=http://127.0.0.1:7897 --set flow_detail=0 --listen-port 8008 --mode regular
```

## 2. 设置手机 Wi-Fi HTTP 代理

在 Android 手机上设置 HTTP 代理：

- **代理方式**：手动
- **代理主机名**：电脑 IP（如 `192.168.1.100`）
- **代理端口**：`8008`（或你 `mitmproxy` 设置的端口）

⚠️ **注意**：
- 手机和电脑必须在同一局域网（同一个 Wi-Fi）
- 代理端口要匹配（`mitmproxy` 用的是多少，手机就填多少）

## 3. 安装证书

在手机浏览器中访问 [http://mitm.it](http://mitm.it)（使用系统浏览器），下载并安装证书。

## 4. 启动应用并抓取请求

访问 [http://127.0.0.1:10808](http://127.0.0.1:10808) 启动应用，可以看到请求被抓取到。在 [response](file://C:\work\crawling_app_tools\crawling_data_hook.py#L86-L110) 中可以运行自定义脚本，进行逻辑处理。
