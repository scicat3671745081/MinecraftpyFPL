@echo off
setlocal enabledelayedexpansion

REM 检测Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python未安装，正在安装...
    REM 这里假设Python安装包名为python-3.13.0-amd64.exe，位于当前目录下
    start /wait python-3.13.0-amd64.exe /quiet InstallAllUsers=1 PrependPath=1
    if !errorlevel! neq 0 (
        echo Python安装失败，请手动安装。
        exit /b 1
    )
    echo Python安装成功。
) else (
    echo Python已安装。
)

REM 检测并安装或更新Python库
set "libraries=PySide6 docopt minecraft-launcher-lib typing IPython requests"
for %%lib in (%libraries%) do (
    python -m pip show %%lib >nul 2>&1
    if !errorlevel! neq 0 (
        echo %%lib未安装，正在安装...
        python -m pip install %%lib
        if !errorlevel! neq 0 (
            echo %%lib安装失败，请手动安装。
        ) else (
            echo %%lib安装成功。
        )
    ) else (
        echo %%lib已安装。
    )
)

REM 检测内置Python模块
set "builtin_modules=subprocess webbrowser time"
for %%module in (%builtin_modules%) do (
    python -c "import %%module" >nul 2>&1
    if !errorlevel! neq 0 (
        echo %%module模块缺失，请检查Python安装。
    ) else (
        echo %%module模块正常。
    )
)

echo 所有依赖库和内置模块检测完成。
pause
