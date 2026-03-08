# -*- coding: utf-8 -*-
"""
数据清洗与导出模块
支持：仅国外 / 仅国内 / 全部，按粉丝数排序，生成 xlsx
"""
import os
import sys

_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from csv_tool import CsvTool
from excel_tool import ExcelTool

# 国内地区关键词
_DOMESTIC = [
    '北京', '天津', '上海', '重庆', '河北', '山西', '辽宁', '吉林', '黑龙江',
    '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南',
    '广东', '海南', '四川', '贵州', '云南', '陕西', '甘肃', '青海', '台湾',
    '内蒙古', '广西', '西藏', '宁夏', '新疆', '香港', '澳门',
    '中国', '中华', '华夏', '神州',
]


def is_foreign(location: str) -> bool:
    """IP 属地是国外返回 True，国内或空值返回 False"""
    if not location or not isinstance(location, str):
        return False
    loc = location.strip().replace(' ', '')
    return not any(kw in loc for kw in _DOMESTIC)


def parse_fans(fans_str: str) -> int:
    """'1.2万' → 12000，'3.5亿' → 350000000"""
    if not fans_str or not isinstance(fans_str, str):
        return 0
    s = fans_str.strip().replace(',', '').replace('，', '')
    units = {'亿': 100_000_000, '萬': 10_000, '万': 10_000,
             'w': 10_000, 'W': 10_000, 'k': 1_000, 'K': 1_000}
    for unit, mult in units.items():
        if unit in s:
            try:
                return int(float(s.replace(unit, '')) * mult)
            except (ValueError, TypeError):
                return 0
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return 0


# ── 主导出函数（GUI 调用入口）─────────────────────────────────────────────────
FILTER_FOREIGN  = "仅国外"
FILTER_DOMESTIC = "仅国内"
FILTER_ALL      = "全部"


def export(csv_path: str, xlsx_path: str, location_filter: str = FILTER_FOREIGN):
    """
    从 csv_path 读取原始爬取数据，按 location_filter 过滤，
    粉丝数从大到小排序，写入 xlsx_path。

    location_filter 可取：
        FILTER_FOREIGN  ("仅国外") — 只保留 IP 属地为国外的用户
        FILTER_DOMESTIC ("仅国内") — 只保留 IP 属地为国内的用户
        FILTER_ALL      ("全部")   — 不过滤，全部导出
    """
    os.makedirs(os.path.dirname(xlsx_path) or ".", exist_ok=True)
    data = CsvTool.read_csv_with_dict(csv_path)

    if not data:
        print(f"⚠️  CSV 为空或不存在：{csv_path}")
        return False

    filtered = []
    for row in data:
        addr = row.get("IP属地", "")
        if location_filter == FILTER_FOREIGN and not is_foreign(addr):
            continue
        if location_filter == FILTER_DOMESTIC and is_foreign(addr):
            continue
        # FILTER_ALL：不过滤
        row["粉丝数量(纯数字)"] = parse_fans(row.get("粉丝数量", ""))
        filtered.append(row)

    if not filtered:
        print(f"⚠️  过滤后无数据（过滤方式：{location_filter}）")
        return False

    sorted_data = sorted(filtered, key=lambda x: x["粉丝数量(纯数字)"], reverse=True)
    ExcelTool.write_dicts_to_excel(sorted_data, xlsx_path, "抖音用户")
    print(f"✅ 导出完成（{location_filter}，共 {len(sorted_data)} 条）\n   → {xlsx_path}")
    return True


# ── 兼容旧入口 ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    export(
        csv_path="cache/结果.csv",
        xlsx_path="Output/Result.xlsx",
        location_filter=FILTER_FOREIGN,
    )
    input("按下任意键结束")