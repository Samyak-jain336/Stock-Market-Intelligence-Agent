import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import base64
from agent.graph import build_graph

# Page config
st.set_page_config(
    page_title="Stock Market Intelligence Agent",
    layout="wide",
    page_icon="📈"
)

try:
    db_url = st.secrets.get("DATABASE_URL", "NOT FOUND")
    st.sidebar.write(f"DB URL: {'YES' if db_url and db_url != 'NOT FOUND' else 'NO - ' + str(db_url)}")
    google_key = st.secrets.get("GOOGLE_API_KEY", "NOT FOUND")
    st.sidebar.write(f"GOOGLE KEY: {'YES' if google_key and google_key != 'NOT FOUND' else 'NO'}")
except Exception as e:
    st.sidebar.write(f"Secrets error: {str(e)}")

# Header
st.title("📈 Stock Market Intelligence Agent")
st.caption("Ask any question about Nifty 50 stocks (2007–2021) in English, Hindi, or Hinglish")

# Sidebar
with st.sidebar:
    st.header("About")
    st.write(
        "Stock Market Intelligence Agent powered by **LangGraph** and **Gemini 2.5 Flash**. "
        "Supports **English**, **Hindi**, and **Hinglish** queries. "
        "Data covers **Nifty 50 stocks** from **2007 to 2021**."
    )
    st.subheader("Sample Questions")
    st.markdown(
        "- Which sector had the highest average closing price in 2020?\n"
        "- Which IT stocks had the highest average volume in 2019?\n"
        "- What is the average closing price of RELIANCE in 2020?\n"
        "- Which banking stocks outperformed in 2018?\n"
        "- 2019 mein sabse zyada volume wala IT stock kaun sa tha?"
    )

# Input section
if "question_input" not in st.session_state:
    st.session_state["question_input"] = ""

text_input = st.text_input("Question", placeholder="Type your question here...", value=st.session_state["question_input"], label_visibility="collapsed")
question = text_input

col_mic, col_btn = st.columns([3, 1])

with col_mic:
    try:
        from streamlit_mic_recorder import mic_recorder
        audio = mic_recorder(key="mic", start_prompt="🎙️ Record", stop_prompt="⏹️ Stop", just_once=True)
        if audio and audio.get("bytes"):
            try:
                from groq import Groq
                groq_api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
                client = Groq(api_key=groq_api_key)
                transcribed = client.audio.transcriptions.create(
                    file=("audio.webm", audio["bytes"]),
                    model="whisper-large-v3",
                    response_format="text"
                )
                st.session_state["question_input"] = transcribed
                st.info(f"🎤 Transcribed: {transcribed}")
                st.rerun()
            except Exception as e:
                st.warning(f"Could not transcribe: {str(e)}")
    except ImportError:
        st.info("Install `streamlit-mic-recorder` and `groq` for voice input.")

with col_btn:
    analyse_clicked = st.button("🔍 Analyse", use_container_width=True)

# On Analyse button click
if analyse_clicked:
    if not question or question.strip() == "":
        st.warning("Please enter a question before clicking Analyse.")
    else:
        with st.spinner("Analysing your question..."):
            graph = build_graph()
            result = graph.invoke({
                "question": question,
                "sql": None,
                "valid_question": None,
                "valid": None,
                "error": None,
                "results": None,
                "execution_error": None,
                "valid_results": None,
                "insight": None,
                "audio_path": None,
                "attempts": 0,
                "language": None
            })

        # Output section
        insight = result.get("insight", "")
        sql = result.get("sql")
        results_df = result.get("results")
        audio_bytes = result.get("audio_bytes")
        st.sidebar.write(f"Audio bytes: {audio_bytes is not None}")
        st.sidebar.write(f"Language: {result.get('language')}")

        # 1. Insight box (full width)
        warning_phrases = [
            "Unable to answer",
            "I can only answer",
            "Invalid input",
            "I am sorry"
        ]
        if insight:
            if any(phrase in insight for phrase in warning_phrases):
                st.warning(insight)
            else:
                st.success(f"💡 **Insight**\n\n{insight}")

        # 2. Two columns: Data table and SQL
        col_data, col_sql = st.columns([3, 2])

        with col_data:
            if results_df is not None and not results_df.empty:
                st.subheader("📊 Data")
                st.dataframe(results_df, use_container_width=True)

        with col_sql:
            if sql is not None:
                st.subheader("🛢️ SQL Generated")
                st.code(sql, language="sql")

        # 3. Audio player (full width)
        if audio_bytes is not None:
            st.audio(audio_bytes, format="audio/mp3")
            st.caption("🔊 Insight read aloud")

        # 4. Divider
        st.divider()
