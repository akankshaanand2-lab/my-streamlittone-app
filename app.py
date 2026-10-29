import json
import os
import requests
import streamlit as st

st.set_page_config(
    page_title="Dubai Tone Coach",
    page_icon="🇦🇪",
    layout="centered"
)

EMIRATI_BUSINESS_SYSTEM_INSTRUCTION = """
You are an expert executive communications coach specializing in UAE and Gulf (GCC) corporate culture.
Rewrite the draft into warm, respectful, culturally polished Emirati business communication.

Key cultural nuances:
1. Warmth & Relationship-First: Gracious pleasantries ("I hope this email finds you well").
2. Diplomatic Phrasing: Soften ultimatums into respectful requests.
3. Hierarchy & Deference: High politeness and respectful address.
4. Professional Clarity: Keep core action points clear.
5. Gracious Sign-offs: Close with genuine hospitality and well-wishes.

Format:
1. **Polished Email / Message**
2. **Cultural Nuances & Adjustments** (2 brief bullets)
"""

st.title("🇦🇪 Dubai Tone Coach")
st.caption("⚡ Live Streaming Mode (Instant Start)")

with st.sidebar:
    st.header("Settings")
    saved_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
    api_key_input = st.text_input(
        "Gemini API Key",
        type="password",
        value=saved_key,
        help="Paste your AQ... key here"
    )

rough_message = st.text_area(
    "Paste your rough draft or draft message:",
    height=180,
    placeholder="e.g., hello habibi"
)

submit_button = st.button("✨ Polish Tone", type="primary")

def stream_response(api_key, text):
    """Streams tokens directly from Google SSE endpoint in real time."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:streamGenerateContent?alt=sse&key={api_key}"
    payload = {
        "contents": [{
            "parts": [{
                "text": f"{EMIRATI_BUSINESS_SYSTEM_INSTRUCTION}\n\nDraft:\n{text}"
            }]
        }],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 600
        }
    }
    
    # stream=True opens the live connection immediately
    with requests.post(url, headers={"Content-Type": "application/json"}, json=payload, stream=True, timeout=15) as res:
        if res.status_code != 200:
            yield f"Error ({res.status_code}): {res.text}"
            return

        for line in res.iter_lines():
            if line:
                decoded = line.decode("utf-8")
                if decoded.startswith("data: "):
                    try:
                        chunk = json.loads(decoded[6:])
                        part_text = chunk["candidates"][0]["content"]["parts"][0]["text"]
                        yield part_text
                    except (KeyError, IndexError, json.JSONDecodeError):
                        continue

if submit_button:
    api_key = api_key_input.strip()

    if not api_key:
        st.error("Please enter your Gemini API key in the sidebar.")
    elif not rough_message.strip():
        st.warning("Please enter a message.")
    else:
        st.markdown("### Result")
        # st.write_stream renders the words live as they arrive
        st.write_stream(stream_response(api_key, rough_message))
