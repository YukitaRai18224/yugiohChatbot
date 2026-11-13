"""YGOPRODeck에서 카드 데이터를 받아 듀얼 상담소용 cards.json을 만듭니다.

사용법: python duel-desk/build_cards.py
YGOPRODeck API 이용 가이드(https://ygoprodeck.com/api-guide/)에 따라
전체 데이터를 한 번만 받아 저장하는 방식입니다. 자주 실행하지 마세요.
"""

import json
import urllib.request
from pathlib import Path

API = "https://db.ygoprodeck.com/api/v7"
OUT = Path(__file__).with_name("cards.json")
FIELDS = ["name", "type", "race", "attribute", "level", "atk", "def", "scale",
          "archetype", "desc", "ban_tcg", "ban_ocg"]


def get(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "duel-desk-card-builder"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)


def main() -> None:
    ver = get(f"{API}/checkDBVer.php")[0]
    data = get(f"{API}/cardinfo.php")["data"]
    rows = []
    for c in data:
        if c.get("frameType") == "skill":  # 스피드 듀얼 스킬 카드는 제외
            continue
        t = c.get("type", "")
        ban = c.get("banlist_info") or {}
        rows.append([
            c["name"],
            c.get("humanReadableCardType") or t,
            c.get("race") or "",
            c.get("attribute") or "",
            c.get("linkval") if "Link" in t else c.get("level"),
            c.get("atk"),
            c.get("def"),
            c.get("scale"),
            c.get("archetype") or "",
            c.get("desc", "").replace("\r\n", "\n"),
            ban.get("ban_tcg") or "",
            ban.get("ban_ocg") or "",
        ])
    out = {
        "version": ver["database_version"],
        "updated": ver["last_update"][:10],
        "fields": FIELDS,
        "cards": rows,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(rows)}장 저장: {OUT} (DB {out['version']}, {out['updated']} 기준)")
    print("index.html의 DB_DATE와 메뉴 안내문의 날짜도 이 기준일로 바꿔 주세요.")


if __name__ == "__main__":
    main()
