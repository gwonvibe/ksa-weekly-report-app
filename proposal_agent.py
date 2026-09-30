"""주간보고 여러 개 → 내부 제안서 초안 1건. (3일차 오전 실습①)

사용법:  python proposal_agent.py 주간보고
  지정한 폴더의 .md 파일을 전부 읽어 output/제안서-초안.md 를 만든다.
API 키:  같은 폴더의 .env 파일에서 읽는다 (ANTHROPIC_API_KEY=...)

weekly_agent.py 와 읽는 자료도 구조도 같다. 다른 것은 시스템 프롬프트뿐이다.
"같은 자료로 규칙만 바꾸면 다른 문서가 나온다"를 보여주는 것이 이 파일의 목적이다.
"""
import os
import pathlib
import sys

import anthropic
from dotenv import load_dotenv

from weekly_agent import load_reports

load_dotenv()

MODEL = "claude-sonnet-5"

SYSTEM = """당신은 제조업 중견기업 경영지원실장의 보조자다.
여러 팀장이 제출한 주간보고를 읽고, 내부 제안서 1건의 초안을 쓴다.

규칙
- 주간보고 여러 개에 반복해서 나오는 문제를 하나 고른다. 여러 개를 나열하지 않는다.
- 그 문제를 해결하자는 제안 한 건을 쓴다.
- 원문에 없는 수치는 지어내지 않는다. 근거가 없으면 숫자 대신 "확인 필요"라고 적는다.
- 말투는 '~함', '~필요' 같은 개조식.

출력 형식 (마크다운)
# 제목
## 1. 현황
## 2. 문제
## 3. 제안
## 4. 기대 효과
## 5. 필요한 것과 일정
"""

# 3-2 에서 수강생이 직접 추가하는 규칙.
# 교차 검증으로 "기대 효과에 없던 숫자가 들어갔다"를 잡은 뒤 붙인다.
# 강사 시연 때는 아래 줄을 SYSTEM 끝에 더해 전후를 비교해 보여 준다.
RULE_AFTER_REVIEW = (
    '- 기대 효과에 숫자를 쓸 때는 원문에 있는 수치만 쓰고, '
    '원문에 없으면 숫자 대신 "확인 필요"라고 적는다.\n'
)


def build_prompt(reports: list[tuple[str, str]]) -> str:
    parts = [f'<report name="{name}">\n{body}\n</report>' for name, body in reports]
    return "다음 주간보고들을 읽고 내부 제안서 초안을 작성해줘.\n\n" + "\n\n".join(parts)


def propose(
    reports: list[tuple[str, str]],
    client: anthropic.Anthropic | None = None,
    system: str = SYSTEM,
) -> str:
    """Claude API를 호출해 제안서 초안 텍스트를 돌려준다."""
    client = client or anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        system=system,
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
        draft = propose(reports)
    except anthropic.AuthenticationError:
        sys.exit("API 키가 올바르지 않습니다.")
    except anthropic.APIStatusError as e:
        sys.exit(f"API 오류 ({e.status_code}). 잠시 후 다시 시도하세요.")
    out = pathlib.Path("output/제안서-초안.md")
    out.parent.mkdir(exist_ok=True)
    out.write_text(draft, encoding="utf-8")
    print(f"\n{out} 저장 완료\n")
    print(draft)
