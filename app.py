import streamlit as st
import sqlite3
import requests
import pandas as pd
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import streamlit.components.v1 as components
import base64
from googletrans import Translator

st.set_page_config(page_title="Smart Waste App", layout="centered")



def get_base64_bg(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

bg_image = get_base64_bg("background.avif")
# 💫 Custom Background and Styling
# Toggle for Dark Mode
dark_mode = st.sidebar.checkbox("🌗 Dark Mode", value=False)


# CSS Styling
page_bg = f"""
<style>
/* Background image */
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/avif;base64,{bg_image}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}



/* Main card blur and transparency */
[data-testid="stAppViewContainer"] > .main {{
    backdrop-filter: blur(6px);
    background-color: {'rgba(25, 25, 25, 0.5)' if dark_mode else 'rgba(255, 255, 255, 0.65)'};
    border-radius: 20px;
    padding: 2rem;
    margin: 2rem;
    color: {'#fff' if dark_mode else '#000'};
}}



/* Custom scrollbar */
[data-testid="stAppViewContainer"]::-webkit-scrollbar {{
    width: 8px;
}}
 /* Custom sidebar toggle */
[data-testid="stSidebar"] {{
    background-color: {'rgba(0, 0, 0, 0.5)' if dark_mode else 'rgba(255, 255, 255, 0.8)'};
    backdrop-filter: blur(6px);
    color: {'#fff' if dark_mode else '#000'};
}}
/* Headings */
h1, h2, h3 {{
    color: {'#90ee90' if dark_mode else '#2E8B57'};
    text-shadow: 1px 1px 3px #00000040;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: linear-gradient(135deg, #E0F7FA 0%, #FFF9C4 100%);
    color: black;
    border-right: 2px solid #ddd;
}}

section[data-testid="stSidebar"] h1, 
section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] h3 {{
    color: black;
}}

/* Form labels */
label, .stTextInput label {{
    color: {'white' if dark_mode else 'black'} !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    font-weight: 500;
    font-size: 16px;
}}

/* --- Prediction Box --- */
.prediction-box {{
    background: linear-gradient(135deg, #e0f7fa, #ffffff);
    color: #004d40;
    border: 2px solid #26a69a;
    padding: 15px;
    border-radius: 12px;
    font-weight: bold;
    text-align: center;
    margin-top: 20px;
    box-shadow: 0 4px 12px rgba(0, 150, 136, 0.2);
    transition: all 0.3s ease-in-out;
}}

.prediction-box:hover {{
    box-shadow: 0 0 20px 4px rgba(0, 150, 136, 0.3);
    transform: scale(1.02);
}}

.dark .prediction-box {{
    background: #263238;
    color: #80cbc4;
    border: 2px solid #4db6ac;
    box-shadow: 0 0 20px 2px rgba(38, 166, 154, 0.3);
}}

/* --- Community Forum Box --- */
.community-box {{
    background: linear-gradient(145deg, #f1f8e9, #ffffff);
    border: 2px solid #aed581;
    border-radius: 16px;
    padding: 20px;
    margin-top: 25px;
    box-shadow: 0 4px 12px rgba(139, 195, 74, 0.25);
    transition: all 0.3s ease-in-out;
}}

.community-box:hover {{
    transform: scale(1.01);
    box-shadow: 0 6px 18px rgba(139, 195, 74, 0.3);
}}

.dark .community-box {{
    background: #1c2e1b;
    border: 2px solid #9ccc65;
    box-shadow: 0 6px 20px rgba(139, 195, 74, 0.4);
    color: #dcedc8;
}}

/* --- Warning Message --- */
.warning-msg {{
    color: #b00020;
    font-size: 15px;
    font-weight: 600;
    margin-top: 10px;
    text-align: center;
    background-color: rgba(255, 235, 238, 0.8);
    border: 1px solid #ffcdd2;
    border-radius: 8px;
    padding: 8px 12px;
}}

.dark .warning-msg {{
    color: #ff8a80;
    background-color: rgba(75, 0, 0, 0.7);
    border: 1px solid #ff5252;
}}


/* --- Buttons --- */
.stButton > button {{
    background-color: {'#90ee90' if dark_mode else '#2E8B57'};
    color: {'black' if dark_mode else 'white'};
    font-weight: bold;
    border-radius: 10px;
    padding: 10px 20px;
    transition: background-color 0.3s ease;
}}

.stButton > button:hover {{
    background-color: {'#77dd77' if dark_mode else '#3CB371'};
}}
</style>
"""

st.markdown(page_bg, unsafe_allow_html=True)



# Initialize translator
translator = Translator()

# Define translation function
def translate(text, dest_lang="en"):
    try:
        if dest_lang != "en":
            return translator.translate(text, dest=dest_lang).text
        return text
    except:
        return text

# Language selection
language_options = {
    "English": "en",
    "Hindi": "hi",
    "Bengali": "bn",
    "Spanish": "es",
    "French": "fr"
}
language_name = st.sidebar.selectbox("🌐 Choose your language", list(language_options.keys()))
dest_lang = language_options[language_name]

# Store selected language in session state
st.session_state.selected_language = dest_lang

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

# ------------------------- LOGIN SECTION --------------------------
if not st.session_state.logged_in:
    st.markdown(
        f"""
        <div style="text-align:center; padding: 2rem;">
            <h2 style="color:#4CAF50;">👤 {translate("Welcome to our AI-based Smart Waste Management App", dest_lang)}</h2>
            <p>{translate("Please enter your name to continue:", dest_lang)}</p>
        </div>
        """, unsafe_allow_html=True
    )

    name_input = st.text_input(translate("Enter your name:", dest_lang), key="login_name")

    if st.button(translate(" 🚪Login", dest_lang)):
        if name_input.strip() != "":
            st.session_state.user_name = name_input.strip().title()
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.warning(translate("Please enter a valid name to proceed.", dest_lang))
    st.stop()

# ------------------------ POST LOGIN VIEW -------------------------

# Show welcome banner
st.markdown(
    f"""
    <div style='text-align:center; background-color:#e0ffe0; padding:1rem; border-radius:10px; margin-bottom:1rem;'>
        <h3>👋 {translate("Welcome", dest_lang)}, <span style="color:#2E8B57;">{st.session_state.user_name}</span>!</h3>
    </div>
    """,
    unsafe_allow_html=True
)





def play_reward_sound():
    sound_html = """
        <audio autoplay>
            <source src="https://www.soundjay.com/buttons/sounds/button-10.mp3" type="audio/mpeg">
        </audio>
    """
    st.markdown(sound_html, unsafe_allow_html=True)



# Initialize session state variables
for key, default in {
    "uploaded_file": None,
    "predicted_class": None,
    "waste_type": None,
    "disposal_method": None,
    "show_prediction": False,
    "show_location_input": False,
    "user_points": 0,
} .items():
    if key not in st.session_state:
        st.session_state[key] = default


# File ID from your Google Drive share link
file_id = "1NgqMCMZDmltzmRAXbDFlxyhQMOH4UfTI"

# Output path where model will be saved in Streamlit Cloud
output_path = "DenseNet201.keras"

# Download only if file doesn't exist (to avoid repeated downloads on rerun)
if not os.path.exists(output_path):
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, output_path, quiet=False)

# Now load the model
from tensorflow.keras.models import load_model
model = load_model(output_path, compile=False)

# Class Names (Based on your dataset)
class_names = ['aerosol_cans', 'aluminum_food_cans', 'aluminum_soda_cans', 'cardboard_boxes',
               'cardboard_packaging', 'clothing', 'coffee_grounds', 'disposable_plastic_cutlery',
               'eggshells', 'food_waste', 'glass_beverage_bottles', 'glass_cosmetic_containers',
               'glass_food_jars', 'magazines', 'newspaper', 'office_paper', 'paper_cups',
               'plastic_cup_lids', 'plastic_detergent_bottles', 'plastic_food_containers',
               'plastic_shopping_bags', 'plastic_soda_bottles', 'plastic_straws', 'plastic_trash_bags',
               'plastic_water_bottles', 'shoes', 'steel_food_cans', 'styrofoam_cups',
               'styrofoam_food_containers', 'tea_bags']

# Waste Categories and Upcycling Ideas
data = {
    "Plastic": ["Turn bottles into planters", "Make eco-bricks", "Create DIY organizers"],
    "Paper and Cardboard": ["Make handmade paper", "Create gift wrapping paper", "Use for composting"],
    "Glass": ["Turn jars into lanterns", "Make decorative vases", "Use broken glass for mosaic art"],
    "Metal": ["Make tin can lanterns", "Create wall art from soda cans", "Reuse as storage containers"],
    "Organic Waste": ["Compost food scraps", "Make DIY plant fertilizer", "Use coffee grounds for skin exfoliation"],
    "Textiles": ["Turn old shirts into tote bags", "Make patchwork quilts", "Upcycle jeans into shorts"],
    "Styrofoam": ["Reuse for craft projects", "Insulate fragile items", "Create DIY decorations"]
}

# Waste Type Mapping
waste_category_mapping = {
    "Plastic": ['plastic_cup_lids', 'plastic_detergent_bottles', 'plastic_shopping_bags', 'plastic_straws', 'plastic_water_bottles', 'plastic_food_containers', 'plastic_soda_bottles'],
    "Paper and Cardboard": ['cardboard_boxes', 'cardboard_packaging', 'magazines', 'newspaper', 'office_paper', 'paper_cups'],
    "Glass": ['glass_beverage_bottles', 'glass_cosmetic_containers', 'glass_food_jars'],
    "Metal": ['aerosol_cans', 'aluminum_food_cans', 'aluminum_soda_cans', 'steel_food_cans'],
    "Organic Waste": ['coffee_grounds', 'eggshells', 'food_waste', 'tea_bags'],
    "Textiles": ['clothing', 'shoes'],
    "Styrofoam": ['styrofoam_cups', 'styrofoam_food_containers']
}

# Category Types
disposal_methods = {
    "Plastic": "Recyclable",
    "Paper and Cardboard": "Recyclable",
    "Glass": "Recyclable",
    "Metal": "Recyclable",
    "Organic Waste": "Disposable",
    "Textiles": "Upcyclable",
    "Styrofoam": "Upcyclable"
}

# Database Setup
def init_db():
    conn = sqlite3.connect("waste_management.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS waste_data (
            id INTEGER PRIMARY KEY,
            waste_type TEXT,
            description TEXT,
            upcycling_idea TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS community_ideas (
            id INTEGER PRIMARY KEY,
            user_name TEXT,
            idea TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Predict Function
def preprocess_and_predict(img):
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)
    predicted_class = class_names[np.argmax(prediction)]

    waste_type = "Unknown"
    for category, items in waste_category_mapping.items():
        if predicted_class in items:
            waste_type = category
            break

    return predicted_class, waste_type, disposal_methods.get(waste_type, "Unknown")


#Streamlit UI
st.image("https://cdn-icons-png.flaticon.com/512/2331/2331944.png", width=100)
st.title(translate("♻️ AI-Powered Smart Waste Managing App", dest_lang))
st.subheader(translate("Upload an image of waste to get recycling, upcycling or disposal suggestions!", dest_lang))


uploaded_file = st.file_uploader(translate("Choose an image...", dest_lang), type=["jpg", "png", "jpeg"])


if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file

    image_data = Image.open(uploaded_file)
    st.image(image_data, caption=translate("Uploaded Image", dest_lang), use_column_width=True)

    
    # Add Predict button
    if st.button(translate("🔍 Predict", dest_lang)):
        predicted_class, waste_type, disposal_method = preprocess_and_predict(image_data)
        
        # Save prediction in session state to retain after rerun
        st.session_state["predicted_class"] = predicted_class
        st.session_state["waste_type"] = waste_type
        st.session_state["disposal_method"] = disposal_method
        st.session_state["show_prediction"] = True
        st.session_state["show_location_input"] = False  # Reset

else:
    # Reset all prediction-related state if no file is uploaded
    st.session_state["uploaded_file"] = None
    st.session_state["predicted_class"] = None
    st.session_state["waste_type"] = None
    st.session_state["disposal_method"] = None
    st.session_state["show_prediction"] = False
    st.session_state["show_location_input"] = False

# Show prediction and interaction menu
if st.session_state.get("show_prediction", False):
    predicted_class = st.session_state["predicted_class"]
    waste_type = st.session_state["waste_type"]
    disposal_method = st.session_state["disposal_method"]
    st.success(translate(f"Predicted Waste Type: {predicted_class} ({waste_type}) - {disposal_method}", dest_lang))


    if disposal_method in ["Recyclable", "Upcyclable"]:
        question = translate(f"Would you like to {disposal_method.lower()} this item?", dest_lang)
        st.write(question)
        col1, col2 = st.columns(2)

        with col1:
            if st.button(translate("Yes", dest_lang)):
                st.subheader(translate(f"{disposal_method} Ideas", dest_lang))
                for idea in data.get(waste_type, []):
                    st.write(f"- {translate(idea, dest_lang)}")
                st.markdown(f"[🔎 Google {translate(disposal_method.lower(), dest_lang)} ideas for {translate(waste_type, dest_lang)}](https://www.google.com/search?q={waste_type}+{disposal_method.lower()}+ideas)")
                
                st.session_state["user_points"] += 10
                st.success(
                    translate(
                        f"🎉 Thank you for choosing to {disposal_method.lower()}! You've earned 10 points.",
                        dest_lang,
                    )
                )
                play_reward_sound()

                badge_html = """
                <div style="text-align: center; margin-top: 10px;">
                    <span style="
                        display: inline-block;
                        padding: 10px 20px;
                        background: linear-gradient(90deg, #00C9FF, #92FE9D);
                        color: white;
                        font-size: 18px;
                        font-weight: bold;
                        border-radius: 30px;
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                        animation: pop 0.5s ease-out;
                    ">🏅 +10 Points!</span>
                </div>
                <style>
                    @keyframes pop {
                        0% { transform: scale(0.8); opacity: 0; }
                        100% { transform: scale(1); opacity: 1; }
                    }
                </style>
                """
                components.html(badge_html, height=100)

        with col2:
            if "show_location_input" not in st.session_state:
                st.session_state["show_location_input"] = False

            if st.button(translate("No", dest_lang)):
                st.session_state["show_location_input"] = True

            if st.session_state["show_location_input"]:
                address = st.text_input(
                    translate("Enter your location (e.g., area, city, or address):", dest_lang),
                    key="no_address",
                )
                if address:
                    query = f"nearest {disposal_method.lower()} center in {address}"
                    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                    st.markdown(
                        translate("[🔎 Click here to find centers near you]", dest_lang).replace(
                            "[🔎 Click here to find centers near you]",
                            f"[🔎 Click here to find centers near you]({search_url})",
                        )
                    )

    elif disposal_method == "Disposable":
        st.warning(translate("This item is disposable and cannot be recycled or upcycled.", dest_lang))
        address = st.text_input(
            translate("Enter your location (e.g., area, city, or address):", dest_lang), key="disposable_address"
        )
        if address:
            query = f"nearest disposable waste collection center in {address}"
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            st.markdown(
                translate("[🔎 Search Disposal Locations Nearby]", dest_lang).replace(
                    "[🔎 Search Disposal Locations Nearby]", f"[🔎 Search Disposal Locations Nearby]({search_url})"
                )
            )
            st.session_state["user_points"] += 5
            st.success(translate("🗑️ Thanks for disposing of your waste responsibly! You've earned 5 points.", dest_lang))
            play_reward_sound()

            badge_html = """
            <div style="text-align: center; margin-top: 10px;">
                <span style="
                    display: inline-block;
                    padding: 10px 20px;
                    background: linear-gradient(90deg, #FF9A8B, #FF6A88);
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 30px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                    animation: pop 0.5s ease-out;
                ">🏅 +5 Points!</span>
            </div>
            <style>
                @keyframes pop {
                    0% { transform: scale(0.8); opacity: 0; }
                    100% { transform: scale(1); opacity: 1; }
                }
            </style>
            """
            components.html(badge_html, height=100)

def get_level(points):
    if points < 50:
        return "♻️ Eco Rookie"
    elif points < 100:
        return "🌱 Green Guardian"
    elif points < 200:
        return "🌿 Planet Protector"
    else:
        return "🌍 Eco Hero"
    
def get_progress(points):
    if points < 50:
        return points / 50
    elif points < 100:
        return (points - 50) / 50
    elif points < 200:
        return (points - 100) / 100
    else:
        return 1.0



# Sidebar for User Profile
st.sidebar.title(translate("User Profile", dest_lang))
st.sidebar.write(translate("Manage your profile and view your points.", dest_lang))

user_points = st.session_state.get("user_points", 0)
user_level = get_level(user_points)
st.sidebar.progress(get_progress(user_points))
st.sidebar.write(translate(f"👤 User Level: {user_level}", dest_lang))

st.sidebar.write(translate(f"💰 Points: {user_points}", dest_lang))

# ---- Logout Button ----
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.sidebar.success("You have been logged out. Please refresh the page.")




#Community Forum
with st.expander(translate("🌍 Community Forum: Share Your Upcycling Ideas", dest_lang)):
    user_name = st.text_input(translate("Your Name", dest_lang))
    user_idea = st.text_area(translate("Share your upcycling idea", dest_lang))

    if st.button("Submit Idea"):
         if user_name and user_idea:
            conn = sqlite3.connect("waste_management.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO community_ideas (user_name, idea) VALUES (?, ?)", (user_name, user_idea))
            conn.commit()
            conn.close()

            # ✅ Safely update points
            if "user_points" not in st.session_state:
                st.session_state["user_points"] = 0
            st.session_state["user_points"] += 20

            st.success(translate("🎉 Idea submitted successfully! You've earned 20 points.", dest_lang))
            play_reward_sound()

            # 🎖️ Show badge animation
            badge_html = """
            <div style="text-align: center; margin-top: 10px;">
                <span style="
                    display: inline-block;
                    padding: 10px 20px;
                    background: linear-gradient(90deg, #00C9FF, #92FE9D);
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 30px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                    animation: pop 0.5s ease-out;
                ">🏅 +20 Points!</span>
            </div>
        
            <style>
                @keyframes pop {
                    0% { transform: scale(0.8); opacity: 0; }
                    100% { transform: scale(1); opacity: 1; }
                }
            </style>
            """
            components.html(badge_html, height=100)

    else:
        st.warning(translate("Please enter both your name and an idea to submit.", dest_lang))       

    conn = sqlite3.connect("waste_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_name, idea FROM community_ideas")
    ideas = cursor.fetchall()
    conn.close()

    for name, idea in ideas:
        st.write(f"**{name}**: {translate(idea, dest_lang)}")


