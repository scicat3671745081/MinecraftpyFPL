import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import json
import requests
import platform
import uuid
import hashlib
import re
import zipfile
import threading

class MinecraftLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Launcher")
        self.root.geometry("600x400")

        # 数据文件夹
        self.data_dir = "MinecraftLauncherData"
        os.makedirs(self.data_dir, exist_ok=True)

        # 配置文件
        self.config_file = os.path.join(self.data_dir, "config.json")
        self.load_config()

        # Java 路径
        self.java_path = tk.StringVar()

        # Minecraft 版本
        self.versions = self.get_versions()

        # 创建界面
        self.create_widgets()

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "java_path": "",
                "selected_version": "",
                "max_use_ram": "2048",
                "player_name": "",
                "access_token": "None",
                "options_lang": "",
                "custom_jvm_params": "",
                "completes_file": True,
                "out_jvm_params": False,
                "background_style": "white",  # 默认背景为白色
                "resolution_width": 800,
                "resolution_height": 600
            }

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)

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
        # 菜单栏
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # 设置菜单
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="设置", menu=settings_menu)
        settings_menu.add_command(label="背景设置", command=self.set_background)
        settings_menu.add_command(label="内存设置", command=self.set_memory)
        settings_menu.add_command(label="分辨率设置", command=self.set_resolution)

        # Java 路径选择
        tk.Label(self.root, text="Java 路径:").pack()
        tk.Entry(self.root, textvariable=self.java_path).pack()
        tk.Button(self.root, text="浏览", command=self.browse_java_path).pack()

        # 版本选择
        tk.Label(self.root, text="Minecraft 版本:").pack()
        self.version_var = tk.StringVar()
        ttk.Combobox(self.root, textvariable=self.version_var, values=self.versions).pack()

        # 最大内存设置
        tk.Label(self.root, text="最大使用内存(MB):").pack()
        self.max_use_ram_var = tk.StringVar(value=self.config["max_use_ram"])
        tk.Entry(self.root, textvariable=self.max_use_ram_var).pack()

        # 玩家名称输入
        tk.Label(self.root, text="玩家名称:").pack()
        self.player_name_var = tk.StringVar(value=self.config["player_name"])
        tk.Entry(self.root, textvariable=self.player_name_var).pack()

        # 完整性检查选项
        self.completes_file_var = tk.BooleanVar(value=self.config["completes_file"])
        tk.Checkbutton(self.root, text="检查文件完整性", variable=self.completes_file_var).pack()

        # 输出 JVM 参数选项
        self.out_jvm_params_var = tk.BooleanVar(value=self.config["out_jvm_params"])
        tk.Checkbutton(self.root, text="输出 JVM 参数", variable=self.out_jvm_params_var).pack()

        # 启动按钮
        tk.Button(self.root, text="启动游戏", command=self.start_game).pack()

    def browse_java_path(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.java_path.set(file_path)

    def start_game(self):
        java_path = self.java_path.get()
        selected_version = self.version_var.get()
        max_use_ram = self.max_use_ram_var.get()
        player_name = self.player_name_var.get()
        completes_file = self.completes_file_var.get()
        out_jvm_params = self.out_jvm_params_var.get()

        if not java_path:
            messagebox.showerror("错误", "请选择 Java 路径")
            return

        if not selected_version:
            messagebox.showerror("错误", "请选择 Minecraft 版本")
            return

        if bool(re.search(pattern=r"[^a-zA-Z0-9\-_+.]", string=player_name)):
            messagebox.showerror("错误", "玩家名称不能包含数字、减号、下划线、加号或英文句号(小数点)以外的字符")
            return

        self.config["java_path"] = java_path
        self.config["selected_version"] = selected_version
        self.config["max_use_ram"] = max_use_ram
        self.config["player_name"] = player_name
        self.config["completes_file"] = completes_file
        self.config["out_jvm_params"] = out_jvm_params
        self.save_config()

        try:
            self.launch_minecraft(java_path, selected_version, max_use_ram, player_name, completes_file, out_jvm_params)
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def launch_minecraft(self, java_path, version_name, max_use_ram, player_name, completes_file, out_jvm_params):
        jvm_params = ""
        jvm_params_list = []
        delimiter = ":"  # Class path 分隔符
        natives_list = []
        jvm_params_list.append(f"\"{java_path}\"")
        system_type = platform.system()  # 获取系统类型

        if system_type == "Windows":  # 判断是否为 Windows
            messagebox.showinfo("系统类型", "Windows")
            system_type = "windows"
            delimiter = ";"
            jvm_params_list.append(" -XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump")
            if platform.release() == "10":  # 判断 Windows 版本是否为 10(11 返回的也是 10)
                jvm_params_list.append(" -Dos.name=\"Windows 10\" -Dos.version=10.0")
            if "64" in platform.machine():  # 判断是否为 64 位
                jvm_params_list.append(" -Xms256M")
            else:
                jvm_params_list.append(" -Xss256M")
        elif system_type == "Linux":  # 判断是否为 Linux
            messagebox.showinfo("系统类型", "Linux")
            system_type = "linux"
            jvm_params_list.append(f" -Xms256M")
        elif system_type == "Darwin":  # 判断是否为 MacOS(OSX)
            messagebox.showinfo("系统类型", "MacOS")
            system_type = "osx"
            jvm_params_list.append(f" -XstartOnFirstThread -Xms256M")
        else:
            raise Exception("您的系统不是 Windows、Linux、MacOS(OSX)")

        jvm_params_list.append(f" -Xmx{max_use_ram}M -XX:+UseG1GC -XX:-UseAdaptiveSizePolicy -XX:-OmitStackTraceInFastThrow -Dfml.ignoreInvalidMinecraftCertificates=True -Dfml.ignorePatchDiscrepancies=True -Dlog4j2.formatMsgNoLookups=true")
        jvm_params += "".join(jvm_params_list)
        jvm_params_list.clear()

        if self.config["custom_jvm_params"]!= "":
            for a_jvm_param in self.config["custom_jvm_params"].split(" "):
                if a_jvm_param!= "":
                    jvm_params_list.append(f" {a_jvm_param.replace(' ', '')}")
            jvm_params += "".join(jvm_params_list)
            jvm_params_list.clear()

        download_lists = []
        with open(f"{self.data_dir}/versions/{version_name}/{version_name}.json", "r", encoding="utf-8") as version_json:  # 读取版本 json
            version_json = json.loads(version_json.read())

        if completes_file:
            messagebox.showinfo("完整性检查", "正在检查当前版本需要补全的依赖库文件...")
            for libraries in version_json.get("libraries"):  # 检测补全 libraries
                libraries_path = f"{self.data_dir}/libraries/{self.name_to_path(name=libraries.get('name'))}"
                if not os.path.isfile(libraries_path):
                    download_lists.append([f"https://bmclapi2.bangbang93.com/{self.name_to_path(name=libraries.get('name'))}", libraries_path])
            messagebox.showinfo("完整性检查", "当前版本需要补全的依赖库文件检查完毕")
        else:
            messagebox.showinfo("完整性检查", "已跳过文件完整性检查")

        find_version = False
        if version_json.get("inheritsFrom") is not None:  # 判断是否是有 Mod 加载器的版本
            messagebox.showinfo("继承检查", "当前版本带有模组加载器, 正在加载原版游戏 Json 文件")
            for game_versions in os.listdir(f"{self.data_dir}/versions"):
                with open(f"{self.data_dir}/versions/{game_versions}/{game_versions}.json", "r", encoding="utf-8") as open_game_json:
                    game_json = json.loads(open_game_json.read())
                if game_json.get("id") == version_json.get("inheritsFrom"):
                    messagebox.showinfo("继承检查", "原版游戏 Json 文件加载完毕")
                    find_version = True
                    if completes_file:
                        messagebox.showinfo("完整性检查", "正在检查原版游戏需要补全的依赖库文件...")
                        for libraries in game_json.get("libraries"):  # 检测补全 libraries
                            libraries_path = f"{self.data_dir}/libraries/{self.name_to_path(name=libraries.get('name'))}"
                            if not os.path.isfile(libraries_path):
                                download_lists.append([f"https://bmclapi2.bangbang93.com/{self.name_to_path(name=libraries.get('name'))}", libraries_path])
                        messagebox.showinfo("完整性检查", "原版游戏需要补全的依赖库文件检查完毕")
                    break
            if not find_version:
                raise Exception("找不到该版本的原版游戏, 请确认原版游戏已正确安装")

        if completes_file:
            if len(download_lists)!= 0:
                max_thread = 64
                messagebox.showinfo("下载管理", f"共有 {len(download_lists)} 个需要补全的文件, 限制最大下载线程为 {max_thread} 个线程\n开始下载需要补全的文件...")
                self.download_manager(download_lists, max_thread)  # 启动下载管理器
            else:
                messagebox.showinfo("下载管理", "没有需要补全的文件")

        messagebox.showinfo("启动参数拼接", "正在拼接游戏启动参数...")
        if version_json.get("arguments") is not None:
            if version_json.get("arguments").get("jvm") is not None:
                for arguments_jvm in version_json.get("arguments").get("jvm"):  # 遍历 json 中的 jvm 参数
                    if type(arguments_jvm) is str:
                        if "${classpath_separator}" in arguments_jvm:  # 这个判断针对 NeoForged 的,为-p 参数的依赖两边加双引号
                            jvm_params_list.append(f" \"{arguments_jvm.replace(' ', '')}\"")
                        else:
                            jvm_params_list.append(f" {arguments_jvm.replace(' ', '')}")
        elif version_json.get("minecraftArguments") is not None:
            jvm_params_list.append(" -Djava.library.path=${natives_directory} -cp ${classpath}")
        jvm_params += "".join(jvm_params_list)
        jvm_params_list.clear()
        main_class = ""
        if "${classpath}" in jvm_params:
            jvm_params = jvm_params.replace("${classpath}", "${classpath}" + f" {version_json.get('mainClass')}")  # 添加游戏主类
        else:
            main_class = version_json.get("mainClass")
        version_jvm_params_list = []
        if version_json.get("arguments") is not None:
            for arguments_game in version_json.get("arguments").get("game"):  # 遍历 json 中的 jvm 参数
                if type(arguments_game) is str:
                    version_jvm_params_list.append(f" {arguments_game.replace(' ', '')}")
        elif version_json.get("minecraftArguments") is not None:
            version_jvm_params_list.append(f" {version_json.get('minecraftArguments')}")
        if not find_version:
            jvm_params += "".join(version_jvm_params_list)
            version_jvm_params_list.clear()
        class_path = "\""
        class_path_list = []
        natives_path_cache_list = []
        for libraries in version_json.get("libraries"):  # 遍历依赖
            libraries_path = f"{self.data_dir}/libraries/{self.name_to_path(name=libraries.get('name'))}{delimiter}"
            class_path_list.append(libraries_path)
            if libraries.get("natives") is not None and libraries.get("natives").get(system_type) is not None:
                natives_path = os.path.dirname(libraries_path)
                if os.path.dirname(natives_path) not in natives_path_cache_list:
                    for natives in os.listdir(natives_path):
                        if "natives" in natives:
                            natives_list.append(f"{natives_path}/{natives}")
                    natives_path_cache_list.append(os.path.dirname(natives_path))
        natives_path_cache_list.clear()
        class_path += "".join(class_path_list)
        class_path_list.clear()
        version_jar = ""
        if os.path.isfile(f"{self.data_dir}/versions/{version_name}/{version_name}.jar"):
            version_jar = f"{self.data_dir}/versions/{version_name}/{version_name}.jar"
            if version_json.get("inheritsFrom") is None:
                class_path += version_jar
        asset_index_id = ""
        if version_json.get("assetIndex") is not None and version_json.get("assetIndex").get("id") is not None:  # 判断 assetIndex id 是否存在
            asset_index_id = version_json.get("assetIndex").get("id")
        if find_version:
            if game_json.get("arguments") is not None:
                for arguments_jvm in game_json.get("arguments").get("jvm"):  # 遍历 json 中的 jvm 参数
                    if type(arguments_jvm) is str and arguments_jvm.replace(' ', '') not in jvm_params:
                        jvm_params_list.append(f" {arguments_jvm.replace(' ', '')}")
            elif game_json.get("minecraftArguments") is not None and " -Djava.library.path=${natives_directory} -cp ${classpath}" not in jvm_params:
                jvm_params_list.append(" -Djava.library.path=${natives_directory} -cp ${classpath}")
            jvm_params += "".join(jvm_params_list)
            jvm_params_list.clear()
            if main_class!= "":
                jvm_params = jvm_params.replace("${classpath}", "${classpath} " + main_class)  # 添加游戏主类
            if game_json.get("arguments") is not None:
                for arguments_game in game_json.get("arguments").get("game"):  # 遍历 json 中的 jvm 参数
                    if type(arguments_game) is str and arguments_game.replace(' ', '') not in jvm_params:
                        jvm_params_list.append(f" {arguments_game.replace(' ', '')}")
            elif game_json.get("minecraftArguments") is not None and game_json.get("minecraftArguments") not in jvm_params:
                jvm_params_list.append(f" {game_json.get('minecraftArguments')}")
            jvm_params += "".join(jvm_params_list)
            jvm_params_list.clear()
            jvm_params += "".join(version_jvm_params_list)
            version_jvm_params_list.clear()
            for libraries in game_json.get("libraries"):  # 遍历依赖
                a_class_path = f"{self.data_dir}/libraries/{self.name_to_path(name=libraries.get('name'))}{delimiter}"
                if a_class_path not in class_path:
                    class_path_list.append(a_class_path)
                if libraries.get("natives") is not None and libraries.get("natives").get(system_type) is not None:
                    natives_path = os.path.dirname(a_class_path)
                    if os.path.dirname(natives_path) not in natives_path_cache_list:
                        for natives in os.listdir(natives_path):
                            if "natives" in natives and natives not in natives_list:
                                natives_list.append(f"{natives_path}/{natives}")
                        natives_path_cache_list.append(os.path.dirname(natives_path))
            natives_path_cache_list.clear()
            class_path += "".join(class_path_list)
            class_path_list.clear()
            if not os.path.isfile(f"{self.data_dir}/versions/{version_name}/{version_name}.jar") and version_jar == "":
                class_path += f"{self.data_dir}/versions/{version_json.get('inheritsFrom')}/{version_json.get('inheritsFrom')}.jar"
            else:
                class_path += version_jar
            if asset_index_id == "":
                asset_index_id = game_json.get("assetIndex").get("id")
        messagebox.showinfo("参数替换", "游戏启动参数拼接完成\n正在替换对应游戏启动参数...")
        jvm_params = jvm_params.replace("${classpath}", class_path.strip(";") + "\"")  # 把-cp 参数内容换成拼接好的依赖路径
        jvm_params = jvm_params.replace("${library_directory}", f"\"{self.data_dir}/libraries\"", 1)  # 依赖文件夹路径
        jvm_params = jvm_params.replace("${assets_root}", f"\"{self.data_dir}/assets\"")  # 资源文件夹路径
        jvm_params = jvm_params.replace("${assets_index_name}", asset_index_id)  # 资源索引 id
        find_natives_dir = False
        for natives_path in os.listdir(f"{self.data_dir}/versions/{version_name}"):
            if "natives" in natives_path:
                find_natives_dir = True
                jvm_params = jvm_params.replace("${natives_directory}", f"\"{self.data_dir}/versions/{version_name}/{natives_path}\"")  # 依赖库文件夹路径
                break
        if not find_natives_dir:
            messagebox.showinfo("解压运行库", "正在解压本地运行库...")
            os.makedirs(f"{self.data_dir}/versions/{version_name}/natives-{system_type}")
            for native_path in natives_list:
                self.unzip(zip_path=native_path, unzip_path=f"{self.data_dir}/versions/{version_name}/natives-{system_type}")
            for not_native in os.listdir(f"{self.data_dir}/versions/{version_name}/natives-{system_type}"):
                if not not_native.endswith(".dll") and os.path.isfile(f"{self.data_dir}/versions/{version_name}/natives-{system_type}/{not_native}"):
                    os.remove(f"{self.data_dir}/versions/{version_name}/natives-{system_type}/{not_native}")
            jvm_params = jvm_params.replace("${natives_directory}", f"\"{self.data_dir}/versions/{version_name}/natives-{system_type}\"")  # 运行库文件夹路径
            messagebox.showinfo("解压完成", "本地运行库解压完毕")
        if not find_natives_dir or self.config["options_lang"]!= "":
            messagebox.showinfo("设置语言", "正在设置游戏默认语言...")
            options_contents = lang = f"lang:{self.config['options_lang']}"
            if os.path.isfile(f"{self.data_dir}/versions/{version_name}/options.txt"):
                with open(f"{self.data_dir}/versions/{version_name}/options.txt", "r", encoding="utf-8") as options:
                    options_contents = options.read()
                options_contents = re.sub(r"lang:\S+", lang, options_contents)
            with open(f"{self.data_dir}/versions/{version_name}/options.txt", "w", encoding="utf-8") as options:
                options.write(options_contents)
            messagebox.showinfo("设置完成", "游戏默认语言设置完毕")
        natives_list.clear()
        jvm_params = jvm_params.replace("${game_directory}", f"\"{self.data_dir}/versions/{version_name}\"")  # 游戏文件存储路径
        jvm_params = jvm_params.replace("${launcher_name}", f"\"{self.root.title}\"")  # 启动器名字
        jvm_params = jvm_params.replace("${launcher_version}", f"\"1.0.0\"")  # 启动器版本
        jvm_params = jvm_params.replace("${version_name}", f"\"{version_name}\"")  # 版本名字
        jvm_params = jvm_params.replace("${auth_player_name}", f"\"{player_name}\"")  # 玩家名字
        jvm_params = jvm_params.replace("${user_type}", "Legacy")  # 登录方式
        if "Legacy" == "Legacy":  # 离线模式设置唯一标识 id
            if self.config["auth_uuid"].isspace():
                auth_uuid = self.name_to_uuid(player_name)
                messagebox.showinfo("生成 UUID", f"没有配置 UUID 自动生成 UUID 为: {auth_uuid}")
            jvm_params = jvm_params.replace("${auth_uuid}", self.config["auth_uuid"])
        jvm_params = jvm_params.replace("${auth_access_token}", self.config["access_token"])  # 正版登录令牌
        jvm_params = jvm_params.replace("${user_properties}", "{}")  # 老版本的用户配置项
        jvm_params = jvm_params.replace("${classpath_separator}", delimiter)  # NeoForged 的逆天参数之一,替换为 Class path 的分隔符就行了
        jvm_params = jvm_params.replace("${library_directory}", f"{self.data_dir}/libraries")  # NeoForged 的逆天参数之二,获取依赖文件夹路径
        if version_jar!= "":
            jvm_params = jvm_params.replace("${primary_jar_name}", os.path.basename(version_jar))  # NeoForged 的逆天参数之三,替换为游戏本体 JAR 文件名就行了
        messagebox.showinfo("替换完成", "游戏启动参数替换完成")
        if out_jvm_params:
            messagebox.showinfo("输出参数", "输出游戏启动参数")
            # 这里可以添加输出 JVM 参数的相关逻辑
        else:
            messagebox.showinfo("生成脚本", "正在生成游戏启动脚本...")
            file_suffix = "sh"
            if system_type == "windows":  # 判断是否为 Windows
                file_suffix = "bat"
            with open(f"./LaunchMinecraft.{file_suffix}", "w", encoding="utf-8") as shell_file:  # 生成启动脚本
                shell_file.write(jvm_params)
            messagebox.showinfo("启动游戏", "游戏启动脚本生成完毕\n正在启动游戏...")
            shell_command = f"\"{os.path.abspath(f'./LaunchMinecraft.{file_suffix}')}\""
            run_shell_command = subprocess.Popen(shell_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)  # 启动游戏
            for get_log in iter(run_shell_command.stdout.readline, b''):
                # 这里可以添加处理游戏日志的逻辑
                pass
            # 这里可以添加处理游戏退出状态的逻辑
            pass

    def name_to_path(self, name):
        at_index = name.find('@')
        if at_index!= -1:
            suffix = name[at_index + 1:]
            name = name[0:at_index]
        else:
            suffix = 'jar'
        parts = name.split(":")
        if len(parts) == 4:
            return f"{parts[0].replace('.', '/')}/{parts[1]}/{parts[2]}/{parts[1]}-{parts[2]}-{parts[3]}.{suffix}"
        elif len(parts) == 3:
            return f"{parts[0].replace('.', '/')}/{parts[1]}/{parts[2]}/{parts[1]}-{parts[2]}.{suffix}"
        else:
            raise Exception("名称无法转换为路径")

    def name_to_uuid(self, name):
        return uuid.UUID(bytes=hashlib.md5(f"OfflinePlayer:{name}".encode('utf-8')).digest()[:16], version=3).hex

    def unzip(self, zip_path, unzip_path):
        zip_object = zipfile.ZipFile(zip_path)
        for file in zip_object.namelist():
            zip_object.extract(file, unzip_path)
        zip_object.close()

    def set_background(self):
        background_style = simpledialog.askstring("背景设置", "选择背景样式（白色/黑色/半透明）")
        if background_style:
            if background_style.lower() == "白色":
                self.root.config(bg="white")
            elif background_style.lower() == "黑色":
                self.root.config(bg="black")
            elif background_style.lower() == "半透明":
                self.root.attributes('-alpha', 0.5)
            self.config["background_style"] = background_style
            self.save_config()

    def set_memory(self):
        memory_mode = simpledialog.askstring("内存设置", "选择内存模式（自动/手动）")
        if memory_mode:
            if memory_mode.lower() == "自动":
                self.config["memory_mode"] = "auto"
            elif memory_mode.lower() == "手动":
                max_memory = simpledialog.askinteger("手动设置内存", "输入最大内存（MB）")
                if max_memory:
                    self.config["max_use_ram"] = str(max_memory)
                    self.config["memory_mode"] = "manual"
            self.save_config()

    def set_resolution(self):
        width = simpledialog.askinteger("分辨率设置 - 宽度", "输入宽度")
        height = simpledialog.askinteger("分辨率设置 - 高度", "输入高度")
        if width and height:
            self.config["resolution_width"] = width
            self.config["resolution_height"] = height
            self.save_config()

    def download_manager(self, download_lists, max_thread):
        global download_list_, downloaded_list_
        download_list_len = len(download_lists)
        if download_list_len!= 0:
            download_list_ = download_lists.copy()
            downloaded_list_ = []
            max_thread = min(max_thread // 2, download_list_len)
            step = download_list_len // max_thread
            remainder = download_list_len % max_thread
            start = 0
            download_threads = []
            for download_task in range(max_thread):
                end = start + step + (download_task < remainder)
                thread = threading.Thread(target=self.download_thread, args=(download_lists[start:end]))
                thread.start()
                download_threads.append(thread)
                start = end
            for wait_thread in download_threads:
                wait_thread.join()

    def download_thread(self, download_list):
        global downloaded_list_
        for download_task in download_list:
            download_task0 = download_task[0]
            download_task1 = download_task[1]
            if not thread_stop:
                path_name = ""
                with thread_lock:
                    for dir_name in re.split(r"[\\/]", os.path.dirname(download_task1)):
                        path_name += f"{dir_name}/"
                        if not os.path.isdir(path_name):
                            os.makedirs(path_name)
                file = int(requests.head(download_task0).headers["Content-Length"])
                half_size = file_size // 2
                download_file = os.path.basename(download_task1)
                part1_path = f"{download_file}.part1"
                thread = threading.Thread(target=self.download_part, args=(download_task0, 0, half_size - 1, part1_path))
                thread.start()
                part2_path = f"{download_file}.part2"
                self.download_part(download_task0, half_size, file_size - 1, part2_path)
                thread.join()
                with open(download_task1, "wb") as save_file:
                    for part in [part1_path, part2_path]:
                        with open(part, 'rb') as part_file:
                            save_file.write(part_file.read())
                        os.remove(part)
                downloaded_list_.append(download_file)
                # 这里可以添加下载进度更新的相关逻辑

    def download_part(self, download_url, part_start, part_end, file_name):
        response = requests.get(download_url, headers={"Range": f"bytes={part_start}-{part_end}"}, stream=True)
        with open(file_name, "wb") as file_part:
            file_part.write(response.content)

if __name__ == "__main__":
    root = tk.Tk()
    app = MinecraftLauncher(root)
    root.mainloop()