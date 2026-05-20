$ErrorActionPreference = "Stop"
$worker = "https://loopforge-contact-proxy.wnsrua01.workers.dev"
Write-Host "[1] Health check" -ForegroundColor Cyan
try { Invoke-RestMethod "$worker/health" | ConvertTo-Json -Depth 5 } catch { Write-Warning $_ }
Write-Host "[2] POST without Turnstile should fail safely" -ForegroundColor Cyan
try {
  Invoke-RestMethod "$worker/api/contact" -Method POST -ContentType "application/json" -Body '{"business_name":"테스트","business_type":"음식점 / 카페","contact":"010-0000-0000","consent_privacy":true}'
} catch { Write-Host "Expected fail: $($_.Exception.Message)" -ForegroundColor Yellow }
