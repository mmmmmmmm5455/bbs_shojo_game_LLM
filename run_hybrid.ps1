Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$src = Join-Path $root "src"
Set-Location $src

# Stable defaults: hybrid persona + fast-enough latency + strict language clean.
$env:BBS_SHOJO_DISABLE_OLLAMA = ""
$env:BBS_SHOJO_PROMPT_MODE = "hybrid"
$env:BBS_SHOJO_OLLAMA_MODEL = "llama3:latest"
$env:BBS_SHOJO_LLM_DEADLINE_SEC = "12"
$env:BBS_SHOJO_OLLAMA_TIMEOUT = "12"
$env:BBS_SHOJO_OLLAMA_NUM_PREDICT = "40"
$env:BBS_SHOJO_STRICT_LANGUAGE_CLEAN = "1"
$env:BBS_SHOJO_OLLAMA_STARTUP_WARMUP = "1"

Write-Host "Launching BBS Shojo with hybrid preset..." -ForegroundColor Cyan
Write-Host "MODE=$env:BBS_SHOJO_PROMPT_MODE MODEL=$env:BBS_SHOJO_OLLAMA_MODEL DEADLINE=$env:BBS_SHOJO_LLM_DEADLINE_SEC" -ForegroundColor DarkGray

python .\main_advanced_v2.py
