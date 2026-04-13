"""ClipReply — AI Video Clip Q&A Assistant

Paste a video link. Get the summary. Ask anything about it.
"""

import streamlit as st
import html
from io import BytesIO

from transcriber import get_transcript, is_youtube_url, extract_video_id
from summarizer import summarize, answer_question

# --- Page Config ---
st.set_page_config(
    page_title="ClipReply — AI Video Q&A",
    page_icon="🎬",
    layout="centered",
)

# --- Custom CSS ---
st.markdown(
    """
    <style>
    /* Header */
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0;
        line-height: 1.2;
    }
    .main-subtitle {
        font-size: 1.05rem;
        opacity: 0.7;
        margin-top: 0.2rem;
        margin-bottom: 1.5rem;
    }

    /* Summary card */
    .summary-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.08);
    }

    /* Video info bar */
    .video-info {
        display: flex;
        gap: 1rem;
        align-items: center;
        padding: 0.6rem 1rem;
        background: rgba(255,255,255,0.04);
        border-radius: 8px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
    }
    .video-info span {
        opacity: 0.7;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Tighter chat spacing */
    .stChatMessage {
        padding: 0.5rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Session State ---
defaults = {
    "transcript": None,
    "summary": None,
    "chat_history": [],
    "video_url": "",
    "video_duration": 0.0,
    "videos_today": 0,
    "input_key": 0,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


def _reset_for_new_video():
    """Callback to clear all state and force a fresh URL input widget."""
    for key, val in defaults.items():
        if key not in ("videos_today", "input_key"):
            st.session_state[key] = val
    # Increment key so Streamlit creates a brand new widget (clears old value)
    st.session_state["input_key"] += 1

FREE_LIMIT = 3

# --- Header ---
st.markdown('<p class="main-title">ClipReply</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="main-subtitle">Paste a video link. Get the summary. Ask anything.</p>',
    unsafe_allow_html=True,
)

# --- URL Input ---
col_input, col_lang, col_btn = st.columns([5, 1, 1])
with col_input:
    url = st.text_input(
        "Video URL",
        key=f"url_input_{st.session_state.input_key}",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="collapsed",
    )
with col_lang:
    output_lang = st.selectbox(
        "Language",
        options=["한국어", "English"],
        key="output_lang",
        label_visibility="collapsed",
    )
with col_btn:
    summarize_btn = st.button("Go", type="primary", use_container_width=True)

# --- Free tier gate ---
remaining = max(0, FREE_LIMIT - st.session_state.videos_today)
if remaining == 0:
    st.warning(
        f"Free limit reached ({FREE_LIMIT}/day). "
        "Upgrade to **Pro ($9/mo)** for unlimited videos, longer transcripts, and PDF export."
    )
    summarize_btn = False


# --- Summarize Action ---
url_changed = url and url != st.session_state.video_url
if (summarize_btn or url_changed) and url:
    try:
        with st.spinner("Extracting transcript..."):
            transcript, source, duration = get_transcript(url)
            st.session_state.transcript = transcript
            st.session_state.video_url = url
            st.session_state.video_duration = duration
            st.session_state.chat_history = []
            st.session_state.videos_today += 1

        with st.spinner("AI is summarizing..."):
            lang = "ko" if output_lang == "한국어" else "en"
            st.session_state.summary = summarize(transcript, lang)
            st.session_state.output_lang = lang

    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Error: {html.escape(str(e))}")


# --- Results ---
if st.session_state.summary:
    # Video info bar
    duration = st.session_state.video_duration
    dur_str = (
        f"{int(duration)}m {int((duration % 1) * 60)}s" if duration > 0 else "N/A"
    )
    word_count = len(st.session_state.transcript.split())
    vid_url = st.session_state.video_url

    st.markdown(
        f'<div class="video-info">'
        f"<span>Duration: <b>{dur_str}</b></span>"
        f"<span>Words: <b>{word_count:,}</b></span>"
        f"<span>Source: <b>YouTube</b></span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Embed YouTube player
    if is_youtube_url(vid_url):
        vid_id = extract_video_id(vid_url)
        if vid_id:
            st.video(f"https://www.youtube.com/watch?v={vid_id}")

    # Summary
    st.subheader("Summary")
    st.markdown(st.session_state.summary)

    # Action buttons
    col_export, col_transcript, col_clear = st.columns(3)

    with col_export:
        # PDF export as plain text file (lightweight, no extra dependency)
        summary_text = (
            f"ClipReply Summary\n"
            f"{'=' * 40}\n"
            f"Video: {vid_url}\n"
            f"Duration: {dur_str}\n\n"
            f"--- Summary ---\n{st.session_state.summary}\n\n"
            f"--- Transcript ---\n{st.session_state.transcript[:5000]}\n"
        )
        st.download_button(
            "Download Summary (.txt)",
            data=summary_text,
            file_name="clipreply_summary.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with col_transcript:
        show_transcript = st.toggle("Show transcript")

    with col_clear:
        st.button(
            "New video",
            use_container_width=True,
            on_click=_reset_for_new_video,
        )

    if show_transcript:
        st.text_area(
            "Full Transcript",
            value=st.session_state.transcript,
            height=300,
            disabled=True,
        )

    # --- Q&A Chat ---
    st.divider()
    st.subheader("Ask about this video")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if question := st.chat_input("Ask anything about the video..."):
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    lang = st.session_state.get("output_lang", "ko")
                    answer = answer_question(
                        st.session_state.transcript,
                        question,
                        st.session_state.chat_history,
                        lang,
                    )
                    st.markdown(answer)
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": answer}
                    )
                except Exception as e:
                    st.error(f"Could not answer: {html.escape(str(e))}")

# --- Footer ---
st.divider()
remaining = max(0, FREE_LIMIT - st.session_state.videos_today)
st.caption(
    f"Free: {remaining}/{FREE_LIMIT} videos remaining today  |  "
    "**Pro $9/mo**: unlimited + long videos + PDF export"
)
