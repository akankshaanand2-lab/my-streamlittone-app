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
Your task is to rewrite raw, informal, blunt, or poorly phrased business drafts into warm, respectful, culturally polished Emirati business communication.

Key cultural nuances to apply:
1. Relationship-First Warmth: UAE business etiquette values relational warmth before transactional details. Begin with gracious, authentic pleasantries (e.g., "I hope this email finds you well and in good health").
2. Diplomatic & Respectful Phrasing: Soften ultimatums or demands. Transform blunt directives into collaborative, respectful requests.
3. Respect & Hierarchy: Maintain high deference and polite titles where applicable.
4. Clarity & Professionalism: While warm, ensure the core action items and business objectives remain distinct, professional, and clear.
5. Gracious Sign-offs: Close with genuine hospitality and well-wishes (e.g., "Wishing you and your team continued success," "Warmest regards").

Output Format:
Provide:
1. **Polished Email / Message**: The complete ready-to-send draft.
2. **Cultural Nuances & Adjustments**: 2-3 brief bullet points explaining key changes made to suit UAE business etiquette.
"""

st.title("🇦🇪 Dubai Tone Coach")
st.caption("⚡ High Speed Mode")

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

if submit_button:
    api_key = api_key_input.strip()

    if not api_key:
        st.error("Please enter your Gemini API key in the sidebar.")
    elif not rough_message.strip():
        st.warning("Please enter a message.")
    else:
        try:
            with st.spinner("Polishing tone in seconds..."):
                # Direct call to your account's working model
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={api_key}"
                
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": f"{EMIRATI_BUSINESS_SYSTEM_INSTRUCTION}\n\nDraft:\n{rough_message}"
                        }]
                    }],
                    "generationConfig": {"temperature": 0.4}
                }

                res = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=10)
                result = res.json()

                if res.status_code == 200:
                    text = result["candidates"][0]["content"]["parts"][0]["text"]
                    st.success("Draft polished in ~1 second!")
                    st.markdown("### Result")
                    st.markdown(text)
                else:
                    st.error(f"Error ({res.status_code}): {result.get('error', {}).get('message', res.text)}")

        except Exception as e:
            st.error(f"Error: {e}")
