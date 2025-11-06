import os
import pandas as pd
import streamlit as st
from openai import OpenAI
from elasticsearch import Elasticsearch

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="춘사마마의 AI 위키 검색기",
    page_icon="📘",
    layout="wide"
)

# -----------------------------
# 커스텀 CSS (세련되고 화려하게)
# -----------------------------
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #eef2ff, #e0f2fe);
        color: #1e293b;
        font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
    }
    .main-title {
        text-align: center;
        color: #1e3a8a;
        font-size: 2.8rem;
        font-weight: 800;
        margin-top: -10px;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }
    .sub-title {
        text-align: center;
        color: #334155;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #2563eb, #1e40af);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.6em 1.2em;
        box-shadow: 0 4px 8px rgba(37,99,235,0.3);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #1e40af, #1d4ed8);
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(37,99,235,0.4);
    }
    .result-card {
        background: white;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        border-left: 5px solid #2563eb;
        animation: fadeIn 0.5s ease-in-out;
    }
    .wiki-card {
        background: #f8fafc;
        border-radius: 10px;
        padding: 12px 15px;
        margin-bottom: 8px;
        transition: all 0.2s ease;
        border: 1px solid #e2e8f0;
    }
    .wiki-card:hover {
        background: #eff6ff;
        transform: translateY(-2px);
        box-shadow: 0 2px 6px rgba(59,130,246,0.2);
    }
    .footer {
        color: #94a3b8;
        font-size: 0.85rem;
        text-align: center;
        margin-top: 40px;
    }
    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(10px);}
        to {opacity: 1; transform: translateY(0);}
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

# 연결 테스트
try:
    es.info()
except Exception as e:
    st.error(f"❌ Elasticsearch 연결 실패: {e}")
    st.stop()

# -----------------------------
# 헤더
# -----------------------------
st.markdown("<h1 class='main-title'>📘 한글로 답변하는 영문 위키 기반 AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Semantic Search + RAG 기반 | Powered by Elasticsearch & OpenAI</p>", unsafe_allow_html=True)
st.divider()

# -----------------------------
# 소개 섹션
# -----------------------------
with st.expander("📄 서비스 소개", expanded=False):
    st.caption("""
    이 서비스는 **영문 위키피디아 데이터셋(25,000건)**을 기반으로  
    한국어 질문을 **의미 검색(Semantic Search)** 및 **RAG(Retrieval-Augmented Generation)** 기술로 분석하여  
    가장 관련 있는 문서를 찾아 **한글로 답변**을 생성합니다.

    **예시 질문**
    - 🌊 대서양은 몇 번째로 큰 바다인가?
    - 🏙 대한민국의 수도는?
    - 🚗 도요타에서 가장 많이 팔리는 차는?
    """)

# -----------------------------
# 질문 입력
# -----------------------------
st.markdown("### 💬 질문을 입력하세요")
question = st.text_inp_
