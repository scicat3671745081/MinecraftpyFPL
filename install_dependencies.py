import subprocess
import time

libraries = ['PySide6', 'docopt','minecraft-launcher-lib', 'typing', 'IPython','requests']

def check_and_install(library):
    try:
        # 检查库是否已安装
        subprocess.run(['pip', 'show', library], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{library} 已安装，无需操作。")
    except subprocess.CalledProcessError:
        # 未安装则进行安装
        print(f"{library} 未安装，准备安装...")
        try:
            start_time = time.time()
            subprocess.run(['pip', 'install', library], check=True)
            end_time = time.time()
            install_time = end_time - start_time
            print(f"{library} 安装成功！安装耗时约 {install_time:.2f} 秒。")
        except subprocess.CalledProcessError:
            print(f"很抱歉，安装 {library} 时出错，请您手动安装。")

print("开始检查和安装所需库...")
for index, lib in enumerate(libraries, 1):
    print(f"正在处理第 {index} 个库: {lib}")
    check_and_install(lib)
print("检查和安装完成。")
