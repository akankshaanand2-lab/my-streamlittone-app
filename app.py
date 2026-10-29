import os
import streamlit as st
from google import genai
from google.genai import types

# Page configuration
st.set_page_config(
    page_title="Dubai Tone Coach",
    page_icon="🇦🇪",
    layout="centered"
)

# Custom system instructions tailored for UAE business etiquette
EMIRATI_BUSINESS_SYSTEM_INSTRUCTION = """
You are an expert executive communications coach specializing in UAE and Gulf (GCC) corporate culture.
Your task is to rewrite raw, informal, blunt, or poorly phrased business drafts into warm, respectful, culturally polished Emirati business communication.

Key cultural nuances to apply:
1. Relationship-First Warmth: UAE business etiquette values relational warmth before transactional details. Begin with gracious, authentic pleasantries (e.g., "I hope this email finds you well and in good health," or appropriate formal greetings).
2. Diplomatic & Respectful Phrasing: Soften ultimatums or demands. Transform blunt directives ("I need this by 2 PM") into collaborative, respectful requests ("Could you kindly share the update by 2:00 PM if your schedule permits?").
3. Respect & Hierarchy: Maintain high deference and polite titles (e.g., "Dear Esteemed Colleague," or respectful executive address where applicable).
4. Clarity & Professionalism: While warm, ensure the core action items and business objectives remain distinct, professional, and clear.
5. Gracious Sign-offs: Close with genuine hospitality and well-wishes (e.g., "Wishing you and your team continued success," "Warmest regards").

Output Format:
Provide:
1. **Polished Email / Message**: The complete ready-to-send draft.
2. **Cultural Nuances & Adjustments**: 2-3 brief bullet points explaining key changes made to suit UAE business etiquette.
"""

# App Header
st.title("🇦🇪 Dubai Tone Coach")
st.markdown(
    "Transform blunt or rushed drafts into warm, relationship-first, and culturally "
    "polished business communication tailored for the UAE corporate landscape."
)

# Sidebar: API Key Configuration
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input(
        "Gemini API Key",
        type="password",
        value=os.environ.get("GEMINI_API_KEY", ""),
        help="Enter your Gemini API key or set it in your GEMINI_API_KEY environment variable."
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
    placeholder="e.g., Need the quarterly financial breakdown right now. If it's not sent by 3 PM the meeting is canceled."
)

col1, col2 = st.columns([1, 4])
with col1:
    submit_button = st.button("✨ Polish Tone", type="primary")

# Generation logic
if submit_button:
    api_key = api_key_input.strip()

    if not api_key:
        st.error("Please enter a valid Gemini API key in the sidebar or set the `GEMINI_API_KEY` environment variable.")
    elif not rough_message.strip():
        st.warning("Please provide a message or email draft to rewrite.")
    else:
        try:
            with st.spinner("Refining tone for UAE business etiquette..."):
                # Initialize GenAI Client
                client = genai.Client(api_key=api_key)

                # Generate rewritten content
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=rough_message,
                    config=types.GenerateContentConfig(
                        system_instruction=EMIRATI_BUSINESS_SYSTEM_INSTRUCTION,
                        temperature=0.4,
                    ),
                )

                st.success("Draft polished successfully!")
                st.markdown("### Result")
                st.markdown(response.text)

        except Exception as e:
            st.error(f"An error occurred while generating content: {e}")

