# 유희왕 챗봇

Claude API를 이용한 유희왕 OCG/TCG 전문 상담 챗봇입니다. 룰 판정, 카드 효과 해석, 덱 구축 상담을 한국어로 도와줍니다.

- 백엔드: Python + FastAPI, Anthropic 공식 SDK(`anthropic`)
- 프런트엔드: 단일 HTML 페이지 (답변이 실시간 스트리밍으로 표시됨)
- 모델: `claude-opus-5-5` (환경 변수로 변경 가능)

## 실행 방법

1. 의존성 설치

```bash
pip install -r requirements.txt
```

2. API 키 설정 ([Anthropic 콘솔](https://console.anthropic.com)에서 발급)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

3. 서버 실행

```bash
uvicorn app.main:app --reload
```

4. 브라우저에서 http://localhost:8000 접속

## 설정 (환경 변수)

| 변수 | 기본값 | 설명 |
|---|---|---|
| `ANTHROPIC_API_KEY` | (필수) | Claude API 키 |
| `CLAUDE_MODEL` | `claude-opus-5-5` | 사용할 모델 |
| `CLAUDE_EFFORT` | `medium` | 사고 깊이: `low` / `medium` / `high` / `xhigh` / `max` (높을수록 정확하지만 느리고 비쌈) |
| `RATE_LIMIT_PER_HOUR` | `30` | IP당 1시간에 보낼 수 있는 메시지 수. `0`이면 제한 없음 |

## 독립 도메인으로 배포하기

배포하면 누구나 접속할 수 있고, **모든 답변 비용은 내 API 키로 청구됩니다.** 먼저 [Anthropic 콘솔](https://console.anthropic.com)의 Limits 메뉴에서 월 사용 한도를 꼭 설정하세요. 서버에도 IP당 요청 제한(`RATE_LIMIT_PER_HOUR`)이 기본으로 켜져 있습니다.

### 방법 1. Render (추천)

1. [render.com](https://render.com)에 GitHub 계정으로 가입합니다.
2. **New → Blueprint**를 누르고 이 저장소를 선택합니다. `render.yaml`을 읽어 설정이 자동으로 채워집니다.
3. `ANTHROPIC_API_KEY` 입력 칸에 API 키를 넣고 **Apply**를 누릅니다.
4. 몇 분 뒤 `https://yugioh-chatbot.onrender.com` 같은 주소가 생깁니다.
5. 내 도메인 연결: 서비스의 **Settings → Custom Domains → Add Custom Domain**에 도메인(예: `chat.example.com`)을 입력하고, 도메인 구입처의 DNS 설정에 Render가 알려주는 CNAME 레코드를 추가합니다. HTTPS 인증서는 자동으로 발급됩니다.

> `render.yaml`은 무료 플랜(`plan: free`)으로 되어 있습니다. 무료 플랜은 15분간 접속이 없으면 잠들어 다음 첫 접속이 30초~1분 정도 느립니다. 항상 빠르게 응답하게 하려면 `starter`로 바꾸세요.

### 방법 2. Railway

1. [railway.com](https://railway.com)에서 **New Project → Deploy from GitHub repo**로 이 저장소를 선택합니다. `railway.json`과 `Dockerfile`로 자동 빌드됩니다.
2. 서비스의 **Variables** 탭에서 `ANTHROPIC_API_KEY`를 추가합니다.
3. **Settings → Networking → Generate Domain**으로 기본 주소를 만들거나, **Custom Domain**에 내 도메인을 입력하고 안내된 CNAME 레코드를 DNS에 추가합니다.

### 방법 3. Docker가 되는 아무 서버

```bash
docker build -t yugioh-chatbot .
docker run -d -p 80:8000 -e ANTHROPIC_API_KEY=sk-ant-... --restart unless-stopped yugioh-chatbot
```

도메인의 A 레코드를 서버 IP로 지정하고, HTTPS는 Caddy나 Nginx 같은 리버스 프록시로 붙이면 됩니다.

### 배포 시 주의

- API 키는 저장소에 절대 커밋하지 말고, 호스팅 서비스의 환경 변수 화면에만 입력하세요.
- 대화 기록은 서버 메모리에 있어서 재배포하거나 서버가 잠들면 사라집니다. 같은 이유로 인스턴스는 1개로 운영하세요.
- 상태 확인 주소: `/healthz`

## 구조

```
app/
  main.py      # FastAPI 서버, Claude API 스트리밍 호출, 세션별 대화 기록
  prompts.py   # 유희왕 챗봇 시스템 프롬프트 (챗봇 성격·답변 규칙은 여기서 수정)
static/
  index.html   # 채팅 화면
Dockerfile     # 컨테이너 이미지 (모든 배포 방법 공통)
render.yaml    # Render 배포 설정
railway.json   # Railway 배포 설정
```

## 참고

- 대화 기록은 서버 메모리에 저장되므로 서버를 재시작하면 사라집니다.
- 시스템 프롬프트에 프롬프트 캐싱을 적용해 반복 요청 비용을 줄입니다.
- 안전 분류기가 요청을 거절하면 서버 측 fallback 기능으로 다른 모델이 자동으로 이어서 답변합니다.
