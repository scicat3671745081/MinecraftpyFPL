@echo off
SETLOCAL EnableDelayedExpansion

:: 检查pip是否安装
where pip >nul 2>&1
if %errorlevel% neq 0 (
    echo pip is not installed. Please install Python and ensure pip is available.
    exit /b 1
)

:: 安装requests库
echo Installing requests package...
pip install requests

:: 安装PyOpenGL库，用于3D渲染
echo Installing PyOpenGL and PyOpenGL_accelerate packages...
pip install PyOpenGL PyOpenGL_accelerate

:: 检查安装是否成功
if %errorlevel% neq 0 (
    echo Failed to install some packages.
    exit /b 1
) else (
    echo All packages installed successfully.
)

echo Done.
pause
