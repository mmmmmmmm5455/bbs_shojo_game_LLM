@echo off
setlocal

set "ROOT=%~dp0"
cd /d "%ROOT%src"

rem Stable defaults: hybrid persona + fast-enough latency + strict language clean.
set "BBS_SHOJO_DISABLE_OLLAMA="
set "BBS_SHOJO_PROMPT_MODE=hybrid"
set "BBS_SHOJO_OLLAMA_MODEL=llama3:latest"
set "BBS_SHOJO_LLM_DEADLINE_SEC=12"
set "BBS_SHOJO_OLLAMA_TIMEOUT=12"
set "BBS_SHOJO_OLLAMA_NUM_PREDICT=40"
set "BBS_SHOJO_STRICT_LANGUAGE_CLEAN=1"
set "BBS_SHOJO_OLLAMA_STARTUP_WARMUP=1"

echo Launching BBS Shojo with hybrid preset...
echo MODE=%BBS_SHOJO_PROMPT_MODE% MODEL=%BBS_SHOJO_OLLAMA_MODEL% DEADLINE=%BBS_SHOJO_LLM_DEADLINE_SEC%

python main_advanced_v2.py
endlocal
