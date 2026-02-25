import os
import csv
from collections import OrderedDict

class CsvTool:
    @staticmethod
    def read_csv_with_dict(file_path):
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return []
        
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            data = [row for row in reader]
        print(f"Read from {file_path}")
        return data

    @staticmethod
    def read_csv(file_path):
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return []
        
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            data = [row for row in reader]
        print(f"Read from {file_path}")
        return data

    @staticmethod
    def write_csv_with_key(data, file_path, key):
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        
        if os.path.exists(file_path):
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                rows = [row for row in reader]
                key_set = set()
                for row in rows:
                    key_set.add(row[key])
                
                for item in data:
                    if item[key] in key_set:
                        for row in rows:
                            if row[key] == item[key]:
                                row.update(item)
                    else:
                        rows.append(item)
                data = rows
        
        fieldnames = data[0].keys() if data else []
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"Written to {file_path}")

    @staticmethod
    def write_csv(data, file_path):
        if os.path.dirname(file_path):
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
        
        fieldnames = data[0].keys() if data else []
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if file.tell() == 0:  # Check if the file is empty
                writer.writeheader()
            writer.writerows(data)
        
        print(f"Written to {file_path}")
