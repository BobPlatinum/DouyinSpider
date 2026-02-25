import tkinter as tk
from tkinter import filedialog

class FileSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏主窗口

    def select_file(self, file_types, title=""):
        """
        打开文件选择器，指示用户选择指定的文件类型。
        
        :param file_types: 文件类型列表，例如 [("Text files", "*.txt"), ("All files", "*.*")]
        :param title: 文件选择器窗口的标题
        :return: 选中的文件路径，如果取消则返回 None
        """
        if not title:
            title = f"请选择{file_types}文件"
        print(title)
        file_path = filedialog.askopenfilename(filetypes=file_types, title=title)
        return file_path

    def select_folder(self, title=""):
        """
        打开文件夹选择器，指示用户选择指定的文件夹。
        
        :param title: 文件夹选择器窗口的标题
        0
        :return: 选中的文件夹路径，如果取消则返回 None
        """
        if not title:
            title = f"请选择需要解析的文件夹"
        print(title)
        folder_path = filedialog.askdirectory(title=title)
        return folder_path