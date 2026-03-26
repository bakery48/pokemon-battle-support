@echo off
chcp 65001 > nul
echo ポケモンバトルサポート を起動します...
echo.

REM Check Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [エラー] Python が見つかりません。
    echo https://www.python.org/ から Python 3.9 以上をインストールしてください。
    pause
    exit /b 1
)

REM Install dependencies
echo 依存パッケージを確認中...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [エラー] パッケージのインストールに失敗しました。
    pause
    exit /b 1
)

echo 起動中...
python main.py
pause
