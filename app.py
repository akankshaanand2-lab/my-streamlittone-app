import os
import requests
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="UAE Tone Coach",
    page_icon="🇦🇪",
    layout="centered"
)

# Custom system instructions tailored for UAE business etiquette
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

# App Header
st.title("UAE Tone Coach")
st.markdown(
    "Transform blunt or rushed drafts into warm, relationship-first, and culturally "
    "polished business communication tailored for the UAE corporate landscape."
)

# Sidebar: Settings
with st.sidebar:
    st.header("Settings")
    saved_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
    api_key_input = st.text_input(
        "Gemini API Key",
        type="password",
        value=saved_key,
        help="Paste your AQ... or AIza... key here."
    )
    
    # Model selection (defaulted to the requested gemini-3.8-flash)
    selected_model = st.selectbox(
        "Model Version",
        options=["gemini-3.8-flash", "gemini-2.0-flash", "gemini-1.5-flash"],
        index=0
    )
    
    st.markdown("---")
    st.markdown(
        "**Why UAE Tone Matters:**\n"
        "- Cultivates trust & goodwill\n"
        "- Respects relationship-first culture\n"
        "- Strikes the right balance between executive clarity and diplomatic warmth"
    )

# Main input form
rough_message = st.text_area(
    "Paste your rough draft or draft message:",
    height=180,
    placeholder="e.g., Need the financial breakdown right now. If it's not sent by 3 PM the meeting is canceled."
)

submit_button = st.button("✨ Polish Tone", type="primary")

# Generation logic
if submit_button:
    api_key = api_key_input.strip()

    if not api_key:
        st.error("Please enter your Gemini API key in the sidebar.")
    elif not rough_message.strip():
        st.warning("Please provide a draft message to rewrite.")
    else:
        try:
            with st.spinner(f"Refining tone using {selected_model}..."):
                # Call Gemini API directly using the model Google requested
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{selected_model}:generateContent?key={api_key}"

                prompt_content = f"{EMIRATI_BUSINESS_SYSTEM_INSTRUCTION}\n\n---\nDraft message to rewrite:\n{rough_message}"

                payload = {
                    "contents": [
                        {
                            "parts": [{"text": prompt_content}]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.4
                    }
                }

                response = requests.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json=payload
                )

                result = response.json()

                if response.status_code == 200:
                    rewritten_text = result["candidates"][0]["content"]["parts"][0]["text"]
                    st.success("Draft polished successfully!")
                    st.markdown("### Result")
                    st.markdown(rewritten_text)
                else:
                    error_msg = result.get("error", {}).get("message", response.text)
                    st.error(f"Google API Error ({response.status_code}): {error_msg}")

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")