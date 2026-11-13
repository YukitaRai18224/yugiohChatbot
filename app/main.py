"""유희왕 챗봇 웹 서버 (FastAPI + Claude API)."""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Any, AsyncIterator

import anthropic
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .prompts import SYSTEM_PROMPT

MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-5-5")
EFFORT = os.environ.get("CLAUDE_EFFORT", "medium")  # low | medium | high | xhigh | max
MAX_TOKENS = 64000
MAX_SESSIONS = 500

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="유희왕 챗봇")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 자격 증명은 환경 변수 ANTHROPIC_API_KEY(또는 `ant auth login` 프로필)에서 읽습니다.
client = anthropic.AsyncAnthropic()

# 세션별 대화 기록 (메모리 저장 - 서버를 재시작하면 사라집니다)
sessions: dict[str, list[dict[str, Any]]] = {}


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str = Field(min_length=1, max_length=8000)


class ResetRequest(BaseModel):
    session_id: str


def _get_history(session_id: str) -> list[dict[str, Any]]:
    if session_id not in sessions:
        if len(sessions) >= MAX_SESSIONS:
            # 가장 오래된 세션부터 정리
            sessions.pop(next(iter(sessions)))
        sessions[session_id] = []
    return sessions[session_id]


async def _stream_reply(history: list[dict[str, Any]], user_text: str) -> AsyncIterator[str]:
    request_messages = history + [{"role": "user", "content": user_text}]
    try:
        async with client.beta.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=request_messages,
            output_config={"effort": EFFORT},
            cache_control={"type": "ephemeral"},
            # 안전 분류기가 요청을 거절하면 서버에서 자동으로 다른 모델로 재시도
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        ) as stream:
            async for text in stream.text_stream:
                yield text
            final = await stream.get_final_message()
    except anthropic.AuthenticationError:
        yield "\n\n⚠️ API 키가 올바르지 않습니다. ANTHROPIC_API_KEY 설정을 확인해 주세요."
        return
    except anthropic.RateLimitError:
        yield "\n\n⚠️ 요청이 너무 많습니다. 잠시 후 다시 시도해 주세요."
        return
    except anthropic.APIStatusError as e:
        yield f"\n\n⚠️ API 오류가 발생했습니다 ({e.status_code}): {e.message}"
        return
    except anthropic.APIConnectionError:
        yield "\n\n⚠️ Claude API 서버에 연결할 수 없습니다. 네트워크를 확인해 주세요."
        return

    if final.stop_reason == "refusal":
        yield "\n\n⚠️ 이 요청에는 답변할 수 없습니다. 질문을 바꿔서 다시 시도해 주세요."
        return  # 거절된 턴은 기록에 남기지 않음
    if final.stop_reason == "max_tokens":
        yield "\n\n(답변이 길어서 중간에 잘렸습니다.)"

    # 성공한 턴만 기록에 추가. thinking 블록 등을 보존하기 위해 content 전체를 그대로 저장합니다.
    history.append({"role": "user", "content": user_text})
    history.append({"role": "assistant", "content": final.content})


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/chat")
async def chat(req: ChatRequest) -> StreamingResponse:
    session_id = req.session_id or str(uuid.uuid4())
    history = _get_history(session_id)
    return StreamingResponse(
        _stream_reply(history, req.message.strip()),
        media_type="text/plain; charset=utf-8",
        headers={"X-Session-Id": session_id, "Cache-Control": "no-cache"},
    )


@app.post("/api/reset")
async def reset(req: ResetRequest) -> dict[str, bool]:
    if req.session_id not in sessions:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    sessions.pop(req.session_id)
    return {"ok": True}
