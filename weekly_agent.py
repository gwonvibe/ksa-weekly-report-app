"""팀원 주간보고 여러 개 → 팀 주간보고 초안 1개.

사용법:  python weekly_agent.py 주간보고
  지정한 폴더의 .md 파일을 전부 읽어 output/팀-주간보고-초안.md 를 만든다.
API 키:  같은 폴더의 .env 파일에서 읽는다 (ANTHROPIC_API_KEY=...)
"""
import os
import pathlib
import sys

import anthropic
from dotenv import load_dotenv

load_dotenv()  # .env 의 키를 환경변수로 올린다. anthropic SDK가 자동으로 집어 간다

MODEL = "claude-sonnet-5"

SYSTEM = """당신은 제조업 중견기업 경영지원실장의 보조자다.
여러 팀장이 제출한 주간보고를 읽고, 대표 보고용 '팀 주간보고 초안' 1장을 쓴다.

규칙
- 보고서에 없는 내용을 지어내지 않는다. 수치는 원문 그대로 옮긴다.
- 여러 팀에 걸친 사안(한 팀의 이슈가 다른 팀의 요청으로 이어지는 것)은 묶어서 하나로 쓴다.
- 말투는 '~함', '~필요' 같은 개조식.

출력 형식 (마크다운)
# 주간 경영 보고 (기간)
## 1. 핵심 요약 (3줄 이내)
## 2. 팀별 실적
## 3. 부서 간 이슈 (연결된 사안 위주, 담당·기한 포함)
## 4. 대표 결정 필요 사항
## 5. 다음 주 주요 일정
"""


def load_reports(folder: str) -> list[tuple[str, str]]:
    """폴더 안의 .md 파일을 (파일명, 내용) 목록으로 읽는다."""
    paths = sorted(pathlib.Path(folder).glob("*.md"))
    return [(p.name, p.read_text(encoding="utf-8")) for p in paths]


def build_prompt(reports: list[tuple[str, str]]) -> str:
    parts = [f"<report name=\"{name}\">\n{body}\n</report>" for name, body in reports]
    return "다음 주간보고들을 읽고 팀 주간보고 초안을 작성해줘.\n\n" + "\n\n".join(parts)


def summarize(reports: list[tuple[str, str]], client: anthropic.Anthropic | None = None) -> str:
    """Claude API를 호출해 초안 텍스트를 돌려준다."""
    client = client or anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        system=SYSTEM,
        messages=[{"role": "user", "content": build_prompt(reports)}],
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("모델이 응답을 거부했습니다. 입력 내용을 확인하세요.")
    return "".join(block.text for block in response.content if block.type == "text")


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "주간보고"
    reports = load_reports(folder)
    if not reports:
        sys.exit(f"{folder}/ 에 .md 파일이 없습니다.")
    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit("API 키가 없습니다. 같은 폴더의 .env 파일을 확인하세요.")
    print(f"{len(reports)}개 보고서를 읽었습니다: {', '.join(n for n, _ in reports)}")
    try:
        draft = summarize(reports)
    except anthropic.AuthenticationError:
        sys.exit("API 키가 올바르지 않습니다.")
    except anthropic.APIStatusError as e:
        sys.exit(f"API 오류 ({e.status_code}). 잠시 후 다시 시도하세요.")
    out = pathlib.Path("output/팀-주간보고-초안.md")
    out.parent.mkdir(exist_ok=True)
    out.write_text(draft, encoding="utf-8")
    print(f"\n{out} 저장 완료\n")
    print(draft)
