# 定义我们将要是用到的命令用来操控这个
'''
Usage:
  mine run <想要启动的我的世界版本号>
  mine install <想要下载的我的世界版本号>
  mine micr
  mine version
  mine v
  mine forge <forge版本> 
'''
# 导库
from docopt import *
import minecraft_launcher_lib
import subprocess
import webbrowser
from typing import *
import IPython.display as ipd
import logging

logging.basicConfig(filename="logs/launcher.log", level=logging.INFO)

try:
    current_max = 0

    def set_status(status: str):
        print(status)

    def set_progress(progress: int):
        if current_max!= 0:
            print(f"下载进度: {progress}/{current_max}")

    def set_max(new_max: int):
        global current_max
        current_max = new_max

    minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()

    callback = {
        "setStatus": set_status,
        "setProgress": set_progress,
        "setMax": set_max
    }

    debug = False

    arguments = docopt(__doc__, options_first=True)
    # 设置minecraft目录为自动读取的默认目录
    # Set the minecraft directory to the default directory automatically read
    minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()

    # 启动minecraft
    # Run minecraft
    if arguments.get("run"):
        # 获取用户输入的版本号
        # Get the version number entered by the user
        lib = arguments['<想要启动的我的世界版本号>']
        options = minecraft_launcher_lib.utils.generate_test_options()  # 验证minecraft的存在 Verify the existence of minecraft
        subprocess.run(minecraft_launcher_lib.command.get_minecraft_command(lib, minecraft_directory,
                                                                            options))  # 获取命令，运行命令，启动游戏 Get the command, run the command, and start the game
        logging.info("启动minecraft，请移步到latest.log")
    # 下载minecraft
    # Download minecraft
    elif arguments.get("install"):
        lib = arguments[
            '<想要下载的我的世界版本号>']  # 获取用户输入的minecraft版本号 Get the minecraft version number entered by the user
        print("正在下载Minecraft", lib)  # 打印信息，给予用户安慰（如用户看的，提醒你，安装时间大约为3-5分钟） Print information to give users comfort (users see it, remind you that the installation time is about 3-5 minutes)
        minecraft_launcher_lib.install.install_minecraft_version(lib, minecraft_directory,
                                                                 callback=callback)  # 安装minecraft Install minecraft

        logging.info("下载Minecraft，请发来程序截图输出内容")
    # 微软登录，软件开发过程中，请勿使用
    # Microsoft login, please do not use during software development
    # 微软登录

    elif arguments.get("micr"):
        if debug == False:
            print("此功能正在潜心研发当中")
        elif debug == True:
            a = minecraft_launcher_lib.microsoft_account.get_login_url(client_id="e1e383f9-59d9-4aa2-bf5e-73fe83b15ba0", redirect_uri="https://login.live.com/oauth20_desktop.srf")
            print(a)
            webbrowser.open(a)
            accd = input("登录好后，请把最后的链接复制到这里")
            c = str(minecraft_launcher_lib.microsoft_account.get_auth_code_from_url(url=accd))
            print("检测到您的id是", c)
            # print(minecraft_launcher_lib.microsoft_account.complete_login(client_id:, redirect_uri: str, auth_code: str, code_verifier: Optional[str]))
            # minecraft_directory.microsoft_account.complete_login(client_id="e1e383f9-59d9-4aa2-bf5e-73fe83b15ba0", redirect_uri="https://login.live.com/oauth20_desktop.srf", auth_code="", code_verifier=Option([]))
    # 获取版本号
    elif arguments.get("version") or arguments.get("v"):
        print("alpha 0.0.1")

    # 初始化，下载最新版本的我的世界
    elif arguments.get("init"):
        lib = latest_release = minecraft_launcher_lib.utils.get_latest_version()["release"]
        minecraft_launcher_lib.install.install_minecraft_version(lib, minecraft_directory)

    # 安装forge，功能潜心研发之中
    elif arguments.get("forge"):
        if debug == False:
            print("此功能正在潜心研发当中")
        elif debug == True:
            lib = arguments['<forge版本>']
            version = minecraft_launcher_lib.forge.find_forge_version(lib)
            if version is None:
                print("没找到对应的Forge版本")
                exit()
            print("正在下载Forge", version)

            minecraft_launcher_lib.forge.install_forge_version(version, minecraft_directory)

except:
    import traceback

    e = traceback.format_exc()
    if debug == False:
        print(
            "程序又出错了，/logs文件夹有所有文件和mc的日志（" + minecraft_directory + "/logs/）你应该把系统打包好的日志反馈发送给我们，而不是在这个页面截图，在这之前你可以尝试重启你的MinecraftpyFPL")
    elif debug == True:
        print(e)
    logging.error("错误,Python输出:\n%s---------------", e)
