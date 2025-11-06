import os
import pandas as pd
import streamlit as st
from openai import OpenAI
from elasticsearch import Elasticsearch

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="강사사의 AI 위키 검색기",
    page_icon="🤖",
    layout="wide"
)

# -----------------------------
# 스타일 커스터마이징
# -----------------------------
st.markdown("""
    <style>
    body {
        background: radial-gradient(circle at top left, #0f172a, #1e293b, #0f172a);
        color: #e2e8f0;
        font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
    }
    .main-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #6366f1, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
        margin-top: -10px;
    }
    .sub-title {
        text-align: center;
        color: #94a3b8;
        font-size: 1.2rem;
        margin-bottom: 40px;
    }
    .result-card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 4px 20px rgba(56,189,248,0.15);
        color: #e2e8f0;
        font-size: 1rem;
        line-height: 1.6;
        transition: transform 0.3s ease;
    }
    .result-card:hover {
        transform: scale(1.01);
        box-shadow: 0 8px 25px rgba(99,102,241,0.3);
    }
    .wiki-card {
        background: rgba(255,255,255,0.05);
        border-left: 4px solid #38bdf8;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
        font-size: 0.9rem;
    }
    .stButton>button {
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 12px;
        font-size: 1.1rem;
        font-weight: bold;
        padding: 0.6em 1.4em;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 4px 15px rgba(99,102,241,0.4);
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #8b5cf6, #6366f1);
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(139,92,246,0.6);
    }
    .footer {
        color: #64748b;
        font-size: 0.85rem;
        text-align: center;
        margin-top: 40px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# OpenAI & Elasticsearch 연결
# -----------------------------
client = OpenAI(api_key=st.secrets["api_key"])
ELASTIC_CLOUD_ID = st.secrets["elastic_cloud_key"]
ELASTIC_API_KEY = st.secrets["elastic_api_key"]

es = Elasticsearch(
    cloud_id=ELASTIC_CLOUD_ID,
    api_key=ELASTIC_API_KEY
)

try:
    es.info()
except Exception as e:
    st.error(f"❌ Elasticsearch 연결 실패: {e}")
    st.stop()

# -----------------------------
# 헤더 섹션
# -----------------------------
st.markdown("<h1 class='main-title'>🤖 AI 위키 검색 어시스턴트</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>한글 질문 → 영어 위키 기반 의미검색 + RAG 응답 시스템</p>", unsafe_allow_html=True)
st.divider()

# -----------------------------
# 질문 입력 섹션
# -----------------------------
st.markdown("### 💬 질문을 입력하세요")
question = st.text_input("Prompt", placeholder="예: 대서양은 몇 번째로 큰 바다인가?")
submit = st.button("🚀 AI에게 물어보기")

# -----------------------------
# 처리 로직
# -----------------------------
if submit and question:
    with st.spinner("🤖 Kevin AI가 답변을 생성 중입니다..."):
        try:
            translation = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"Translate this Korean question into English: {question}"}]
            ).choices[0].message.content.strip()

            embedding = client.embeddings.create(
                input=[translation],
                model="text-embedding-ada-002"
            ).data[0].embedding

            response = es.search(
                index="wikipedia_vector_index",
                knn={
                    "field": "content_vector",
                    "query_vector": embedding,
                    "k": 5,
                    "num_candidates": 50
                }
            )

            top_hit = response['hits']['hits'][0]['_source']
            summary = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an assistant that answers in Korean based on the given context."},
                    {"role": "user", "content": f"질문: {question}\n\n참고 문서: {top_hit['text']}"}
                ]
            )

            st.divider()
            st.markdown("### 🧠 AI의 답변")
            st.markdown(f"<div class='result-card'>{summary.choices[0].message.content}</div>", unsafe_allow_html=True)

            st.markdown("### 🔍 참고 문서 목록")
            for hit in response['hits']['hits']:
                title = hit['_source']['title']
                url = hit['_source']['url']
                score = round(hit['_score'], 2)
                st.markdown(f"<div class='wiki-card'>🔗 <a href='{url}' target='_blank'>{title}</a> — 점수: {score}</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"⚠️ 오류 발생: {e}")

# -----------------------------
# Footer
# -----------------------------
st.markdown("<div class='footer'>© 2025 Kevin AI | Powered by OpenAI & Elasticsearch | Designed with 💎 by Streamlit</div>", unsafe_allow_html=True)
