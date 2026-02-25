# 按照发的视频进行爬取
from DrissionPage import ChromiumPage, ChromiumOptions, WebPage, SessionPage
from DrissionPage.errors import PageDisconnectedError
from DrissionPage.common import Actions
from datetime import datetime, timedelta
from lxml import etree
from excel_tool import ExcelTool
import datetime
import time
import os
from file_tool import FileSelector
import re
from datetime import datetime, timedelta
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from csv_tool import CsvTool
from excel_tool import ExcelTool
import re
import json
from string_utils import StringUtils
import sys
import config
sys.setrecursionlimit(50000)  # 设置为5000层





co  = ChromiumOptions()
co.incognito(True)

# co.no_imgs(True)
# co.set_paths(local_port=13006)
# co.set_proxy('http://localhost:15001')

driver = ChromiumPage(addr_or_opts=co)
# driver.set.auto_handle_alert()
# driver.set.load_mode.eager()
# driver.set.download_path(r'cache')




def get_user(html, url):
    
    tree = etree.HTML(html)
    user = tree.xpath("string(.//h1[@class='a34DMvQe'])")
    # data-e2e="user-info-fans"
    fans = tree.xpath("string(.//div[@data-e2e='user-info-fans'])")
    fans = fans.replace("粉丝", "").strip()
    ip_address = tree.xpath("string(.//span[contains(text(), 'IP属地')])")
    ip_address = ip_address.replace("IP属地：", "")

    print(f"获取到用户:{user} 粉丝数量:{fans} 属地:{ip_address}")
    info = {
        "抖音用户": user,
        "粉丝数量": fans,
        "IP属地": ip_address,
        "用户网址": url,
    }
    CsvTool.write_csv_with_key([info], "cache/结果.csv", "抖音用户")
    return user






def get_list(url):
    try:
        if driver.url != url:
            driver.get(url)

        old_data = CsvTool.read_csv_with_dict("cache/结果.csv")
        old_users = [i["抖音用户"] for i in old_data]



        for i in range(10):
            print("向下滚动")
            driver.scroll.to_bottom()
            time.sleep(2)
            if "暂时没有更多了" in driver.html:
                break


        eles = driver.eles("@text()=@")

        for i, button in enumerate(eles):

            # print(button.next().text)
            user = button.next().text
            if not user or  user in old_users:
                print(f"用户: {user} 已查询, 跳过")
                continue
            # print(f'正在处理第 {i} 个按钮...')
            
            # 点击按钮（会打开新标签页）
            button.click()
            
            # 等待新标签页出现并切换到它
            wait = driver.wait.new_tab()
            if not wait:
                continue
            time.sleep(1)
            new_tab = driver.get_tab(driver.latest_tab)

            # 在新标签页中获取HTML
            html = new_tab.html
            # print(f'获取到新窗口HTML，长度: {len(html)}')
            new_user = get_user(html, new_tab.url)
            old_users.append(new_user)

            # 关闭新标签页
            new_tab.close()
            
            # 切换回原始标签页

            
            # print(f'第 {i} 个按钮处理完成\n')
            # if i >=1:
            #     break
    except Exception as e:
        print(e)

def reset_ip():
    """
        只在我电脑上有效， 其他电脑无视此功能
    """
    url = "http://router.asus.com/Advanced_WAN_Content.asp"
    driver.get(url)
    time.sleep(1)
    ele = driver.ele("@value=应用本页面设置")
    if ele:
        ele.click()
        print("重置ip")
        time.sleep(60)


def get_keyword(keyword):
   url = f"https://www.douyin.com/search/{keyword}?type=general"
   get_list(url)


def start():
    for k in config.countries_and_cities:
        # keyword = f"在{k}"
        keyword = f"{k}"
        get_keyword(keyword)
        # reset_ip()


if __name__ == '__main__':
    start()

    input("按下任意键结束")
