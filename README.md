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

## 구조

```
app/
  main.py      # FastAPI 서버, Claude API 스트리밍 호출, 세션별 대화 기록
  prompts.py   # 유희왕 챗봇 시스템 프롬프트 (챗봇 성격·답변 규칙은 여기서 수정)
static/
  index.html   # 채팅 화면
```

## 참고

- 대화 기록은 서버 메모리에 저장되므로 서버를 재시작하면 사라집니다.
- 시스템 프롬프트에 프롬프트 캐싱을 적용해 반복 요청 비용을 줄입니다.
- 안전 분류기가 요청을 거절하면 서버 측 fallback 기능으로 다른 모델이 자동으로 이어서 답변합니다.
