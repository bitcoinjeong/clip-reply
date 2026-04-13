"""ClipReply - AI Video Clip Q&A Assistant"""

import streamlit as st
import html
import requests

from transcriber import get_transcript, is_youtube_url, is_tiktok_url
from summarizer import summarize, answer_question

st.set_page_config(page_title="ClipReply", page_icon="🎬", layout="wide")

# --- Session State ---
if "transcript" not in st.session_state:
    st.session_state.transcript = None
if "summary" not in st.session_state:
    st.session_state.summary = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "video_url" not in st.session_state:
    st.session_state.video_url = ""
if "videos_today" not in st.session_state:
    st.session_state.videos_today = 0

FREE_LIMIT = 3

# --- Header ---
st.title("ClipReply")
st.caption("Paste a video link. Get the summary. Ask anything about it.")

# --- URL Input ---
col1, col2 = st.columns([4, 1])
with col1:
    url = st.text_input("Video URL", key="video_url_input", placeholder="https://www.youtube.com/watch?v=...")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    summarize_btn = st.button("Summarize", type="primary", use_container_width=True)

# --- Free tier notice ---
if st.session_state.videos_today >= FREE_LIMIT:
    st.warning(f"You've reached the free limit of {FREE_LIMIT} videos today. Upgrade to Pro for unlimited access ($9/month).")
    summarize_btn = False

# --- Summarize Action ---
if summarize_btn and url:
    try:
        with st.spinner("Extracting transcript..."):
            transcript, source = get_transcript(url)
            st.session_state.transcript = transcript
            st.session_state.video_url = url
            st.session_state.chat_history = []
            st.session_state.videos_today += 1

        with st.spinner("Generating summary..."):
            st.session_state.summary = summarize(transcript)

        st.success("Done! Summary ready.")
    except ValueError as e:
        st.error(str(e))
    except requests.exceptions.Timeout:
        st.error("Request timed out. The video may be too long or the API is slow. Try again.")
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the API. Please try again later.")
    except Exception as e:
        st.error(f"An error occurred: {html.escape(str(e))}")

# --- Clear Button ---
if st.session_state.transcript:
    if st.button("Clear", key="clear_btn"):
        st.session_state.transcript = None
        st.session_state.summary = None
        st.session_state.chat_history = []
        st.session_state.video_url = ""
        st.rerun()

# --- Summary Display ---
if st.session_state.summary:
    st.subheader("Summary")
    st.markdown(st.session_state.summary)

    # --- Transcript (collapsible) ---
    with st.expander("View full transcript"):
        st.text_area("Transcript", value=st.session_state.transcript, height=200, disabled=True, key="transcript_view")

    # --- Q&A Section ---
    st.divider()
    st.subheader("Ask about this video")

    # Chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if question := st.chat_input("Ask a question about the video..."):
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer = answer_question(
                        st.session_state.transcript,
                        question,
                        st.session_state.chat_history,
                    )
                    st.markdown(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                except Exception as e:
                    error_msg = f"Could not generate answer: {html.escape(str(e))}"
                    st.error(error_msg)

# --- Footer ---
st.divider()
st.caption(f"Free plan: {max(0, FREE_LIMIT - st.session_state.videos_today)} videos remaining today | Pro: $9/month for unlimited")