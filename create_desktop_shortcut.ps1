Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$targetBat = Join-Path $root "run_hybrid.bat"

if (-not (Test-Path $targetBat)) {
    throw "找不到启动脚本：$targetBat"
}

$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "BBS Shojo (Hybrid).lnk"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $targetBat
$shortcut.WorkingDirectory = $root
$shortcut.Description = "Launch BBS Shojo with hybrid preset"

$exeIcon = Join-Path $root "src\dist\BBSShojoGame\BBSShojoGame.exe"
if (Test-Path $exeIcon) {
    $shortcut.IconLocation = "$exeIcon,0"
}

$shortcut.Save()
Write-Host "桌面快捷方式已创建：" -NoNewline
Write-Host " $shortcutPath" -ForegroundColor Green
