import os
import requests
import streamlit as st

# Page configuration
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
st.markdown(
    "Transform blunt or rushed drafts into warm, relationship-first, and culturally "
    "polished business communication tailored for the UAE corporate landscape."
)

# Sidebar
with st.sidebar:
    st.header("Settings")
    saved_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
    api_key_input = st.text_input(
        "Gemini API Key",
        type="password",
        value=saved_key,
        help="Paste your AQ... or AIza... key here."
    )
    
    selected_model = st.selectbox(
        "Model",
        options=["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
        index=0
    )

# Main input
rough_message = st.text_area(
    "Paste your rough draft or draft message:",
    height=180,
    placeholder="e.g., Need the financial breakdown right now. If it's not sent by 3 PM the meeting is canceled."
)

submit_button = st.button("✨ Polish Tone", type="primary")

def call_gemini(model, text, api_key):
    """Sends request to Google Gemini with a 15-second timeout."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{EMIRATI_BUSINESS_SYSTEM_INSTRUCTION}\n\n---\nDraft message to rewrite:\n{text}"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.4
        }
    }
    # 15 second timeout prevents endless loading
    return requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=15)

if submit_button:
    api_key = api_key_input.strip()

    if not api_key:
        st.error("Please expand the sidebar (click the >> in the top left) and enter your Gemini API key.")
    elif not rough_message.strip():
        st.warning("Please provide a draft message to rewrite.")
    else:
        try:
            with st.spinner(f"Polishing tone with {selected_model}..."):
                # Try the selected model first
                response = call_gemini(selected_model, rough_message, api_key)
                
                # If 404, automatically try the fallback model
                if response.status_code == 404 and selected_model != "gemini-1.5-flash":
                    st.info(f"{selected_model} was not found, trying gemini-1.5-flash...")
                    response = call_gemini("gemini-1.5-flash", rough_message, api_key)

                result = response.json()

                if response.status_code == 200:
                    rewritten_text = result["candidates"][0]["content"]["parts"][0]["text"]
                    st.success("Draft polished successfully!")
                    st.markdown("### Result")
                    st.markdown(rewritten_text)
                else:
                    error_msg = result.get("error", {}).get("message", response.text)
                    st.error(f"Google API Error ({response.status_code}): {error_msg}")

        except requests.exceptions.Timeout:
            st.error("Request timed out. Google's servers took too long to respond. Please try again.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")