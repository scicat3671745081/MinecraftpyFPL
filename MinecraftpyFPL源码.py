import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import json
import requests
import webbrowser
import sys
import threading
import time
from tkinter import simpledialog
import winsound  # Windows自带的声音库
import shutil
import pyperclip  # 确保导入pyperclip模块
import traceback

class MinecraftLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Launcher")
        self.root.geometry("600x400")
        
        # 检查Python是否安装
        if not self.check_python_installed():
            messagebox.showerror("错误", "未检测到Python，请安装Python后再运行此程序。")
            webbrowser.open("https://www.python.org/downloads/")
            sys.exit()

        # 软件所在文件夹
        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 数据文件夹路径
        self.data_dir = os.path.join(self.app_dir, "MinecraftLauncher")
        self.logs_dir = os.path.join(self.data_dir, "logs")
        self.versions_dir = os.path.join(self.data_dir, "versions")
        self.libraries_dir = os.path.join(self.data_dir, "libraries")
        self.skins_dir = os.path.join(self.data_dir, "skins")
        self.mods_dir = os.path.join(self.data_dir, "mods")
        self.assets_dir = os.path.join(self.data_dir, "assets")
        self.downloads_dir = os.path.join(self.data_dir, "downloads")  # 新建下载文件夹
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(self.versions_dir, exist_ok=True)
        os.makedirs(self.libraries_dir, exist_ok=True)
        os.makedirs(self.skins_dir, exist_ok=True)
        os.makedirs(self.mods_dir, exist_ok=True)
        os.makedirs(self.assets_dir, exist_ok=True)
        os.makedirs(self.downloads_dir, exist_ok=True)
        
        # 配置文件路径
        self.config_file = os.path.join(self.data_dir, "config.json")
        self.load_config()
        
        # 设置Java路径
        self.java_path = tk.StringVar(value=self.config.get("java_path", "java"))
        
        # Minecraft版本列表
        self.versions = self.get_versions()
        
        # 启动次数计数器
        self.startup_count = self.config.get("startup_count", 0)
        
        # 创建界面
        self.create_widgets()

    def check_python_installed(self):
        try:
            subprocess.run(["python", "--version"], check=True, stdout=subprocess.DEVNULL)
            return True
        except FileNotFoundError:
            return False

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "java_path": "java",
                "memory_mode": "auto",
                "max_memory": "2048",
                "skin": "default",
                "resolution_width": 854,
                "resolution_height": 480,
                "auto_start": False,
                "language": "English",
                "background_style": "default"
            }
            self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get_versions(self):
        try:
            response = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json")
            response.raise_for_status()
            versions = response.json()["versions"]
            return [version["id"] for version in versions]
        except requests.RequestException as e:
            messagebox.showerror("错误", "无法获取版本列表: " + str(e))
            return []

    def create_widgets(self):
        self.root.tk_setPalette(background='#ffffff')

        # 创建菜单栏
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # 创建主菜单
        main_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="主菜单", menu=main_menu)
        main_menu.add_command(label="关于软件/作者", command=self.about_author)
        main_menu.add_command(label="下载", command=self.open_resource_page)
        main_menu.add_command(label="设置", command=self.open_settings)
        
        # 创建游戏设置界面
        self.game_settings_frame = tk.Frame(self.root)
        self.game_settings_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(self.game_settings_frame, text="Java路径:").grid(row=0, column=0, sticky=tk.W)
        entry_java_path = tk.Entry(self.game_settings_frame, textvariable=self.java_path, width=40)
        entry_java_path.grid(row=0, column=1)
        tk.Button(self.game_settings_frame, text="浏览", command=self.browse_java_path).grid(row=0, column=2)
        
        tk.Label(self.game_settings_frame, text="Minecraft版本:").grid(row=1, column=0, sticky=tk.W)
        self.version = tk.StringVar(value=self.versions[0] if self.versions else "")
        version_dropdown = ttk.Combobox(self.game_settings_frame, textvariable=self.version, values=self.versions, state="readonly")
        version_dropdown.grid(row=1, column=1)
        version_dropdown.current(0)
        
        tk.Button(self.game_settings_frame, text="更改皮肤", command=self.change_skin).grid(row=2, column=1, pady=10)
        
        tk.Button(self.game_settings_frame, text="更改背景", command=self.change_background).grid(row=3, column=1, pady=10)
        
        tk.Button(self.game_settings_frame, text="安装插件/模组", command=self.install_plugin_mod).grid(row=4, column=1, pady=10)
        
        # 内存分配
        tk.Label(self.game_settings_frame, text="内存分配:").grid(row=5, column=0, sticky=tk.W)
        self.memory_mode = tk.StringVar(value=self.config.get("memory_mode", "auto"))
        memory_mode_auto = tk.Radiobutton(self.game_settings_frame, text="自动", variable=self.memory_mode, value="auto")
        memory_mode_auto.grid(row=5, column=1)
        memory_mode_manual = tk.Radiobutton(self.game_settings_frame, text="手动", variable=self.memory_mode, value="manual")
        memory_mode_manual.grid(row=6, column=1)
        
        if self.memory_mode.get() == "manual":
            self.max_memory = tk.StringVar(value=str(self.config.get("max_memory", 2048)))
            tk.Label(self.game_settings_frame, text="最大内存(MB):").grid(row=7, column=0, sticky=tk.W)
            entry_max_memory = tk.Entry(self.game_settings_frame, textvariable=self.max_memory, width=10)
            entry_max_memory.grid(row=7, column=1)
            entry_max_memory.validate = self.validate_memory
            entry_max_memory.validate_command = entry_max_memory.register(self.validate_memory)

        # 分辨率设置
        tk.Label(self.game_settings_frame, text="分辨率宽度:").grid(row=8, column=0, sticky=tk.W)
        self.resolution_width = tk.IntVar(value=self.config.get("resolution_width", 854))
        entry_resolution_width = tk.Entry(self.game_settings_frame, textvariable=self.resolution_width, width=10)
        entry_resolution_width.grid(row=8, column=1)
        
        tk.Label(self.game_settings_frame, text="分辨率高度:").grid(row=9, column=0, sticky=tk.W)
        self.resolution_height = tk.IntVar(value=self.config.get("resolution_height", 480))
        entry_resolution_height = tk.Entry(self.game_settings_frame, textvariable=self.resolution_height, width=10)
        entry_resolution_height.grid(row=9, column=1)
        
        tk.Button(self.game_settings_frame, text="启动游戏", command=self.start_game).grid(row=10, column=1, pady=10)
        
        tk.Button(self.game_settings_frame, text="关于作者", command=self.about_author).grid(row=11, column=1, pady=10)

    def validate_memory(self, P, C, V):
        try:
            if V == "" or int(V) <= 0:
                messagebox.showerror("错误", "内存大小必须大于0")
                return False
            if '.' in V:
                messagebox.showerror("错误", "内存大小不能包含小数点")
                return False
            return True
        except ValueError:
            messagebox.showerror("错误", "内存大小必须为数字")
            return False

    def browse_java_path(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.java_path.set(file_path)
            self.save_config()

    def change_skin(self):
        skin_path = filedialog.askopenfilename(title="选择皮肤", filetypes=[("Image files", "*.png *.jpg")])
 if skin_path:
 skin_name = os.path.basename(skin_path)
 skin_dest = os.path.join(self.skins_dir, skin_name)
 shutil.copy(skin_path, skin_dest)
 self.config["skin"] = skin_name
 self.save_config()
def change_background(self):
    background_style = simpledialog.askstring("更改背景", "输入背景样式（深色/半透明）或选择背景图片：")
    if background_style:
        if background_style.lower() in ["深色", "半透明"]:
            self.config["background_style"] = background_style.lower()
        else:
            background_image = filedialog.askopenfilename(title="选择背景图片", filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
            if background_image:
                self.config["background_style"] = background_image
        self.apply_background_style()
        self.save_config()

def apply_background_style(self):
    if self.config["background_style"] in ["深色"]:
        self.root.config(bg="#333")
    elif self.config["background_style"] == "半透明":
        self.root.attributes('-alpha', 0.5)  # 设置窗口半透明
    else:
        # 设置背景图片
        self.root.config(bg=self.config["background_style"])

def install_plugin_mod(self):
    plugin_mod_path = filedialog.askopenfilename(title="选择插件/模组", filetypes=[("Jar files", "*.jar")])
    if plugin_mod_path:
        plugin_mod_dir = self.mods_dir
        os.makedirs(plugin_mod_dir, exist_ok=True)
        plugin_mod_name = os.path.basename(plugin_mod_path)
        plugin_mod_dest = os.path.join(plugin_mod_dir, plugin_mod_name)
        shutil.copy(plugin_mod_path, plugin_mod_dest)
        messagebox.showinfo("成功", "插件/模组安装成功")

def about_author(self):
    messagebox.showinfo("关于作者", "感谢使用MinecraftpyFPL\n作者邮箱：3671745081@qq.com")
    if messagebox.askyesno("打赏支持", "是否要打赏支持作者？"):
        webbrowser.open('https://b23.tv/LyN8NqX')

def open_resource_page(self):
    webbrowser.open("https://www.mcmod.cn/")

def open_settings(self):
    settings_window = tk.Toplevel(self.root)
    settings_window.title("设置")
    settings_window.geometry("300x200")

    tk.Label(settings_window, text="自动启动：").pack(pady=5)
    self.auto_start_var = tk.BooleanVar(value=self.config.get("auto_start", False))
    auto_start_checkbox = tk.Checkbutton(settings_window, variable=self.auto_start_var)
    auto_start_checkbox.pack()

    tk.Label(settings_window, text="语言设置：").pack(pady=5)
    language_var = tk.StringVar(value=self.config.get("language", "English"))
    language_dropdown = ttk.Combobox(settings_window, textvariable=language_var, values=["English", "中文"], state="readonly")
    language_dropdown.pack()
    language_dropdown.current(self.config.get("language", "English") == "中文")

    def save_settings():
        self.config["auto_start"] = self.auto_start_var.get()
        self.config["language"] = language_var.get()
        self.save_config()
        settings_window.destroy()

    tk.Button(settings_window, text="保存设置", command=save_settings).pack(pady=10)

def start_game(self):
    self.startup_count += 1
    self.save_config()

    if self.startup_count >= 10:
        messagebox.showinfo("支持作者", "您已启动游戏10次，如果您喜欢这个启动器，请支持作者：\nhttps://b23.tv/kmfqwBQ")
        if messagebox.askyesno("重置计数器", "是否重置启动次数计数器？"):
            self.startup_count = 0
            self.save_config()

    java_path = self.java_path.get()
    version = self.version.get()

    if not os.path.exists(os.path.join(self.versions_dir, version, f"{version}.jar")):
        messagebox.showerror("错误", "找不到Minecraft版本文件")
        return

    if not os.path.exists(java_path):
        messagebox.showerror("错误", "找不到Java路径")
        return

    version_json_path = os.path.join(self.versions_dir, version, f"{version}.json")
    if not os.path.exists(version_json_path):
        self.download_version_files(version)

    self.show_launch_animation()

    # 从{version}.json构建启动参数
    with open(version_json_path, 'r') as f:
        version_data = json.load(f)

    classpath = self.get_classpath(version_data)
    assets_root = self.assets_dir
    assets_index = os.path.join(assets_root, "indexes", "official.json")
    assets = os.path.join(assets_root, "objects")

    # 根据内存分配模式设置JVM参数
    if self.memory_mode.get() == "auto":
        max_memory = self.config.get("max_memory", "2048") + "m"
    else:
        max_memory = self.max_memory.get() + "m"

    # 根据分辨率设置游戏窗口大小
    width = self.resolution_width.get()
    height = self.resolution_height.get()

    args = [
        java_path,
        "-Xmx" + max_memory,
        "-Xms" + max_memory,
        "-Djava.library.path=" + os.path.join(self.versions_dir, version, "natives"),
        "-cp",
        classpath,
        "--version",
        version,
        "--gameDir",
        self.data_dir,
        "--assetsDir",
        assets,
        "--assetIndex",
        "official",
        "--width",
        str(width),
        "-height",
        str(height),
        version_data["mainClass"]
    ]

    try:
        subprocess.run(args, cwd=os.path.join(self.versions_dir, version))
    except Exception as e:
        self.handle_error(e)

def get_classpath(self, version_data):
    classpath = [os.path.join(self.versions_dir, version_data["id"], version_data["id"] + ".jar")]
    for lib in version_data["libraries"]:
        lib_path = os.path.join(self.libraries_dir, lib["downloads"]["artifact"]["path"])
        classpath.append(lib_path)
    return ":".join(classpath)

def download_version_files(self, version):
    # 下载游戏jar文件和依赖库文件
    version_url = f"https://launcher.meta.mojang.com/mc/game/{version}/{version}.json"
    response = requests.get(version_url)
    response.raise_for_status()
    version_data = response.json()

    # 下载游戏jar文件
    jar_url = version_data["downloads"]["client"]["url"]
    self.download_file(jar_url, os.path.join(self.versions_dir, version, f"{version}.jar"))

    # 下载依赖库文件
    for lib in version_data["libraries"]:
        lib_url = lib["downloads"]["artifact"]["url"]
        lib_path = os.path.join(self.libraries_dir, lib["downloads"]["artifact"]["path"])
        self.download_file(lib_url, lib_path)

    # 下载资产索引文件
    assets_url = version_data["assetIndex"]["url"]
    self.download_file(assets_url, os.path.join(self.assets_dir, "indexes", "official.json"))

def download_file(self, url, destination):
    # 下载文件并保存到指定路径
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        winsound.Beep(440)  # 播放下载完成的声音
        messagebox.showinfo("下载完成", "文件下载完成。")
    except requests.RequestException as e:
        messagebox.showerror("下载失败", f"文件下载失败: {e}")
        self.retry_download(url, destination)

def retry_download(self, url, destination):
    def retry():
        try:
            self.download_file(url, destination)
        except Exception as e:
            messagebox.showerror("下载失败", f"重试下载失败: {e}")
            self.retry_download(url, destination)  # 递归调用以实现重试机制

    button_retry = tk.Button(self.root, text="尝试重新连接", command=retry)
    button_retry.pack(pady=10)

def show_launch_animation(self):
    # 创建启动动画窗口
    animation_window = tk.Toplevel(self.root)
    animation_window.title("启动中...")
    animation_window.geometry("300x200")

    # 添加进度条
    progress_label = tk.Label(animation_window, text="启动中...", font=("Helvetica", 16))
    progress_label.pack(pady=20)

    progress_var = tk.DoubleVar(value=0.0)
    progress_bar = ttk.Progressbar(animation_window, variable=progress_var, maximum=100, length=200)
 progress_bar.pack(pady=20)
     # 添加挖矿动画
    self.add_mining_animation(animation_window)

    # 更新进度条
    def update_progress():
        for i in range(100):
            progress_var.set(i + 1)
            animation_window.update_idletasks()
            time.sleep(0.03)
        animation_window.destroy()

    threading.Thread(target=update_progress).start()

def add_mining_animation(self, animation_window):
    # 这里可以添加一个简单的挖矿动画
    # 例如，使用Label显示挖矿的文本
    mining_label = tk.Label(animation_window, text="您的每一次启动都是对作者的支持\n开发团队目前只有科技猫和bilibilibili：-价值5个硬币的昵称-\n关注scicat科技猫新号和-价值5个硬币的昵称-查看后续更新\n开发不易，感谢支持", font=("Helvetica", 10), wraplength=280)
    mining_label.pack(pady=20)

    # 循环显示文本
    def cycle_text():
        messages = [
            "您的每一次启动都是对作者的支持",
            "开发团队目前只有科技猫和bilibili：-价值5个硬币的昵称-",
            "关注scicat科技猫新号和价值5个硬币的昵称-开发者查看后续更新",
            "开发不易，感谢支持"
        ]
        while True:
            for message in messages:
                mining_label.config(text=message)
                animation_window.update_idletasks()
                time.sleep(2)

    threading.Thread(target=cycle_text).start()

def handle_error(self, e):
    # 处理错误，弹出日志复制和重启按钮
    error_log = f"Error: {str(e)}\n\n" + traceback.format_exc()
    with open(os.path.join(self.logs_dir, "error.log"), "w") as f:
        f.write(error_log)
    
    messagebox.showerror("错误", "游戏启动失败，错误日志已保存。\n您可以复制日志并重启程序。")
    copy_log_button = tk.Button(self.root, text="复制日志并重启", command=lambda: self.copy_log_and_restart(error_log))
    copy_log_button.pack(pady=10)

def copy_log_and_restart(self, error_log):
    # 复制日志到剪贴板
    pyperclip.copy(error_log)
    
    # 重启程序
    restart_cmd = f'"{sys.executable}" "{__file__}"'
    subprocess.Popen(restart_cmd, shell=True)
    # 关闭当前窗口
    self.root.destroy()
    if name == "main":
 root = tk.Tk()
 app = MinecraftLauncher(root)
 root.mainloop()