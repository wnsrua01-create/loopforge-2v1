@echo off
cd /d "D:\1???\LoopForge AI"
npx wrangler pages deploy . --project-name=loopforge-2v1 --commit-dirty=true
pause