"""팀 주간보고 초안 생성기 — Streamlit 화면.

로컬 실행:  streamlit run app.py
API 키:    로컬은 .env 파일, 배포는 Streamlit Cloud의 Secrets 칸. 둘 다 같은 이름을 쓴다
"""
import os

import anthropic
import streamlit as st
from dotenv import load_dotenv

from weekly_agent import summarize

load_dotenv()

st.set_page_config(page_title="팀 주간보고 초안 생성기")
st.title("팀 주간보고 초안 생성기")
st.caption("팀원들의 주간보고 파일을 올리면 대표 보고용 초안 1장을 만듭니다.")

files = st.file_uploader(
    "팀원 주간보고 파일 (.md / .txt, 여러 개 선택 가능)",
    type=["md", "txt"],
    accept_multiple_files=True,
)

if st.button("초안 만들기", type="primary", disabled=not files):
    reports = [(f.name, f.read().decode("utf-8")) for f in files]
    api_key = os.getenv("ANTHROPIC_API_KEY")  # 로컬 .env
    if not api_key:
        try:
            api_key = st.secrets["ANTHROPIC_API_KEY"]  # 배포 Secrets
        except Exception:
            api_key = None
    if not api_key:
        st.error("API 키가 없습니다. 로컬은 .env 파일, 배포는 Secrets 설정을 확인하세요.")
        st.stop()
    with st.spinner(f"{len(reports)}개 보고서를 읽고 초안을 쓰는 중..."):
        try:
            client = anthropic.Anthropic(api_key=api_key)
            draft = summarize(reports, client)
        except anthropic.AuthenticationError:
            st.error("API 키가 올바르지 않습니다.")
            st.stop()
        except anthropic.APIStatusError as e:
            st.error(f"API 오류 ({e.status_code}). 잠시 후 다시 시도하세요.")
            st.stop()
    st.subheader("초안")
    st.markdown(draft)
    st.download_button("마크다운으로 다운로드", draft, file_name="팀-주간보고-초안.md", on_click="ignore")
