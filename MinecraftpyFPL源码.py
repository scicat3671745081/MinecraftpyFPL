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
from OpenGL.GL import *
from OpenGL.GLUT import *

class MinecraftLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("MinecraftpyFPL")
        self.root.geometry("600x400")
        
        # 数据文件夹路径
        self.data_dir = os.path.join(os.path.expanduser("~"), "MinecraftpyFPL")
        self.logs_dir = os.path.join(self.data_dir, "logs")
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # 配置文件路径
        self.config_file = os.path.join(self.data_dir, "config.json")
        self.load_config()
        
        # 设置游戏目录
        self.game_dir = tk.StringVar(value=self.config.get("game_dir", os.path.join(os.path.expanduser("~"), "Minecraft")))
        
        # 设置Java路径
        self.java_path = tk.StringVar(value=self.config.get("java_path", "java"))
        
        # Minecraft版本列表
        self.versions = self.get_versions()
        
        # 启动次数计数器
        self.startup_count = self.config.get("startup_count", 0)
        
        # 创建界面
        self.create_widgets()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "game_dir": os.path.join(os.path.expanduser("~"), "Minecraft"),
                "java_path": "java",
                "memory_mode": "auto",
                "max_memory": "2048m",
                "skin": "default"
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
        
        tk.Label(self.root, text="游戏目录:").grid(row=0, column=0, sticky=tk.W)
        entry_game_dir = tk.Entry(self.root, textvariable=self.game_dir, width=40)
        entry_game_dir.grid(row=0, column=1)
        tk.Button(self.root, text="浏览", command=self.browse_game_dir).grid(row=0, column=2)
        
        tk.Label(self.root, text="Java路径:").grid(row=1, column=0, sticky=tk.W)
        entry_java_path = tk.Entry(self.root, textvariable=self.java_path, width=40)
        entry_java_path.grid(row=1, column=1)
        tk.Button(self.root, text="浏览", command=self.browse_java_path).grid(row=1, column=2)
        
        tk.Label(self.root, text="Minecraft版本:").grid(row=2, column=0, sticky=tk.W)
        self.version = tk.StringVar(value=self.versions[0] if self.versions else "")
        version_dropdown = ttk.Combobox(self.root, textvariable=self.version, values=self.versions, state="readonly")
        version_dropdown.grid(row=2, column=1)
        version_dropdown.current(0)
        
        tk.Button(self.root, text="选择本地版本", command=self.select_local_version).grid(row=2, column=2)
        
        tk.Button(self.root, text="更改皮肤", command=self.change_skin).grid(row=3, column=1, pady=10)
        
        tk.Button(self.root, text="更改背景", command=self.change_background).grid(row=4, column=1, pady=10)
        
        tk.Button(self.root, text="安装插件/模组", command=self.install_plugin_mod).grid(row=5, column=1, pady=10)
        
        # 内存分配
        tk.Label(self.root, text="内存分配:").grid(row=6, column=0, sticky=tk.W)
        self.memory_mode = tk.StringVar(value=self.config.get("memory_mode", "auto"))
        memory_mode_radio = tk.Radiobutton(self.root, text="自动", variable=self.memory_mode, value="auto")
        memory_mode_radio.grid(row=6, column=1)
        memory_mode_radio = tk.Radiobutton(self.root, text="手动", variable=self.memory_mode, value="manual")
        memory_mode_radio.grid(row=6, column=2)
        
        if self.memory_mode.get() == "manual":
            self.max_memory = tk.IntVar(value=int(self.config.get("max_memory", 2048)))
            tk.Label(self.root, text="最大内存(MB):").grid(row=7, column=0, sticky=tk.W)
            scale_max_memory = tk.Scale(self.root, from_=512, to=8192, orient=tk.HORIZONTAL, variable=self.max_memory)
            scale_max_memory.grid(row=7, column=1)
        
        tk.Button(self.root, text="启动游戏", command=self.start_game).grid(row=8, column=1, pady=10)
        
        tk.Button(self.root, text="关于作者", command=self.about_author).grid(row=9, column=1, pady=10)
    
    def browse_game_dir(self):
        directory = filedialog.askdirectory()
        self.game_dir.set(directory)
        self.save_config()
    
    def browse_java_path(self):
        file_path = filedialog.askopenfilename()
        self.java_path.set(file_path)
        self.save_config()
    
    def select_local_version(self):
        version_path = filedialog.askopenfilename(title="选择本地版本", filetypes=[("Jar files", "*.jar")])
        if version_path:
            self.version.set(os.path.basename(version_path))
            self.config["version"] = self.version.get()
            self.save_config()
    
    def change_skin(self):
        skin_path = filedialog.askopenfilename(title="选择皮肤", filetypes=[("Image files", "*.png *.jpg")])
        if skin_path:
            skin_dir = os.path.join(self.game_dir.get(), "skins")
            os.makedirs(skin_dir, exist_ok=True)
            skin_name = os.path.basename(skin_path)
            skin_dest = os.path.join(skin_dir, skin_name)
            with open(skin_dest, 'wb') as f:
                f.write(open(skin_path, 'rb').read())
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
            plugin_mod_dir = os.path.join(self.game_dir.get(), "mods")
            os.makedirs(plugin_mod_dir, exist

            messagebox.showinfo("成功", "插件/模组安装成功")
    
    def about_author(self):
        messagebox.showinfo("关于作者", "关注scicat科技猫新号用于查看后续更新。\n打赏支持作者：https://b23.tv/LyN8NqX")
        if messagebox.askyesno("打赏支持", "是否要打赏支持作者？"):
            webbrowser.open('https://b23.tv/LyN8NqX')
    
    def start_game(self):
        self.startup_count += 1
        self.save_config()
        
        if self.startup_count >= 10:
            messagebox.showinfo("支持作者", "您已启动游戏10次，如果您喜欢这个启动器，请支持作者：\nhttps://b23.tv/kmfqwBQ")
            if messagebox.askyesno("支持作者", "是否现在访问支持页面？"):
                webbrowser.open('https://b23.tv/LyN8NqX')
                self.startup_count = 0
        
        java_path = self.java_path.get()
        game_dir = self.game_dir.get()
        version = self.version.get()
        
        if not os.path.exists(os.path.join(game_dir, "versions", version, f"{version}.jar")):
            messagebox.showerror("错误", "找不到Minecraft版本文件")
            return
        
        if not os.path.exists(java_path):
            messagebox.showerror("错误", "找不到Java路径")
            return
        
        # 显示启动动画和进度条
        self.show_launch_animation()

        # 构建classpath
        classpath = self.get_classpath(game_dir, version)
        assets_root = os.path.join(game_dir, "assets")
        assets_index = os.path.join(assets_root, "indexes", "official.json")
        assets = os.path.join(assets_root, "objects")
        
        # 根据内存分配模式设置JVM参数
        if self.memory_mode.get() == "auto":
            max_memory = self.config.get("max_memory", "2048m")
        else:
            max_memory = str(self.max_memory.get()) + 'm'
        
        args = [
            java_path,
            "-Xmx" + max_memory,
            "-Xms" + max_memory,
            "-Djava.library.path=" + os.path.join(game_dir, "natives"),
            "-cp",
            classpath,
            "--version",
            version,
            "--gameDir",
            game_dir,
            "--assetsDir",
            assets,
            "--assetIndex",
            "official",
            "net.minecraft.client.main.Main"
        ]
        
        try:
            subprocess.run(args, cwd=game_dir)
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def get_classpath(self, game_dir, version):
        jar_path = os.path.join(game_dir, "versions", version, f"{version}.jar")
        libraries_path = os.path.join(game_dir, "libraries")
        classpath = [jar_path]
        
        for lib in os.listdir(libraries_path):
            if lib.endswith(".jar"):
                classpath.append(os.path.join(libraries_path, lib))
        
        return ":".join(classpath)

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
        mining_label = tk.Label(animation_window, text="您的每一次启动都是对作者的支持\n开发团队只有科技猫一个人\n关注scicat科技猫新号查看后续更新\n开发不易，感谢支持", font=("Helvetica", 10), wraplength=280)
        mining_label.pack(pady=20)
        
        # 循环显示文本
        def cycle_text():
            messages = [
                "您的每一次启动都是对作者的支持",
                "开发团队只有科技猫一个人",
                "关注scicat科技猫新号查看后续更新",
                "开发不易，感谢支持"
            ]
            while True:
                for message in messages:
                    mining_label.config(text=message)
                    animation_window.update_idletasks()
                    time.sleep(2)
        
        threading.Thread(target=cycle_text).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = MinecraftLauncher(root)
    root.mainloop()
