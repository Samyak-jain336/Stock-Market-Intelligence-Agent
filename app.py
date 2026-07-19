import streamlit as st
import os
import tempfile
import base64
from agent.graph import build_graph
import io
import shutil
from pydub import AudioSegment
import pydub.utils

os.environ["PATH"] += os.pathsep + r"C:\Users\samya\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin"

FFMPEG_PATH = r"C:\Users\samya\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin\ffmpeg.exe"
FFPROBE_PATH = r"C:\Users\samya\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin\ffprobe.exe"

if shutil.which("ffmpeg"):
    AudioSegment.converter = shutil.which("ffmpeg")
    AudioSegment.ffprobe = shutil.which("ffprobe")
elif os.path.exists(FFMPEG_PATH):
    AudioSegment.converter = FFMPEG_PATH
    AudioSegment.ffprobe = FFPROBE_PATH
# Page config
st.set_page_config(
    page_title="Stock Market Intelligence Agent",
    layout="wide",
    page_icon="📈"
)

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

text_input = st.text_input("", placeholder="Type your question here...", value=st.session_state["question_input"])
question = text_input

col_mic, col_btn = st.columns([3, 1])

with col_mic:
    try:
        from streamlit_mic_recorder import mic_recorder
        audio = mic_recorder(key="mic", start_prompt="🎙️ Record", stop_prompt="⏹️ Stop", just_once=True)
        if audio and audio.get("bytes"):
            import speech_recognition as sr
            # Save audio bytes to a temp WAV file
            audio_segment = AudioSegment.from_file(io.BytesIO(audio["bytes"]))
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                audio_segment.export(tmp.name, format="wav")
                tmp_path = tmp.name
            recognizer = sr.Recognizer()
            with sr.AudioFile(tmp_path) as source:
                audio_data = recognizer.record(source)
            try:
                transcribed = recognizer.recognize_google(audio_data)
                st.session_state["question_input"] = transcribed
                st.info(f"🎤 Transcribed: {transcribed}")
                st.rerun()
            except sr.UnknownValueError:
                st.warning("Could not transcribe. Please type your question.")
            except sr.RequestError:
                st.warning("Could not transcribe. Please type your question.")
            finally:
                os.unlink(tmp_path)
    except ImportError:
        st.info("Install `streamlit-mic-recorder` and `SpeechRecognition` for voice input.")

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
        audio_path = result.get("audio_path")

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
        if audio_path is not None and os.path.exists(audio_path):
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3")
            st.caption("🔊 Insight read aloud")

        # 4. Divider
        st.divider()
