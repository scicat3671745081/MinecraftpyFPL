# This Python file uses the following encoding: utf-8
import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QMessageBox, QProgressBar
from PySide6.QtUiTools import QUiLoader
from docopt import *
import minecraft_launcher_lib
import subprocess
import webbrowser
from typing import *
import IPython.display as ipd
import logging
import time
import requests  # 用于发送 HTTP 请求

class MinecraftLauncher:
    def __init__(self):
        # 收集电脑里面安装的minecraft的版本号
        self.minecraft_install_lib = []
        logging.basicConfig(filename="logs/launcher.log", level=logging.INFO)
        minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
        for i in minecraft_launcher_lib.utils.get_installed_versions(minecraft_directory):
            self.minecraft_install_lib.append(i["id"])
        print(self.minecraft_install_lib)

        # 定义现在发行的版本号
        self.minecraft_release_lib = []
        for i in minecraft_launcher_lib.utils.get_available_versions(minecraft_directory):
            self.minecraft_release_lib.append(i["id"])
        print(self.minecraft_release_lib)

        # 从 Minecraft 官网获取版本
        self.get_versions_from_website()

        self.current_max = 0
        self.offline_username = ""  # 新增：存储离线用户名

    def set_status(self, status: str):
        print(status)

    def set_progress(self, progress: int):
        if self.current_max!= 0:
            progress_bar.setValue(progress * 100 / self.current_max)  # 更新进度条
            print(f"{progress}/{self.current_max}")

    def set_max(self, new_max: int):
        if new_max > 0:  # 确保最大值不为 0
            self.current_max = new_max

    def load_ui(self):
        # 获取当前脚本所在的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, 'run.ui')
        try:
            self.ui = QUiLoader().load(ui_path)
        except Exception as e:
            # 处理加载 UI 时的异常
            print(f"加载 UI 出错: {str(e)}")
            return

        # 初始化
        self.ui.label_5.setText("安装进度")
        self.ui.comboBox_2.addItems(self.minecraft_release_lib)
        self.ui.comboBox.addItems(self.minecraft_install_lib)

        # 添加进度条
        self.progress_bar = QProgressBar(self.ui)
        self.progress_bar.setGeometry(50, 50, 200, 25)

        # 连接信号
        self.ui.pushButton_3.clicked.connect(self.run_minecraft)
        self.ui.pushButton.clicked.connect(self.install_minecraft)

    def run_minecraft(self):
        lib = self.ui.comboBox.currentText()
        self.run_thread = RunThread(lib, minecraft_launcher_lib.utils.get_minecraft_directory())
        self.run_thread.start()

    def install_minecraft(self):
        lib = self.ui.comboBox_2.currentText()
        self.install_thread = InstallThread(lib, minecraft_launcher_lib.utils.get_minecraft_directory())
        self.install_thread.progress_signal.connect(self.update_progress)
        self.install_thread.status_signal.connect(self.update_status)
        self.install_thread.start()

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)

    def update_status(self, status):
        self.ui.label_5.setText(status)
        self.ui.label_5.repaint()

    def get_versions_from_website(self):
        url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"  # Minecraft 版本信息的 URL
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                versions = [version["id"] for version in data["versions"]]
                self.minecraft_release_lib.extend(versions)
            else:
                logging.error("无法从 Minecraft 官网获取版本信息，状态码: %s", response.status_code)
        except requests.exceptions.RequestException as e:
            logging.error("获取 Minecraft 版本信息时出错: %s", e)

    def set_offline_username(self, username):  # 新增：设置离线用户名的方法
        self.offline_username = username

    def get_offline_username(self):  # 新增：获取离线用户名的方法
        return self.offline_username

class InstallThread(QThread):
    progress_signal = Signal(int)
    status_signal = Signal(str)

    def __init__(self, lib, minecraft_directory):
        super().__init__()
        self.lib = lib
        self.minecraft_directory = minecraft_directory

    def run(self):
        try:
            self.status_signal.emit("正在下载")
            minecraft_launcher_lib.install.install_minecraft_version(self.lib, self.minecraft_directory, callback=self.callback)
            self.status_signal.emit("下载完成")
        except Exception as e:
            # 处理下载过程中的异常
            self.status_signal.emit(f"下载出错: {str(e)}")
            logging.error(f"下载 Minecraft 出错: {str(e)}")

    def callback(self, progress, total, status):
        self.progress_signal.emit(int(progress / total * 100))
        self.status_signal.emit(status)

class RunThread(QThread):
    def __init__(self, lib, minecraft_directory):
        super().__init__()
        self.lib = lib
        self.minecraft_directory = minecraft_directory

    def run(self):
        try:
            options = minecraft_launcher_lib.utils.generate_test_options()
            subprocess.run(minecraft_launcher_lib.command.get_minecraft_command(self.lib, self.minecraft_directory, options))
            logging.info("启动minecraft，请移步到latest.log")
        except Exception as e:
            # 处理启动过程中的异常
            logging.error(f"启动 Minecraft 出错: {str(e)}")

if __name__ == "__main__":
    app = QApplication([])
    launcher = MinecraftLauncher()
    launcher.load_ui()
    launcher.ui.show()
    app.exec_()
