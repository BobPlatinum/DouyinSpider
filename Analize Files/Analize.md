# Analize.md

面向对象：只会 Python 语法、对爬虫一窍不通的读者。

本文帮助你看懂这个项目做什么、每个文件负责什么、数据如何流动，以及你需要理解的最少爬虫概念。

## 1. 项目一句话说明
这是一个“根据关键词在抖音搜索用户并采集账号信息”的脚本项目，结果先写入 CSV，再可筛选并导出到 Excel。

## 2. 你需要知道的最小爬虫概念
- **网页 = 浏览器渲染出的 HTML**：脚本会打开网页，拿到 HTML 字符串，再从里面找需要的内容。
- **XPath**：一种“在 HTML 里找元素”的语法。本项目用 `lxml.etree` 的 XPath 来提取文字。
- **页面滚动**：很多网站需要向下滚动才能加载更多内容，所以脚本会“下滑”多次。
- **新标签页**：点击某些按钮会打开新页面，脚本需要切到新标签页才能拿到该页面的 HTML。

## 3. 数据流（最重要）
从输入到输出的整体流程如下：

1. **读取关键词**：来自 `config.py` 的 `countries_and_cities` 列表。
2. **搜索页面**：在 `main.py` 中拼出搜索链接（抖音搜索）。
3. **滚动页面**：向下滚动加载更多搜索结果。
4. **逐个点击用户**：打开新标签页进入用户主页。
5. **解析用户信息**：用 XPath 拿到用户名、粉丝数、IP 属地。
6. **写入 CSV**：写入 `cache/结果.csv`，并按“抖音用户”去重更新。
7. **可选二次处理**：`change_data.py` 读取 CSV，筛选“国外属地”，把粉丝数转换为纯数字，并导出 Excel。

## 4. 文件逐个解释（从入口开始）

### `main.py`（爬取主流程）
核心功能：打开网页、滚动、点击用户、提取信息、写入 CSV。

关键点：
- `ChromiumPage`：来自 `DrissionPage`，相当于“自动化浏览器”。
- `get_user(html, url)`：
  - 输入：用户主页 HTML 和 URL
  - 输出：用户名字符串，并写入 CSV
  - 做的事：用 XPath 找到用户名、粉丝数量、IP属地
- `get_list(url)`：
  - 输入：搜索页面 URL
  - 做的事：滚动页面，找到“@xxx”的按钮，逐个点击打开新标签页，再调用 `get_user`
- `get_keyword(keyword)`：拼接搜索链接并调用 `get_list`
- `start()`：遍历配置里的关键词列表，一次一词进行搜索

你最需要看懂的几行：
- `tree = etree.HTML(html)`：把 HTML 解析成可以用 XPath 访问的对象。
- `tree.xpath("string(.//h1[@class='a34DMvQe'])")`：从 HTML 中找用户名。
- `driver.scroll.to_bottom()`：滚动页面，加载更多内容。
- `button.click()` + `driver.wait.new_tab()`：点击后切到新标签页。

### `config.py`（关键词列表）
这里是要搜索的关键词。脚本会按顺序搜索它们。

你可以在这个列表里“加词 / 删词”。

### `csv_tool.py`（CSV 读写工具）
提供了 CSV 的读写函数：
- `read_csv_with_dict(file_path)`：返回“字典列表”，每一行是一个字典。
- `write_csv_with_key(data, file_path, key)`：
  - 以 `key` 作为“唯一键”去重。
  - 如果已有同名用户，会更新该行；否则追加。

这是“去重 + 更新”的关键逻辑。

### `excel_tool.py`（Excel 读写工具）
把字典列表写进 Excel，支持去重并自动调整列宽。

该文件在主流程中未直接使用，但 `change_data.py` 会调用它。

### `change_data.py`（结果二次处理）
用途：
- 从 `cache/结果.csv` 读取数据。
- 判断 IP 属地是否为“国外”。
- 把粉丝数（比如 “1.2万”）转换成纯数字。
- 按粉丝数排序，写入 `导出/结果.xlsx`。

关键函数：
- `is_foreign_location(location)`：判断是否是国外属地。
- `parse_fans_count(fans_str)`：把“万/亿/k”等单位转换为整数。

### `string_utils.py` 和 `file_tool.py`
- `string_utils.py`：通用字符串工具（本项目当前主流程里基本没用到）。
- `file_tool.py`：图形化选择文件/文件夹（本项目当前主流程里没用到）。

## 5. 代码里出现的 Python 语法速查
下面是你可能会卡住的语法点：

- **字典**：
  ```python
  info = {
      "抖音用户": user,
      "粉丝数量": fans,
      "IP属地": ip_address,
      "用户网址": url,
  }
  ```
  “键: 值”结构，像一张表的一行。

- **列表推导式**：
  ```python
  old_users = [i["抖音用户"] for i in old_data]
  ```
  把所有用户名字提取成一个列表。

- **异常捕获**：
  ```python
  try:
      # 可能出错的代码
  except Exception as e:
      print(e)
  ```
  防止程序中途崩溃。

- **函数的返回**：
  ```python
  return user
  ```
  返回值可以被上层函数继续使用。

## 6. 你可能想做的改动（不需要爬虫知识）
- **改关键词**：编辑 `config.py` 的 `countries_and_cities`。
- **改输出字段**：修改 `get_user` 里的 `info` 字典。
- **改输出文件名**：修改 `CsvTool.write_csv_with_key` 里的路径。

## 7. 使用提示（仅解释，不强制）
- 项目依赖浏览器自动化，启动时会打开浏览器窗口。
- 如果页面结构变化（比如类名变了），XPath 就要跟着改。
- 批量运行时，注意不要频繁操作网页或切换页面。

## 8. 建议的阅读顺序
1. `config.py` 看关键词。
2. `main.py` 理解流程和关键函数。
3. `csv_tool.py` 看结果怎么写入。
4. `change_data.py` 了解导出与排序。
5. 其他工具文件可先略读。

## 9. 你如果要继续学习爬虫
只要搞懂以下三个关键词就够开始了：
- **HTML**：网页源代码。
- **XPath**：在 HTML 里找元素。
- **自动化浏览器**：让代码控制浏览器打开网页、点击、滚动。

这三个概念理解后，你就能看懂 80% 的爬虫脚本了。

