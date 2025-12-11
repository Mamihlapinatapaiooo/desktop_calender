# app/data_manager.py
import json
import os
from PyQt6.QtCore import Qt

class TaskManager:
    def __init__(self, filename="tasks.json"):
        self.filename = filename
        self.data = self.load_data() # 结构变更为整个字典，不再只是tasks

    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_data(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    # --- 任务相关 ---
    def add_task(self, date_str, text):
        if date_str not in self.data:
            self.data[date_str] = {"tasks": [], "work_seconds": 0}
        # 兼容旧数据结构：如果某个日期下是列表，转化为字典
        if isinstance(self.data[date_str], list):
             self.data[date_str] = {"tasks": self.data[date_str], "work_seconds": 0}
             
        self.data[date_str]["tasks"].append({"text": text, "completed": False})
        self.sort_tasks(date_str)
        self.save_data()

    def get_tasks(self, date_str):
        day_data = self.data.get(date_str, {})
        # 兼容旧数据
        if isinstance(day_data, list): return day_data
        return day_data.get("tasks", [])

    def remove_task(self, date_str, index):
        day_data = self.data.get(date_str)
        if day_data and isinstance(day_data, dict):
            tasks = day_data.get("tasks", [])
            if 0 <= index < len(tasks):
                tasks.pop(index)
                self.save_data()
                return True
        elif isinstance(day_data, list): # 旧数据兼容
            if 0 <= index < len(day_data):
                day_data.pop(index)
                self.save_data()
                return True
        return False
    
    def toggle_task_status(self, date_str, index):
        day_data = self.data.get(date_str)
        if day_data:
            tasks = day_data.get("tasks", []) if isinstance(day_data, dict) else day_data
            if 0 <= index < len(tasks):
                tasks[index]['completed'] = not tasks[index]['completed']
                self.sort_tasks(date_str)
                self.save_data()

    def sort_tasks(self, date_str):
        day_data = self.data.get(date_str)
        if day_data:
            tasks = day_data.get("tasks", []) if isinstance(day_data, dict) else day_data
            tasks.sort(key=lambda x: x['completed'])

    def has_tasks(self, qdate):
        date_str = qdate.toString(Qt.DateFormat.ISODate)
        if date_str in self.data:
            tasks = self.get_tasks(date_str)
            return len(tasks) > 0
        return False

    # --- 新增：工作时长统计 ---
    def add_work_time(self, date_str, seconds):
        if date_str not in self.data:
            self.data[date_str] = {"tasks": [], "work_seconds": 0}
        
        if isinstance(self.data[date_str], list):
             self.data[date_str] = {"tasks": self.data[date_str], "work_seconds": 0}
             
        current = self.data[date_str].get("work_seconds", 0)
        self.data[date_str]["work_seconds"] = current + seconds
        self.save_data()

    def get_work_time(self, date_str):
        day_data = self.data.get(date_str, {})
        if isinstance(day_data, dict):
            return day_data.get("work_seconds", 0)
        return 0