将Tkinter导入为tk
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
                "游戏目录(_d)"：os.路径.参加(操作系统。路径.expanduser("~"),"Minecraft"),
                "java_path":"java",
                "memory_mode":"自动",
                "max_memory":"2048m",
                "皮肤":"默认",
                "resolution_width":854,
                "resolution_height":480
            }
自己。保存配置(_C)()
    
    定义 保存配置(_C)(自己):
        和……一起 打开(自己。config_file,'W') 作为f：
JSON.倾倒(自己。配置，f，缩进=4)
    
    定义 获取版本(_V)(自己):
        尝试:
响应=请求。得到("https://launchermeta.mojang.com/mc/game/version_manifest.json")
响应。提高状态()
版本=响应。JSON()["版本"]
            返回 [版本["ID"] 为版本在……内版本]
        除……之外请求。RequestException 作为e：
MessageBox。淋浴器("错误","无法获取版本列表: "+str(e))
            返回 []
    
    定义 创建小部件(_W)(自己):
自己。根.TK_setPalette(背景='#ffffff')
        
        # 创建菜单栏
menu_bar=tk。菜单(自己。根)
自己。根.配置(menu=menu_bar)
        
        # 创建主菜单
main_menu=tk。菜单(menu_bar，tearoff=0)
菜单栏(_B)。add_cascade(标签="主菜单"，menu=main_menu)
主菜单(_M)。add_command(标签="关于软件/作者"，command=self。关于作者(_A))
主菜单(_M)。add_command(标签="下载"，command=self。打开资源页)
主菜单(_M)。add_command(标签="设置"，command=self。打开设置(_S))
        
        # 创建游戏设置界面
自己。游戏设置帧=tk.框架(自己。根)
自己。游戏设置帧.包装(fill=tk.双方，展开=正确)
        
TK.标签(自己。游戏设置帧，文本="游戏目录：").网格(行=0，列=0，sticky=tk.W)
entry_game_dir=tk.进入(自己。游戏设置帧，text变量=self.游戏目录(_D)，宽度=40)
entry_game_dir。网格(行=0，列=1)
TK.按钮(自己。游戏设置帧，文本="浏览"，command=self。浏览游戏目录).网格(行=0，列=2)
        
TK.标签(自己。游戏设置帧，text="Java路径：").网格(行=1，列=0，sticky=tk.W)
entry_java_path=tk。进入(自己。游戏设置帧，text变量=self.Java路径(_P)，宽度=40)
entry_java_path。网格(行=1，列=1)
TK.按钮(自己。游戏设置帧，文本="浏览"，command=self.浏览java路径).网格(行=1，列=2)
        
TK.标签(自己。游戏设置帧，text="Minecraft版本：").网格(行=2，列=0，sticky=tk.W)
自己。版本=tk.StringVar(值=self.版本[0]如果自己。版本其他“”)
version_dropdown=ttk.combobox(自己。游戏设置帧，文本变量=self.版本，值=self.版本，状态="只读")
version_dropdown。网格(行=2，列=1)
version_dropdown。当前(0)
        
TK.按钮(自己。游戏设置帧，文本="选择本地版本"，command=self。选择本地版本).网格(行=2，列=2)
        
TK.按钮(自己。游戏设置帧，文本="更改皮肤"，command=self.更改皮肤(_S)).网格(行=3，列=1，pady=10)
        
TK.按钮(自己。游戏设置帧，文本="更改背景"，command=self.更改背景(_B)).网格(行=4，列=1，pady=10)
        
TK.按钮(自己。游戏设置帧，文本="安装插件/模组"，command=self.install_plugin_mod).网格(行=5，列=1，pady=10)
        
# 内存分配
TK.标签(自己。游戏设置帧，文本="内存分配：").网格(行=6，列=0，sticky=tk.W)
自己。memory_mode=tk.StringVar(值=self.配置.得到("memory_mode"，"自动"))
memory_mode_radio=tk.RadioButton(自己。游戏设置帧，文本="自动"，变量=self.memory_mode，值="自动")
memory_mode_radio。网格(行=6，列=1)
memory_mode_radio=tk.RadioButton(自己。游戏设置帧，文本="手动"，变量=self.memory_mode，值="手动")
memory_mode_radio。网格(行=6，列=2)
        
如果自己。memory_mode。得到()=="手动"：
自己。Max_memory=tk.INTVAR(价值=int(自己.配置.得到("max_memory"，2048)))
TK.标签(自己。游戏设置帧，文本="最大内存(MB)：").网格(行=7，列=0，sticky=tk.W)
scale_max_memory=tk。规模(自己。游戏设置帧，from_=512，to=8192，方向=tk。水平的，变量=self.Max_memory)
scale_max_memory。网格(行=7，列=1)
        
# 分辨率设置
TK.标签(自己。游戏设置帧，文本="分辨率宽度：").网格(行=8，列=0，sticky=tk.W)
自己。分辨率_宽度=tk.INTVAR(值=self.配置.得到("resolution_width"，854))
entry_resolution_width=tk。进入(自己。游戏设置帧，text变量=self.分辨率_宽度，宽度=10)
entry_resolution_width。网格(行=8，列=1)
        
TK.标签(自己。游戏设置帧，文本="分辨率高度：").网格(行=9，列=0，sticky=tk.W)
自己。分辨率_高度=tk.INTVAR(值=self.配置.得到("resolution_height"，480))
entry_resolution_height=tk。进入(自己。游戏设置帧，text变量=self.分辨率_高度，宽度=10)
entry_resolution_height.grid(行=9，列=1)
        
tk.Button(self.game_settings_frame，text="启动游戏"，command=self.start_game).grid(row=10，column=1，pady=10)
        
tk.Button(self.game_settings_frame，text="关于作者"，command=self.about_author).grid(row=11，column=1，pady=10)
    
Def浏览游戏目录(自)：
directory=fileialog.askdirectory()
self.game_dir.set(目录)
self.save_config()
    
Def浏览java路径(自身)：
file_path=fileialog.askopenfilename()
self.java_path.set(文件路径)
self.save_config()
    
定义选择本地版本(自身)：
version_path=fileialog.askopenfilename(title="选择本地版本"，filetypes=[("Jar文件"，"*.jar")])
如果版本路径：
自己。版本。设置(os.路径。基本名称(版本路径)
self.config["version"]=self.version.get()
self.save_config()
    
Def change_skin(自身)：
skin_path=fileialog.askopenfilename(title="选择皮肤"，filetypes=[("图像文件"，"*.png*.jpg")])
如果皮肤路径：
skin_dir=os.path.join(self.game_dir.get)，"皮肤")
os.makedirs(皮肤目录，存在确定=真)
皮肤名称=os.path.basename(皮肤路径)
skin_dest=os.path.join(皮肤目录，皮肤名称)
open(skin_dest，'wb')为f：
f.write(打开(皮肤路径，'rb').read())
self.config["皮肤"]=皮肤名称
self.save_config()

定义变更背景(自)(_B)：
background_style=simpledialog.askstring("更改背景"，"输入背景样式（深色/半透明）或选择背景图片：")
如果背景样式(_S)：
如果在["深色"，"半透明"]中使用background_style.lower()：
self.config["background_style"]=background_style.lower()
其他：
background_image=fileialog.askopenfilename(标题="选择背景图片"，filetypes=[("图像文件"，"*.png*.jpg*.jpeg*.bmp")])
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
            os.makedirs(plugin_mod_dir, exist_ok=True)
            plugin_mod_name = os.path.basename(plugin_mod_path)
            plugin_mod_dest = os.path.join(plugin_mod_dir, plugin_mod_name)
            with open(plugin_mod_dest, 'wb') as f:
                f.write(open(plugin_mod_path, 'rb').read())
            messagebox.showinfo("成功", "插件/模组安装成功")

    def about_author(self):
        messagebox.showinfo("关于作者", "关注scicat科技猫新号用于查看后续更新。\n开源地址：https://github.com/scicat3671745081/MinecraftpyFPL")
        if messagebox.askyesno("打赏支持", "是否要打赏支持作者？"):
            webbrowser.open('https://b23.tv/LyN8NqX')

    def open_resource_page(self):
        webbrowser.open("https://www.mcmod.cn/")

    def open_settings(self):
        # 打开设置界面
        pass

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

        # 根据分辨率设置游戏窗口大小
        width = self.resolution_width.get()
        height = self.resolution_height.get()

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
            "--width",
            str(width),
            "--height",
            str(height),
            "net.minecraft.client.main.Main"
        ]

        try:
            subprocess.run(args, cwd=game_dir)
        except Exception as e:
            messagebox.showerror("错误", str(e))

        # 播放Minecraft开关声效
        winsound.Beep(2500, 500)  # 频率2500Hz，持续500ms

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
