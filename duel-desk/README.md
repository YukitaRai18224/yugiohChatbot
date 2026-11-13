# 듀얼 상담소 (claude.ai 페이지 버전)

claude.ai에 게시한 유희왕 상담 챗봇 페이지의 원본입니다. 오랜 찐친 나나세가 반말로 편하게 룰 판정, 카드 효과 해석, 덱 고민을 같이 봐 줍니다.

- 게시 주소: https://claude.ai/artifact/EmLAy2GsK6pDTAfCePinbD
- API 키가 필요 없습니다. 답변은 페이지를 연 사람의 Claude 계정으로 생성됩니다.
- 이 페이지는 claude.ai의 Artifact 기능(`window.claude.use("sample")`)으로 Claude를 호출하므로, 파일을 브라우저에서 직접 열면 Claude에 연결되지 않습니다. 수정한 뒤에는 claude.ai에 다시 게시해야 반영됩니다.
- `index.html`에는 `<html>`, `<head>` 태그가 없습니다. 게시할 때 claude.ai가 자동으로 감싸 줍니다.

## 파일

| 파일 | 설명 |
|---|---|
| `index.html` | 페이지 본문 (화면, 스타일, 챗봇 지침, 동작 스크립트) |
| `nanase-face.webp` | 기본 얼굴 (`images/nanase.png`에서 잘라 줄인 것) |
| `nanase_smile-face.webp` | 미소 얼굴 (`images/nanase_smile.png`에서 잘라 줄인 것) |
| `nanase-full.webp` | 처음 화면의 전신 이미지 |

## 미소 표정 동작

챗봇 지침(`index.html`의 `RULES`)에 따라 Claude가 웃는 표정이 어울리는 답변 끝에 `[[미소]]` 표시를 남기면, 화면에서는 표시를 숨기고 얼굴 이미지를 미소 모습으로 바꿉니다. 웃는 조건을 바꾸려면 `RULES`의 "표정 표시" 문단을 수정하세요.
