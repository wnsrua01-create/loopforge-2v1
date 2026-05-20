@echo off
chcp 65001 >nul
echo.
echo  LoopForge AI Session Loader
echo  ============================

REM 세션 요약 파일 클립보드 복사
type "D:\loopforge\LoopForge_sesyon_v2.txt" | clip

REM Claude.ai 열기
start "" "https://claude.ai/new"

echo.
echo  [OK] Claude.ai opened
echo  [OK] Session summary copied to clipboard
echo.
echo  Claude chat opens in browser.
echo  Press Ctrl+V to paste session summary.
echo.
pause
