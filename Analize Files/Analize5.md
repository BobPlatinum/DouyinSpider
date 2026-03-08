# Analize5.md — python/Lib/site-packages 全部第三方库逐个解释

本文档对 `python/Lib/site-packages` 目录里的**每一个第三方库**逐个说明：它是干什么的、在本项目里有没有用到、以及和其他库的关系。

按功能分组排列，方便阅读。

---

## 一、爬虫核心（本项目直接使用）

### DrissionPage `4.1.0.17`
**本项目核心库，直接使用。**  
一个国产的浏览器自动化 + 网络请求二合一库。相比 Selenium，它可以直接接管已经打开的浏览器，速度更快、配置更简单。本项目用它来控制 Chrome 浏览器打开网页、点击按钮、抓取页面数据。  
`from DrissionPage import ChromiumPage, ChromiumOptions`

### DataRecorder `3.6.2`
**本项目间接使用（DrissionPage 的依赖）。**  
DrissionPage 的配套数据记录工具，负责把抓到的数据方便地写入文件（CSV、Excel 等）。DrissionPage 内部会自动调用它。

### DownloadKit `2.0.7`
**本项目间接使用（DrissionPage 的依赖）。**  
DrissionPage 的配套文件下载工具，支持多线程下载、断点续传。DrissionPage 内部会用它来处理文件下载任务。

---

## 二、数据处理（本项目直接使用）

### pandas `2.2.3`
**本项目直接使用。**  
Python 里最强的数据分析库，可以把数据装进"表格"（DataFrame）里进行增删改查、排序、统计、导出等操作。本项目用它来处理爬取下来的 CSV 和 Excel 数据。  
`import pandas as pd`

### openpyxl `3.1.5`
**本项目直接使用。**  
专门读写 `.xlsx` 格式 Excel 文件的库。pandas 在写 Excel 时会在底层调用它。本项目的 `excel_tool.py` 同时直接使用了它。  
`import openpyxl`

### et_xmlfile `2.0.0`
**间接依赖（openpyxl 的依赖）。**  
openpyxl 写 Excel 文件时在底层使用的 XML 处理工具，不需要直接操作它。

### python-dateutil `2.9.0`
**本项目直接使用。**  
非常强大的日期解析库，能把各种格式的日期字符串（"2024年1月1日"、"Jan 1, 2024"、"2024-01-01"等）自动识别并转换为 Python 的 datetime 对象。  
`from dateutil.parser import parse`  
`from dateutil.relativedelta import relativedelta`

### pytz `2024.2`
**间接依赖（pandas/dateutil 的依赖）。**  
时区处理库，提供世界各地时区数据。pandas 和 dateutil 在处理带时区的时间时会用到它。

### tzdata `2024.2`
**间接依赖（pytz 的依赖）。**  
时区数据库的纯 Python 版本，存放 IANA 时区规则（和 pytz 配合使用）。

### numpy `2.2.1`
**间接依赖（pandas 的依赖）。**  
Python 科学计算的基础库，提供高效的多维数组和数学运算。pandas 底层大量依赖它，本项目代码没有直接调用，但 pandas 运行时必须有它。

---

## 三、HTML/网络请求（本项目直接/间接使用）

### lxml `5.3.0`
**本项目直接使用。**  
高性能的 XML/HTML 解析库，用 C 语言编写，速度极快。本项目用它来解析网页的 HTML 结构，提取所需数据。  
`from lxml import etree`

### requests `2.32.3`
**间接依赖（DrissionPage 的依赖）。**  
Python 最常用的 HTTP 请求库，简单易用。虽然本项目代码里没有直接写 `import requests`，但 DrissionPage 内部会用它发送普通的 HTTP 请求（SessionPage 模式）。

### urllib3 `2.3.0`
**间接依赖（requests 的依赖）。**  
requests 库底层使用的 HTTP 连接池管理库，负责真正建立 TCP 连接、发送请求、处理响应。

### certifi `2024.12.14`
**间接依赖（requests 的依赖）。**  
提供一份可信的 SSL/TLS 根证书集合，requests 在进行 HTTPS 请求时用它来验证服务器证书，防止假冒网站。

### charset-normalizer `3.4.1`
**间接依赖（requests 的依赖）。**  
自动检测和修正文本编码（比如判断一段文字是 UTF-8 还是 GBK），requests 用它来正确解析网页内容的编码。

### idna `3.10`
**间接依赖（requests 的依赖）。**  
处理国际化域名（如中文域名 `中国.cn`）的编码转换，把它转成 ASCII 兼容格式，requests 在解析 URL 时会用到。

### cssselect `1.2.0`
**间接依赖（lxml 的依赖）。**  
让 lxml 支持 CSS 选择器语法（如 `div.title > a`）来查找 HTML 元素，lxml 内部使用。

### soupsieve `2.6`
**间接依赖（beautifulsoup4 的依赖）。**  
BeautifulSoup 的 CSS 选择器引擎，bs4 在使用 `soup.select()` 时内部调用它。

### bs4 / beautifulsoup4 `4.12.3`
**本项目未直接使用，但已安装。**  
网页解析利器，可以用简单的方式从 HTML 中提取数据（比 lxml 更易上手，但速度稍慢）。本项目使用 lxml，bs4 是冗余安装。

### requests-file `2.1.0`
**间接依赖。**  
让 requests 库支持 `file://` 协议（读取本地文件），通常是其他库的依赖。

### simplejson `3.19.3`
**间接依赖。**  
Python 内置 `json` 模块的增强版，解析速度更快、对特殊格式支持更好，部分库会优先使用它。

---

## 四、加密与安全（mitmproxy 的依赖链）

### cryptography `44.0.0`
**间接依赖（mitmproxy、pyOpenSSL 的依赖）。**  
Python 里最全面的加密库，提供 AES、RSA、TLS 等各种加密算法的实现。mitmproxy 用它来处理 HTTPS 流量的加解密，本项目没有直接用。

### pyOpenSSL `24.3.0`
**间接依赖（mitmproxy、requests 的依赖）。**  
对 OpenSSL 的 Python 封装，提供 SSL/TLS 证书操作等功能。requests 和 mitmproxy 都会用到。

### cffi `1.17.1`
**间接依赖（cryptography 的依赖）。**  
C Foreign Function Interface，让 Python 能直接调用 C 语言写的函数。cryptography 库底层用 C 实现高性能加密，cffi 是桥梁。

### pycparser `2.22`
**间接依赖（cffi 的依赖）。**  
C 语言代码的解析器，cffi 在解析 C 头文件时使用，属于底层工具。

### pycryptodome `3.21.0`
**间接依赖。**  
另一个加密库（PyCryptodome），提供 AES、DES、RSA 等加密算法，是老版 PyCrypto 库的替代品。

### pyasn1 `0.6.1`
**间接依赖（pyOpenSSL、service-identity 的依赖）。**  
ASN.1（一种数据序列化格式，常用于证书和网络协议）的 Python 解析库，处理 SSL 证书时会用到。

### pyasn1-modules `0.4.1`
**间接依赖（pyasn1 的扩展）。**  
pyasn1 的补充模块，包含常用 ASN.1 数据结构定义（如 X.509 证书结构）。

### service-identity `24.2.0`
**间接依赖（mitmproxy/Twisted 的依赖）。**  
验证 TLS 证书身份（服务器域名是否与证书匹配），用于安全连接校验。

### passlib `1.7.4`
**间接依赖（mitmproxy 的依赖）。**  
密码哈希库，支持 bcrypt、MD5、SHA 等多种哈希算法，常用于存储用户密码。

### OpenSSL（pyOpenSSL 的包名）
**同 pyOpenSSL，见上。**

---

## 五、网络抓包工具 mitmproxy（本项目未使用）

### mitmproxy `11.0.2`
**本项目未使用。**  
一个强大的交互式中间人代理工具（Man-In-The-Middle Proxy），可以拦截、查看、修改 HTTP/HTTPS 流量。常用于抓包分析、调试接口、逆向分析 App 通信。本项目里有它可能是原作者用来分析目标网站接口用的，爬虫运行不需要它。

### mitmproxy_rs `0.10.7`
**mitmproxy 的依赖（Rust 实现的核心组件）。**  
mitmproxy 用 Rust 语言重写的高性能核心部分，处理底层网络数据包。

### mitmproxy-windows `0.10.7`
**mitmproxy 的 Windows 平台组件。**  
mitmproxy 在 Windows 上透明代理功能的支持包。

### pydivert `2.1.0`
**mitmproxy 的 Windows 依赖。**  
在 Windows 上拦截和重定向网络数据包的库（基于 WinDivert 驱动），mitmproxy 在 Windows 上实现透明代理时使用它。

### kaitaistruct `0.10`
**间接依赖（mitmproxy 的依赖）。**  
Kaitai Struct 的 Python 运行时，用于解析各种二进制文件格式（如网络协议数据包）。

### ruamel.yaml `0.18.6` / ruamel.yaml.clib `0.2.12`
**间接依赖（mitmproxy 的依赖）。**  
功能比 PyYAML 更全的 YAML 读写库，支持保留注释、圆角引号等。mitmproxy 用 YAML 格式存储配置文件。

### msgpack `1.1.0`
**间接依赖（mitmproxy 的依赖）。**  
MessagePack 序列化格式的实现，比 JSON 更紧凑，速度更快，适合网络传输。

### publicsuffix2 `2.20191221`
**间接依赖（mitmproxy/tldextract 的依赖）。**  
提供公共后缀列表（Public Suffix List），用于判断域名的注册级别（如 `.com.cn` 是二级后缀）。

### tldextract `5.1.3`
**间接依赖（mitmproxy 的依赖）。**  
从 URL 中精确提取顶级域名（TLD）、二级域名、子域名，比正则更准确。

### urwid `2.6.16`
**间接依赖（mitmproxy 的依赖）。**  
终端 UI 框架，在终端里绘制文本界面（按钮、列表、输入框等）。mitmproxy 的交互式终端界面就是用它写的。

### wcwidth `0.2.13`
**间接依赖（urwid 的依赖）。**  
计算字符在终端里占几列宽（中文字符占 2 列，英文占 1 列），urwid 排版终端界面时需要它。

### prettytable `3.12.0`
**间接依赖（mitmproxy 的依赖）。**  
在终端里打印漂亮的 ASCII 表格，mitmproxy 展示连接信息时用到。

### zstandard `0.23.0`
**间接依赖（mitmproxy 的依赖）。**  
Facebook 开发的 Zstandard 压缩算法的 Python 绑定，速度极快，压缩率高。mitmproxy 处理压缩的 HTTP 响应时使用。

### Brotli `1.1.0`
**间接依赖（mitmproxy/requests 的依赖）。**  
Google 开发的 Brotli 压缩算法实现，现代浏览器和服务器常用此格式压缩网页内容。

### sortedcontainers `2.4.0`
**间接依赖（mitmproxy/trio 的依赖）。**  
提供高性能的有序数据结构（SortedList、SortedDict、SortedSet），纯 Python 实现但速度接近 C 扩展。

### wsproto `1.2.0`
**间接依赖（mitmproxy 的依赖）。**  
WebSocket 协议的纯 Python 实现（仅协议解析，不含网络 I/O），mitmproxy 用它处理 WebSocket 流量。

### h11 `0.14.0`
**间接依赖（mitmproxy/httpx 的依赖）。**  
HTTP/1.1 协议的纯 Python 实现（仅协议解析），mitmproxy 用它解析 HTTP 请求和响应。

### h2 `4.1.0`
**间接依赖（mitmproxy/httpx 的依赖）。**  
HTTP/2 协议的纯 Python 实现，mitmproxy 支持拦截 HTTP/2 流量时使用。

### hpack `4.0.0`
**间接依赖（h2 的依赖）。**  
HTTP/2 的 Header 压缩算法（HPACK）实现，h2 处理 HTTP/2 请求头时使用。

### hyperframe `6.0.1`
**间接依赖（h2 的依赖）。**  
HTTP/2 帧（Frame）格式的解析库，h2 内部使用。

---

## 六、异步并发框架（本项目未使用）

### trio `0.28.0`
**本项目未使用。**  
Python 的异步并发库，提供比 asyncio 更友好的 API，专注于"结构化并发"。mitmproxy 用它作为异步 I/O 框架处理并发连接。

### trio-websocket `0.11.1`
**trio 的扩展，本项目未使用。**  
基于 trio 的 WebSocket 客户端/服务端实现。

### sniffio `1.3.1`
**间接依赖（trio/asyncio 的辅助）。**  
检测当前代码运行在哪个异步框架里（trio 还是 asyncio），让库代码能兼容多种异步环境。

### outcome `1.3.0`
**间接依赖（trio 的依赖）。**  
封装"计算结果"的工具，可以表示一个操作的成功值或异常，trio 内部用它传递异步任务结果。

### exceptiongroup `1.2.2`
**间接依赖（trio 的依赖）。**  
Python 3.11 新增的异常组（ExceptionGroup）功能的向后兼容实现，让 Python 3.10 也能使用。

### aioquic `1.2.0`
**本项目未使用。**  
QUIC 协议（HTTP/3 底层传输协议）和 HTTP/3 的纯 Python 实现。QUIC 是 Google 开发的新一代网络传输协议，比 TCP 更快。mitmproxy 11.x 版本新增了 HTTP/3 支持，aioquic 是它的依赖。

### asgiref `3.8.1`
**间接依赖。**  
ASGI（异步服务器网关接口）规范的参考实现，Django、Channels 等框架使用，通常作为异步 Web 框架的基础。

### tornado `6.4.2`
**本项目未使用。**  
一个高性能的 Python Web 框架和异步网络库，擅长处理大量并发长连接（如 WebSocket）。这里可能是某个库的依赖。

---

## 七、Web 框架 Flask（本项目未使用）

### Flask `3.1.0`
**本项目未使用。**  
Python 最流行的轻量级 Web 框架，几十行代码就能写一个网站后端。本项目里有它可能是原作者预留了一个本地 Web 管理界面的想法，但目前没有实现。

### Werkzeug `3.1.3`
**间接依赖（Flask 的依赖）。**  
Flask 底层使用的 WSGI 工具库，提供路由、请求/响应对象、调试服务器等功能。Flask 本质上是对 Werkzeug 的封装。

### Jinja2 `3.1.5`
**间接依赖（Flask 的依赖）。**  
Python 最常用的模板引擎，Flask 用它来渲染 HTML 模板（把变量填入 HTML 文件中）。

### MarkupSafe `3.0.2`
**间接依赖（Jinja2 的依赖）。**  
安全地处理 HTML 中的特殊字符（如把 `<script>` 转义成 `&lt;script&gt;`），Jinja2 防止 XSS 注入时使用。

### itsdangerous `2.2.0`
**间接依赖（Flask 的依赖）。**  
安全地对数据进行签名和序列化，Flask 用它来生成/验证 session cookie，防止数据被篡改。

### blinker `1.9.0`
**间接依赖（Flask 的依赖）。**  
Python 的信号/事件系统库，Flask 用它来发送钩子信号（如请求开始、请求结束的事件通知）。

### click `8.1.8`
**间接依赖（Flask、mitmproxy 的依赖）。**  
Python 命令行参数解析库，比 argparse 更简洁优雅。Flask 的 `flask run` 命令就是用它写的。

### colorama `0.4.6`
**间接依赖（click/mitmproxy 的依赖）。**  
让 Windows 终端支持 ANSI 彩色文字输出，使 `print("\033[31m红色\033[0m")` 在 Windows 上也能正常显示颜色。

---

## 八、科学计算（本项目未使用）

### scipy `1.15.1`
**本项目未使用。**  
建立在 numpy 之上的科学计算库，提供数值积分、微分方程、信号处理、线性代数、统计等功能。体积最大（118.8MB），本项目完全没有用到，是最值得删除的包。

### scikit-learn `1.6.1`（sklearn）
**本项目未使用。**  
Python 最流行的机器学习库，提供分类、回归、聚类、降维等算法，以及数据预处理工具。本项目没有用到任何机器学习功能，是第二大无用包（40.5MB）。

### joblib `1.4.2`
**间接依赖（scikit-learn 的依赖）。**  
提供轻量级任务并行化和结果缓存，scikit-learn 用它加速模型训练时的并行计算。

### threadpoolctl `3.5.0`
**间接依赖（scikit-learn/numpy 的依赖）。**  
控制 numpy、scipy 等底层 BLAS/OpenMP 库的线程数量，防止不同库之间争抢线程资源。

---

## 九、生物信息（本项目未使用）

### biopython `1.85`（Bio、BioSQL）
**本项目完全未使用。**  
生物信息学领域的工具库，提供 DNA/RNA/蛋白质序列分析、基因组数据处理、PDB 结构文件读取等功能。出现在这个爬虫项目里纯属意外，很可能是原环境里装了别的项目用到的包，被一起打包进来了。

---

## 十、PDF 处理（本项目未使用）

### PyMuPDF `1.25.2`（fitz）
**本项目未使用。**  
高性能的 PDF/文档处理库（底层基于 MuPDF），可以读取、渲染、编辑 PDF 文件，提取文字、图片、表格等。体积较大（约 40MB），本项目没有用到。

---

## 十一、Selenium 浏览器自动化（本项目未使用，已被 DrissionPage 替代）

### selenium `4.27.1`
**本项目未使用（DrissionPage 已替代其功能）。**  
Python 最经典的浏览器自动化测试框架，通过 WebDriver 协议控制 Chrome/Firefox 等浏览器。DrissionPage 在功能上覆盖了 Selenium，且更易使用，本项目直接用 DrissionPage，Selenium 是冗余安装。

### websocket-client `1.8.0`
**间接依赖（Selenium 的依赖）。**  
WebSocket 客户端库，Selenium 4.x 通过 WebSocket 与浏览器 DevTools 协议通信时使用。

---

## 十二、Word 文档处理（本项目未使用）

### python-docx `1.1.2`（docx）
**本项目未使用。**  
读写 `.docx` 格式 Word 文档的库，可以创建、修改 Word 文件，添加段落、表格、图片等。本项目只处理 Excel，没有用到。

---

## 十三、LDAP 目录服务（本项目未使用）

### ldap3 `2.9.1`
**本项目未使用。**  
LDAP（轻量级目录访问协议）客户端库，用于连接企业内网的用户目录（如 Active Directory）进行用户认证和查询。出现在爬虫项目里较为罕见，可能是原环境安装的。

---

## 十四、图表可视化（本项目未使用）

### pyecharts `2.0.7`
**本项目未使用。**  
基于百度 ECharts 的 Python 图表库，可以生成各种交互式图表（折线图、柱状图、地图、词云等）并导出为 HTML 文件。本项目只输出 Excel，没有用到。

---

## 十五、系统工具

### psutil `6.1.1`
**间接依赖（DrissionPage/mitmproxy 的依赖）。**  
获取系统信息的库（CPU 使用率、内存占用、进程列表、网络连接等）。DrissionPage 用它来管理浏览器进程（检测浏览器是否在运行、关闭浏览器等）。

### filelock `3.17.0`
**间接依赖（DrissionPage/其他库的依赖）。**  
跨平台的文件锁实现，防止多个进程同时写同一个文件造成数据混乱。

### pyperclip `1.9.0`
**间接依赖（DrissionPage 的依赖）。**  
跨平台的剪贴板操作库，可以读取/写入系统剪贴板内容。DrissionPage 在某些操作（如模拟粘贴）中会用到。

---

## 十六、代理工具

### PySocks `1.7.1`（socks.py）
**间接依赖（requests/urllib3 的依赖）。**  
SOCKS4/SOCKS5 代理协议支持，让 Python 的网络请求能通过 SOCKS 代理服务器（如 Shadowsocks）发出。

---

## 十七、打包与开发工具（运行时不需要）

### pip `24.2`
**打包工具，运行时不需要。**  
Python 的包管理器，用来安装/卸载/更新第三方库（`pip install xxx`）。放在 site-packages 里是便于独立 Python 环境自我管理，Conda 环境里不需要它。

### setuptools `75.1.0`
**打包工具，运行时不需要。**  
Python 包的构建和安装工具，是 `python setup.py install` 的基础。安装第三方库时会用到，但项目运行时不需要。

### wheel `0.44.0`
**打包工具，运行时不需要。**  
Python 的二进制包格式（`.whl` 文件）的构建工具，`pip install` 时会用 `.whl` 文件安装，但运行时不需要 wheel 库本身。

### pkg_resources
**间接依赖（setuptools 的一部分）。**  
setuptools 提供的运行时包资源访问工具，部分库用它来读取自己的版本信息或内置资源文件。

---

## 十八、类型系统与兼容性工具

### typing_extensions `4.11.0`
**广泛使用的间接依赖。**  
把 Python 新版本的类型注解功能（如 `TypeAlias`、`Protocol`、`Literal`）向后移植到旧版本 Python，几乎所有现代库都依赖它。

### attrs `24.3.0` / attr
**间接依赖（trio/mitmproxy 的依赖）。**  
简化 Python 类的定义，自动生成 `__init__`、`__repr__`、`__eq__` 等方法，让代码更简洁。

### six `1.17.0`（six.py）
**间接依赖（老库的兼容层）。**  
Python 2 和 Python 3 兼容库，提供跨版本的统一 API。现在 Python 2 已死，但一些老库还依赖它。

### pyparsing `3.2.0`
**间接依赖（packaging 等库的依赖）。**  
通用的文本解析框架，可以用 Python 代码定义语法规则来解析结构化文本。

### pyperclip `1.9.0`
**见"系统工具"章节。**

---

## 十九、其他杂项

### colorama `0.4.6`
**见"Web 框架 Flask"章节。**

### simplejson `3.19.3`
**见"HTML/网络请求"章节。**

---

## 汇总表

| 库名 | 版本 | 本项目是否用到 | 分类 | 可否删除（已有Conda） |
|---|---|---|---|---|
| DrissionPage | 4.1.0.17 | ✅ 直接使用 | 爬虫核心 | 可删（Conda已有） |
| DataRecorder | 3.6.2 | ✅ 间接（DrissionPage依赖） | 爬虫核心 | 可删 |
| DownloadKit | 2.0.7 | ✅ 间接（DrissionPage依赖） | 爬虫核心 | 可删 |
| pandas | 2.2.3 | ✅ 直接使用 | 数据处理 | 可删（Conda已有） |
| openpyxl | 3.1.5 | ✅ 直接使用 | 数据处理 | 可删（Conda已有） |
| lxml | 5.3.0 | ✅ 直接使用 | HTML解析 | 可删（Conda已有） |
| python-dateutil | 2.9.0 | ✅ 直接使用 | 数据处理 | 可删（Conda已有） |
| numpy | 2.2.1 | ✅ 间接（pandas依赖） | 科学计算 | 可删（Conda已有） |
| requests | 2.32.3 | ✅ 间接（DrissionPage依赖） | 网络请求 | 可删（Conda已有） |
| scipy | 1.15.1 | ❌ 完全未用 | 科学计算 | **优先删除（118MB）** |
| sklearn | 1.6.1 | ❌ 完全未用 | 机器学习 | **优先删除（40MB）** |
| selenium | 4.27.1 | ❌ 未用（DrissionPage替代） | 浏览器自动化 | **优先删除（26MB）** |
| pymupdf / fitz | 1.25.2 | ❌ 完全未用 | PDF处理 | **优先删除（~40MB）** |
| Bio / biopython | 1.85 | ❌ 完全未用 | 生物信息 | **优先删除（16MB）** |
| mitmproxy | 11.0.2 | ❌ 完全未用 | 网络抓包 | 可删（6MB） |
| ldap3 | 2.9.1 | ❌ 完全未用 | 目录服务 | 可删 |
| pyecharts | 2.0.7 | ❌ 完全未用 | 图表 | 可删 |
| flask | 3.1.0 | ❌ 完全未用 | Web框架 | 可删 |
| tornado | 6.4.2 | ❌ 完全未用 | 异步Web | 可删 |
| aioquic | 1.2.0 | ❌ 完全未用 | 网络协议 | 可删 |
| trio | 0.28.0 | ❌ 完全未用 | 异步框架 | 可删 |
| python-docx | 1.1.2 | ❌ 完全未用 | Word处理 | 可删 |
| psutil | 6.1.1 | ✅ 间接（DrissionPage依赖） | 系统工具 | 可删（Conda已有） |
| pip / setuptools / wheel | - | ❌ 运行时不需要 | 打包工具 | 可删 |

> **结论：整个 `python/` 目录已被 Conda 环境完全替代，推荐直接整体删除（见 Analize4.md 方案一）。**

