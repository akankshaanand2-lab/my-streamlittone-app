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

# Main input
rough_message = st.text_area(
    "Paste your rough draft or draft message:",
    height=180,
    placeholder="e.g., Need the financial breakdown right now. If it's not sent by 3 PM the meeting is canceled."
)

submit_button = st.button("✨ Polish Tone", type="primary")

def find_working_model_and_api(api_key):
    """Queries Google ListModels across v1 and v1beta to discover available models."""
    for api_version in ["v1", "v1beta"]:
        url = f"https://generativelanguage.googleapis.com/{api_version}/models?key={api_key}"
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                models = data.get("models", [])
                
                # Filter models that support content generation
                supported = [
                    m["name"] for m in models 
                    if "generateContent" in m.get("supportedGenerationMethods", [])
                ]
                
                if supported:
                    # Preferred models in priority order
                    for pref in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-pro"]:
                        for model_path in supported:
                            if pref in model_path:
                                return api_version, model_path
                    
                    # Return the first supported model if preferred not found
                    return api_version, supported[0]
        except Exception:
            continue
            
    return None, None

if submit_button:
    api_key = api_key_input.strip()

    if not api_key:
        st.error("Please expand the sidebar (click >> on top-left) and enter your Gemini API key.")
    elif not rough_message.strip():
        st.warning("Please provide a message or email draft to rewrite.")
    else:
        try:
            with st.spinner("Connecting to Google and discovering available models..."):
                api_version, model_path = find_working_model_and_api(api_key)

                if not model_path:
                    st.error(
                        "No text-generation models found for this API key. "
                        "Please verify that the **Generative Language API** is enabled in your Google Cloud project."
                    )
                else:
                    # Call generateContent on the discovered working model
                    generate_url = f"https://generativelanguage.googleapis.com/{api_version}/{model_path}:generateContent?key={api_key}"
                    
                    prompt = f"{EMIRATI_BUSINESS_SYSTEM_INSTRUCTION}\n\n---\nDraft to rewrite:\n{rough_message}"
                    payload = {
                        "contents": [
                            {"parts": [{"text": prompt}]}
                        ],
                        "generationConfig": {
                            "temperature": 0.4
                        }
                    }

                    response = requests.post(
                        generate_url,
                        headers={"Content-Type": "application/json"},
                        json=payload,
                        timeout=20
                    )

                    result = response.json()

                    if response.status_code == 200:
                        clean_name = model_path.replace("models/", "")
                        rewritten_text = result["candidates"][0]["content"]["parts"][0]["text"]
                        
                        st.success(f"Polished using active model: `{clean_name}` ({api_version})")
                        st.markdown("### Result")
                        st.markdown(rewritten_text)
                    else:
                        error_msg = result.get("error", {}).get("message", response.text)
                        st.error(f"Google API Error ({response.status_code}): {error_msg}")

        except requests.exceptions.Timeout:
            st.error("The request timed out. Please try again.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")