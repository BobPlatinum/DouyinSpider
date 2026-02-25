# Analize4.md — python/ 目录清理策划

本文档记录：为什么可以删除 `python/` 目录、删之前需要做什么准备、以及三种不同力度的删除方案。

---

## 1. 背景与前提

### 1.1 `python/` 目录是什么

`python/` 是项目自带的一个**可移植 Python 3.10 运行环境**，内部含有 `conda-meta/`，说明它原本是从某个 Conda 环境打包出来的。它的作用是让项目"开箱即用"——不需要用户自己安装 Python 和依赖库，直接双击 bat 就能跑。

### 1.2 现在为什么可以删

你已经完成了以下操作：

- 新建了 Conda 环境 `Spider`（路径：`D:\Anaconda\envs\Spider\`）
- 在该环境里安装了项目所需的全部依赖库
- 验证了环境可以正常运行

**`python/` 目录现在已经完全被 Conda 环境替代，是一份冗余数据。**

### 1.3 删之前必须做的一件事

项目的两个启动脚本原本硬编码指向 `python/python.exe`：

```bat
# 原来（已废弃）
start  python/python.exe src/main.py
start  python/python.exe src/change_data.py
```

**已于本次操作中修改为指向 Conda 环境：**

```bat
# 现在（已生效）
start  D:\Anaconda\envs\Spider\python.exe src/main.py
start  D:\Anaconda\envs\Spider\python.exe src/change_data.py
```

✅ 两个 bat 文件均已修改完毕，可以放心删除 `python/`。

---

## 2. `python/` 目录的体积分布

删除前先了解各部分大小，方便决定删多少：

| 目录 / 文件类型 | 大小 | 说明 |
|---|---|---|
| `Lib\site-packages\scipy` | **118.8 MB** | 科学计算，项目完全未用 |
| `Lib\site-packages\pandas` | 52.8 MB | 项目有用，但 Conda 已有 |
| `Lib\site-packages\sklearn` | 40.5 MB | 机器学习，项目完全未用 |
| `Lib\site-packages\numpy` | 28.5 MB | pandas 依赖，但 Conda 已有 |
| `Lib\site-packages\selenium` | 25.5 MB | 浏览器自动化，项目未用 |
| `Lib\site-packages\pymupdf` (fitz) | ~40 MB | PDF 处理，项目未用 |
| `Lib\site-packages\cryptography` | 8.7 MB | 加密库，项目未直接用 |
| `Lib\site-packages\setuptools` | 6.5 MB | 打包工具，运行时不需要 |
| `Lib\site-packages\mitmproxy` | 5.7 MB | 网络抓包，项目未用 |
| `Lib\site-packages\Bio` (biopython) | 15.8 MB | 生物信息，项目未用 |
| `Lib\site-packages\aioquic` | 4.2 MB | QUIC 协议，项目未用 |
| `Lib\site-packages\ldap3` | 3.8 MB | LDAP 目录，项目未用 |
| `Lib\site-packages\tornado` | 2.9 MB | Web 框架，项目未用 |
| `Lib\site-packages\trio` | 2.8 MB | 异步框架，项目未用 |
| `Lib\idlelib` | 2.6 MB | Python 自带 IDE，不需要 |
| `Lib\site-packages\urwid` | 1.8 MB | 终端 UI，项目未用 |
| `Lib\site-packages\DrissionPage` | 1.4 MB | 项目核心库，但 Conda 已有 |
| `Lib\tkinter` | 1.2 MB | GUI 库，项目未用 |
| `Lib\site-packages\mitmproxy_windows` | 1.2 MB | 抓包工具 Windows 组件 |
| `Lib\distutils` | 1.4 MB | 打包工具，运行时不需要 |
| `Lib\site-packages\bs4` | 1.0 MB | HTML 解析，项目未用 |
| `Tools` | 1.0 MB | Python 开发辅助工具 |
| 根目录 `*.dll` 文件 | ~10 MB | Windows 运行时，Conda 自带 |
| **合计（整个 python/ 目录）** | **~400 MB+** | |

---

## 3. 三种删除方案

### ✅ 方案一：删掉整个 `python/` 目录（强烈推荐）

**适合：** 已确认 Conda 环境配置完成、bat 已修改、不再需要便携式 Python 的情况。

```powershell
Remove-Item -Recurse -Force "D:\Coding\PycharmCode\Spider\python"
```

- 一条命令，彻底释放约 **400MB+** 空间
- bat 已改好，双击启动不受任何影响
- 项目代码（`src/`）完全不依赖 `python/` 目录

---

### 🔶 方案二：只删 site-packages 里的大型无用库（保守清理）

**适合：** 想保留便携式 Python 解释器本体、偶尔还想直接用 `python/python.exe` 的情况。

在 PowerShell 中执行以下命令（可以整段复制粘贴）：

```powershell
$base = "D:\Coding\PycharmCode\Spider\python\Lib\site-packages"

# ---- 科学计算（共约 180MB，项目完全未用）----
Remove-Item -Recurse -Force "$base\scipy"
Remove-Item -Recurse -Force "$base\scipy-1.15.1.dist-info"
Remove-Item -Recurse -Force "$base\scipy.libs"
Remove-Item -Recurse -Force "$base\scipy-1.15.1-cp310-cp310-win_amd64.whl"
Remove-Item -Recurse -Force "$base\sklearn"
Remove-Item -Recurse -Force "$base\scikit_learn-1.6.1.dist-info"
Remove-Item -Recurse -Force "$base\numpy"
Remove-Item -Recurse -Force "$base\numpy-2.2.1.dist-info"
Remove-Item -Recurse -Force "$base\numpy.libs"
Remove-Item -Recurse -Force "$base\numpy-2.2.1-cp310-cp310-win_amd64.whl"
Remove-Item -Recurse -Force "$base\joblib"
Remove-Item -Recurse -Force "$base\joblib-1.4.2.dist-info"
Remove-Item -Recurse -Force "$base\threadpoolctl.py"
Remove-Item -Recurse -Force "$base\threadpoolctl-3.5.0.dist-info"

# ---- 生物信息（约 16MB，项目完全未用）----
Remove-Item -Recurse -Force "$base\Bio"
Remove-Item -Recurse -Force "$base\BioSQL"
Remove-Item -Recurse -Force "$base\biopython-1.85.dist-info"

# ---- PDF 处理（约 40MB，项目完全未用）----
Remove-Item -Recurse -Force "$base\pymupdf"
Remove-Item -Recurse -Force "$base\pymupdf-1.25.2.dist-info"
Remove-Item -Recurse -Force "$base\fitz"

# ---- 网络抓包 mitmproxy（约 7MB，项目完全未用）----
Remove-Item -Recurse -Force "$base\mitmproxy"
Remove-Item -Recurse -Force "$base\mitmproxy-11.0.2.dist-info"
Remove-Item -Recurse -Force "$base\mitmproxy_windows"
Remove-Item -Recurse -Force "$base\mitmproxy_windows-0.10.7.dist-info"
Remove-Item -Recurse -Force "$base\mitmproxy_rs"
Remove-Item -Recurse -Force "$base\mitmproxy_rs-0.10.7.dist-info"
Remove-Item -Recurse -Force "$base\pydivert"
Remove-Item -Recurse -Force "$base\pydivert-2.1.0.dist-info"
Remove-Item -Recurse -Force "$base\publicsuffix2"
Remove-Item -Recurse -Force "$base\publicsuffix2-2.20191221.dist-info"
Remove-Item -Recurse -Force "$base\tldextract"
Remove-Item -Recurse -Force "$base\tldextract-5.1.3.dist-info"

# ---- Selenium 浏览器自动化（约 26MB，项目未用，DrissionPage 已替代）----
Remove-Item -Recurse -Force "$base\selenium"
Remove-Item -Recurse -Force "$base\selenium-4.27.1.dist-info"
Remove-Item -Recurse -Force "$base\websocket"
Remove-Item -Recurse -Force "$base\websocket_client-1.8.0.dist-info"

# ---- Flask Web 框架（约 2MB，项目完全未用）----
Remove-Item -Recurse -Force "$base\flask"
Remove-Item -Recurse -Force "$base\flask-3.1.0.dist-info"
Remove-Item -Recurse -Force "$base\werkzeug"
Remove-Item -Recurse -Force "$base\werkzeug-3.1.3.dist-info"
Remove-Item -Recurse -Force "$base\jinja2"
Remove-Item -Recurse -Force "$base\jinja2-3.1.5.dist-info"
Remove-Item -Recurse -Force "$base\markupsafe"
Remove-Item -Recurse -Force "$base\MarkupSafe-3.0.2.dist-info"
Remove-Item -Recurse -Force "$base\itsdangerous"
Remove-Item -Recurse -Force "$base\itsdangerous-2.2.0.dist-info"
Remove-Item -Recurse -Force "$base\blinker"
Remove-Item -Recurse -Force "$base\blinker-1.9.0.dist-info"

# ---- 异步/网络协议（约 7MB，项目完全未用）----
Remove-Item -Recurse -Force "$base\aioquic"
Remove-Item -Recurse -Force "$base\aioquic-1.2.0.dist-info"
Remove-Item -Recurse -Force "$base\trio"
Remove-Item -Recurse -Force "$base\trio-0.28.0.dist-info"
Remove-Item -Recurse -Force "$base\trio_websocket"
Remove-Item -Recurse -Force "$base\trio_websocket-0.11.1.dist-info"
Remove-Item -Recurse -Force "$base\wsproto"
Remove-Item -Recurse -Force "$base\wsproto-1.2.0.dist-info"
Remove-Item -Recurse -Force "$base\h2"
Remove-Item -Recurse -Force "$base\h2-4.1.0.dist-info"
Remove-Item -Recurse -Force "$base\hpack"
Remove-Item -Recurse -Force "$base\hpack-4.0.0.dist-info"
Remove-Item -Recurse -Force "$base\hyperframe"
Remove-Item -Recurse -Force "$base\hyperframe-6.0.1.dist-info"
Remove-Item -Recurse -Force "$base\h11"
Remove-Item -Recurse -Force "$base\h11-0.14.0.dist-info"

# ---- 图表工具（约 0.8MB）----
Remove-Item -Recurse -Force "$base\pyecharts"
Remove-Item -Recurse -Force "$base\pyecharts-2.0.7.dist-info"
Remove-Item -Recurse -Force "$base\prettytable"
Remove-Item -Recurse -Force "$base\prettytable-3.12.0.dist-info"

# ---- 其他无用工具（约 10MB）----
Remove-Item -Recurse -Force "$base\ldap3"
Remove-Item -Recurse -Force "$base\ldap3-2.9.1.dist-info"
Remove-Item -Recurse -Force "$base\urwid"
Remove-Item -Recurse -Force "$base\urwid-2.6.16.dist-info"
Remove-Item -Recurse -Force "$base\tornado"
Remove-Item -Recurse -Force "$base\tornado-6.4.2.dist-info"
Remove-Item -Recurse -Force "$base\passlib"
Remove-Item -Recurse -Force "$base\passlib-1.7.4.dist-info"
Remove-Item -Recurse -Force "$base\msgpack"
Remove-Item -Recurse -Force "$base\msgpack-1.1.0.dist-info"
Remove-Item -Recurse -Force "$base\setuptools"
Remove-Item -Recurse -Force "$base\setuptools-75.1.0-py3.10.egg-info"
Remove-Item -Recurse -Force "$base\wheel"
Remove-Item -Recurse -Force "$base\wheel-0.44.0.dist-info"
Remove-Item -Recurse -Force "$base\pip"
Remove-Item -Recurse -Force "$base\pip-24.2.dist-info"

# ---- Python 标准库开发辅助（共约 6MB，运行时不需要）----
$pylib = "D:\Coding\PycharmCode\Spider\python\Lib"
Remove-Item -Recurse -Force "$pylib\idlelib"
Remove-Item -Recurse -Force "$pylib\turtledemo"
Remove-Item -Recurse -Force "$pylib\tkinter"
Remove-Item -Recurse -Force "$pylib\distutils"
Remove-Item -Recurse -Force "$pylib\lib2to3"
Remove-Item -Recurse -Force "$pylib\test"

# ---- 开发辅助目录（约 2MB，运行时不需要）----
Remove-Item -Recurse -Force "D:\Coding\PycharmCode\Spider\python\Tools"
Remove-Item -Recurse -Force "D:\Coding\PycharmCode\Spider\python\include"
```

---

### 📌 方案三：什么都不删（仅供参考）

如果你不确定 Conda 环境是否完全正常，可以先保留 `python/` 目录，待验证通过后再执行方案一。

---

## 4. 绝对不能删的内容（项目实际依赖）

无论选哪个方案，以下内容在 Conda 环境里都要保证已安装：

| 库名 | 说明 |
|---|---|
| `DrissionPage` | 爬虫核心，浏览器自动化 |
| `DataRecorder` | DrissionPage 的依赖 |
| `DownloadKit` | DrissionPage 的依赖 |
| `lxml` | HTML 解析（`from lxml import etree`） |
| `pandas` | CSV/Excel 数据处理 |
| `openpyxl` | Excel 文件写入 |
| `python-dateutil` | 日期字符串解析（`dateutil`） |
| `requests` | HTTP 请求（DrissionPage 间接依赖） |
| `certifi` / `charset-normalizer` / `idna` / `urllib3` | requests 的依赖链 |

---

## 5. 删除后验证

执行删除之后，运行以下命令确认项目仍然正常：

```powershell
# 激活 Conda 环境
conda activate Spider

# 一键检查所有依赖
python -c "
import sys
print('Python 版本:', sys.version)
libs = {
    'DrissionPage': 'from DrissionPage import ChromiumPage',
    'lxml':         'from lxml import etree',
    'pandas':       'import pandas as pd',
    'openpyxl':     'import openpyxl',
    'dateutil':     'from dateutil.parser import parse',
}
ok = True
for name, stmt in libs.items():
    try:
        exec(stmt)
        print(f'  [OK] {name}')
    except ImportError as e:
        print(f'  [FAIL] {name} -- {e}')
        ok = False
print()
print('全部通过！' if ok else '有缺失，请补装。')
"

# 最终验证：直接跑项目
cd D:\Coding\PycharmCode\Spider\src
python main.py
```

---

## 6. 已完成的配套修改

| 文件 | 修改内容 |
|---|---|
| `1.启动.bat` | `python/python.exe` → `D:\Anaconda\envs\Spider\python.exe` |
| `2.导出结果.bat` | `python/python.exe` → `D:\Anaconda\envs\Spider\python.exe` |
| `Requirements/requirements_full.txt` | 已标记为弃用，统一使用 `Requirements/requirements.txt` |

---

## 7. 总结

```
推荐操作顺序：

1. 确认 Conda 环境 Spider 的依赖验证全部 [OK]
2. 执行方案一，一条命令删掉整个 python/ 目录
3. 双击 1.启动.bat 验证爬虫能正常弹出浏览器
4. 完成，节省约 400MB 磁盘空间
```

> ⚠️ 删除前请确认 Conda 环境验证已全部通过（见 Analize3.md 第9节）。  
> ⚠️ 删除操作不可撤销，如有顾虑请先把 `python/` 整体剪切到其他地方备份。

