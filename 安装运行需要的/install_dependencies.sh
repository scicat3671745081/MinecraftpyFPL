#!/bin/bash

# 检测Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "Python未安装，正在安装..."
    # 这里以Ubuntu为例，其他发行版的安装命令可能不同
    sudo apt update
    sudo apt install -y python3
    if [ $? -ne 0 ]; then
        echo "Python安装失败，请手动安装。"
        exit 1
    fi
    echo "Python安装成功。"
else
    echo "Python已安装。"
fi

# 检测并安装或更新Python库
libraries=(PySide6 docopt minecraft-launcher-lib typing IPython requests)
for lib in "${libraries[@]}"; do
    if ! python3 -m pip show "$lib" &> /dev/null; then
        echo "$lib未安装，正在安装..."
        python3 -m pip install "$lib"
        if [ $? -ne 0 ]; then
            echo "$lib安装失败，请手动安装。"
        else
            echo "$lib安装成功。"
        fi
    else
        echo "$lib已安装。"
    fi
done

# 检测内置Python模块
builtin_modules=(subprocess webbrowser time)
for module in "${builtin_modules[@]}"; do
    if ! python3 -c "import $module" &> /dev/null; then
        echo "$module模块缺失，请检查Python安装。"
    else
        echo "$module模块正常。"
    fi
done

echo "所有依赖库和内置模块检测完成。"
