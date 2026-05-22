# LoopForge AI — 헤르메스 에이전트 컨텍스트

> 새 창에서 이 문서를 Claude에 붙여넣으면 전체 프로젝트 컨텍스트가 즉시 복원됩니다.

---

## 🤖 나는 누구인가

나는 **LoopForge AI** 프로젝트의 AI 자동화 아키텍트입니다.

- 프로젝트: 소상공인 리뷰 AI 자동화 서비스
- 역할: 사업 전략가 + 자동화 아키텍트 + 영업 카피라이터
- 현재 상태: MVP 배포 완료, 영업 시작 단계

---

## 📦 현재 배포된 인프라

### Cloudflare (계정: wnsrua01@gmail.com)
- Account ID: `fc803653c06c6fcb04a44fc1412abdd5`

| Worker/Pages | URL | 상태 |
|---|---|---|
| loopforge-review-api | https://loopforge-review-api.wnsrua01.workers.dev | ✅ 작동 |
| loopforge-webhook-proxy | https://loopforge-webhook-proxy.wnsrua01.workers.dev | ✅ 배포 |
| Pages (랜딩) | https://loopforge-2v1.pages.dev | ✅ 작동 |

### 환경변수 현황
| Worker | 변수 | 값/상태 |
|---|---|---|
| review-api | OPENROUTER_API_KEY | ✅ 설정됨 |
| review-api | WEBHOOK_SECRET | lf2026 |
| webhook-proxy | WEBHOOK_SECRET | lf2026 |
| webhook-proxy | N8N_WEBHOOK_URL | ⏳ 미설정 (n8n 필요) |

### Google Sheets
- 파일: LoopForge 리뷰 분석 결과
- ID: `1E4UpklUu1r2QhyV1KXc8eq_ZhQ0XMoAYZD0EZNbmSn8`
- Apps Script: `https://script.google.com/macros/s/AKfycbwRHTxA4dqpzZuwvDzesgla6LvDHTMAVzlu-MP0MCQTDZZZDZw4u_Wd0fYU8GX5EDc8qg/exec`
- 시트: `positive_reviews`, `negative_reviews`

### 카카오
- 채널명: LoopForge AI
- 검색 ID: loopforgeai
- URL: http://pf.kakao.com/_wLasX

---

## 🧠 핵심 비즈니스 로직

### AI 분석 흐름
```
리뷰 입력 (POST)
  ↓ X-Webhook-Secret: lf2026
Cloudflare Worker
  ↓ Bearer OpenRouter API Key
meta-llama/llama-3.3-70b-instruct
  ↓ JSON 응답
Google Sheets 자동 저장
```

### 가격 구조
- 무료 진단 → 49만 원 테스트 → 99만 원 스탠다드 → 월 30만 원 유지관리

### 첫 영업 타깃
1. 음식점/카페 (성수, 홍대, 강남)
2. 스마트스토어 셀러
3. 피부샵/병원

---

## 🔧 다음에 해야 할 작업

### 즉시 (내일)
1. Railway n8n 설치: `railway.app/new/template/n8n`
2. n8n 환경변수: N8N_ENCRYPTION_KEY, WEBHOOK_URL
3. loopforge-review-workflow.json import
4. Webhook Proxy N8N_WEBHOOK_URL 업데이트

### 이번 주
1. 영업 타깃 20곳 인스타 DM 발송
2. Lovable 대시보드 제작

### 다음 주
1. 카카오 알림톡 템플릿 심사
2. 첫 무료 진단 3건
3. 49만 원 패키지 계약

---

## 📝 중요 파일 목록

| 파일명 | 용도 |
|---|---|
| loopforge-landing.html | 랜딩페이지 (배포 완료) |
| loopforge-review-workflow.json | n8n 워크플로우 |
| cf-worker-review-api.js | Worker 코드 (OpenRouter 버전) |
| cf-worker-webhook-proxy.js | Proxy Worker 코드 |
| loopforge-proposal.md | 고객 제안서 |
| loopforge-dm-scripts.md | 업종별 DM 문구 |

---

## ⚠️ 트러블슈팅 히스토리

| 문제 | 원인 | 해결 |
|---|---|---|
| Groq 403 | CF Worker IP 차단 | OpenRouter로 전환 |
| 인증 실패 | 헤더값 잘림 | WEBHOOK_SECRET을 lf2026으로 단축 |
| Sheets 저장 안됨 | Apps Script 권한 "나만" | "모든 사용자"로 변경 |

---

## 💬 새 창에서 이어서 작업하려면

이 문서 전체를 Claude에 붙여넣고 아래처럼 말하세요:

```
위 컨텍스트를 기반으로 [작업 내용] 해줘
```

예시:
- "위 컨텍스트 기반으로 Railway n8n 설치 가이드 알려줘"
- "위 컨텍스트 기반으로 Lovable 대시보드 프롬프트 작성해줘"
- "위 컨텍스트 기반으로 카카오 알림톡 템플릿 작성해줘"

---

## 🔗 관련 문서 및 시스템 연계

- **[[LoopForge_종합인덱스_및_교차검증]] ([종합 인덱스](./LoopForge_종합인덱스_및_교차검증.md))** - 🌟 전체 문서의 마스터 맵 및 교차검증 보고서
- **[[LoopForge_Obsidian]] ([옵시디언 노트](./LoopForge_Obsidian.md))** - 프로젝트 개요, Mermaid 아키텍처, 수익 목표 및 할 일
- **[[LoopForge_Wiki]] ([프로젝트 위키](./LoopForge_Wiki.md))** - 세부 기술 스택, API 명세, Sheets 구조
- **[[LoopForge_헤르메스_엔지니어링]] ([엔지니어링 문서](./LoopForge_헤르메스_엔지니어링.md))** - 세부 코드 구조, 구글 앱스 스크립트 코드, n8n 가이드
