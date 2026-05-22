# LoopForge AI 위키

## 목차

1. [프로젝트 소개](#1-프로젝트-소개)
2. [기술 스택](#2-기술-스택)
3. [배포 인프라](#3-배포-인프라)
4. [API 명세](#4-api-명세)
5. [Google Sheets 구조](#5-google-sheets-구조)
6. [영업 자료](#6-영업-자료)
7. [로드맵](#7-로드맵)
8. [트러블슈팅](#8-트러블슈팅)

---

## 1. 프로젝트 소개

**LoopForge AI**는 소상공인·1인기업의 반복 업무를 AI와 노코드 자동화 도구로 줄여주는 1인 AI 자동화 기업이다.

### 핵심 사업 구조

```
1. AI 자동화 대행으로 첫 현금흐름 창출
2. 반복 발생 문제 발굴
3. n8n으로 워크플로우 표준화
4. Micro-SaaS / 템플릿으로 제품화
5. 국내 원화 + 글로벌 달러 매출
```

### 첫 MVP: Review-to-Marketing Auto-Loop

네이버 리뷰를 AI로 분석해서 아래 5가지를 자동 생성:
- 감사 답글 초안
- 부정 리뷰 CS 대응 문구
- 네이버 블로그 홍보글 초안
- 키워드 추출
- 월간 리포트

---

## 2. 기술 스택

| 분류 | 도구 | 용도 |
|---|---|---|
| 자동화 엔진 | n8n (Railway) | 워크플로우 실행 |
| API 게이트웨이 | Cloudflare Workers | 인증 + 라우팅 |
| AI/LLM | OpenRouter (Llama 3.3 70B) | 리뷰 분석 |
| 프론트엔드 | Cloudflare Pages | 랜딩페이지 |
| 데이터 저장 | Google Sheets | 분석 결과 저장 |
| 알림 | 카카오 비즈채널 | 고객 문의 |
| 결제 | 토스페이먼츠 | (추후) |

---

## 3. 배포 인프라

### Cloudflare Account
- Account ID: `fc803653c06c6fcb04a44fc1412abdd5`
- 하위 도메인: `wnsrua01.workers.dev`

### Workers

#### loopforge-review-api
```
URL: https://loopforge-review-api.wnsrua01.workers.dev
역할: 리뷰 분석 메인 API
인증: X-Webhook-Secret 헤더
AI: OpenRouter API (Llama 3.3 70B)
저장: Google Apps Script → Sheets
```

#### loopforge-webhook-proxy
```
URL: https://loopforge-webhook-proxy.wnsrua01.workers.dev
역할: n8n 웹훅 보안 프록시
인증: X-Webhook-Secret 헤더
포워딩: N8N_WEBHOOK_URL로 전달
```

### Pages
```
프로젝트: loopforge
URL: https://loopforge-2v1.pages.dev
파일: loopforge-landing.html
```

---

## 4. API 명세

### POST /reviews (loopforge-review-api)

**요청 헤더**
```
Content-Type: application/json
X-Webhook-Secret: lf2026
```

**요청 바디**
```json
{
  "business_name": "string (필수)",
  "platform": "naver_place | naver_smartstore | ...",
  "reviews": [
    {
      "id": "string",
      "text": "string (필수)",
      "rating": "number 1-5 (필수)",
      "author": "string",
      "date": "YYYY-MM-DD"
    }
  ]
}
```

**응답**
```json
{
  "success": true,
  "business_name": "string",
  "summary": {
    "total": "number",
    "negative_count": "number",
    "positive_count": "number",
    "avg_sentiment_score": "number",
    "top_keywords": ["string"]
  },
  "results": [
    {
      "review_id": "string",
      "sentiment_score": "number 1-5",
      "sentiment_label": "positive | negative | neutral",
      "keywords": ["string"],
      "personal_thanks": "string | null",
      "cs_defense": "string | null",
      "blog_draft": "string | null",
      "risk_note": "string | null",
      "is_negative": "boolean"
    }
  ],
  "processed_at": "ISO 8601"
}
```

**에러 응답**
```json
{
  "success": false,
  "error": "에러 메시지"
}
```

| 상태코드 | 의미 |
|---|---|
| 200 | 성공 |
| 400 | 잘못된 요청 |
| 401 | 인증 실패 |
| 405 | GET 요청 (POST만 허용) |

---

## 5. Google Sheets 구조

### 파일 정보
- 이름: `LoopForge 리뷰 분석 결과`
- ID: `1E4UpklUu1r2QhyV1KXc8eq_ZhQ0XMoAYZD0EZNbmSn8`
- Apps Script: `https://script.google.com/macros/s/AKfycbwRHTxA4dqpzZuwvDzesgla6LvDHTMAVzlu-MP0MCQTDZZZDZw4u_Wd0fYU8GX5EDc8qg/exec`

### positive_reviews 시트
| 컬럼 | 설명 |
|---|---|
| 처리일시 | 분석 시각 (한국 시간) |
| 업체명 | 비즈니스 이름 |
| 감정점수 | 1.0 ~ 5.0 |
| 키워드 | 콤마 구분 |
| 감사답글_초안 | 검토 후 사용 |
| 블로그_초안 | 검토 후 사용 |
| 리스크_메모 | 주의 표현 |

### negative_reviews 시트
| 컬럼 | 설명 |
|---|---|
| 처리일시 | 분석 시각 |
| 업체명 | 비즈니스 이름 |
| 감정점수 | 1.0 ~ 5.0 |
| 키워드 | 콤마 구분 |
| CS_대응_초안 | 검토 후 사용 (절대 자동 발송 금지) |
| 리스크_메모 | 주의 표현 |

---

## 6. 영업 자료

### 가격표
| 상품 | 가격 |
|---|---|
| 무료 진단 | 무료 |
| 테스트 패키지 | 49만 원 |
| 스탠다드 | 99만 원 |
| 월 유지관리 | 30만 원~ |
| SaaS 구독 | 월 4.9만 원 (예정) |

### 채널
- 랜딩페이지: https://loopforge-2v1.pages.dev
- 카카오: http://pf.kakao.com/_wLasX
- 카카오 채팅: http://pf.kakao.com/_wLasX/chat

---

## 7. 로드맵

### Phase 1 (완료)
- [x] Cloudflare Worker 배포
- [x] OpenRouter AI 연동
- [x] Google Sheets 저장
- [x] 랜딩페이지 배포
- [x] 카카오 채널 생성

### Phase 2 (진행 중)
- [ ] Railway n8n 설치
- [ ] 영업 타깃 20곳 DM
- [ ] 첫 고객 3명 확보

### Phase 3 (예정)
- [ ] Lovable 대시보드
- [ ] 카카오 알림톡 연동
- [ ] SaaS 플랜 설계

### Phase 4 (장기)
- [ ] Gumroad 템플릿 판매
- [ ] Product Hunt 런칭
- [ ] 글로벌 확장

---

## 8. 트러블슈팅

### Groq API 403 오류
**원인:** Cloudflare Workers IP가 Groq에서 차단됨  
**해결:** OpenRouter로 전환 (Llama 모델 동일하게 사용 가능)

### WEBHOOK_SECRET 인증 실패
**원인:** Cloudflare 편집기에서 헤더 값이 잘림  
**해결:** 짧은 값(`lf2026`)으로 변경

### Google Sheets 저장 안 됨
**원인:** Apps Script 배포 시 액세스 권한이 "나만"으로 설정됨  
**해결:** "모든 사용자"로 변경 후 재배포

---

## 🔗 관련 문서 및 시스템 연계

- **[[LoopForge_종합인덱스_및_교차검증]] ([종합 인덱스](./LoopForge_종합인덱스_및_교차검증.md))** - 🌟 전체 문서의 마스터 맵 및 교차검증 보고서
- **[[LoopForge_Obsidian]] ([옵시디언 노트](./LoopForge_Obsidian.md))** - 프로젝트 개요, Mermaid 아키텍처, 수익 목표 및 할 일
- **[[LoopForge_헤르메스_엔지니어링]] ([엔지니어링 문서](./LoopForge_헤르메스_엔지니어링.md))** - 세부 코드 구조, 구글 앱스 스크립트 코드, n8n 가이드
- **[[LoopForge_헤르메스_에이전트_컨텍스트]] ([에이전트 컨텍스트](./LoopForge_헤르메스_에이전트_컨텍스트.md))** - Claude용 핵심 컨텍스트 요약 및 트러블슈팅 이력
