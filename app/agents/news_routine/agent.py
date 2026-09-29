# app/agents/news_routiner.py (예시 뼈대)

import os
import json
import asyncio
from langchain.agents import create_agent
from app.utils import init_chat_model
from app.tools.common import file_read, file_writer, bash_command, glob_search, web_fetch, web_search
from app.utils.context import AgentContext

AGENT_METADATA = {
    "name": "news_routine",  # 여러분의 에이전트 이름 (소문자 권장)
    "description": "뉴스 루틴(매일 아침 최신 뉴스를 요약)을 제공하는 서브 에이전트"
}

# 1. 서브 에이전트 전용 시스템 프롬프트 정의
WORKER_SYSTEM_PROMPT = """
당신은 뉴스제공 에이전트입니다.
당신의 임무는 전달받은 주소의 뉴스 홈페이지에서 최근(오늘) 기사들을 가공/분석하여 빠르게 요약된 내용과 링크를 생성하는 것입니다.

[행동 수칙]
1. 사용자가 요청한 뉴스 웹페이지를 입력 데이터로 사용하세요.
2. 요청이 없을시에는 이미 지정된 뉴스 웹페이지를 기본으로 사용하세요. (.env)
3. 필요한 도구(`web_fetch`, `web_search`, `bash_command`, `file_writer` 등)을 사용하여 데이터를 수집하고 결과 산출물을 `artifacts/news` 폴더에 파일로 저장하세요. 파일명은 `news_YYYYMMDD_HHMMSS.json` 형식으로 생성하세요.
4. 수집한 뉴스 데이터는 JSON 형식으로 저장하며, 각 뉴스 항목은 다음과 같은 구조를 가져야 합니다:
   {
       "title": "뉴스 제목",
       "summary": "뉴스 요약 내용",
       "url": "뉴스 링크",
       "published_at": "YYYY-MM-DD HH:MM:SS"
   }
5. JSON으로 수집된 데이터를 기반으로, HTML 문서를 생성하여 `artifacts/news/news_summary_YYYYMMDD_HHMMSS.html` 형식으로 저장하세요. HTML 문서에는 뉴스 제목, 요약, 링크가 포함되어야 합니다.
6. 모든 뉴스 항목은 오늘 날짜 기준으로 필터링하여 저장하세요.
7. 그밖에 필요한 도구는 `tool_search`를 사용하여 검색 후 동적으로 로드하세요.
8. 모든 작업은 비동기적으로 수행하며, 각 단계별 진행 상황을 로그로 기록하세요.
9. 작업 완료 후 Supervisor에게는 다음 5줄 요약 포맷으로만 간결히 보고하세요:
   [TASK REPORT]
   - Status: SUCCESS | FAILED | BLOCKER
   - Target Files: (대상 파일 경로)
   - Artifacts Created: (생성한 산출물 파일 경로)
   - Summary: (핵심 결과 요약 1~2줄)
   - Issues: None
"""

# 2. 에이전트 팩토리 함수 (이 함수가 있어야 서버가 자동 로드합니다)
async def create_agent_executor():
    llm = init_chat_model(model="gemini-3.8-flash", temperature=0.0)
    
    # 에이전트에게 필요한 도구 목록 선택
    tools = [file_read, file_writer, bash_command, glob_search, web_fetch, web_search]
    
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=WORKER_SYSTEM_PROMPT,
        context_schema=AgentContext
    )
    return agent
