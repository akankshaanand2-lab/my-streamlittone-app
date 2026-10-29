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
st.caption("🟢 App Version 2.2 (Multi-Model Resolver)")

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

def get_candidate_models(api_key):
    """Gathers candidate models from Google, strictly excluding deprecated 2.5-flash."""
    candidates = ["models/gemini-3.8-flash", "models/gemini-2.0-flash", "models/gemini-1.5-flash-latest"]
    try:
        r = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}", timeout=10)
        if r.status_code == 200:
            found = [
                m["name"] for m in r.json().get("models", [])
                if "generateContent" in m.get("supportedGenerationMethods", [])
            ]
            # Exclude the deprecated 2.5-flash
            valid = [m for m in found if "2.5-flash" not in m]
            for m in valid:
                if m not in candidates:
                    candidates.append(m)
    except Exception:
        pass
    return candidates

if submit_button:
    api_key = api_key_input.strip()

    if not api_key:
        st.error("Please enter your Gemini API key in the sidebar.")
    elif not rough_message.strip():
        st.warning("Please enter a message.")
    else:
        try:
            with st.spinner("Finding active model and generating polished tone..."):
                candidates = get_candidate_models(api_key)
                
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": f"{EMIRATI_BUSINESS_SYSTEM_INSTRUCTION}\n\nDraft:\n{rough_message}"
                        }]
                    }],
                    "generationConfig": {"temperature": 0.4}
                }

                success = False
                last_error = ""

                # Try models in order until one succeeds
                for model in candidates:
                    url = f"https://generativelanguage.googleapis.com/v1beta/{model}:generateContent?key={api_key}"
                    try:
                        res = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=15)
                        if res.status_code == 200:
                            result = res.json()
                            text = result["candidates"][0]["content"]["parts"][0]["text"]
                            clean_model = model.replace("models/", "")
                            st.success(f"Polished using active model: `{clean_model}`")
                            st.markdown("### Result")
                            st.markdown(text)
                            success = True
                            break
                        else:
                            last_error = f"{model} -> {res.text}"
                    except Exception:
                        continue

                if not success:
                    st.error(f"Could not connect to an active model. Last error: {last_error}")

        except Exception as e:
            st.error(f"Error: {e}")
