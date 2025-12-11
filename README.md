# 📅 Desktop Calendar 

> 一个简洁、高效的 Python 桌面日历应用程序。
> A simple and efficient Desktop Calendar application built with Python.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Build](https://img.shields.io/badge/Build-PyInstaller-green?logo=windows)](https://pyinstaller.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)

## 📖 简介 | Introduction

**Desktop Calendar** 是一个运行在 Windows 桌面上的日历工具。它旨在提供比系统日历更便捷的体验，支持待办事项记录、农历显示、透明背景等功能。

项目采用 Python 编写，并配置了 PyInstaller 打包脚本，可以轻松编译为独立的 `.exe` 可执行文件。

## ✨ 功能特性 | Features

* **轻量级**：占用内存小，启动速度快。
* **独立运行**：打包后无需安装 Python 环境即可运行。
* **UI 美观**：包含自定义的应用图标 (`item.ico`)。
* [功能点 1]: 例如 - 支持快速添加日程备注。
* [功能点 2]: 例如 - 始终悬浮在桌面顶层 (Topmost)。
* [功能点 3]: 例如 - 随系统自动启动。

## 📂 项目结构 | Project Structure

```text
desktop_calender/
├── app/                 # 核心源代码文件夹 (Core logic)
├── build/               # (Git ignored) 构建过程中的临时文件
├── dist/                # (Git ignored) 最终生成的 exe 文件存放处
├── item.ico             # 应用程序图标
├── main.py              # 程序启动入口 (Entry point)
├── MyCalender.spec      # PyInstaller 打包配置文件
├── README.md            # 项目说明文档
└── .gitignore           # Git 忽略配置
```

## 🚀 快速开始 | Quick Start
1. 环境准备
确保你的环境已安装 Python 3.x。

```bash
# 克隆项目
git clone [https://github.com/Mamihlapinatapaiooo/desktop_calender.git](https://github.com/Mamihlapinatapaiooo/desktop_calender.git)

# 进入目录
cd desktop_calender
```

## 2. 运行开发版
直接通过 Python 解释器运行：

```bash
python main.py
```
