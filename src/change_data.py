from csv_tool import CsvTool
from excel_tool import ExcelTool

def is_foreign_location(location):
    """
    判断输入的地点名称是否为国外
    
    参数:
        location (str): 输入的地点名称字符串
    
    返回:
        bool: 如果是国外返回True，如果是国内或空值返回False
    """
    # 国内省份、自治区、直辖市和特别行政区列表
    domestic_regions = [
        '北京', '天津', '上海', '重庆', '河北', '山西', '辽宁', '吉林', '黑龙江',
        '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南',
        '广东', '海南', '四川', '贵州', '云南', '陕西', '甘肃', '青海', '台湾',
        '内蒙古', '广西', '西藏', '宁夏', '新疆', '香港', '澳门',
        '中国'  # 包含"中国"的情况
    ]
    
    # 处理空值或非字符串输入
    if not location or not isinstance(location, str):
        return False
    
    # 去除前后空格并转换为无空格形式（避免简繁体问题）
    location = location.strip().replace(' ', '')
    
    # 检查是否是国内地区
    for region in domestic_regions:
        if region in location:
            return False
    
    # 检查常见中国别称
    china_aliases = ['中华', '华夏', '神州']
    for alias in china_aliases:
        if alias in location:
            return False
    
    # 如果以上都不匹配，则认为是国外
    return True


def parse_fans_count(fans_str):
    """
    将带中文单位的粉丝数量字符串转换为整数
    
    参数:
        fans_str (str): 粉丝数量字符串，可能包含"万"、"亿"等单位
        
    返回:
        int: 转换后的粉丝数量
        
    示例:
        >>> parse_fans_count("1.2万")
        12000
        >>> parse_fans_count("3.5亿")
        350000000
        >>> parse_fans_count("10")
        10
    """
    if not fans_str or not isinstance(fans_str, str):
        return 0
    
    # 去除空格和逗号等干扰字符
    cleaned_str = fans_str.strip().replace(',', '').replace('，', '')
    
    # 定义单位映射
    unit_map = {
        '亿': 100000000,
        '萬': 10000,  # 繁体万
        '万': 10000,
        'w': 10000,   # 小写w表示万
        'W': 10000,   # 大写W表示万
        'k': 1000,    # 千
        'K': 1000,    # 千
    }
    
    # 尝试匹配单位
    for unit, multiplier in unit_map.items():
        if unit in cleaned_str:
            num_str = cleaned_str.replace(unit, '')
            try:
                return int(float(num_str) * multiplier)
            except (ValueError, TypeError):
                return 0
    
    # 没有单位的情况
    try:
        return int(float(cleaned_str))
    except (ValueError, TypeError):
        return 0
    

def start():
    data = CsvTool.read_csv_with_dict("cache/结果.csv")
    new_data = []
    for i in data:
        address = i["IP属地"]
        fans = i["粉丝数量"]
        if not is_foreign_location(address):
            continue
        i["粉丝数量(纯数字)"]  = parse_fans_count(fans)
        new_data.append(i)
    
    # 按"粉丝数量(纯数字)"从大到小排序
    sorted_data = sorted(new_data, key=lambda x: x["粉丝数量(纯数字)"], reverse=True)
    
    ExcelTool.write_dicts_to_excel(sorted_data, "Output/Result.xlsx", "Tiktok members")
        
    


if __name__ == '__main__':
    start()

    input("按下任意键结束")