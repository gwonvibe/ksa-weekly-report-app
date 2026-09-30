# 강사용 완성본 — 팀 주간보고 초안 생성기

2일차 6장(주간보고 초안 생성기)과 3일차 2장(제안서)·5장(Streamlit 화면)의 도착 지점. 수강생은 Claude Code로 이걸 *만들어 가는* 것이고, 이 폴더는 강사 시연·막힌 수강생 Fallback용이다.

## 구조
```
weekly_agent.py     2일차 6장 — 폴더 읽기 → 프롬프트 조립 → Claude 호출 → 초안 저장
proposal_agent.py   3일차 2장 — 같은 자료·같은 구조, 시스템 프롬프트만 바꿔 제안서를 뽑는다
app.py              3일차 5장 — 파일 업로드 → 버튼 → 초안 표시·다운로드
requirements.txt    anthropic, python-dotenv, streamlit
.env.example        API 키 자리 (복사해서 .env 로 만들고 키 입력, git 제외)
.streamlit/config.toml   테마(색·폰트)
```

`proposal_agent.py` 는 `weekly_agent.py` 의 `load_reports` 를 그대로 가져다 쓴다. **다른 것은 `SYSTEM` 하나뿐**이고, 그걸 나란히 놓고 보여 주는 것이 3일차 오전의 요점이다.
파일 안의 `RULE_AFTER_REVIEW` 는 수강생이 3-2(교차 검증 후)에 직접 붙이는 규칙이다. 시연 때 `propose(reports, system=SYSTEM + RULE_AFTER_REVIEW)` 로 전후를 비교해 보여 준다.

## 실행
키는 `.env` 하나로 통일돼 있다. **수강생 교안에는 터미널 명령이 없다** — 전부 앱에 말로 시킨다. 아래는 강사가 직접 확인할 때 쓰는 명령.
```bash
pip install -r requirements.txt
cp .env.example .env      # 파일을 열어 ANTHROPIC_API_KEY= 뒤에 키 입력
python weekly_agent.py ../샘플파일/한빛정밀/주간보고
python proposal_agent.py ../샘플파일/한빛정밀/주간보고
streamlit run app.py
```
`app.py` 는 `.env` 를 먼저 보고, 없으면 Streamlit Secrets를 본다. 로컬과 배포가 같은 코드로 돈다.

## 배포 (Streamlit Community Cloud)
1. GitHub 저장소에 push (`.env`는 .gitignore로 제외됨 확인)
2. share.streamlit.io → New app → 저장소·브랜치·`app.py` 선택
3. Advanced settings → Secrets 에 `ANTHROPIC_API_KEY = "sk-ant-..."` 입력
4. Deploy → URL 공유

## 모델·비용
- `claude-sonnet-5` (9/15 확정). 세 파일 모두 같은 모델을 쓴다.
- 주간보고 5개 1회 실행 ≈ **입력 3K + 출력 1.5K 토큰**

| 단가 가정 | 1회 | 10명 × 1인 30회 = 300회 |
|---|---|---|
| 입력 $3 / 출력 $15 (per MTok) | **≈ $0.03** (약 45원) | **≈ $9** |

- 옛 추정($0.05/회 · 총 $15)은 opus 기준이었고 계산도 맞지 않았다. 위 표로 교체한다.
- **단가는 강의 직전에 공식 가격표로 다시 확인할 것** (console.anthropic.com → Billing). 위 숫자는 가정 단가에 토큰 수를 곱한 것이다.
- 노션 3일차 10장 "한 번 돌리는 데 100원이 채 들지 않습니다"가 이 계산에 맞춰져 있다. 단가가 바뀌면 그 문장도 같이 본다.
- 더 낮추려면 모델 이름 한 줄만 더 저렴한 것으로 바꾼다 — 강사 판단.
