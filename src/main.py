# 按照发的视频进行爬取
from DrissionPage import ChromiumPage, ChromiumOptions
from csv_tool import CsvTool
from excel_tool import ExcelTool
import datetime
import time
import os
import re
import sys
import threading
import config

sys.setrecursionlimit(50000)

co = ChromiumOptions()
co.incognito(True)

driver = ChromiumPage(addr_or_opts=co)


# ── 文件名工具 ────────────────────────────────────────────────────────────────
def kw_safe(keywords: list) -> str:
    """把关键词列表转为安全文件名片段，多个关键词用 + 连接"""
    raw = "+".join(keywords)
    return re.sub(r'[\\/:*?"<>|]', '_', raw)


def make_csv_path(keywords: list) -> str:
    """生成带时间戳的新 CSV 路径"""
    ts  = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join("cache", f"{ts}_{kw_safe(keywords)}_Result.csv")


def find_resume_csv(keywords: list) -> str | None:
    """
    在 cache/ 目录查找关键词完全相同的最新 CSV（断点续传用）。
    文件名格式：YYYYMMDD_HHMMSS_关键词片段_Result.csv
    """
    folder = "cache"
    if not os.path.exists(folder):
        return None
    target = kw_safe(keywords)
    matched = []
    for fname in os.listdir(folder):
        if not fname.endswith("_Result.csv"):
            continue
        body  = fname[: -len("_Result.csv")]
        parts = body.split("_", 2)          # [日期, 时间, 关键词片段]
        if len(parts) == 3 and parts[2] == target:
            matched.append(os.path.join(folder, fname))
    return sorted(matched)[-1] if matched else None


# ── 核心爬取 ──────────────────────────────────────────────────────────────────
def _ele_text(tab, *css_or_xpath_list) -> str:
    """
    依次尝试多个 CSS/XPath 选择器，返回第一个找到的非空文本。
    以 'xpath:' 开头的视为 XPath，否则视为 CSS 选择器。
    """
    for selector in css_or_xpath_list:
        try:
            if selector.startswith("xpath:"):
                ele = tab.ele(f"x:{selector[6:]}", timeout=0)
            else:
                ele = tab.ele(selector, timeout=0)
            if ele:
                txt = (ele.text or "").strip()
                if txt:
                    return txt
        except Exception:
            continue
    return ""


def get_user(tab, csv_path: str) -> tuple:
    """
    用 DrissionPage 的 live tab 直接读取元素，写入 CSV。
    返回 (用户名, 干净URL)
    """
    url = tab.url
    clean_url = url.split("?")[0].rstrip("/")

    # ── 等页面主体出现（最多 5 秒）──────────────────────────────────────
    try:
        tab.wait.ele_displayed("@data-e2e=user-page", timeout=5)
    except Exception:
        pass  # 超时就继续，用已加载的内容

    # ── 用户名 ───────────────────────────────────────────────────────────
    user = _ele_text(
        tab,
        "@data-e2e=user-name",
        "@data-e2e=user-title",
        "xpath:.//h1[@data-e2e='user-title']",
        "xpath:.//span[@data-e2e='user-name']",
        "xpath:.//h1[1]",
    )

    # ── 粉丝数 ───────────────────────────────────────────────────────────
    fans_raw = _ele_text(
        tab,
        "@data-e2e=user-info-fans",
        "xpath:.//div[contains(@data-e2e,'fans')]",
        "xpath:.//span[contains(.,'粉丝')]",
        "xpath:.//strong[contains(.,'粉丝')]",
    )
    fans = fans_raw.replace("粉丝", "").strip()

    # ── IP 属地 ──────────────────────────────────────────────────────────
    ip_raw = _ele_text(
        tab,
        "xpath:.//span[contains(.,'IP属地')]",
        "xpath:.//p[contains(.,'IP属地')]",
        "xpath:.//div[contains(.,'IP属地')]",
    )
    ip_address = ip_raw.replace("IP属地：", "").replace("IP属地:", "").strip()

    print(f"获取到用户:{user}  粉丝:{fans}  属地:{ip_address}")
    info = {
        "抖音用户": user,
        "粉丝数量": fans,
        "IP属地":   ip_address,
        "用户网址": clean_url,
    }
    CsvTool.write_csv_with_key([info], csv_path, "用户网址")
    return user, clean_url


def crawl_url(url: str, csv_path: str,
              stop_event: threading.Event = None,
              max_count: int = 0):
    """
    打开 url，滚动加载，逐个点击用户卡片写入 csv_path。
    stop_event : 外部传入的停止信号（GUI 停止按钮）
    max_count  : 最多爬取多少个新用户，0 表示不限
    """
    def _stopped():
        return stop_event is not None and stop_event.is_set()

    try:
        if driver.url != url:
            driver.get(url)

        old_data  = CsvTool.read_csv_with_dict(csv_path)
        # 用 URL 作为去重集合
        old_urls  = {row.get("用户网址", "").split("?")[0].rstrip("/")
                     for row in old_data}
        new_count = 0   # 本次新增计数

        for _ in range(50):           # 最多滚动 50 次，防止死循环
            if _stopped():
                break
            print("向下滚动")
            driver.scroll.to_bottom()
            time.sleep(2)
            if _stopped():
                break
            if "暂时没有更多了" in driver.html:
                break

        if _stopped():
            return

        eles = driver.eles("@text()=@")
        for button in eles:
            if _stopped():
                print("⏹ 已停止爬取")
                break

            # 检查数量限制
            if max_count > 0 and new_count >= max_count:
                print(f"✅ 已达到目标数量 {max_count} 个，停止爬取")
                break

            user_text = button.next().text
            # 不再用用户名去重，改用后续打开的 URL 去重
            button.click()
            wait = driver.wait.new_tab()
            if not wait:
                continue
            if _stopped():
                # 关掉刚刚打开的标签再退出
                try:
                    driver.get_tab(driver.latest_tab).close()
                except Exception:
                    pass
                break
            time.sleep(2)
            new_tab  = driver.get_tab(driver.latest_tab)
            tab_url  = new_tab.url.split("?")[0].rstrip("/")

            if tab_url in old_urls:
                print(f"用户: {user_text} 已查询（URL重复）, 跳过")
                new_tab.close()
                continue

            _, saved_url = get_user(new_tab, csv_path)
            old_urls.add(saved_url)
            new_count += 1
            new_tab.close()

    except Exception as e:
        import traceback
        print(f"[crawl_url 错误] {e}\n{traceback.format_exc()}")


def run_keywords(keywords: list, csv_path: str,
                 stop_event: threading.Event = None,
                 max_count: int = 0):
    """
    用所有关键词拼成一条搜索词爬取，结果写入 csv_path。
    这是 GUI 调用的主入口。
    stop_event : GUI 停止事件
    max_count  : 最多爬取多少个新用户，0 表示不限
    """
    os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)

    # 多个关键词用空格拼接，构成一条抖音搜索词
    search_term = " ".join(keywords)
    url = f"https://www.douyin.com/search/{search_term}?type=general"
    print(f"🔍 搜索词：{search_term}")
    print(f"🌐 URL：{url}\n")
    crawl_url(url, csv_path, stop_event=stop_event, max_count=max_count)


# ── 兼容旧入口 ────────────────────────────────────────────────────────────────
def start():
    keywords = config.countries_and_cities
    csv_path = make_csv_path(keywords)
    run_keywords(keywords, csv_path)


if __name__ == "__main__":
    start()
    input("按下任意键结束")
