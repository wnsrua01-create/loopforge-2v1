@echo off
chcp 65001 >nul
echo ========================================
echo LoopForge v5.3 배포 전 체크
echo ========================================
echo 1. dist\index.html 의 Turnstile Site Key 교체 확인
echo 2. dist\assets\app.js 같이 업로드 확인
echo 3. cloudflare\_headers 를 Pages 루트에 배치 확인
echo 4. Worker Secret: GAS_WEBHOOK_URL, TURNSTILE_SECRET_KEY, ALLOWED_ORIGINS 확인
echo 5. RATE_LIMIT_KV binding 확인
echo.
echo 로컬 확인 파일: dist\index-v5-3-standalone.html
echo 배포 파일: dist\index.html + dist\assets\app.js
pause
