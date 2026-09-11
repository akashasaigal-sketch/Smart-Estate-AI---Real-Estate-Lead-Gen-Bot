import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# .env file load karein
load_dotenv()

# Page Config Setup
st.set_page_config(page_title="Real Estate AI Assistant", page_icon="🏢", layout="centered")

# API Key & Client Setup (.env se GEMINI_API_KEY read kar raha hai)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Real Estate System Instructions
SYSTEM_PROMPT = """
You are 'NEXUS', a smart 24/7 AI Real Estate Assistant for a premium agency in Lahore, Pakistan.
Your Goal: Help potential property buyers, collect their budget/requirements, and schedule a site visit.

CORE CONVERSATION FLOW:
1. Greet politely in Roman Urdu mixed with English.
2. Ask if they want to Buy or Rent a property.
3. Ask for Property Type (House, Apartment, Commercial, or Plot).
4. Ask for Total Budget range (e.g. 1 Crore, 5 Crore).
5. Ask for Preferred Area in Lahore (DHA, Gulberg, Bahria Town, Lake City, etc.).
6. Schedule a Site Visit / Meeting timing.

FAQ HANDLING:
- If asked about Rent: Say "G bilkul, hamare paas rental houses aur apartments bhi available hain. Aapka monthly rental budget kitna hai?"
- If asked about Office Location: Say "Hamara office Gulberg III, Lahore mein hai. Office hours subah 10 baje se raat 8 baje tak hain."
- If asked about Office Visit: Say "Aap kisi bhi waqt office visit kar sakte hain! Kya main kal dopahar ka time confirm kar doon?"

RULES:
- Keep answers short (max 2-3 sentences).
- Speak professionally in Roman Urdu.
- Ask ONLY ONE question at a time.
"""

st.title("🏢 Real Estate 24/7 AI Assistant")
st.markdown("---")

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR UI ENHANCEMENTS ---
with st.sidebar:
    st.header("⚙️ Options & Quick Actions")
    
    # Reset / Clear Chat Button
    if st.button("🗑️ Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.subheader("💡 Quick Prompts")
    
    # Quick Action Buttons
    btn_buy = st.button("🏡 Buy Property", use_container_width=True)
    btn_rent = st.button("🏢 Rent Property", use_container_width=True)
    btn_location = st.button("📍 Office Location", use_container_width=True)

# Display Existing Chat Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Quick Button Logic
quick_text = None
if btn_buy:
    quick_text = "Mujhe property khareedni hai."
elif btn_rent:
    quick_text = "Mujhe property rent par chahiye."
elif btn_location:
    quick_text = "Aapka office kahan par hai?"

# Determine active input (Chat input OR Quick Button click)
user_input = st.chat_input("Apna message yahan type karein...") or quick_text

# Main Chat Input & Processing Logic
if user_input:
    # Render user message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Convert Streamlit roles ("assistant") to GenAI API roles ("model")
    formatted_history = []
    for msg in st.session_state.messages[:-1]:
        api_role = "model" if msg["role"] == "assistant" else "user"
        formatted_history.append(
            types.Content(
                role=api_role,
                parts=[types.Part.from_text(text=msg["content"])]
            )
        )

    with st.chat_message("assistant"):
        with st.spinner("Assistant reply kar raha hai..."):
            chat = client.chats.create(
                model="gemini-3.6-flash",
                history=formatted_history,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                )
            )
            
            response = chat.send_message(user_input)
            st.markdown(response.text)
            
            # Save assistant response to state
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
    # Agar quick action trigger hua tha toh page rerun karein UI sync rakhne ke liye
    if quick_text:
        st.rerun()