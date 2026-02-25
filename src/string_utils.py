import re
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse





class StringUtils:
    @staticmethod
    def try_convert_to_int(input_string):
        """
        尝试将字符串转换为整数。
        :param input_string: 输入的字符串
        :return: 如果转换成功，返回整数；否则返回 False
        """
        try:
            # 尝试将字符串转换为整数
            return int(input_string)
        except (ValueError, TypeError):
            # 如果转换失败（例如输入不是数字或类型不匹配），返回 False
            return False
        
    @staticmethod
    def find_number_hyphen_number(input_string):
        """
        查找字符串中是否包含 英文字母、数字和连字符的字符串 格式的子字符串。
        :param input_string: 输入的字符串
        :return: 如果找到匹配的子字符串，返回该字符串；否则返回 False
        """
        # - 必须在文本中出现，否则返回 False
        if "-" in input_string:
            # 定义正则表达式：匹配只包含英文字母、数字和连字符的字符串
            pattern = r"[A-Za-z0-9-]+"
            # 搜索第一个匹配的文本
            match = re.search(pattern, input_string)
            # 如果找到匹配，返回匹配的文本；否则返回 False
            return match.group(0) if match else False
        else:
            return False
        
    @staticmethod
    def generate_export_filename():
        """
        生成一个格式为 "导出结果-时间戳.xlsx" 的文件名。
        :return: 生成的文件名字符串
        """
        # 获取当前时间戳，格式为 YYYYMMDD_HHMMSS
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        # 生成文件名
        filename = f"导出结果-{timestamp}"
        return filename
    
    @staticmethod
    def get_substring_after(main_str, sub_str):
        # 找到子字符串在主字符串中的起始位置
        start_index = main_str.find(sub_str)
        
        # 如果子字符串不存在于主字符串中，返回空字符串
        if start_index == -1:
            return ""
        
        # 计算子字符串结束的位置
        end_index = start_index + len(sub_str)
        
        # 返回子字符串之后的字符串
        return main_str[end_index:]
    
    @staticmethod
    def get_current_time_string():
        # 获取当前时间
        now = datetime.now()
        # 格式化时间为 "年-月-日 时:分:秒"
        time_string = now.strftime("%Y-%m-%d %H:%M:%S")
        return time_string
    
    @staticmethod
    def modify_url_params(url, params):
        # 解析URL
        parsed_url = urlparse(url)
        
        # 获取原始的查询参数并转换为字典
        query_params = parse_qs(parsed_url.query)
        
        # 更新或添加新的参数
        for key, value in params.items():
            query_params[key] = [value]
        
        # 将查询参数转换回字符串形式
        new_query = urlencode(query_params, doseq=True)
        
        # 构建新的URL
        new_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment
        ))
        
        return new_url

    @staticmethod
    def replace_domain(url, new_domain):
        # 解析URL
        parsed_url = urlparse(url)
        # 构建新的URL，只替换域名部分
        new_url = parsed_url._replace(netloc=new_domain).geturl()
        return new_url
    
    @staticmethod
    def find_first_number(text):
        match = re.search(r'\d+', text)  # 查找连续的数字
        return int(match.group()) if match else 0


    