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
st.caption("🟢 App Version 2.1 (Auto-Detect Model)")

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

def find_active_model(api_key):
    """Finds the actual model Google has enabled for this key."""
    for ver in ["v1beta", "v1"]:
        try:
            r = requests.get(f"https://generativelanguage.googleapis.com/{ver}/models?key={api_key}", timeout=10)
            if r.status_code == 200:
                models = [
                    m["name"] for m in r.json().get("models", [])
                    if "generateContent" in m.get("supportedGenerationMethods", [])
                ]
                if models:
                    # Prefer flash models, otherwise first available
                    flash_models = [m for m in models if "flash" in m]
                    chosen = flash_models[0] if flash_models else models[0]
                    return ver, chosen
        except Exception:
            continue
    return None, None

if submit_button:
    api_key = api_key_input.strip()

    if not api_key:
        st.error("Please enter your Gemini API key in the sidebar.")
    elif not rough_message.strip():
        st.warning("Please enter a message.")
    else:
        try:
            with st.spinner("Finding your account's active model & polishing tone..."):
                ver, model_path = find_active_model(api_key)

                if not model_path:
                    st.error("No active text models found for this API key. Make sure the Generative Language API is enabled in your Google Cloud console.")
                else:
                    # Use the model that Google verified exists
                    url = f"https://generativelanguage.googleapis.com/{ver}/{model_path}:generateContent?key={api_key}"
                    
                    payload = {
                        "contents": [{
                            "parts": [{
                                "text": f"{EMIRATI_BUSINESS_SYSTEM_INSTRUCTION}\n\nDraft:\n{rough_message}"
                            }]
                        }],
                        "generationConfig": {"temperature": 0.4}
                    }

                    res = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=25)
                    result = res.json()

                    if res.status_code == 200:
                        text = result["candidates"][0]["content"]["parts"][0]["text"]
                        model_name = model_path.replace("models/", "")
                        st.success(f"Polished using active model: `{model_name}`")
                        st.markdown("### Result")
                        st.markdown(text)
                    else:
                        st.error(f"Error ({res.status_code}): {result.get('error', {}).get('message', res.text)}")

        except Exception as e:
            st.error(f"Error: {e}")
