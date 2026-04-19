@echo off
REM 在「本 bat 所在目录」（即 src）下生成 dist\BBSShojoGame\
cd /d "%~dp0"
python -m PyInstaller --noconfirm main_advanced_v2.spec
if errorlevel 1 exit /b 1
echo 完成: dist\BBSShojoGame\BBSShojoGame.exe
