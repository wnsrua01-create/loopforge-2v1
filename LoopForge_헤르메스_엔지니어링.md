# LoopForge AI — 엔지니어링 문서

> 기술 구현 세부 사항, 코드 구조, 배포 방법

---

## 1. 아키텍처 개요

```
┌─────────────────────────────────────────────────┐
│                  클라이언트                       │
│  (브라우저 / Lovable 대시보드 / n8n)              │
└──────────────────────┬──────────────────────────┘
                       │ POST + X-Webhook-Secret
                       ▼
┌─────────────────────────────────────────────────┐
│         Cloudflare Workers (Edge)                │
│                                                 │
│  loopforge-review-api                           │
│  ├── CORS 처리                                   │
│  ├── 인증 (WEBHOOK_SECRET)                       │
│  ├── PII 마스킹 (이름, 전화번호)                  │
│  ├── OpenRouter API 호출                         │
│  ├── 배치 처리 (5개씩)                            │
│  └── 집계 리포트 생성                             │
└──────────────────────┬──────────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
┌──────────────────┐    ┌──────────────────────────┐
│  OpenRouter API  │    │  Google Apps Script       │
│  (백그라운드)     │    │  (백그라운드 저장)         │
│  Llama 3.3 70B  │    │  ├── positive_reviews     │
└──────────────────┘    │  └── negative_reviews     │
                        └──────────────────────────┘
```

---

## 2. Worker 코드 구조

### loopforge-review-api (핵심 로직)

```javascript
// 처리 순서
1. CORS 헤더 설정
2. OPTIONS preflight 처리
3. POST 메서드 검증
4. X-Webhook-Secret 인증
5. JSON 파싱
6. 필수값 검증 (business_name, reviews)
7. 리뷰 수 검증 (1~50개)
8. PII 마스킹 (이름, 전화번호)
9. OpenRouter API 병렬 호출 (BATCH_SIZE=5)
10. 결과 집계 (negative_count, avg_score, top_keywords)
11. Google Apps Script로 백그라운드 저장
12. JSON 응답 반환
```

### System Prompt (LLM)
```
너는 한국 소상공인 리뷰를 분석하는 AI 마케팅 전문가다.
반드시 아래 JSON 형식으로만 출력한다.

{
  "sentiment_score": 1~5 숫자,
  "sentiment_label": "positive|negative|neutral",
  "keywords": ["키워드1", "키워드2", "키워드3"],
  "personal_thanks": "긍정이면 감사 답글. 부정이면 null",
  "cs_defense": "부정이면 CS 대응. 긍정이면 null",
  "blog_draft": "블로그 홍보글 초안 150~200자",
  "risk_note": "주의 표현 있으면 작성. 없으면 null"
}

주의: 의료효과, 금융수익, 법률보장 표현 금지.
과장광고 금지. 검토용 초안임.
```

---

## 3. 환경변수

### review-api Worker
```bash
OPENROUTER_API_KEY=sk-or-v1-...  # Secret
WEBHOOK_SECRET=lf2026              # Secret
```

### webhook-proxy Worker
```bash
WEBHOOK_SECRET=lf2026              # Secret
N8N_WEBHOOK_URL=https://...        # Secret (n8n 설치 후)
```

---

## 4. Google Apps Script

```javascript
function doPost(e) {
  const data = JSON.parse(e.postData.contents);
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const now = new Date().toLocaleString('ko-KR', {timeZone: 'Asia/Seoul'});

  data.results.forEach(result => {
    if (result.is_negative) {
      // negative_reviews 시트에 저장
      ss.getSheetByName('negative_reviews').appendRow([
        now, data.business_name, result.sentiment_score,
        result.keywords.join(', '), result.cs_defense, result.risk_note
      ]);
    } else {
      // positive_reviews 시트에 저장
      ss.getSheetByName('positive_reviews').appendRow([
        now, data.business_name, result.sentiment_score,
        result.keywords.join(', '), result.personal_thanks,
        result.blog_draft, result.risk_note
      ]);
    }
  });

  return ContentService
    .createTextOutput(JSON.stringify({success: true}))
    .setMimeType(ContentService.MimeType.JSON);
}
```

---

## 5. n8n 워크플로우 (다음 단계)

### Railway 배포
```bash
# 1. railway.app/new/template/n8n 접속
# 2. 환경변수 설정
N8N_ENCRYPTION_KEY=랜덤32자
WEBHOOK_URL=https://{railway-url}
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=loopforge
N8N_BASIC_AUTH_PASSWORD=안전한비밀번호
```

### 워크플로우 import
```
n8n 대시보드 → Settings → Import → loopforge-review-workflow.json
```

### Cloudflare 업데이트
```
loopforge-webhook-proxy 설정 →
N8N_WEBHOOK_URL = https://{railway-url}/webhook/loopforge-review
```

---

## 6. 테스트

### curl 테스트
```bash
curl -X POST https://loopforge-review-api.wnsrua01.workers.dev \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: lf2026" \
  -d '{
    "business_name": "테스트 카페",
    "platform": "naver_place",
    "reviews": [
      {
        "id": "r001",
        "text": "커피가 정말 맛있어요! 또 올게요.",
        "rating": 5,
        "author": "김수진",
        "date": "2026-05-17"
      },
      {
        "id": "r002",
        "text": "서비스가 너무 불친절했어요.",
        "rating": 1,
        "author": "이영희",
        "date": "2026-05-17"
      }
    ]
  }'
```

### 예상 응답
```json
{
  "success": true,
  "summary": {
    "total": 2,
    "negative_count": 1,
    "positive_count": 1,
    "avg_sentiment_score": 3.0
  }
}
```

---

## 7. 보안 체크리스트

- [x] HTTPS (Cloudflare 자동)
- [x] Webhook Secret 인증
- [x] PII 마스킹
- [x] API 키 환경변수 관리
- [x] AI 초안 자동 발송 금지 (검토용만)
- [ ] Rate Limiting (추후)
- [ ] IP Allowlist (추후)
- [ ] n8n 서버 인증 (설치 후)

---

## 8. 비용 구조

| 서비스 | 비용 |
|---|---|
| Cloudflare Workers | 무료 (10만 req/일) |
| Cloudflare Pages | 무료 |
| OpenRouter (Llama) | ~$0.0001/리뷰 |
| Google Sheets | 무료 |
| Railway n8n | $5~/월 |
| 카카오 채널 | 무료 |

**월 예상 비용:** 리뷰 1,000건 기준 약 $5~10 (약 7,000~14,000원)

---

## 🔗 관련 문서 및 시스템 연계

- **[[LoopForge_종합인덱스_및_교차검증]] ([종합 인덱스](./LoopForge_종합인덱스_및_교차검증.md))** - 🌟 전체 문서의 마스터 맵 및 교차검증 보고서
- **[[LoopForge_Obsidian]] ([옵시디언 노트](./LoopForge_Obsidian.md))** - 프로젝트 개요, Mermaid 아키텍처, 수익 목표 및 할 일
- **[[LoopForge_Wiki]] ([프로젝트 위키](./LoopForge_Wiki.md))** - 세부 기술 스택, API 명세, Sheets 구조
- **[[LoopForge_헤르메스_에이전트_컨텍스트]] ([에이전트 컨텍스트](./LoopForge_헤르메스_에이전트_컨텍스트.md))** - Claude용 핵심 컨텍스트 요약 및 트러블슈팅 이력
