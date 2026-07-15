# ==========================================
# LeadSpill Web App: Streamlit Slay Edition 💅✨
# ==========================================

import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os

# --- PAGE CONFIGURATION (The Vibe Setup) ---
st.set_page_config(
    page_title="LeadSpill Premium",
    page_icon="💅",
    layout="wide"
)

# --- THE AESTHETIC STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0d0d0d; color: #ffffff; }
    h1 { color: #ff69b4 !important; font-family: 'Helvetica Neue', sans-serif; }
    .stButton>button {
        background-color: #ff69b4 !important;
        color: white !important;
        border-radius: 20px !important;
        border: none !important;
        padding: 10px 24px !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- TITLE & DESCRIPTION ---
st.title("💅 LeadSpill Premium ✨")
st.write("### *Spilling the tea on your next top clients, live in the cloud!* 💖")

# --- SIDEBAR: SETTINGS & SECRETS ---
st.sidebar.header("⚙️ Slay Settings")
api_key_input = st.sidebar.text_input("🔑 Enter Gemini API Key (Optional)", type="password")

# --- ALGORITHM ENGINE (Slay Score) ---
def calculate_slay_score(phone, years_active):
    score = 30
    if phone and "No Phone" not in phone:
        score += 30
    if years_active and "New & Fresh" not in years_active:
        score += 25
        try:
            numeric_years = int(''.join(filter(str.isdigit, years_active)))
            if numeric_years >= 10:
                score += 15
        except ValueError:
            pass
    return min(score, 100)

# --- AI ENGINE (Gemini Pitches) ---
def generate_ai_pitch(api_key, business_name, category, location, years_active):
    if not api_key:
        return "No API key provided. Add one in the sidebar to generate custom pitches! 🔑"
        
    url = f"[https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=](https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=){api_key}"
    headers = {"Content-Type": "application/json"}
    
    system_prompt = "You are a professional marketing consultant. Write a bubbly, warm, highly persuasive 3-sentence B2B pitch."
    user_prompt = f"Write an email pitch to '{business_name}' ({category}) in '{location}' active for '{years_active}'."

    payload = {
        "contents": [{"parts": [{"text": user_prompt}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]}
    }

    # Exponential Backoff
    for delay in [1, 2, 4]:
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=8)
            if response.status_code == 200:
                return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception:
            pass
        time.sleep(delay)
    return "Pitch skipped due to API timeout."

# --- USER INPUT FIELDS ---
col1, col2 = st.columns(2)
with col1:
    niche = st.text_input("🔍 What niche are you hunting for?", value="Spas")
with col2:
    location = st.text_input("📍 In what city?", value="Miami")

# --- THE SCRAPING ENGINE ---
if st.button("🚀 Spill the Tea!"):
    if not niche or not location:
        st.error("Please fill in both fields, babe! 💖")
    else:
        st.info(f"✨ Searching for {niche} in {location}... This will take just a moment! ✨")
        
        search_url = f"[https://www.yellowpages.com/search?key=](https://www.yellowpages.com/search?key=){niche}&location={location}"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
        }

        try:
            response = requests.get(search_url, headers=headers)
            if response.status_code != 200:
                st.error("Oh no! The directory gave us a silent block. Try again in a minute!")
            else:
                soup = BeautifulSoup(response.text, "html.parser")
                listings = soup.find_all("div", class_="result")

                if not listings:
                    st.warning("No listings found! Try checking your spelling.")
                else:
                    leads_list = []
                    progress_bar = st.progress(0)
                    total_listings = min(len(listings), 5) # Process top 5 to keep it super fast for web users
                    
                    st.write(f"🎉 Processing top {total_listings} prime leads...")

                    for idx in range(total_listings):
                        business = listings[idx]
                        name_tag = business.find("a", class_="business-name")
                        name = name_tag.text.strip() if name_tag else "Unknown Slay Queen Business"

                        phone_tag = business.find("div", class_="phones")
                        phone = phone_tag.text.strip() if phone_tag else "No Phone (DM them!)"

                        categories_tag = business.find("div", class_="categories")
                        category = categories_tag.text.strip() if categories_tag else "General Business"

                        years_tag = business.find("div", class_="years-in-business")
                        years_active = years_tag.text.strip() if years_tag else "New & Fresh"

                        # Run our Features!
                        slay_score = calculate_slay_score(phone, years_active)
                        
                        pitch = "Pitch is generating..."
                        if api_key_input:
                            pitch = generate_ai_pitch(api_key_input, name, category, location, years_active)
                        else:
                            pitch = "Enter your API Key in the sidebar to generate a custom pitch! ✨"

                        leads_list.append({
                            "Business Name": name,
                            "Phone Number": phone,
                            "Category": category,
                            "Experience": years_active,
                            "Slay Score 🏆": slay_score,
                            "AI Pitch ✉️": pitch
                        })

                        progress_bar.progress((idx + 1) / total_listings)
                        time.sleep(0.5)

                    # Display results!
                    df = pd.DataFrame(leads_list)
                    st.success("💖 Leads spilled successfully! Here is your table:")
                    st.dataframe(df)

                    # Export button
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Leads Spreadsheet (CSV)",
                        data=csv,
                        file_name=f"leads_{niche.lower()}_{location.lower()}.csv",
                        mime="text/csv"
                    )
        except Exception as e:
            st.error(f"Error occurred: {e}")
